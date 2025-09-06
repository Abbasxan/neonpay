"""
NEONPAY Subscriptions - Recurring payment management system
Handles subscription-based payments with automatic renewal
"""

import asyncio
import logging
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Union

logger = logging.getLogger(__name__)


class SubscriptionStatus(Enum):
    """Subscription status enumeration"""

    ACTIVE = "active"
    PAUSED = "paused"
    CANCELLED = "cancelled"
    EXPIRED = "expired"
    PENDING = "pending"


class SubscriptionPeriod(Enum):
    """Subscription billing periods"""

    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    YEARLY = "yearly"


@dataclass
class SubscriptionPlan:
    """
    Subscription plan configuration
    """

    plan_id: str
    name: str
    description: str
    price: int  # Price in Telegram Stars
    period: SubscriptionPeriod
    trial_days: int = 0
    max_subscribers: Optional[int] = None
    active: bool = True
    features: List[str] = field(default_factory=list)
    created_at: float = field(default_factory=time.time)

    def __post_init__(self) -> None:
        """Validate subscription plan configuration"""
        # Validate plan_id
        if not isinstance(self.plan_id, str) or not self.plan_id.strip():
            raise ValueError("Plan ID must be a non-empty string")

        if len(self.plan_id) > 64:
            raise ValueError("Plan ID must be 64 characters or less")

        # Validate name
        if not isinstance(self.name, str) or not self.name.strip():
            raise ValueError("Plan name must be a non-empty string")

        if len(self.name) > 100:
            raise ValueError("Plan name must be 100 characters or less")

        # Validate description
        if not isinstance(self.description, str) or not self.description.strip():
            raise ValueError("Plan description must be a non-empty string")

        if len(self.description) > 500:
            raise ValueError("Plan description must be 500 characters or less")

        # Validate price
        if not isinstance(self.price, int) or self.price <= 0:
            raise ValueError("Price must be a positive integer")

        if not (1 <= self.price <= 2500):
            raise ValueError("Price must be between 1 and 2500 Telegram Stars")

        # Validate period
        if not isinstance(self.period, SubscriptionPeriod):
            raise ValueError("Period must be a valid SubscriptionPeriod")

        # Validate trial_days
        if not isinstance(self.trial_days, int) or self.trial_days < 0:
            raise ValueError("Trial days must be a non-negative integer")

        if self.trial_days > 365:
            raise ValueError("Trial period cannot exceed 365 days")

        # Validate max_subscribers
        if self.max_subscribers is not None:
            if not isinstance(self.max_subscribers, int) or self.max_subscribers <= 0:
                raise ValueError("Max subscribers must be a positive integer")


@dataclass
class Subscription:
    """
    User subscription instance
    """

    subscription_id: str
    user_id: int
    plan: SubscriptionPlan
    status: SubscriptionStatus = SubscriptionStatus.PENDING
    created_at: float = field(default_factory=time.time)
    started_at: Optional[float] = None
    expires_at: Optional[float] = None
    next_billing_at: Optional[float] = None
    cancelled_at: Optional[float] = None
    trial_ends_at: Optional[float] = None
    payments_count: int = 0
    total_paid: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Initialize subscription dates"""
        if self.started_at is None and self.status == SubscriptionStatus.ACTIVE:
            self.started_at = time.time()

        # Set trial end date if trial period exists
        if self.plan.trial_days > 0 and self.trial_ends_at is None:
            self.trial_ends_at = time.time() + (self.plan.trial_days * 24 * 60 * 60)

    def is_in_trial(self) -> bool:
        """Check if subscription is in trial period"""
        if not self.trial_ends_at:
            return False
        return time.time() < self.trial_ends_at

    def is_active(self) -> bool:
        """Check if subscription is currently active"""
        return self.status == SubscriptionStatus.ACTIVE

    def is_expired(self) -> bool:
        """Check if subscription has expired"""
        if not self.expires_at:
            return False
        return time.time() > self.expires_at

    def days_until_renewal(self) -> Optional[int]:
        """Get days until next renewal"""
        if not self.next_billing_at:
            return None

        days = (self.next_billing_at - time.time()) / (24 * 60 * 60)
        return max(0, int(days))

    def calculate_next_billing_date(self) -> float:
        """Calculate next billing date based on plan period"""
        current_time = time.time()

        if self.plan.period == SubscriptionPeriod.DAILY:
            return current_time + (24 * 60 * 60)
        if self.plan.period == SubscriptionPeriod.WEEKLY:
            return current_time + (7 * 24 * 60 * 60)
        if self.plan.period == SubscriptionPeriod.MONTHLY:
            return current_time + (30 * 24 * 60 * 60)  # Approximate month
        if self.plan.period == SubscriptionPeriod.YEARLY:
            return current_time + (365 * 24 * 60 * 60)  # Approximate year

        # Defensive fallback (should never happen if enum is exhaustive)
        raise ValueError(f"Unsupported subscription period: {self.plan.period}")


class SubscriptionManager:
    """
    Subscription management system

    Handles subscription plans, user subscriptions, and automatic renewals
    """

    def __init__(self, max_plans: int = 100, max_subscriptions: int = 10000) -> None:
        self._plans: Dict[str, SubscriptionPlan] = {}
        self._subscriptions: Dict[str, Subscription] = {}
        self._user_subscriptions: Dict[int, List[str]] = (
            {}
        )  # user_id -> subscription_ids
        self._renewal_callbacks: List[Callable[[Subscription], Any]] = []
        self._expiration_callbacks: List[Callable[[Subscription], Any]] = []
        self._max_plans = max_plans
        self._max_subscriptions = max_subscriptions
        self._auto_renewal_enabled = True

        logger.info("SubscriptionManager initialized")

    def create_plan(
        self,
        plan_id: str,
        name: str,
        description: str,
        price: int,
        period: Union[SubscriptionPeriod, str],
        **kwargs: Any,
    ) -> SubscriptionPlan:
        """Create a new subscription plan"""
        # Check maximum plans limit
        if len(self._plans) >= self._max_plans:
            raise ValueError(f"Maximum number of plans ({self._max_plans}) reached")

        # Check if plan already exists
        if plan_id in self._plans:
            raise ValueError(f"Plan with ID '{plan_id}' already exists")

        # Convert string period to enum if needed
        if isinstance(period, str):
            try:
                period = SubscriptionPeriod(period)
            except ValueError:
                raise ValueError(f"Invalid period: {period}")

        plan = SubscriptionPlan(
            plan_id=plan_id,
            name=name,
            description=description,
            price=price,
            period=period,
            **kwargs,
        )

        self._plans[plan_id] = plan
        logger.info(f"Created subscription plan: {plan_id}")

        return plan

    def get_plan(self, plan_id: str) -> Optional[SubscriptionPlan]:
        """
        Get a subscription plan by ID

        Args:
            plan_id: ID of the plan to get

        Returns:
            SubscriptionPlan if found, None otherwise
        """
        """Get subscription plan by ID"""
        return self._plans.get(plan_id)

    def list_plans(self, active_only: bool = True) -> Dict[str, SubscriptionPlan]:
        """Get all subscription plans"""
        if active_only:
            return {k: v for k, v in self._plans.items() if v.active}
        return self._plans.copy()

    def subscribe_user(
        self, user_id: int, plan_id: str, subscription_id: Optional[str] = None
    ) -> Subscription:
        """Subscribe user to a plan"""
        # Check maximum subscriptions limit
        if len(self._subscriptions) >= self._max_subscriptions:
            raise ValueError(
                f"Maximum number of subscriptions ({self._max_subscriptions}) reached"
            )

        plan = self.get_plan(plan_id)
        if not plan:
            raise ValueError(f"Plan '{plan_id}' not found")

        if not plan.active:
            raise ValueError(f"Plan '{plan_id}' is not active")

        # Check plan subscriber limit
        if plan.max_subscribers:
            active_subs = sum(
                1
                for sub in self._subscriptions.values()
                if sub.plan.plan_id == plan_id and sub.is_active()
            )
            if active_subs >= plan.max_subscribers:
                raise ValueError(f"Plan '{plan_id}' has reached maximum subscribers")

        # Generate subscription ID if not provided
        if not subscription_id:
            subscription_id = f"sub_{user_id}_{plan_id}_{int(time.time())}"

        # Check if subscription already exists
        if subscription_id in self._subscriptions:
            raise ValueError(f"Subscription '{subscription_id}' already exists")

        subscription = Subscription(
            subscription_id=subscription_id,
            user_id=user_id,
            plan=plan,
            status=(
                SubscriptionStatus.ACTIVE
                if plan.trial_days == 0
                else SubscriptionStatus.PENDING
            ),
        )

        # Set billing dates
        if plan.trial_days == 0:
            subscription.next_billing_at = subscription.calculate_next_billing_date()
        else:
            subscription.next_billing_at = subscription.trial_ends_at

        self._subscriptions[subscription_id] = subscription

        # Add to user subscriptions
        if user_id not in self._user_subscriptions:
            self._user_subscriptions[user_id] = []
        self._user_subscriptions[user_id].append(subscription_id)

        logger.info(f"User {user_id} subscribed to plan {plan_id}")

        return subscription

    def get_subscription(self, subscription_id: str) -> Optional[Subscription]:
        """
        Get a subscription by ID

        Args:
            subscription_id: ID of the subscription to get

        Returns:
            Subscription if found, None otherwise
        """
        """Get subscription by ID"""
        return self._subscriptions.get(subscription_id)

    def get_user_subscriptions(
        self, user_id: int, active_only: bool = True
    ) -> List[Subscription]:
        """
        Get all subscriptions for a user

        Args:
            user_id: ID of the user
            active_only: Whether to return only active subscriptions

        Returns:
            List of user's subscriptions
        """
        """Get all subscriptions for a user"""
        subscription_ids = self._user_subscriptions.get(user_id, [])
        subscriptions = []

        for sub_id in subscription_ids:
            subscription = self._subscriptions.get(sub_id)
            if subscription:
                if not active_only or subscription.is_active():
                    subscriptions.append(subscription)

        return subscriptions

    def cancel_subscription(
        self, subscription_id: str, immediate: bool = False
    ) -> bool:
        """Cancel a subscription"""
        subscription = self.get_subscription(subscription_id)
        if not subscription:
            return False

        if immediate:
            subscription.status = SubscriptionStatus.CANCELLED
            subscription.expires_at = time.time()
        else:
            subscription.status = SubscriptionStatus.CANCELLED
            # Let it expire at next billing date
            if subscription.next_billing_at:
                subscription.expires_at = subscription.next_billing_at

        subscription.cancelled_at = time.time()

        logger.info(f"Cancelled subscription: {subscription_id}")
        return True

    def pause_subscription(self, subscription_id: str) -> bool:
        """Pause a subscription"""
        subscription = self.get_subscription(subscription_id)
        if not subscription or not subscription.is_active():
            return False

        subscription.status = SubscriptionStatus.PAUSED
        logger.info(f"Paused subscription: {subscription_id}")
        return True

    def resume_subscription(self, subscription_id: str) -> bool:
        """Resume a paused subscription"""
        subscription = self.get_subscription(subscription_id)
        if not subscription or subscription.status != SubscriptionStatus.PAUSED:
            return False

        subscription.status = SubscriptionStatus.ACTIVE
        subscription.next_billing_at = subscription.calculate_next_billing_date()

        logger.info(f"Resumed subscription: {subscription_id}")
        return True

    def process_payment(self, subscription_id: str, amount: int) -> bool:
        """Process a subscription payment"""
        subscription = self.get_subscription(subscription_id)
        if not subscription:
            return False

        subscription.payments_count += 1
        subscription.total_paid += amount
        subscription.status = SubscriptionStatus.ACTIVE

        # Update billing dates
        subscription.next_billing_at = subscription.calculate_next_billing_date()

        # If was in trial, mark trial as ended
        if subscription.is_in_trial():
            subscription.trial_ends_at = time.time()

        logger.info(
            f"Processed payment for subscription {subscription_id}: {amount} Stars"
        )
        return True

    def on_renewal(self, callback: Callable[[Subscription], Any]) -> None:
        """Register renewal callback"""
        if not callable(callback):
            raise ValueError("Callback must be callable")

        self._renewal_callbacks.append(callback)
        logger.info(f"Renewal callback registered: {callback.__name__}")

    def on_expiration(self, callback: Callable[[Subscription], Any]) -> None:
        """Register expiration callback"""
        if not callable(callback):
            raise ValueError("Callback must be callable")

        self._expiration_callbacks.append(callback)
        logger.info(f"Expiration callback registered: {callback.__name__}")

    async def _check_renewals(self) -> List[Subscription]:
        """
        Check for subscriptions that need to be renewed

        Returns:
            List of renewed subscriptions
        """
        """Check for subscriptions that need renewal"""
        current_time = time.time()
        renewals_needed = []

        for subscription in self._subscriptions.values():
            if (
                subscription.is_active()
                and subscription.next_billing_at
                and current_time >= subscription.next_billing_at
            ):

                renewals_needed.append(subscription)

                # Call renewal callbacks
                for callback in self._renewal_callbacks:
                    try:
                        if asyncio.iscoroutinefunction(callback):
                            await callback(subscription)
                        else:
                            callback(subscription)
                    except Exception as e:
                        logger.error(f"Error in renewal callback: {e}")

        return renewals_needed

    async def _check_expirations(self) -> List[Subscription]:
        """
        Check for expired subscriptions

        Returns:
            List of expired subscriptions
        """
        """Check for expired subscriptions"""
        expired_subscriptions = []

        for subscription in self._subscriptions.values():
            if (
                subscription.is_expired()
                and subscription.status != SubscriptionStatus.EXPIRED
            ):
                subscription.status = SubscriptionStatus.EXPIRED
                expired_subscriptions.append(subscription)

                # Call expiration callbacks
                for callback in self._expiration_callbacks:
                    try:
                        if asyncio.iscoroutinefunction(callback):
                            await callback(subscription)
                        else:
                            callback(subscription)
                    except Exception as e:
                        logger.error(f"Error in expiration callback: {e}")

        return expired_subscriptions

    def get_stats(self) -> Dict[str, Any]:
        """
        Get subscription statistics

        Returns:
            Dictionary containing subscription statistics
        """
        """Get subscription system statistics"""
        active_subs = sum(1 for sub in self._subscriptions.values() if sub.is_active())
        total_revenue = sum(sub.total_paid for sub in self._subscriptions.values())

        return {
            "total_plans": len(self._plans),
            "active_plans": sum(1 for plan in self._plans.values() if plan.active),
            "total_subscriptions": len(self._subscriptions),
            "active_subscriptions": active_subs,
            "total_revenue": total_revenue,
            "total_users": len(self._user_subscriptions),
            "max_plans": self._max_plans,
            "max_subscriptions": self._max_subscriptions,
        }

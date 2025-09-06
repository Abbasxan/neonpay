"""
NEONPAY Core - Modern payment processing system for Telegram bots
Supports multiple Telegram bot libraries with unified API
"""

import asyncio
import json
import logging
import re
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Union
from urllib.parse import urlparse

from .promotions import DiscountType, PromoSystem
from .security import ActionType, SecurityManager, ThreatLevel
from .subscriptions import SubscriptionManager, SubscriptionPeriod

logger = logging.getLogger(__name__)


class PaymentStatus(Enum):
    """Payment status enumeration"""

    PENDING = "pending"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    FAILED = "failed"
    REFUNDED = "refunded"


class BotLibrary(Enum):
    """Supported bot libraries"""

    PYROGRAM = "pyrogram"
    AIOGRAM = "aiogram"
    PYTHON_TELEGRAM_BOT = "python-telegram-bot"
    TELEBOT = "telebot"
    BOTAPI = "botapi"


def validate_url(url: str, require_https: bool = False) -> bool:
    """
    Validate URL format and security.
    Returns True if URL is valid and optionally HTTPS.
    """
    if not url:
        return False

    try:
        parsed = urlparse(url)
        if not parsed.scheme or not parsed.netloc:
            return False

        if require_https and parsed.scheme.lower() != "https":
            return False

        return True
    except Exception:
        return False


def validate_json_payload(payload: Any) -> bool:
    """
    Validate JSON payload structure and size.
    Returns True if payload is a dict, JSON-serializable, and <= 1024 bytes.
    """
    if not isinstance(payload, dict):
        return False

    try:
        # Попытка сериализации payload
        serialized = json.dumps(payload).encode("utf-8")
        return len(serialized) <= 1024
    except (TypeError, ValueError):
        return False


@dataclass
class PaymentStage:
    """
    Payment stage configuration

    Represents a complete payment setup with all necessary information
    for processing Telegram Stars payments.
    """

    title: str
    description: str
    price: int  # Price in Telegram Stars
    label: str = "Payment"
    photo_url: Optional[str] = None
    payload: Optional[Dict[str, Any]] = field(default_factory=dict)
    provider_token: str = ""
    start_parameter: str = "neonpay"

    def __post_init__(self) -> None:
        """Validate payment stage data with enhanced security"""
        # Validate price
        if not isinstance(self.price, int):
            raise ValueError("Price must be an integer")

        if not (1 <= self.price <= 2500):
            raise ValueError("Price must be between 1 and 2500 Telegram Stars")

        # Validate title
        if not isinstance(self.title, str) or not self.title.strip():
            raise ValueError("Title must be a non-empty string")

        if len(self.title) > 32:
            raise ValueError("Title must be 32 characters or less")

        # Validate description
        if not isinstance(self.description, str) or not self.description.strip():
            raise ValueError("Description must be a non-empty string")

        if len(self.description) > 255:
            raise ValueError("Description must be 255 characters or less")

        # Validate label
        if not isinstance(self.label, str) or not self.label.strip():
            raise ValueError("Label must be a non-empty string")

        if len(self.label) > 32:
            raise ValueError("Label must be 32 characters or less")

        # Validate photo URL
        if self.photo_url is not None:
            if not isinstance(self.photo_url, str):
                raise ValueError("Photo URL must be a string")

            if not validate_url(self.photo_url):
                raise ValueError("Photo URL must be a valid URL")

        # Validate payload
        if self.payload is not None:
            if not isinstance(self.payload, dict):
                raise ValueError("Payload must be a dictionary")

            if not validate_json_payload(self.payload):
                raise ValueError("Payload must be valid JSON and under 1024 bytes")

        # Validate start parameter
        if (
            not isinstance(self.start_parameter, str)
            or not self.start_parameter.strip()
        ):
            raise ValueError("Start parameter must be a non-empty string")

        if len(self.start_parameter) > 64:
            raise ValueError("Start parameter must be 64 characters or less")

        # Validate start parameter format (alphanumeric + underscore only)
        if not re.match(r"^[a-zA-Z0-9_]+$", self.start_parameter):
            raise ValueError(
                "Start parameter can only contain letters, numbers, and underscores"
            )


@dataclass
class PaymentResult:
    """Payment processing result with enhanced validation"""

    user_id: int
    amount: int
    currency: str = "XTR"
    status: PaymentStatus = PaymentStatus.COMPLETED
    stage: Optional[PaymentStage] = None
    transaction_id: Optional[str] = None
    timestamp: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Validate payment result data"""
        # Validate user_id
        if not isinstance(self.user_id, int) or self.user_id <= 0:
            raise ValueError("User ID must be a positive integer")

        # Validate amount
        if not isinstance(self.amount, int) or self.amount <= 0:
            raise ValueError("Amount must be a positive integer")

        # Validate currency
        if not isinstance(self.currency, str) or self.currency != "XTR":
            raise ValueError("Currency must be 'XTR' for Telegram Stars")

        # Validate status
        if not isinstance(self.status, PaymentStatus):
            raise ValueError("Status must be a valid PaymentStatus")

        # Validate transaction_id
        if self.transaction_id is not None:
            if (
                not isinstance(self.transaction_id, str)
                or not self.transaction_id.strip()
            ):
                raise ValueError("Transaction ID must be a non-empty string")

        # Validate timestamp
        if self.timestamp is not None:
            if not isinstance(self.timestamp, (int, float)) or self.timestamp <= 0:
                raise ValueError("Timestamp must be a positive number")

        # Validate metadata
        if not isinstance(self.metadata, dict):
            raise ValueError("Metadata must be a dictionary")


class PaymentAdapter(ABC):
    """Abstract base class for bot library adapters"""

    @abstractmethod
    async def send_invoice(self, user_id: int, stage: PaymentStage) -> bool:
        """Send payment invoice to user"""
        pass

    @abstractmethod
    async def setup_handlers(
        self, payment_callback: Callable[[PaymentResult], Any]
    ) -> None:
        """Setup payment event handlers"""
        pass

    @abstractmethod
    def get_library_info(self) -> Dict[str, str]:
        """Get information about the bot library"""
        pass


class NeonPayCore:
    """
    Core NEONPAY payment processor

    Universal payment system that works with multiple Telegram bot libraries
    through adapter pattern with enhanced features.
    """

    def __init__(
        self,
        adapter: PaymentAdapter,
        thank_you_message: Optional[str] = None,
        enable_logging: bool = True,
        max_stages: int = 100,
        enable_promotions: bool = True,
        enable_subscriptions: bool = True,
        enable_security: bool = True,
        webhook_secret: Optional[str] = None,
    ) -> None:
        self.adapter: PaymentAdapter = adapter
        self.thank_you_message: str = thank_you_message or "Thank you for your payment!"
        self._payment_stages: Dict[str, PaymentStage] = {}
        self._payment_callbacks: List[Callable[[PaymentResult], Any]] = []
        self._setup_complete: bool = False
        self._enable_logging: bool = enable_logging
        self._max_stages: int = max_stages

        self._promo_system: Optional[PromoSystem] = (
            PromoSystem() if enable_promotions else None
        )
        self._subscription_manager: Optional[SubscriptionManager] = (
            SubscriptionManager() if enable_subscriptions else None
        )
        self._security_manager: Optional[SecurityManager] = (
            SecurityManager(webhook_secret=webhook_secret) if enable_security else None
        )

        if self._enable_logging:
            logger.info(f"NeonPayCore initialized with {adapter.__class__.__name__}")
            if enable_promotions:
                logger.info("Promotions system enabled")
            if enable_subscriptions:
                logger.info("Subscriptions system enabled")
            if enable_security:
                logger.info("Security system enabled")

    def create_payment_stage(self, stage_id: str, stage: PaymentStage) -> None:
        """Create a new payment stage with validation"""
        if not isinstance(stage_id, str) or not stage_id.strip():
            raise ValueError("Stage ID is required")
        if len(stage_id) > 64:
            raise ValueError("Stage ID must be 64 characters or less")
        if stage_id in self._payment_stages:
            raise ValueError(f"Payment stage with ID '{stage_id}' already exists")
        if len(self._payment_stages) >= self._max_stages:
            raise ValueError(
                f"Maximum number of payment stages ({self._max_stages}) reached"
            )
        self._payment_stages[stage_id] = stage
        if self._enable_logging:
            logger.info(f"Created payment stage: {stage_id}")

    def get_payment_stage(self, stage_id: str) -> Optional[PaymentStage]:
        """Get payment stage by ID"""
        if not isinstance(stage_id, str):
            raise ValueError("Stage ID must be a string")
        return self._payment_stages.get(stage_id)

    def list_payment_stages(self) -> Dict[str, PaymentStage]:
        """Get all payment stages"""
        return self._payment_stages.copy()

    def remove_payment_stage(self, stage_id: str) -> bool:
        """Remove payment stage"""
        if not isinstance(stage_id, str):
            raise ValueError("Stage ID must be a string")
        if stage_id in self._payment_stages:
            del self._payment_stages[stage_id]
            if self._enable_logging:
                logger.info(f"Removed payment stage: {stage_id}")
            return True
        return False

    async def setup(self) -> None:
        """Initialize the payment system"""
        if self._setup_complete:
            return
        await self.adapter.setup_handlers(self._handle_payment)
        self._setup_complete = True
        if self._enable_logging:
            logger.info("Payment system initialized")

    def on_payment(self, callback: Callable[[PaymentResult], Any]) -> None:
        """Register payment completion callback"""
        if not callable(callback):
            raise ValueError("Callback must be callable")
        self._payment_callbacks.append(callback)
        if self._enable_logging:
            logger.info(f"Payment callback registered: {callback.__name__}")

    async def send_payment(
        self, user_id: int, stage_id: str, promo_code: Optional[str] = None
    ) -> bool:
        """Send payment invoice to user with validation and promo code support"""
        if not isinstance(user_id, int) or user_id <= 0:
            raise ValueError("User ID must be a positive integer")
        if not isinstance(stage_id, str) or not stage_id.strip():
            raise ValueError("Stage ID is required")

        if self._security_manager:
            is_allowed, _ = self._security_manager.check_rate_limit(
                user_id, ActionType.PAYMENT_REQUEST
            )
            if not is_allowed:
                logger.warning(f"Rate limit exceeded for user {user_id}")
                return False

        if not self._setup_complete:
            await self.setup()

        stage = self.get_payment_stage(stage_id)
        if not stage:
            logger.error("Payment stage not found")
            return False

        final_price: int = stage.price
        applied_promo: Optional[Any] = None

        if promo_code and self._promo_system:
            try:
                promo_result = self._promo_system.apply_promo_code(
                    promo_code, user_id, stage.price
                )
                final_price = promo_result[0]
                applied_promo = promo_result[1]
                logger.info(f"Promo code applied: {stage.price} -> {final_price} Stars")
            except ValueError as e:
                logger.warning(f"Promo code validation failed: {e}")
                return False

        if final_price != stage.price:
            from copy import deepcopy

            stage = deepcopy(stage)
            stage.price = final_price
            if applied_promo:
                stage.description += f" (Discount applied: {applied_promo.code})"

        try:
            result = await self.adapter.send_invoice(user_id, stage)
            if result:
                if self._enable_logging:
                    logger.info(f"Payment invoice sent: {stage.price} Stars")
            return result
        except Exception as e:
            logger.error(f"Failed to send payment invoice: {e}")
            return False

    def create_promo_code(
        self,
        code: str,
        discount_type: DiscountType,
        discount_value: Union[int, float],
        **kwargs: Any,
    ) -> Any:
        """Create a new promo code"""
        if not self._promo_system:
            raise RuntimeError("Promotions system is not enabled")
        return self._promo_system.create_promo_code(
            code, discount_type, discount_value, **kwargs
        )

    def validate_promo_code(
        self, code: str, user_id: int, amount: int
    ) -> Union[tuple[bool, str, Optional[Any]], Any]:
        """Validate promo code for user and amount"""
        if not self._promo_system:
            return False, "Promotions system is not enabled", None
        return self._promo_system.validate_promo_code(code, user_id, amount)

    def create_subscription_plan(
        self,
        plan_id: str,
        name: str,
        description: str,
        price: int,
        period: SubscriptionPeriod,
        **kwargs: Any,
    ) -> Any:
        """Create a new subscription plan"""
        if not self._subscription_manager:
            raise RuntimeError("Subscriptions system is not enabled")
        return self._subscription_manager.create_plan(
            plan_id, name, description, price, period, **kwargs
        )

    def subscribe_user(self, user_id: int, plan_id: str) -> Any:
        """Subscribe user to a plan"""
        if not self._subscription_manager:
            raise RuntimeError("Subscriptions system is not enabled")
        return self._subscription_manager.subscribe_user(user_id, plan_id)

    def get_user_subscriptions(
        self, user_id: int, active_only: bool = True
    ) -> List[Any]:
        """Get user subscriptions"""
        if not self._subscription_manager:
            return []
        return self._subscription_manager.get_user_subscriptions(user_id, active_only)

    def block_user(self, user_id: int, duration: Optional[int] = None) -> None:
        """Block user for specified duration"""
        if not self._security_manager:
            raise RuntimeError("Security system is not enabled")
        self._security_manager.block_user(user_id, duration)

    def trust_user(self, user_id: int) -> None:
        """Mark user as trusted"""
        if not self._security_manager:
            raise RuntimeError("Security system is not enabled")
        self._security_manager.trust_user(user_id)

    def get_user_risk_assessment(self, user_id: int) -> Dict[str, Any]:
        """Get user risk assessment"""
        if not self._security_manager:
            return {"error": "Security system is not enabled"}
        return self._security_manager.get_user_risk_assessment(user_id)

    async def _handle_payment(self, result: PaymentResult) -> None:
        """Internal payment handler with error handling and enhanced features"""
        if self._security_manager:
            is_allowed, _ = self._security_manager.check_rate_limit(
                result.user_id, ActionType.PAYMENT_COMPLETION
            )
            if not is_allowed:
                logger.warning(
                    f"Payment completion rate limit exceeded for user {result.user_id}"
                )
                return
            is_fraudulent, reason = self._security_manager.detect_payment_fraud(
                result.user_id, result.amount
            )
            if is_fraudulent:
                logger.warning(f"Fraudulent payment detected: {reason}")
                self._security_manager.report_suspicious_activity(
                    result.user_id,
                    "fraudulent_payment",
                    ThreatLevel.HIGH,
                    f"Fraudulent payment detected: {reason}",
                    amount=result.amount,
                )
                return
        if self._enable_logging:
            logger.info(f"Payment completed: {result.amount} Stars")
        for callback in self._payment_callbacks:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(result)
                else:
                    callback(result)
            except Exception as e:
                logger.error(f"Error in payment callback {callback.__name__}: {e}")

    def get_stats(self) -> Dict[str, Any]:
        """Get payment system statistics with enhanced modules"""
        stats: Dict[str, Any] = {
            "total_stages": len(self._payment_stages),
            "registered_callbacks": len(self._payment_callbacks),
            "setup_complete": self._setup_complete,
            "adapter_info": self.adapter.get_library_info(),
            "max_stages": self._max_stages,
            "logging_enabled": self._enable_logging,
        }
        if self._promo_system:
            stats["promotions"] = self._promo_system.get_stats()
        if self._subscription_manager:
            stats["subscriptions"] = self._subscription_manager.get_stats()
        if self._security_manager:
            stats["security"] = self._security_manager.get_security_stats()
        return stats

    async def cleanup_old_data(self, max_age_days: int = 30) -> Dict[str, int]:
        """Clean up old data from all modules"""
        cleanup_results: Dict[str, int] = {}
        if self._security_manager:
            cleanup_results["security_records"] = (
                self._security_manager.cleanup_old_data(max_age_days)
            )
        if self._promo_system:
            cleanup_results["expired_promos"] = len(
                self._promo_system.cleanup_expired()
            )
        if self._subscription_manager:
            renewals = await self._subscription_manager._check_renewals()
            expirations = await self._subscription_manager._check_expirations()
            cleanup_results["subscription_renewals"] = len(renewals)
            cleanup_results["subscription_expirations"] = len(expirations)
        return cleanup_results

    @property
    def promotions(self) -> Optional[PromoSystem]:
        """Access to promotions system"""
        return self._promo_system

    @property
    def subscriptions(self) -> Optional[SubscriptionManager]:
        """Access to subscriptions system"""
        return self._subscription_manager

    @property
    def security(self) -> Optional[SecurityManager]:
        """Access to security system"""
        return self._security_manager

"""
NEONPAY Security - Rate limiting and protection system
Provides comprehensive security features for payment processing
"""

import hashlib
import hmac
import logging
import time
from collections import defaultdict, deque
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple

logger = logging.getLogger(__name__)


class ThreatLevel(Enum):
    """Security threat levels"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ActionType(Enum):
    """Types of actions that can be rate limited"""

    PAYMENT_REQUEST = "payment_request"
    PAYMENT_COMPLETION = "payment_completion"
    PROMO_CODE_USE = "promo_code_use"
    SUBSCRIPTION_CREATE = "subscription_create"
    API_CALL = "api_call"


@dataclass
class RateLimit:
    """Rate limit configuration"""

    max_requests: int
    time_window: int  # seconds
    action_type: ActionType
    enabled: bool = True

    def __post_init__(self) -> None:
        """Validate rate limit configuration"""
        if not isinstance(self.max_requests, int) or self.max_requests <= 0:
            raise ValueError("Max requests must be a positive integer")

        if not isinstance(self.time_window, int) or self.time_window <= 0:
            raise ValueError("Time window must be a positive integer")

        if not isinstance(self.action_type, ActionType):
            raise ValueError("Action type must be a valid ActionType")


@dataclass
class SecurityEvent:
    """Security event record"""

    user_id: int
    event_type: str
    threat_level: ThreatLevel
    description: str
    timestamp: float = field(default_factory=time.time)
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class UserSecurityProfile:
    """User  security profile with risk assessment"""

    user_id: int
    risk_score: float = 0.0
    is_blocked: bool = False
    blocked_until: Optional[float] = None
    failed_attempts: int = 0
    last_activity: float = field(default_factory=time.time)
    suspicious_activities: List[SecurityEvent] = field(default_factory=list)
    trusted: bool = False
    created_at: float = field(default_factory=time.time)

    def is_currently_blocked(self) -> bool:
        """Check if user is currently blocked"""
        if not self.is_blocked:
            return False

        if self.blocked_until and time.time() > self.blocked_until:
            self.is_blocked = False
            self.blocked_until = None
            return False

        return True

    def add_suspicious_activity(self, event: SecurityEvent) -> None:
        """Add suspicious activity to profile"""
        self.suspicious_activities.append(event)
        self.last_activity = time.time()

        # Keep only last 100 events
        if len(self.suspicious_activities) > 100:
            self.suspicious_activities = self.suspicious_activities[-100:]

        # Update risk score based on threat level
        threat_scores: Dict[ThreatLevel, int] = {
            ThreatLevel.LOW: 1,
            ThreatLevel.MEDIUM: 5,
            ThreatLevel.HIGH: 15,
            ThreatLevel.CRITICAL: 50,
        }

        self.risk_score += threat_scores.get(event.threat_level, 1)

        # Decay risk score over time (max 100)
        self.risk_score = min(100, self.risk_score)


class RateLimiter:
    """Rate limiting implementation using sliding window"""

    def __init__(self) -> None:
        self._requests: Dict[str, deque[float]] = defaultdict(deque)
        self._limits: Dict[ActionType, RateLimit] = {}

    def set_limit(
        self, action_type: ActionType, max_requests: int, time_window: int
    ) -> None:
        """Set rate limit for action type"""
        self._limits[action_type] = RateLimit(
            max_requests=max_requests, time_window=time_window, action_type=action_type
        )
        logger.info(
            f"Set rate limit for {action_type.value}: {max_requests}/{time_window}s"
        )

    def is_allowed(
        self, user_id: int, action_type: ActionType
    ) -> Tuple[bool, Optional[int]]:
        """
        Check if action is allowed for user

        Returns:
            (is_allowed, retry_after_seconds)
        """
        if action_type not in self._limits:
            return True, None

        limit = self._limits[action_type]
        if not limit.enabled:
            return True, None

        key = f"{user_id}:{action_type.value}"
        current_time = time.time()

        # Clean old requests
        while (
            self._requests[key]
            and current_time - self._requests[key][0] > limit.time_window
        ):
            self._requests[key].popleft()

        # Check if limit exceeded
        if len(self._requests[key]) >= limit.max_requests:
            # Calculate retry after time
            oldest_request = self._requests[key][0]
            retry_after = int(limit.time_window - (current_time - oldest_request)) + 1
            return False, retry_after

        # Add current request
        self._requests[key].append(current_time)
        return True, None

    def get_remaining_requests(
        self, user_id: int, action_type: ActionType
    ) -> Optional[int]:
        """Get remaining requests for user and action type"""
        if action_type not in self._limits:
            return None

        limit = self._limits[action_type]
        key = f"{user_id}:{action_type.value}"
        current_time = time.time()

        # Clean old requests
        while (
            self._requests[key]
            and current_time - self._requests[key][0] > limit.time_window
        ):
            self._requests[key].popleft()

        return max(0, limit.max_requests - len(self._requests[key]))

    def reset_user_limits(self, user_id: int) -> None:
        """Reset all rate limits for a user"""
        keys_to_remove = [
            key for key in self._requests.keys() if key.startswith(f"{user_id}:")
        ]
        for key in keys_to_remove:
            del self._requests[key]

        logger.info(f"Reset rate limits for user {user_id}")


class SecurityManager:
    """
    Comprehensive security management system

    Provides rate limiting, fraud detection, and user protection
    """

    def __init__(
        self,
        webhook_secret: Optional[str] = None,
        max_risk_score: float = 80.0,
        auto_block_enabled: bool = True,
    ) -> None:
        self._rate_limiter = RateLimiter()
        self._user_profiles: Dict[int, UserSecurityProfile] = {}
        self._blocked_ips: Set[str] = set()
        self._webhook_secret = webhook_secret
        self._max_risk_score = max_risk_score
        self._auto_block_enabled = auto_block_enabled
        self._security_events: List[SecurityEvent] = []

        # Set default rate limits
        self._set_default_limits()

        logger.info("SecurityManager initialized")

    def _set_default_limits(self) -> None:
        """Set default rate limits"""
        # Payment requests: 10 per minute
        self._rate_limiter.set_limit(ActionType.PAYMENT_REQUEST, 10, 60)

        # Payment completions: 5 per minute
        self._rate_limiter.set_limit(ActionType.PAYMENT_COMPLETION, 5, 60)

        # Promo code usage: 3 per minute
        self._rate_limiter.set_limit(ActionType.PROMO_CODE_USE, 3, 60)

        # Subscription creation: 2 per hour
        self._rate_limiter.set_limit(ActionType.SUBSCRIPTION_CREATE, 2, 3600)

        # API calls: 100 per minute
        self._rate_limiter.set_limit(ActionType.API_CALL, 100, 60)

    def set_rate_limit(
        self, action_type: ActionType, max_requests: int, time_window: int
    ) -> None:
        """Set custom rate limit"""
        self._rate_limiter.set_limit(action_type, max_requests, time_window)

    def check_rate_limit(
        self, user_id: int, action_type: ActionType
    ) -> Tuple[bool, Optional[int]]:
        """Check if user action is within rate limits"""
        # Check if user is blocked
        profile = self._get_user_profile(user_id)
        if profile.is_currently_blocked():
            return False, None

        return self._rate_limiter.is_allowed(user_id, action_type)

    def _get_user_profile(self, user_id: int) -> UserSecurityProfile:
        """Get or create user security profile"""
        if user_id not in self._user_profiles:
            self._user_profiles[user_id] = UserSecurityProfile(user_id=user_id)
        return self._user_profiles[user_id]

    def report_suspicious_activity(
        self,
        user_id: int,
        event_type: str,
        threat_level: ThreatLevel,
        description: str,
        **metadata: Any,
    ) -> None:
        """Report suspicious activity"""
        event = SecurityEvent(
            user_id=user_id,
            event_type=event_type,
            threat_level=threat_level,
            description=description,
            metadata=metadata,
        )

        profile = self._get_user_profile(user_id)
        profile.add_suspicious_activity(event)

        self._security_events.append(event)

        # Keep only last 10000 events
        if len(self._security_events) > 10000:
            self._security_events = self._security_events[-10000:]

        # Auto-block if risk score too high
        if (
            self._auto_block_enabled
            and profile.risk_score >= self._max_risk_score
            and not profile.trusted
        ):
            self.block_user(user_id, duration=3600)  # Block for 1 hour

        logger.warning(f"Suspicious activity reported: {event_type} for user {user_id}")

    def block_user(self, user_id: int, duration: Optional[int] = None) -> None:
        """Block user for specified duration"""
        profile = self._get_user_profile(user_id)
        profile.is_blocked = True

        if duration:
            profile.blocked_until = time.time() + duration

        # Reset rate limits for blocked user
        self._rate_limiter.reset_user_limits(user_id)

        logger.warning(
            f"User  {user_id} blocked"
            + (f" for {duration}s" if duration else " permanently")
        )

    def unblock_user(self, user_id: int) -> None:
        """Unblock user"""
        profile = self._get_user_profile(user_id)
        profile.is_blocked = False
        profile.blocked_until = None
        profile.risk_score = max(0, profile.risk_score - 20)  # Reduce risk score

        logger.info(f"User  {user_id} unblocked")

    def trust_user(self, user_id: int) -> None:
        """Mark user as trusted (immune to auto-blocking)"""
        profile = self._get_user_profile(user_id)
        profile.trusted = True
        profile.risk_score = 0

        if profile.is_blocked:
            self.unblock_user(user_id)

        logger.info(f"User  {user_id} marked as trusted")

    def block_ip(self, ip_address: str) -> None:
        """Block IP address"""
        self._blocked_ips.add(ip_address)
        logger.warning(f"IP address blocked: {ip_address}")

    def unblock_ip(self, ip_address: str) -> None:
        """Unblock IP address"""
        self._blocked_ips.discard(ip_address)
        logger.info(f"IP address unblocked: {ip_address}")

    def is_ip_blocked(self, ip_address: str) -> bool:
        """Check if IP address is blocked"""
        return ip_address in self._blocked_ips

    def verify_webhook_signature(self, payload: bytes, signature: str) -> bool:
        """Verify webhook signature"""
        if not self._webhook_secret:
            logger.warning("Webhook secret not configured")
            return True  # Allow if no secret configured

        try:
            expected_signature = hmac.new(
                self._webhook_secret.encode(), payload, hashlib.sha256
            ).hexdigest()

            return hmac.compare_digest(signature, expected_signature)
        except Exception as e:
            logger.error(f"Webhook signature verification failed: {e}")
            return False

    def detect_payment_fraud(
        self, user_id: int, amount: int, payment_method: str = "telegram_stars"
    ) -> Tuple[bool, str]:
        """
        Detect potential payment fraud

        Returns:
            (is_fraudulent, reason)
        """
        profile = self._get_user_profile(user_id)

        # Check if user is blocked
        if profile.is_currently_blocked():
            return True, "User  is blocked"

        # Check high risk score
        if profile.risk_score > self._max_risk_score:
            return True, "High risk score"

        # Check for rapid successive payments
        recent_events = [
            event
            for event in profile.suspicious_activities
            if (
                event.event_type == "payment_completion"
                and time.time() - event.timestamp < 300
            )  # Last 5 minutes
        ]

        if len(recent_events) > 5:
            return True, "Too many recent payments"

        # Check for unusually high amounts
        if amount > 1000:  # More than 1000 Stars
            recent_high_payments = [
                event
                for event in profile.suspicious_activities
                if (
                    event.event_type == "high_amount_payment"
                    and time.time() - event.timestamp < 3600
                )  # Last hour
            ]

            if len(recent_high_payments) > 2:
                return True, "Multiple high-amount payments"

        return False, ""

    def get_user_risk_assessment(self, user_id: int) -> Dict[str, Any]:
        """Get comprehensive risk assessment for user"""
        profile = self._get_user_profile(user_id)

        return {
            "user_id": user_id,
            "risk_score": profile.risk_score,
            "is_blocked": profile.is_currently_blocked(),
            "is_trusted": profile.trusted,
            "failed_attempts": profile.failed_attempts,
            "suspicious_activities_count": len(profile.suspicious_activities),
            "last_activity": profile.last_activity,
            "account_age_days": (time.time() - profile.created_at) / (24 * 60 * 60),
        }

    def cleanup_old_data(self, max_age_days: int = 30) -> int:
        """Clean up old security data"""
        cutoff_time = time.time() - (max_age_days * 24 * 60 * 60)
        cleaned_count = 0

        # Clean old security events
        old_events_count = len(self._security_events)
        self._security_events = [
            event for event in self._security_events if event.timestamp > cutoff_time
        ]
        cleaned_count += old_events_count - len(self._security_events)

        # Clean old user profile activities
        for profile in self._user_profiles.values():
            old_activities_count = len(profile.suspicious_activities)
            profile.suspicious_activities = [
                activity
                for activity in profile.suspicious_activities
                if activity.timestamp > cutoff_time
            ]
            cleaned_count += old_activities_count - len(profile.suspicious_activities)

            # Decay risk scores for inactive users
            if profile.last_activity < cutoff_time:
                profile.risk_score = max(0, profile.risk_score * 0.5)

        logger.info(f"Cleaned up {cleaned_count} old security records")
        return cleaned_count

    def get_security_stats(self) -> Dict[str, Any]:
        """Get security system statistics"""
        blocked_users = sum(
            1
            for profile in self._user_profiles.values()
            if profile.is_currently_blocked()
        )
        high_risk_users = sum(
            1 for profile in self._user_profiles.values() if profile.risk_score > 50
        )
        trusted_users = sum(
            1 for profile in self._user_profiles.values() if profile.trusted
        )

        return {
            "total_users": len(self._user_profiles),
            "blocked_users": blocked_users,
            "high_risk_users": high_risk_users,
            "trusted_users": trusted_users,
            "blocked_ips": len(self._blocked_ips),
            "security_events": len(self._security_events),
            "auto_block_enabled": self._auto_block_enabled,
            "max_risk_score": self._max_risk_score,
        }

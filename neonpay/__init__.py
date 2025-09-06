"""
NEONPAY - Modern Telegram Stars Payment Library

Simple and powerful payment processing for Telegram bots
"""

# Core classes
from .core import NeonPayCore, PaymentStage, PaymentResult, PaymentStatus, BotLibrary

# Promotions system
from .promotions import PromoSystem, PromoCode, DiscountType

# Subscriptions system
from .subscriptions import (
    SubscriptionManager,
    SubscriptionPlan,
    Subscription,
    SubscriptionStatus,
    SubscriptionPeriod,
)

# Security system
from .security import (
    SecurityManager,
    RateLimiter,
    SecurityEvent,
    UserSecurityProfile,
    ThreatLevel,
    ActionType,
)

# Factory
from .factory import create_neonpay

# Errors
from .errors import (
    NeonPayError,
    PaymentError,
    ConfigurationError,
    AdapterError,
    ValidationError,
    StarsPaymentError,  # Legacy compatibility
)

# Legacy compatibility
from .payments import NeonStars

# Version
from ._version import __version__

__author__ = "Abbas Sultanov"
__email__ = "sultanov.abas@outlook.com"

from typing import Any, Optional, Type


# Lazy loading for adapters to avoid import errors
class _LazyAdapter:
    """Lazy loading adapter class"""

    def __init__(self, adapter_name: str) -> None:
        self.adapter_name: str = adapter_name
        self._adapter_class: Optional[Type[Any]] = None

    def _load_adapter(self) -> Type[Any]:
        """Load the actual adapter class"""
        if self._adapter_class is None:
            try:
                if self.adapter_name == "PyrogramAdapter":
                    from .adapters.pyrogram_adapter import PyrogramAdapter

                    self._adapter_class = PyrogramAdapter
                elif self.adapter_name == "AiogramAdapter":
                    from .adapters.aiogram_adapter import AiogramAdapter

                    self._adapter_class = AiogramAdapter
                elif self.adapter_name == "PythonTelegramBotAdapter":
                    from .adapters.ptb_adapter import PythonTelegramBotAdapter

                    self._adapter_class = PythonTelegramBotAdapter
                elif self.adapter_name == "TelebotAdapter":
                    from .adapters.telebot_adapter import TelebotAdapter

                    self._adapter_class = TelebotAdapter
                elif self.adapter_name == "RawAPIAdapter":
                    from .adapters.raw_api_adapter import RawAPIAdapter

                    self._adapter_class = RawAPIAdapter
                elif self.adapter_name == "BotAPIAdapter":
                    from .adapters.botapi_adapter import BotAPIAdapter

                    self._adapter_class = BotAPIAdapter
                else:
                    raise ImportError(f"Unknown adapter: {self.adapter_name}")
            except ImportError as e:
                raise ImportError(
                    f"Failed to import {self.adapter_name}: {e}. "
                    f"Install required dependencies: pip install neonpay[{self.adapter_name.lower().replace('adapter', '')}]"
                )
        return self._adapter_class

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        """Create adapter instance when called"""
        adapter_class = self._load_adapter()
        return adapter_class(*args, **kwargs)

    def __getattr__(self, name: str) -> Any:
        """Delegate attribute access to the actual adapter class"""
        adapter_class = self._load_adapter()
        return getattr(adapter_class, name)


# Create lazy adapter instances (type: Any to satisfy mypy)
PyrogramAdapter: Any = _LazyAdapter("PyrogramAdapter")
AiogramAdapter: Any = _LazyAdapter("AiogramAdapter")
PythonTelegramBotAdapter: Any = _LazyAdapter("PythonTelegramBotAdapter")
TelebotAdapter: Any = _LazyAdapter("TelebotAdapter")
RawAPIAdapter: Any = _LazyAdapter("RawAPIAdapter")
BotAPIAdapter: Any = _LazyAdapter("BotAPIAdapter")

__all__ = [
    # Core
    "NeonPayCore",
    "PaymentStage",
    "PaymentResult",
    "PaymentStatus",
    "BotLibrary",
    # Promotions
    "PromoSystem",
    "PromoCode",
    "DiscountType",
    # Subscriptions
    "SubscriptionManager",
    "SubscriptionPlan",
    "Subscription",
    "SubscriptionStatus",
    "SubscriptionPeriod",
    # Security
    "SecurityManager",
    "RateLimiter",
    "SecurityEvent",
    "UserSecurityProfile",
    "ThreatLevel",
    "ActionType",
    # Adapters (lazy loaded)
    "PyrogramAdapter",
    "AiogramAdapter",
    "PythonTelegramBotAdapter",
    "TelebotAdapter",
    "RawAPIAdapter",
    "BotAPIAdapter",
    # Factory
    "create_neonpay",
    # Errors
    "NeonPayError",
    "PaymentError",
    "ConfigurationError",
    "AdapterError",
    "ValidationError",
    "StarsPaymentError",
    # Legacy
    "NeonStars",
    # Version (public only)
    "__version__",
]

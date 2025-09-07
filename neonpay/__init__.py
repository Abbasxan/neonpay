"""
NEONPAY - Modern Telegram Stars Payment Library

Simple and powerful payment processing for Telegram bots
"""

# Version
from ._version import __version__

# Analytics system
from .analytics import (
    AnalyticsDashboard,
    AnalyticsManager,
    AnalyticsPeriod,
    ConversionData,
    ProductPerformance,
    RevenueData,
)

# Backup system
from .backup import (
    BackupConfig,
    BackupInfo,
    BackupManager,
    BackupStatus,
    BackupType,
    SyncConfig,
    SyncManager,
)

# Core classes
from .core import BotLibrary, NeonPayCore, PaymentResult, PaymentStage, PaymentStatus

# Errors
from .errors import StarsPaymentError  # Legacy compatibility
from .errors import (
    AdapterError,
    ConfigurationError,
    NeonPayError,
    PaymentError,
    ValidationError,
)

# Event collection system
from .event_collector import (
    CentralEventCollector,
    EventCollectorConfig,
    MultiBotEventCollector,
    RealTimeEventCollector,
)

# Factory
from .factory import create_neonpay

# Multi-bot analytics system
from .multi_bot_analytics import (
    BotAnalytics,
    EventType,
    MultiBotAnalyticsManager,
    MultiBotEvent,
    NetworkAnalytics,
)

# Notifications system
from .notifications import (
    NotificationConfig,
    NotificationManager,
    NotificationMessage,
    NotificationPriority,
    NotificationType,
)

# Legacy compatibility
from .payments import NeonStars

# Promotions system
from .promotions import DiscountType, PromoCode, PromoSystem

# Security system
from .security import (
    ActionType,
    RateLimiter,
    SecurityEvent,
    SecurityManager,
    ThreatLevel,
    UserSecurityProfile,
)

# Subscriptions system
from .subscriptions import (
    Subscription,
    SubscriptionManager,
    SubscriptionPeriod,
    SubscriptionPlan,
    SubscriptionStatus,
)

# Sync system
from .sync import (
    ConflictResolution,
    MultiBotSyncManager,
)
from .sync import SyncConfig as BotSyncConfig
from .sync import (
    SyncConflict,
    SyncDirection,
)
from .sync import SyncManager as BotSyncManager
from .sync import (
    SyncResult,
    SyncStatus,
)

# Templates system
from .templates import (
    TemplateCategory,
    TemplateConfig,
    TemplateManager,
    TemplateProduct,
    TemplateType,
    ThemeColor,
    ThemeConfig,
)

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
    # Analytics
    "AnalyticsManager",
    "AnalyticsPeriod",
    "AnalyticsDashboard",
    "RevenueData",
    "ConversionData",
    "ProductPerformance",
    # Notifications
    "NotificationManager",
    "NotificationType",
    "NotificationPriority",
    "NotificationConfig",
    "NotificationMessage",
    # Templates
    "TemplateManager",
    "TemplateType",
    "ThemeConfig",
    "ThemeColor",
    "TemplateConfig",
    "TemplateProduct",
    "TemplateCategory",
    # Backup
    "BackupManager",
    "BackupType",
    "BackupStatus",
    "BackupConfig",
    "BackupInfo",
    "SyncManager",
    "SyncConfig",
    # Bot Sync
    "BotSyncManager",
    "MultiBotSyncManager",
    "BotSyncConfig",
    "SyncDirection",
    "SyncStatus",
    "ConflictResolution",
    "SyncResult",
    "SyncConflict",
    # Multi-bot Analytics
    "MultiBotAnalyticsManager",
    "MultiBotEvent",
    "BotAnalytics",
    "NetworkAnalytics",
    "EventType",
    # Event Collection
    "MultiBotEventCollector",
    "EventCollectorConfig",
    "CentralEventCollector",
    "RealTimeEventCollector",
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

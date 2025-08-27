"""
NEONPAY - Modern Telegram Stars Payment Library
Simple and powerful payment processing for Telegram bots
"""

# Core classes
from .core import (
    NeonPayCore,
    PaymentStage,
    PaymentResult,
    PaymentStatus,
    BotLibrary,
)

# Adapters
from .adapters import (
    PyrogramAdapter,
    AiogramAdapter,
    PythonTelegramBotAdapter,
    TelebotAdapter,
    RawAPIAdapter,
)

# Factory
from .factory import AdapterFactory, create_neonpay

# Errors
from .errors import (
    NeonPayError,
    PaymentError,
    ConfigurationError,
    AdapterError,
    ValidationError,
    StarsPaymentError,
)

# Legacy compatibility
from .payments import NeonStars

# Version & metadata
from ._version import __version__, __version_info__, VERSION_HISTORY

__author__ = "Abbas Sultanov"
__email__ = "sultanov.abas@outlook.com"

__all__ = [
    # Core
    "NeonPayCore",
    "PaymentStage",
    "PaymentResult",
    "PaymentStatus",
    "BotLibrary",

    # Adapters
    "PyrogramAdapter",
    "AiogramAdapter",
    "PythonTelegramBotAdapter",
    "TelebotAdapter",
    "RawAPIAdapter",

    # Factory
    "AdapterFactory",
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

    # Version
    "__version__",
    "__version_info__",
    "VERSION_HISTORY",
]

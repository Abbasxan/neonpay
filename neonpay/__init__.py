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
    BotLibrary
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
    StarsPaymentError  # Legacy compatibility
)

# Legacy compatibility
from .payments import NeonStars

__version__ = "2.2.0"
__author__ = "Abbas Sultanov"
__email__ = "sultanov.abas@outlook.com"

# Lazy loading for adapters to avoid import errors
class _LazyAdapter:
    """Lazy loading adapter class"""
    def __init__(self, adapter_name: str):
        self.adapter_name = adapter_name
        self._adapter_class = None
    
    def _load_adapter(self):
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
                else:
                    raise ImportError(f"Unknown adapter: {self.adapter_name}")
            except ImportError as e:
                raise ImportError(
                    f"Failed to import {self.adapter_name}: {e}. "
                    f"Install required dependencies: pip install neonpay[{self.adapter_name.lower().replace('adapter', '')}]"
                )
        return self._adapter_class
    
    def __call__(self, *args, **kwargs):
        """Create adapter instance when called"""
        adapter_class = self._load_adapter()
        return adapter_class(*args, **kwargs)
    
    def __getattr__(self, name):
        """Delegate attribute access to the actual adapter class"""
        adapter_class = self._load_adapter()
        return getattr(adapter_class, name)

# Create lazy adapter instances
PyrogramAdapter = _LazyAdapter("PyrogramAdapter")
AiogramAdapter = _LazyAdapter("AiogramAdapter")
PythonTelegramBotAdapter = _LazyAdapter("PythonTelegramBotAdapter")
TelebotAdapter = _LazyAdapter("TelebotAdapter")
RawAPIAdapter = _LazyAdapter("RawAPIAdapter")

__all__ = [
    # Core
    "NeonPayCore",
    "PaymentStage", 
    "PaymentResult",
    "PaymentStatus",
    "BotLibrary",
    
    # Adapters (lazy loaded)
    "PyrogramAdapter",
    "AiogramAdapter",
    "PythonTelegramBotAdapter",
    "TelebotAdapter",
    "RawAPIAdapter",
    
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
    "NeonStars"
]

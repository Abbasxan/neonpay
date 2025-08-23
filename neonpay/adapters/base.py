"""Base adapter with localization support."""

from abc import ABC, abstractmethod
from typing import Dict, Any, Callable, Union
from ..core import PaymentStage, PaymentResult
from ..localization import LocalizationManager, Language


class PaymentAdapter(ABC):
    """Abstract base class for bot library adapters with localization support"""
    
    def __init__(self, language: Union[Language, str] = Language.EN):
        """Initialize adapter with localization support.
        
        Args:
            language: Language for payment messages
        """
        self.localization = LocalizationManager(language)
    
    def set_language(self, language: Union[Language, str]) -> None:
        """Change adapter language.
        
        Args:
            language: New language code or Language enum
        """
        self.localization.set_language(language)
    
    def get_text(self, key: str, **kwargs) -> str:
        """Get localized text.
        
        Args:
            key: Translation key
            **kwargs: Format arguments
            
        Returns:
            Localized text
        """
        return self.localization.get(key, **kwargs)
    
    @abstractmethod
    async def send_invoice(self, user_id: int, stage: PaymentStage) -> bool:
        """Send payment invoice to user"""
        pass
    
    @abstractmethod
    async def setup_handlers(self, payment_callback: Callable[[PaymentResult], None]) -> None:
        """Setup payment event handlers"""
        pass
    
    @abstractmethod
    def get_library_info(self) -> Dict[str, str]:
        """Get information about the bot library"""
        pass

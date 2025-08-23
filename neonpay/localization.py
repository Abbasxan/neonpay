"""Localization system for NEONPAY."""

import json
from pathlib import Path
from typing import Dict, Any, Optional, Union
from enum import Enum


class Language(Enum):
    """Supported languages."""
    EN = "en"
    RU = "ru"
    AZ = "az"


class LocalizationManager:
    """Manages translations and localization for NEONPAY."""
    
    def __init__(self, language: Union[Language, str] = Language.EN):
        """Initialize localization manager.
        
        Args:
            language: Language code or Language enum
        """
        if isinstance(language, str):
            try:
                self.language = Language(language.lower())
            except ValueError:
                self.language = Language.EN
        else:
            self.language = language
            
        self._translations: Dict[str, Any] = {}
        self._load_translations()
    
    def _load_translations(self) -> None:
        """Load translations for the current language."""
        translations_dir = Path(__file__).parent / "translations"
        translation_file = translations_dir / f"{self.language.value}.json"
        
        try:
            if translation_file.exists():
                with open(translation_file, 'r', encoding='utf-8') as f:
                    self._translations = json.load(f)
            else:
                # Fallback to English if translation file doesn't exist
                fallback_file = translations_dir / "en.json"
                if fallback_file.exists():
                    with open(fallback_file, 'r', encoding='utf-8') as f:
                        self._translations = json.load(f)
        except (json.JSONDecodeError, IOError):
            # Use built-in fallback translations
            self._translations = self._get_fallback_translations()
    
    def _get_fallback_translations(self) -> Dict[str, Any]:
        """Get fallback translations in case files are not available."""
        return {
            "payment": {
                "title": "Payment",
                "description": "Complete your payment using Telegram Stars",
                "button_pay": "💫 Pay {amount} Stars",
                "button_cancel": "❌ Cancel",
                "success": "✅ Payment successful!",
                "cancelled": "❌ Payment cancelled",
                "failed": "❌ Payment failed: {error}",
                "processing": "⏳ Processing payment...",
                "refunded": "💰 Payment refunded"
            },
            "errors": {
                "invalid_amount": "Invalid payment amount",
                "payment_not_found": "Payment not found",
                "already_paid": "Payment already completed",
                "insufficient_stars": "Insufficient Telegram Stars",
                "network_error": "Network error occurred",
                "unknown_error": "Unknown error occurred"
            },
            "notifications": {
                "payment_received": "New payment received: {amount} Stars",
                "refund_processed": "Refund processed: {amount} Stars"
            }
        }
    
    def get(self, key: str, **kwargs) -> str:
        """Get translated text by key.
        
        Args:
            key: Translation key (e.g., 'payment.title')
            **kwargs: Format arguments for the translation
            
        Returns:
            Translated and formatted text
        """
        keys = key.split('.')
        value = self._translations
        
        try:
            for k in keys:
                value = value[k]
            
            if isinstance(value, str) and kwargs:
                return value.format(**kwargs)
            return str(value)
        except (KeyError, TypeError):
            return key  # Return key if translation not found
    
    def set_language(self, language: Union[Language, str]) -> None:
        """Change the current language.
        
        Args:
            language: New language code or Language enum
        """
        if isinstance(language, str):
            try:
                self.language = Language(language.lower())
            except ValueError:
                return  # Invalid language, keep current
        else:
            self.language = language
        
        self._load_translations()


# Global localization manager instance
_localization_manager = LocalizationManager()


def get_localization_manager() -> LocalizationManager:
    """Get the global localization manager instance."""
    return _localization_manager


def set_global_language(language: Union[Language, str]) -> None:
    """Set the global language for all NEONPAY operations.
    
    Args:
        language: Language code or Language enum
    """
    _localization_manager.set_language(language)


def _(key: str, **kwargs) -> str:
    """Shortcut function for getting translations.
    
    Args:
        key: Translation key
        **kwargs: Format arguments
        
    Returns:
        Translated text
    """
    return _localization_manager.get(key, **kwargs)

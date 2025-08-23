"""
NEONPAY Adapter Factory
Automatic adapter detection and creation
"""

from typing import Any, Optional, Union
import logging

from .core import PaymentAdapter, NeonPayCore
from .adapters import PyrogramAdapter, AiogramAdapter
from .errors import ConfigurationError

logger = logging.getLogger(__name__)


class AdapterFactory:
    """Factory for creating appropriate adapters based on bot library"""
    
    @staticmethod
    def create_adapter(bot_instance: Any) -> PaymentAdapter:
        """
        Automatically detect bot library and create appropriate adapter
        
        Args:
            bot_instance: Bot instance from any supported library
            
        Returns:
            Appropriate PaymentAdapter instance
            
        Raises:
            ConfigurationError: If bot library is not supported
        """
        bot_type = type(bot_instance).__name__
        module_name = type(bot_instance).__module__
        
        # Pyrogram detection
        if "pyrogram" in module_name.lower() and bot_type == "Client":
            from .adapters.pyrogram_adapter import PyrogramAdapter
            return PyrogramAdapter(bot_instance)
        
        # Aiogram detection
        elif "aiogram" in module_name.lower() and bot_type == "Bot":
            from .adapters.aiogram_adapter import AiogramAdapter
            # For aiogram, we need dispatcher too
            return AiogramAdapter(bot_instance)
        
        # python-telegram-bot detection
        elif "telegram" in module_name.lower() and bot_type == "Application":
            from .adapters.ptb_adapter import PythonTelegramBotAdapter
            return PythonTelegramBotAdapter(bot_instance)
        
        # telebot detection
        elif "telebot" in module_name.lower() and bot_type == "TeleBot":
            from .adapters.telebot_adapter import TelebotAdapter
            return TelebotAdapter(bot_instance)
        
        else:
            raise ConfigurationError(
                f"Unsupported bot library: {module_name}.{bot_type}. "
                f"Supported libraries: pyrogram, aiogram, python-telegram-bot, pyTelegramBotAPI"
            )
    
    @staticmethod
    def create_neonpay(
        bot_instance: Any,
        thank_you_message: str = "Thank you for your payment!"
    ) -> NeonPayCore:
        """
        Create NeonPayCore instance with automatic adapter detection
        
        Args:
            bot_instance: Bot instance from any supported library
            thank_you_message: Thank you message for payments
            
        Returns:
            Configured NeonPayCore instance
        """
        adapter = AdapterFactory.create_adapter(bot_instance)
        return NeonPayCore(adapter, thank_you_message)


# Convenience function
def create_neonpay(
    bot_instance: Any,
    thank_you_message: str = "Thank you for your payment!"
) -> NeonPayCore:
    """
    Convenience function to create NeonPayCore with automatic adapter detection
    
    Args:
        bot_instance: Bot instance from any supported library
        thank_you_message: Thank you message for payments
        
    Returns:
        Configured NeonPayCore instance
    """
    return AdapterFactory.create_neonpay(bot_instance, thank_you_message)

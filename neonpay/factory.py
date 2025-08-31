"""
Factory functions for creating NEONPAY adapters and instances
Automatic detection and creation of appropriate bot library adapters
"""

import logging
from typing import Union, Optional, TYPE_CHECKING

from .core import PaymentAdapter, NeonPayCore
from .errors import ConfigurationError

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from aiogram import Bot, Dispatcher
    from pyrogram import Client
    from telegram import Bot as PTBBot
    from telegram.ext import Application
    import telebot


def create_adapter(
    bot_instance: Union["Bot", "Client", "PTBBot", "telebot.TeleBot"],
    dispatcher: Optional["Dispatcher"] = None,
    application: Optional["Application"] = None
) -> PaymentAdapter:
    """
    Create appropriate adapter based on bot instance type
    
    Args:
        bot_instance: Bot instance from any supported library
        dispatcher: Aiogram dispatcher (required for aiogram)
        application: PTB application (required for python-telegram-bot)
        
    Returns:
        Configured PaymentAdapter instance
        
    Raises:
        ConfigurationError: If required dependencies are missing
    """
    try:
        # Try Aiogram
        if hasattr(bot_instance, 'send_message') and hasattr(bot_instance, 'get_me'):
            if dispatcher is None:
                raise ConfigurationError("Aiogram adapter requires dispatcher parameter")
            
            from .adapters.aiogram_adapter import AiogramAdapter
            return AiogramAdapter(bot_instance, dispatcher)
        
        # Try Pyrogram
        elif hasattr(bot_instance, 'send_message') and hasattr(bot_instance, 'get_me'):
            from .adapters.pyrogram_adapter import PyrogramAdapter
            return PyrogramAdapter(bot_instance)
        
        # Try Python Telegram Bot
        elif hasattr(bot_instance, 'send_message') and hasattr(bot_instance, 'get_me'):
            if application is None:
                raise ConfigurationError("Python Telegram Bot adapter requires application parameter")
            
            from .adapters.ptb_adapter import PythonTelegramBotAdapter
            return PythonTelegramBotAdapter(bot_instance, application)
        
        # Try pyTelegramBotAPI
        elif hasattr(bot_instance, 'send_message') and hasattr(bot_instance, 'get_me'):
            from .adapters.telebot_adapter import TelebotAdapter
            return TelebotAdapter(bot_instance)
        
        else:
            raise ConfigurationError("Unsupported bot library. Please use a supported library or create custom adapter.")
            
    except ImportError as e:
        raise ConfigurationError(f"Required dependencies not installed: {e}")


def create_neonpay(
    bot_instance: Union["Bot", "Client", "PTBBot", "telebot.TeleBot"],
    thank_you_message: Optional[str] = None,
    dispatcher: Optional["Dispatcher"] = None,
    application: Optional["Application"] = None,
    enable_logging: bool = True,
    max_stages: int = 100
) -> NeonPayCore:
    """
    Create NEONPAY instance with automatic adapter detection
    
    Args:
        bot_instance: Bot instance from any supported library
        thank_you_message: Custom thank you message
        dispatcher: Aiogram dispatcher (required for aiogram)
        application: PTB application (required for python-telegram-bot)
        enable_logging: Enable security logging
        max_stages: Maximum number of payment stages
        
    Returns:
        Configured NeonPayCore instance
    """
    adapter = create_adapter(bot_instance, dispatcher, application)
    
    return NeonPayCore(
        adapter=adapter,
        thank_you_message=thank_you_message,
        enable_logging=enable_logging,
        max_stages=max_stages
    )

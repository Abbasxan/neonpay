""" 
Factory functions for creating NEONPAY adapters and instances

Automatic detection and creation of appropriate bot library adapters
"""

import logging
from typing import Union, Optional, TYPE_CHECKING, Any

from .core import PaymentAdapter, NeonPayCore
from .errors import ConfigurationError

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from aiogram import Bot, Dispatcher
    from pyrogram import Client
    from telegram import Bot as PTBBot
    from telegram.ext import Application
    import telebot

# Dynamic imports with mypy-compatible Optional[Any]
try:
    from aiogram import Bot as AiogramBot
except ImportError:
    AiogramBot: Optional[Any] = None

try:
    from pyrogram import Client as PyroClient
except ImportError:
    PyroClient: Optional[Any] = None

try:
    from telegram import Bot as PTBBotClass
except ImportError:
    PTBBotClass: Optional[Any] = None

try:
    import telebot
except ImportError:
    telebot: Optional[Any] = None


def create_adapter(
    bot_instance: Union["Bot", "Client", "PTBBot", "telebot.TeleBot"],
    dispatcher: Optional["Dispatcher"] = None,
    application: Optional["Application"] = None,
    adapter_type: Optional[str] = None,
) -> PaymentAdapter:
    """
    Create appropriate adapter based on bot instance type

    Args:
        bot_instance: Bot instance from any supported library
        dispatcher: Aiogram dispatcher (required for aiogram)
        application: PTB application (required for python-telegram-bot)
        adapter_type: Optional explicit adapter type ('botapi' or 'ptb')

    Returns:
        Configured PaymentAdapter instance

    Raises:
        ConfigurationError: If required dependencies are missing
    """
    try:
        # Aiogram
        if AiogramBot is not None and isinstance(bot_instance, AiogramBot):
            if dispatcher is None:
                raise ConfigurationError(
                    "Aiogram adapter requires dispatcher parameter"
                )
            from .adapters.aiogram_adapter import AiogramAdapter
            return AiogramAdapter(bot_instance, dispatcher)

        # Pyrogram
        elif PyroClient is not None and isinstance(bot_instance, PyroClient):
            from .adapters.pyrogram_adapter import PyrogramAdapter
            return PyrogramAdapter(bot_instance)

        # PTB vs BotAPI
        elif PTBBotClass is not None and isinstance(bot_instance, PTBBotClass):
            if adapter_type == "botapi":
                from .adapters.botapi_adapter import BotAPIAdapter
                return BotAPIAdapter(bot_instance)
            else:
                if application is None:
                    raise ConfigurationError(
                        "Python Telegram Bot adapter requires application parameter"
                    )
                from .adapters.ptb_adapter import PythonTelegramBotAdapter
                return PythonTelegramBotAdapter(bot_instance, application)

        # Telebot
        elif telebot is not None and isinstance(bot_instance, telebot.TeleBot):
            from .adapters.telebot_adapter import TelebotAdapter
            return TelebotAdapter(bot_instance)

        else:
            raise ConfigurationError(
                f"Unsupported bot type: {type(bot_instance).__name__}. "
                "Please use a supported library or create custom adapter."
            )

    except ImportError as e:
        raise ConfigurationError(f"Required dependencies not installed: {e}")


def create_neonpay(
    bot_instance: Union["Bot", "Client", "PTBBot", "telebot.TeleBot"],
    thank_you_message: Optional[str] = None,
    dispatcher: Optional["Dispatcher"] = None,
    application: Optional["Application"] = None,
    enable_logging: bool = True,
    max_stages: int = 100,
    adapter_type: Optional[str] = None,
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
        adapter_type: Optional explicit adapter type ('botapi' or 'ptb')

    Returns:
        Configured NeonPayCore instance
    """
    adapter = create_adapter(bot_instance, dispatcher, application, adapter_type)

    return NeonPayCore(
        adapter=adapter,
        thank_you_message=thank_you_message,
        enable_logging=enable_logging,
        max_stages=max_stages,
)
        

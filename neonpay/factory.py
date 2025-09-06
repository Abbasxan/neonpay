"""
Factory functions for creating NEONPAY adapters and instances
Automatic detection and creation of appropriate bot library adapters
"""

import importlib
import logging
from typing import TYPE_CHECKING, Any, Optional, Union

from .core import NeonPayCore, PaymentAdapter
from .errors import ConfigurationError

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    import telebot
    from aiogram import Bot, Dispatcher
    from pyrogram import Client
    from telegram import Bot as PTBBot
    from telegram.ext import Application


# Dynamic runtime imports
def _safe_import(module: str, attr: Optional[str] = None) -> Optional[Any]:
    try:
        mod = importlib.import_module(module)
        return getattr(mod, attr) if attr else mod
    except ImportError:
        return None


AiogramBot = _safe_import("aiogram", "Bot")
PyroClient = _safe_import("pyrogram", "Client")
PTBBotClass = _safe_import("telegram", "Bot")
TelebotModule = _safe_import("telebot")


def create_adapter(
    bot_instance: Union["Bot", "Client", "PTBBot", "telebot.TeleBot"],
    dispatcher: Optional["Dispatcher"] = None,
    application: Optional["Application"] = None,
    adapter_type: Optional[str] = None,
) -> PaymentAdapter:
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
        elif TelebotModule is not None and isinstance(
            bot_instance, TelebotModule.TeleBot
        ):
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
    adapter = create_adapter(bot_instance, dispatcher, application, adapter_type)

    return NeonPayCore(
        adapter=adapter,
        thank_you_message=thank_you_message,
        enable_logging=enable_logging,
        max_stages=max_stages,
    )

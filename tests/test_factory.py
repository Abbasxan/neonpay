from unittest.mock import MagicMock, patch

import pytest

from neonpay.adapters.aiogram_adapter import AiogramAdapter
from neonpay.adapters.ptb_adapter import PythonTelegramBotAdapter
from neonpay.adapters.pyrogram_adapter import PyrogramAdapter
from neonpay.adapters.raw_api_adapter import RawAPIAdapter
from neonpay.adapters.telebot_adapter import TelebotAdapter
from neonpay.errors import ConfigurationError
from neonpay.factory import create_adapter


class TestAdapterFactory:
    @patch("neonpay.factory.PyroClient", MagicMock)
    def test_create_pyrogram_adapter(self):
        mock_client = MagicMock()
        mock_client.__class__.__name__ = "Client"
        mock_client.__module__ = "pyrogram"

        adapter = create_adapter(mock_client)
        assert isinstance(adapter, PyrogramAdapter)

    @patch("neonpay.factory.AiogramBot", MagicMock)
    def test_create_aiogram_adapter(self):
        mock_bot = MagicMock()
        mock_bot.__class__.__name__ = "Bot"
        mock_bot.__module__ = "aiogram"
        mock_dispatcher = MagicMock()

        adapter = create_adapter(mock_bot, dispatcher=mock_dispatcher)
        assert isinstance(adapter, AiogramAdapter)

    @patch("neonpay.factory.PTBBotClass", MagicMock)
    def test_create_ptb_adapter(self):
        mock_bot = MagicMock()
        mock_bot.__class__.__name__ = "Bot"
        mock_bot.__module__ = "telegram"
        mock_application = MagicMock()

        adapter = create_adapter(mock_bot, application=mock_application)
        assert isinstance(adapter, PythonTelegramBotAdapter)

    @patch("neonpay.factory.TelebotModule")
    def test_create_telebot_adapter(self, mock_telebot_module):
        # Create a proper mock TeleBot class that can be used with isinstance
        class MockTeleBot:
            pass

        mock_telebot_module.TeleBot = MockTeleBot

        mock_bot = MagicMock()
        mock_bot.__class__ = MockTeleBot
        mock_bot.__class__.__name__ = "TeleBot"
        mock_bot.__module__ = "telebot"

        adapter = create_adapter(mock_bot)
        assert isinstance(adapter, TelebotAdapter)

    def test_create_raw_api_adapter_with_token(self):
        adapter = RawAPIAdapter("1234567890:ABCDEF")
        assert isinstance(adapter, RawAPIAdapter)

    def test_unsupported_client_raises_error(self):
        unsupported_client = MagicMock()
        unsupported_client.__class__.__name__ = "UnsupportedBot"
        unsupported_client.__module__ = "unknown"

        with pytest.raises(ConfigurationError, match="Unsupported bot type"):
            create_adapter(unsupported_client)

import pytest
from unittest.mock import MagicMock
from neonpay.factory import AdapterFactory
from neonpay.adapters.pyrogram_adapter import PyrogramAdapter
from neonpay.adapters.aiogram_adapter import AiogramAdapter
from neonpay.adapters.ptb_adapter import PTBAdapter
from neonpay.adapters.telebot_adapter import TelebotAdapter
from neonpay.adapters.raw_api_adapter import RawAPIAdapter


class TestAdapterFactory:
    def test_create_pyrogram_adapter(self):
        mock_client = MagicMock()
        mock_client.__class__.__name__ = "Client"
        mock_client.__module__ = "pyrogram"

        adapter = AdapterFactory.create_adapter(mock_client)
        assert isinstance(adapter, PyrogramAdapter)

    def test_create_aiogram_adapter(self):
        mock_bot = MagicMock()
        mock_bot.__class__.__name__ = "Bot"
        mock_bot.__module__ = "aiogram"

        adapter = AdapterFactory.create_adapter(mock_bot)
        assert isinstance(adapter, AiogramAdapter)

    def test_create_ptb_adapter(self):
        mock_bot = MagicMock()
        mock_bot.__class__.__name__ = "Bot"
        mock_bot.__module__ = "telegram"

        adapter = AdapterFactory.create_adapter(mock_bot)
        assert isinstance(adapter, PTBAdapter)

    def test_create_telebot_adapter(self):
        mock_bot = MagicMock()
        mock_bot.__class__.__name__ = "TeleBot"
        mock_bot.__module__ = "telebot"

        adapter = AdapterFactory.create_adapter(mock_bot)
        assert isinstance(adapter, TelebotAdapter)

    def test_create_raw_api_adapter_with_token(self):
        adapter = AdapterFactory.create_adapter("1234567890:ABCDEF")
        assert isinstance(adapter, RawAPIAdapter)

    def test_unsupported_client_raises_error(self):
        unsupported_client = MagicMock()
        unsupported_client.__class__.__name__ = "UnsupportedBot"
        unsupported_client.__module__ = "unknown"

        with pytest.raises(ValueError, match="Unsupported client type"):
            AdapterFactory.create_adapter(unsupported_client)

from unittest.mock import AsyncMock, patch

import pytest

from neonpay.adapters.aiogram_adapter import AiogramAdapter
from neonpay.adapters.pyrogram_adapter import PyrogramAdapter
from neonpay.core import PaymentStage


class TestPyrogramAdapter:
    @pytest.fixture
    def mock_client(self):
        client = AsyncMock()
        # Mock InputPeerUser object
        mock_peer = AsyncMock()
        client.resolve_peer = AsyncMock(return_value=mock_peer)
        client.invoke = AsyncMock()
        return client

    @pytest.fixture
    def adapter(self, mock_client):
        return PyrogramAdapter(mock_client)

    @pytest.fixture
    def payment_stage(self):
        return PaymentStage(
            title="Test Product",
            description="Test Description",
            price=100,
        )

    @pytest.mark.asyncio
    @patch("neonpay.adapters.pyrogram_adapter.isinstance")
    async def test_send_invoice_success(
        self, mock_isinstance, adapter, mock_client, payment_stage
    ):
        # Mock isinstance to return True for InputPeerUser check
        mock_isinstance.return_value = True

        result = await adapter.send_invoice(12345, payment_stage)

        assert result is True
        mock_client.resolve_peer.assert_called_once_with(12345)
        mock_client.invoke.assert_called_once()

    @pytest.mark.asyncio
    @patch("neonpay.adapters.pyrogram_adapter.isinstance")
    async def test_send_invoice_with_logo(self, mock_isinstance, adapter, mock_client):
        # Mock isinstance to return True for InputPeerUser check
        mock_isinstance.return_value = True

        stage = PaymentStage(
            title="Test Product",
            description="Test Description",
            price=100,
            photo_url="https://example.com/logo.png",
        )

        result = await adapter.send_invoice(12345, stage)
        assert result is True

    def test_get_library_info(self, adapter):
        info = adapter.get_library_info()
        assert "library" in info
        assert "version" in info


class TestAiogramAdapter:
    @pytest.fixture
    def mock_bot(self):
        bot = AsyncMock()
        bot.send_invoice = AsyncMock()
        return bot

    @pytest.fixture
    def mock_dispatcher(self):
        return AsyncMock()

    @pytest.fixture
    def adapter(self, mock_bot, mock_dispatcher):
        return AiogramAdapter(mock_bot, mock_dispatcher)

    @pytest.fixture
    def payment_stage(self):
        return PaymentStage(
            title="Test Product",
            description="Test Description",
            price=100,
        )

    @pytest.mark.asyncio
    async def test_send_invoice_success(self, adapter, mock_bot, payment_stage):
        result = await adapter.send_invoice(12345, payment_stage)

        assert result is True
        mock_bot.send_invoice.assert_called_once()

    def test_get_library_info(self, adapter):
        info = adapter.get_library_info()
        assert "library" in info
        assert "version" in info

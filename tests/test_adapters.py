import pytest
from unittest.mock import AsyncMock, MagicMock
from neonpay.adapters.pyrogram_adapter import PyrogramAdapter
from neonpay.adapters.aiogram_adapter import AiogramAdapter
from neonpay.core import PaymentStage


class TestPyrogramAdapter:
    @pytest.fixture
    def mock_client(self):
        client = AsyncMock()
        client.resolve_peer = AsyncMock(return_value="peer_123")
        client.invoke = AsyncMock()
        return client
    
    @pytest.fixture
    def adapter(self, mock_client):
        return PyrogramAdapter(mock_client)
    
    @pytest.fixture
    def payment_stage(self):
        return PaymentStage(
            stage_id="test_stage",
            title="Test Product",
            description="Test Description",
            amount=100,
            currency="XTR"
        )
    
    @pytest.mark.asyncio
    async def test_send_invoice_success(self, adapter, mock_client, payment_stage):
        result = await adapter.send_invoice(12345, payment_stage)
        
        assert result is True
        mock_client.resolve_peer.assert_called_once_with(12345)
        mock_client.invoke.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_send_invoice_with_logo(self, adapter, mock_client):
        stage = PaymentStage(
            stage_id="test_stage",
            title="Test Product",
            description="Test Description",
            amount=100,
            currency="XTR",
            logo_url="https://example.com/logo.png"
        )
        
        result = await adapter.send_invoice(12345, stage)
        assert result is True
    
    @pytest.mark.asyncio
    async def test_handle_payment(self, adapter):
        payment_data = {
            "user_id": 12345,
            "stage_id": "test_stage",
            "amount": 100,
            "payment_id": "pay_123"
        }
        
        result = await adapter.handle_payment(payment_data)
        
        assert result.success is True
        assert result.payment_id == "pay_123"
        assert result.amount == 100
        assert result.user_id == 12345


class TestAiogramAdapter:
    @pytest.fixture
    def mock_bot(self):
        bot = AsyncMock()
        bot.send_invoice = AsyncMock()
        return bot
    
    @pytest.fixture
    def adapter(self, mock_bot):
        return AiogramAdapter(mock_bot)
    
    @pytest.fixture
    def payment_stage(self):
        return PaymentStage(
            stage_id="test_stage",
            title="Test Product",
            description="Test Description",
            amount=100,
            currency="XTR"
        )
    
    @pytest.mark.asyncio
    async def test_send_invoice_success(self, adapter, mock_bot, payment_stage):
        result = await adapter.send_invoice(12345, payment_stage)
        
        assert result is True
        mock_bot.send_invoice.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_handle_payment(self, adapter):
        payment_data = {
            "user_id": 12345,
            "stage_id": "test_stage",
            "amount": 100,
            "payment_id": "pay_123"
        }
        
        result = await adapter.handle_payment(payment_data)
        
        assert result.success is True
        assert result.payment_id == "pay_123"
        assert result.amount == 100

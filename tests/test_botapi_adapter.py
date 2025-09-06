import asyncio

import pytest

from neonpay.adapters.botapi_adapter import BotAPIAdapter
from neonpay.core import PaymentResult, PaymentStage, PaymentStatus


class DummyBot:
    """Fake telegram.Bot for testing"""

    def __init__(self):
        self.invoices = []
        self.pre_checkout_answered = False

    def send_invoice(self, **kwargs):
        self.invoices.append(kwargs)
        return True

    def answer_pre_checkout_query(self, pre_checkout_query_id, ok):
        self.pre_checkout_answered = True
        return True


@pytest.mark.asyncio
async def test_send_invoice():
    bot = DummyBot()
    adapter = BotAPIAdapter(bot)

    stage = PaymentStage(
        title="Test", description="Test invoice", price=50, label="Test Label"
    )
    result = await adapter.send_invoice(user_id=123, stage=stage)

    assert result is True
    assert bot.invoices[0]["chat_id"] == 123
    assert bot.invoices[0]["title"] == "Test"


@pytest.mark.asyncio
async def test_pre_checkout_query():
    bot = DummyBot()
    adapter = BotAPIAdapter(bot)

    class Query:
        id = "12345"

    await adapter.handle_pre_checkout_query(Query())
    assert bot.pre_checkout_answered is True


@pytest.mark.asyncio
async def test_successful_payment_callback():
    bot = DummyBot()
    adapter = BotAPIAdapter(bot)
    results = []

    async def callback(result: PaymentResult):
        results.append(result)

    await adapter.setup_handlers(callback)

    class Message:
        class FromUser:
            id = 42

        class Payment:
            total_amount = 100
            currency = "XTR"
            invoice_payload = '{"test": "ok"}'
            telegram_payment_charge_id = "tx_001"

        from_user = FromUser()
        successful_payment = Payment()

    await adapter.handle_successful_payment(Message())
    await asyncio.sleep(0.1)

    assert len(results) == 1
    assert results[0].user_id == 42
    assert results[0].status == PaymentStatus.COMPLETED
    assert results[0].metadata["test"] == "ok"

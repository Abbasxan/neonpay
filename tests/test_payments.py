from unittest.mock import AsyncMock, patch

import pytest

from neonpay.errors import StarsPaymentError
from neonpay.payments import NeonStars


# Тестируем класс ошибки
def test_error_class():
    with pytest.raises(StarsPaymentError):
        raise StarsPaymentError("Тестовая ошибка")


# Тестируем NeonStars.send_donate без подключения к Telegram
@pytest.mark.asyncio
async def test_send_donate_mock():
    mock_client = AsyncMock()

    # Mock Pyrogram availability and types for testing
    with (
        patch("neonpay.payments.PYROGRAM_AVAILABLE", True),
        patch("neonpay.payments._load_pyrogram", return_value=True),
        patch("neonpay.payments.Invoice"),
        patch("neonpay.payments.LabeledPrice"),
        patch("neonpay.payments.InputMediaInvoice"),
        patch("neonpay.payments.DataJSON"),
        patch("neonpay.payments.InputWebDocument"),
        patch("neonpay.payments.UpdateBotPrecheckoutQuery"),
        patch("neonpay.payments.MessageActionPaymentSentMe"),
        patch("neonpay.payments.SendMedia"),
        patch("neonpay.payments.SetBotPrecheckoutResults"),
    ):

        stars = NeonStars(mock_client, thank_you="Спасибо!")

        # Подменяем resolve_peer и invoke, чтобы не было реального запроса
        mock_client.resolve_peer = AsyncMock(return_value="peer_id")
        mock_client.invoke = AsyncMock()

        # Проверяем, что метод send_donate не вызывает ошибок с валидными данными
        try:
            await stars.send_donate(
                user_id=12345,
                amount=1,
                label="☕ 1 ⭐",
                title="Тест",
                description="Тестовая оплата",
            )
        except StarsPaymentError:
            pytest.fail("send_donate вызвал StarsPaymentError при мок-тесте")

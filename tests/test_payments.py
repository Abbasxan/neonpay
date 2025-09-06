import pytest
from neonpay.errors import StarsPaymentError
from neonpay.payments import NeonStars
from unittest.mock import AsyncMock, patch


# Тестируем класс ошибки
def test_error_class():
    with pytest.raises(StarsPaymentError):
        raise StarsPaymentError("Тестовая ошибка")


# Тестируем NeonStars.send_donate без подключения к Telegram
@pytest.mark.asyncio
async def test_send_donate_mock():
    mock_client = AsyncMock()
    
    # Mock Pyrogram availability and types for testing
    with patch('neonpay.payments.PYROGRAM_AVAILABLE', True), \
         patch('neonpay.payments._load_pyrogram', return_value=True), \
         patch('neonpay.payments.Invoice') as mock_invoice, \
         patch('neonpay.payments.LabeledPrice') as mock_labeled_price, \
         patch('neonpay.payments.InputMediaInvoice') as mock_input_media_invoice, \
         patch('neonpay.payments.DataJSON') as mock_data_json, \
         patch('neonpay.payments.InputWebDocument') as mock_input_web_document, \
         patch('neonpay.payments.UpdateBotPrecheckoutQuery') as mock_update_bot_precheckout_query, \
         patch('neonpay.payments.MessageActionPaymentSentMe') as mock_message_action_payment_sent_me, \
         patch('neonpay.payments.SendMedia') as mock_send_media, \
         patch('neonpay.payments.SetBotPrecheckoutResults') as mock_set_bot_precheckout_results:
        
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

"""
pyTelegramBotAPI adapter for NEONPAY
Supports pyTelegramBotAPI v4.0+ with Telegram Stars payments
"""

import asyncio
import json
import logging
import threading
from collections.abc import Awaitable, Coroutine
from typing import TYPE_CHECKING, Any, Callable, Dict, Optional

if TYPE_CHECKING:
    import telebot

from ..core import PaymentAdapter, PaymentResult, PaymentStage, PaymentStatus
from ..errors import NeonPayError

logger = logging.getLogger(__name__)


class TelebotAdapter(PaymentAdapter):
    """pyTelegramBotAPI library adapter for NEONPAY"""

    def __init__(self, bot: "telebot.TeleBot"):
        """
        Initialize Telebot adapter

        Args:
            bot: Telebot instance
        """
        self.bot = bot
        self._payment_callback: Optional[Callable[[PaymentResult], Any]] = None
        self._handlers_setup = False

    async def send_invoice(self, user_id: int, stage: PaymentStage) -> bool:
        """Send payment invoice using pyTelegramBotAPI"""
        try:
            from telebot.types import LabeledPrice

            payload_data = {"user_id": user_id, "amount": stage.price}
            if stage.payload:
                payload_data.update(stage.payload)
            payload = json.dumps(payload_data)

            prices = [LabeledPrice(label=stage.label, amount=stage.price)]

            self.bot.send_invoice(
                chat_id=user_id,
                title=stage.title,
                description=stage.description,
                invoice_payload=payload,
                provider_token="",  # Empty for Telegram Stars  # nosec B106
                currency="XTR",
                prices=prices,
                photo_url=stage.photo_url or "",
                start_parameter=stage.start_parameter or "neonpay_invoice",
            )
            return True
        except Exception as e:
            raise NeonPayError(f"Telegram API error: {e}") from e

    async def setup_handlers(
        self, payment_callback: Callable[[PaymentResult], Any]
    ) -> None:
        """Setup pyTelegramBotAPI payment handlers"""
        if self._handlers_setup:
            return
        self._payment_callback = payment_callback

        # Register handlers
        self.bot.pre_checkout_query_handler(func=lambda q: True)(
            self._handle_pre_checkout_query
        )
        self.bot.message_handler(func=lambda m: m.successful_payment is not None)(
            self._handle_successful_payment
        )

        self._handlers_setup = True

    def _handle_pre_checkout_query(self, pre_checkout_query: Any) -> None:
        """Handle pre-checkout query"""
        try:
            self.bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)
        except Exception as e:
            logger.error(f"Error handling pre-checkout query: {e}")

    def _handle_successful_payment(self, message: Any) -> None:
        """Handle successful payment"""
        if not self._payment_callback or not hasattr(message, "successful_payment"):
            return

        payment = message.successful_payment
        if payment is None:
            return

        user_id = message.from_user.id

        payload_data = {}
        try:
            if payment.invoice_payload:
                payload_data = json.loads(payment.invoice_payload)
        except json.JSONDecodeError:
            pass

        result = PaymentResult(
            user_id=user_id,
            amount=payment.total_amount,
            currency=payment.currency,
            status=PaymentStatus.COMPLETED,
            transaction_id=payment.telegram_payment_charge_id,
            metadata=payload_data,
        )

        self._call_async_callback(result)

    def _call_async_callback(self, result: PaymentResult) -> None:
        """Безопасный вызов коллбека (sync или async)"""
        callback = self._payment_callback
        if callback is None:
            return

        try:
            loop = asyncio.get_event_loop()
            ret = callback(result)

            if isinstance(ret, Awaitable):
                if loop.is_running():
                    if isinstance(ret, Coroutine):
                        asyncio.create_task(ret)
                    else:
                        asyncio.ensure_future(ret)
                else:
                    loop.run_until_complete(ret)

        except RuntimeError:
            # Нет активного event loop → создаём новый поток
            def run() -> None:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    ret = callback(result)
                    if isinstance(ret, Awaitable):
                        loop.run_until_complete(ret)
                finally:
                    loop.close()

            threading.Thread(target=run, daemon=True).start()

        except Exception as e:
            logger.error(f"Ошибка при вызове payment callback: {e}")

    def get_library_info(self) -> Dict[str, str]:
        """Get pyTelegramBotAPI adapter information"""
        return {
            "library": "pyTelegramBotAPI",
            "version": "4.0+",
            "features": "Telegram Stars payments, Pre-checkout handling, Payment status tracking",
        }

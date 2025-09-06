"""
Python Telegram Bot adapter for NEONPAY
Supports python-telegram-bot v20.0+ with Telegram Stars payments
"""

import json
import logging
from typing import TYPE_CHECKING, Any, Awaitable, Callable, Dict, Optional

from ..core import PaymentAdapter, PaymentResult, PaymentStage, PaymentStatus
from ..errors import NeonPayError

if TYPE_CHECKING:
    from telegram import Bot, Update
    from telegram.ext import Application, ContextTypes

logger = logging.getLogger(__name__)


class PythonTelegramBotAdapter(PaymentAdapter):
    """Python Telegram Bot library adapter for NEONPAY"""

    def __init__(self, bot: "Bot", application: "Application"):
        """
        Initialize Python Telegram Bot adapter
        Args:
            bot: PTB Bot instance
            application: PTB Application instance
        """
        self.bot = bot
        self.application = application
        self._handlers_setup = False
        # callback всегда async
        self._payment_callback: Optional[Callable[[PaymentResult], Awaitable[None]]] = (
            None
        )

    async def send_invoice(self, user_id: int, stage: PaymentStage) -> bool:
        """Send payment invoice using Python Telegram Bot"""
        try:
            from telegram import LabeledPrice

            prices = [LabeledPrice(label=stage.label, amount=stage.price)]
            payload = json.dumps(
                {"user_id": user_id, "amount": stage.price, **(stage.payload or {})}
            )

            await self.bot.send_invoice(
                chat_id=user_id,
                title=stage.title,
                description=stage.description,
                payload=payload,
                provider_token="",  # Empty for Telegram Stars  # nosec B106
                currency="XTR",
                prices=prices,
                photo_url=stage.photo_url,
                start_parameter=stage.start_parameter,
            )
            return True

        except Exception as e:
            raise NeonPayError(f"Telegram API error: {e}")

    async def setup_handlers(
        self, payment_callback: Callable[[PaymentResult], Any]
    ) -> None:
        """Setup Python Telegram Bot payment handlers"""
        if self._handlers_setup:
            return

        # Оборачиваем callback (sync или async) в async для безопасного await
        async def async_cb(result: PaymentResult) -> None:
            maybe_awaitable = payment_callback(result)
            if hasattr(maybe_awaitable, "__await__"):
                await maybe_awaitable

        self._payment_callback = async_cb

        from telegram.ext import MessageHandler, PreCheckoutQueryHandler, filters

        # Pre-checkout handler
        self.application.add_handler(
            PreCheckoutQueryHandler(self._handle_pre_checkout_query)
        )

        # Successful payment handler
        self.application.add_handler(
            MessageHandler(filters.SUCCESSFUL_PAYMENT, self._handle_successful_payment)
        )

        self._handlers_setup = True

    async def _handle_pre_checkout_query(
        self, update: "Update", context: "ContextTypes.DEFAULT_TYPE"
    ) -> None:
        """Handle pre-checkout query"""
        query = update.pre_checkout_query
        if not query:
            return
        try:
            await query.answer(ok=True)
        except Exception as e:
            logger.error(f"Error handling pre-checkout query: {e}")

    async def _handle_successful_payment(
        self, update: "Update", context: "ContextTypes.DEFAULT_TYPE"
    ) -> None:
        """Handle successful payment"""
        if not self._payment_callback:
            return

        message = update.message
        if not message or not message.successful_payment or not message.from_user:
            return

        try:
            payload_data: Dict[str, Any] = {}
            if message.successful_payment.invoice_payload:
                payload_data = json.loads(message.successful_payment.invoice_payload)
        except json.JSONDecodeError:
            payload_data = {}

        result = PaymentResult(
            user_id=message.from_user.id,
            amount=message.successful_payment.total_amount,
            currency=message.successful_payment.currency,
            status=PaymentStatus.COMPLETED,
            transaction_id=message.successful_payment.telegram_payment_charge_id,
            metadata=payload_data,
        )

        await self._payment_callback(result)

    def get_library_info(self) -> Dict[str, str]:
        """Get Python Telegram Bot adapter information"""
        return {
            "library": "python-telegram-bot",
            "version": "20.0+",
            "features": "Telegram Stars, Pre-checkout handling, Payment callbacks",
        }

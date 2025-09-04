"""
Python Telegram Bot adapter for NEONPAY
Supports python-telegram-bot v20.0+ with Telegram Stars payments
"""

import json
import logging
from typing import Dict, Callable, Optional, TYPE_CHECKING, Any

from ..core import PaymentAdapter, PaymentStage, PaymentResult, PaymentStatus
from ..errors import NeonPayError

if TYPE_CHECKING:
    from telegram import Bot, PreCheckoutQuery, Message
    from telegram.ext import Application

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
        self._payment_callback: Optional[Callable[[PaymentResult], None]] = None

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
                provider_token="",  # Empty for Telegram Stars
                currency="XTR",
                prices=prices,
                photo_url=stage.photo_url,
                start_parameter=stage.start_parameter,
            )
            return True

        except Exception as e:
            raise NeonPayError(f"Telegram API error: {e}")

    async def setup_handlers(
        self, payment_callback: Callable[[PaymentResult], None]
    ) -> None:
        """Setup Python Telegram Bot payment handlers"""
        if self._handlers_setup:
            return

        self._payment_callback = payment_callback

        from telegram.ext import PreCheckoutQueryHandler, MessageHandler, filters

        # Pre-checkout handler
        self.application.add_handler(
            PreCheckoutQueryHandler(self._handle_pre_checkout_query)
        )

        # Successful payment handler
        self.application.add_handler(
            MessageHandler(filters.SUCCESSFUL_PAYMENT, self._handle_successful_payment)
        )

        self._handlers_setup = True

    async def _handle_pre_checkout_query(self, pre_checkout_query: "PreCheckoutQuery") -> None:
        """Handle pre-checkout query"""
        try:
            await pre_checkout_query.answer(ok=True)
        except Exception as e:
            logger.error(f"Error handling pre-checkout query: {e}")

    async def _handle_successful_payment(self, message: "Message") -> None:
        """Handle successful payment"""
        if not self._payment_callback:
            return

        payment = message.successful_payment
        if not payment or not message.from_user:
            return

        try:
            payload_data: Dict[str, Any] = {}
            if payment.invoice_payload:
                payload_data = json.loads(payment.invoice_payload)
        except json.JSONDecodeError:
            payload_data = {}

        result = PaymentResult(
            user_id=message.from_user.id,
            amount=payment.total_amount,
            currency=payment.currency,
            status=PaymentStatus.COMPLETED,
            transaction_id=payment.telegram_payment_charge_id,
            metadata=payload_data,
        )

        # callback может быть sync/async → поддержим оба варианта
        cb = self._payment_callback
        if cb:
            res = cb(result)
            if hasattr(res, "__await__"):  # async
                await res

    def get_library_info(self) -> Dict[str, str]:
        """Get Python Telegram Bot adapter information"""
        return {
            "library": "python-telegram-bot",
            "version": "20.0+",
            "features": "Telegram Stars, Pre-checkout handling, Payment callbacks",
            }

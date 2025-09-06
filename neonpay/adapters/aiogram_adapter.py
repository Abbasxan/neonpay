"""
Aiogram adapter for NEONPAY
Supports Aiogram v3.0+ with Telegram Stars payments
"""

import json
import logging
from typing import TYPE_CHECKING, Any, Awaitable, Callable, Dict, Optional

if TYPE_CHECKING:
    from aiogram import Bot, Dispatcher
    from aiogram.types import PreCheckoutQuery, Message

from ..core import PaymentAdapter, PaymentResult, PaymentStage, PaymentStatus
from ..errors import NeonPayError

logger = logging.getLogger(__name__)


class AiogramAdapter(PaymentAdapter):
    """Aiogram library adapter for NEONPAY"""

    def __init__(self, bot: "Bot", dispatcher: "Dispatcher"):
        """
        Initialize Aiogram adapter
        Args:
            bot: Aiogram Bot instance
            dispatcher: Aiogram Dispatcher instance (required)
        """
        self.bot = bot
        self.dispatcher = dispatcher
        self._handlers_setup = False
        # callback теперь async
        self._payment_callback: Optional[Callable[[PaymentResult], Awaitable[None]]] = (
            None
        )

    async def send_invoice(self, user_id: int, stage: PaymentStage) -> bool:
        """Send payment invoice using Aiogram"""
        try:
            from aiogram.types import LabeledPrice

            prices = [LabeledPrice(label=stage.label, amount=stage.price)]
            photo = stage.photo_url if stage.photo_url else None

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
                photo_url=photo,
                start_parameter=stage.start_parameter,
            )
            return True

        except Exception as e:
            raise NeonPayError(f"Telegram API error: {e}")

    async def setup_handlers(
        self, payment_callback: Callable[[PaymentResult], Any]
    ) -> None:
        """Setup Aiogram payment handlers"""
        if self._handlers_setup:
            return

        # Оборачиваем callback (sync или async) в async для безопасного await
        async def async_cb(result: PaymentResult) -> None:
            maybe_awaitable = payment_callback(result)
            if hasattr(maybe_awaitable, "__await__"):
                await maybe_awaitable

        self._payment_callback = async_cb

        self.dispatcher.pre_checkout_query.register(self._handle_pre_checkout_query)
        self.dispatcher.message.register(
            self._handle_successful_payment,
            lambda message: message.successful_payment is not None,
        )

        self._handlers_setup = True

    async def _handle_pre_checkout_query(
        self, pre_checkout_query: "PreCheckoutQuery"
    ) -> None:
        """Handle pre-checkout query"""
        try:
            await self.bot.answer_pre_checkout_query(
                pre_checkout_query_id=pre_checkout_query.id, ok=True
            )
        except Exception as e:
            logger.error(f"Error handling pre-checkout query: {e}")

    async def _handle_successful_payment(self, message: "Message") -> None:
        """Handle successful payment"""
        if not self._payment_callback:
            return

        if not message.successful_payment or not message.from_user:
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
        """Get Aiogram adapter information"""
        return {
            "library": "aiogram",
            "version": "3.0+",
            "features": "Telegram Stars, Pre-checkout handling, Payment callbacks",
        }

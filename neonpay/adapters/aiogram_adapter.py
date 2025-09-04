"""
Aiogram adapter for NEONPAY
Supports Aiogram v3.0+ with Telegram Stars payments
"""

from typing import Dict, Callable, Optional, TYPE_CHECKING
import json
import logging

if TYPE_CHECKING:
    from aiogram import Bot, Dispatcher
    from aiogram.types import PreCheckoutQuery, Message

from ..core import PaymentAdapter, PaymentStage, PaymentResult, PaymentStatus
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
        self._payment_callback: Optional[Callable[[PaymentResult], None]] = None

    async def send_invoice(self, user_id: int, stage: PaymentStage) -> bool:
        """Send payment invoice using Aiogram"""
        try:
            # Import aiogram types
            from aiogram.types import LabeledPrice

            # Create price list
            prices = [LabeledPrice(label=stage.label, amount=stage.price)]

            # Prepare photo
            photo = stage.photo_url if stage.photo_url else None

            # Create payload
            payload = json.dumps(
                {"user_id": user_id, "amount": stage.price, **stage.payload}
            )

            # Send invoice
            await self.bot.send_invoice(
                chat_id=user_id,
                title=stage.title,
                description=stage.description,
                payload=payload,
                provider_token="",  # Empty for Telegram Stars
                currency="XTR",
                prices=prices,
                photo_url=photo,
                start_parameter=stage.start_parameter,
            )
            return True

        except Exception as e:
            raise NeonPayError(f"Telegram API error: {e}")

    async def setup_handlers(
        self, payment_callback: Callable[[PaymentResult], None]
    ) -> None:
        """Setup Aiogram payment handlers"""
        if self._handlers_setup:
            return

        self._payment_callback = payment_callback

        # Register handlers
        self.dispatcher.pre_checkout_query.register(self._handle_pre_checkout_query)
        self.dispatcher.message.register(
            self._handle_successful_payment,
            lambda message: message.successful_payment is not None,
        )

        self._handlers_setup = True

    async def _handle_pre_checkout_query(self, pre_checkout_query: "PreCheckoutQuery"):
        """Handle pre-checkout query"""
        try:
            await self.bot.answer_pre_checkout_query(
                pre_checkout_query_id=pre_checkout_query.id, ok=True
            )
        except Exception as e:
            logger.error(f"Error handling pre-checkout query: {e}")

    async def _handle_successful_payment(self, message: "Message"):
        """Handle successful payment"""
        if not self._payment_callback:
            return

        payment = message.successful_payment
        if not payment:
            return

        user_id = message.from_user.id

        # Parse payload
        payload_data = {}
        try:
            if payment.invoice_payload:
                payload_data = json.loads(payment.invoice_payload)
        except json.JSONDecodeError:
            pass

        # Create payment result
        result = PaymentResult(
            user_id=user_id,
            amount=payment.total_amount,
            currency=payment.currency,
            status=PaymentStatus.COMPLETED,
            transaction_id=payment.telegram_payment_charge_id,
            metadata=payload_data,
        )

        # Call payment callback
        await self._payment_callback(result)

    def get_library_info(self) -> Dict[str, str]:
        """Get Aiogram adapter information"""
        return {
            "library": "aiogram",
            "version": "3.0+",
            "features": [
                "Telegram Stars payments",
                "Pre-checkout handling",
                "Payment callbacks",
            ],
        }

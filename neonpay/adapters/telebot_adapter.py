"""
pyTelegramBotAPI adapter for NEONPAY
Supports pyTelegramBotAPI v4.0+ with Telegram Stars payments
"""

import json
import logging
import asyncio
import threading
from typing import Dict, Callable, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    import telebot

from ..core import PaymentAdapter, PaymentStage, PaymentResult, PaymentStatus
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
        self._payment_callback: Optional[Callable[[PaymentResult], None]] = None
        self._handlers_setup = False

    async def send_invoice(self, user_id: int, stage: PaymentStage) -> bool:
        """Send payment invoice using pyTelegramBotAPI"""
        try:
            # Create payload
            payload = json.dumps(
                {"user_id": user_id, "amount": stage.price, **stage.payload}
            )

            # Send invoice
            self.bot.send_invoice(
                user_id,
                title=stage.title,
                description=stage.description,
                invoice_payload=payload,
                provider_token="",  # Empty for Telegram Stars
                currency="XTR",
                prices=[{"label": stage.label, "amount": stage.price}],
                photo_url=stage.photo_url,
                start_parameter=stage.start_parameter,
            )
            return True

        except Exception as e:
            raise NeonPayError(f"Telegram API error: {e}")

    async def setup_handlers(
        self, payment_callback: Callable[[PaymentResult], None]
    ) -> None:
        """Setup pyTelegramBotAPI payment handlers"""
        if self._handlers_setup:
            return

        self._payment_callback = payment_callback

        # Register handlers
        self.bot.pre_checkout_query_handler(func=lambda query: True)(
            self._handle_pre_checkout_query
        )
        self.bot.message_handler(
            func=lambda message: message.successful_payment is not None
        )(self._handle_successful_payment)

        self._handlers_setup = True

    def _handle_pre_checkout_query(self, pre_checkout_query):
        """Handle pre-checkout query"""
        try:
            self.bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)
        except Exception as e:
            logger.error(f"Error handling pre-checkout query: {e}")

    def _handle_successful_payment(self, message):
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

        # Call payment callback safely (telebot is sync, callback might be async)
        self._call_async_callback(result)

    def _call_async_callback(self, result: PaymentResult):
        """Safely call async callback from sync context"""
        if not self._payment_callback:
            return

        try:
            # Try to get running loop
            try:
                asyncio.create_task(self._payment_callback(result))
            except RuntimeError:
                # No event loop running, create one in a separate thread
                def run_callback():
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    try:
                        loop.run_until_complete(self._payment_callback(result))
                    finally:
                        loop.close()

                thread = threading.Thread(target=run_callback)
                thread.start()

        except Exception as e:
            logger.error(f"Error calling payment callback: {e}")

    def get_library_info(self) -> Dict[str, str]:
        """Get pyTelegramBotAPI adapter information"""
        return {
            "library": "pyTelegramBotAPI",
            "version": "4.0+",
            "features": [
                "Telegram Stars payments",
                "Pre-checkout handling",
                "Payment callbacks",
            ],
        }

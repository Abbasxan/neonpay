"""
Official Telegram Bot API adapter for NEONPAY
Supports sync and async usage with Telegram Bot API.
"""

import asyncio
import json
import logging
import threading
from typing import Any, Awaitable, Callable, Dict, Optional, Union

from ..core import PaymentAdapter, PaymentResult, PaymentStage, PaymentStatus
from ..errors import NeonPayError

logger = logging.getLogger(__name__)


class BotAPIAdapter(PaymentAdapter):
    """Telegram Bot API adapter for NEONPAY"""

    def __init__(self, bot: Any) -> None:
        """
        Initialize Bot API adapter.

        Args:
            bot: telegram.Bot instance (from python-telegram-bot)
        """
        self.bot = bot
        self._handlers_setup = False
        self._payment_callback: Optional[
            Callable[[PaymentResult], Union[None, Awaitable[None]]]
        ] = None

    async def send_invoice(self, user_id: int, stage: PaymentStage) -> bool:
        """Send payment invoice using official Bot API"""
        payload_data = {"user_id": user_id, "amount": stage.price}
        if stage.payload:
            payload_data.update(stage.payload)
        payload = json.dumps(payload_data)

        try:
            await self._call_async(
                self.bot.send_invoice,
                chat_id=user_id,
                title=stage.title,
                description=stage.description,
                payload=payload,
                provider_token="",  # Empty for Telegram Stars  # nosec B106
                currency="XTR",
                prices=[{"label": stage.label, "amount": stage.price}],
                photo_url=stage.photo_url,
                start_parameter=stage.start_parameter,
            )
            return True
        except Exception as e:
            raise NeonPayError(f"Bot API error: {e}")

    async def setup_handlers(
        self, payment_callback: Callable[[PaymentResult], Union[None, Awaitable[None]]]
    ) -> None:
        """Setup Bot API payment handlers"""
        if self._handlers_setup:
            return

        self._payment_callback = payment_callback
        self._handlers_setup = True

    async def handle_pre_checkout_query(self, query: Any) -> None:
        """Handle pre-checkout query"""
        try:
            await self._call_async(
                self.bot.answer_pre_checkout_query,
                pre_checkout_query_id=query.id,
                ok=True,
            )
        except Exception as e:
            logger.error(f"Error handling pre-checkout query: {e}")

    async def handle_successful_payment(self, message: Any) -> None:
        """Handle successful payment"""
        if not self._payment_callback:
            return

        payment = message.successful_payment
        if not payment:
            return

        user_id = message.from_user.id
        payload_data: Dict[str, Any] = {}
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

        await self._call_async_callback(result)

    async def _call_async_callback(self, result: PaymentResult) -> None:
        """Safely call async callback from sync context"""
        if not self._payment_callback:
            return

        try:
            try:
                asyncio.get_running_loop()
                if self._payment_callback is not None:
                    task = self._payment_callback(result)
                    if asyncio.iscoroutine(task):
                        asyncio.create_task(task)
            except RuntimeError:

                def run() -> None:
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    try:
                        if self._payment_callback is not None:
                            task = self._payment_callback(result)
                            if asyncio.iscoroutine(task):
                                loop.run_until_complete(task)
                    finally:
                        loop.close()

                thread = threading.Thread(target=run)
                thread.start()
        except Exception as e:
            logger.error(f"Error calling payment callback: {e}")

    async def _call_async(self, func: Any, *args: Any, **kwargs: Any) -> Any:
        """Call sync function in thread-safe async way"""
        if asyncio.iscoroutinefunction(func):
            return await func(*args, **kwargs)
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, lambda: func(*args, **kwargs))

    def get_library_info(self) -> Dict[str, Any]:
        return {
            "library": "python-telegram-bot",
            "version": "20+",
            "features": [
                "Telegram Stars payments",
                "Pre-checkout handling",
                "Payment callbacks",
            ],
        }

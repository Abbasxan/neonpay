"""
Pyrogram adapter for NEONPAY

Supports Pyrogram v2.0+ with Telegram Stars payments
"""

import json
import logging
from typing import Dict, Callable, Optional, TYPE_CHECKING, Any
import asyncio
import threading

if TYPE_CHECKING:
    from pyrogram import Client
    from pyrogram.types import Message, SuccessfulPayment

from ..core import PaymentAdapter, PaymentStage, PaymentResult, PaymentStatus
from ..errors import NeonPayError

logger = logging.getLogger(__name__)


class PyrogramAdapter(PaymentAdapter):
    """Pyrogram library adapter for NEONPAY"""

    def __init__(self, client: "Client") -> None:
        """
        Initialize Pyrogram adapter
        Args:
            client: Pyrogram Client instance
        """
        self.client = client
        self._payment_callback: Optional[Callable[[PaymentResult], Any]] = None

    async def send_invoice(self, user_id: int, stage: PaymentStage) -> bool:
        """Send payment invoice using Pyrogram"""
        try:
            # Подготовим фото (у Pyrogram нет InputWebDocument, поэтому даём URL напрямую)
            photo = stage.photo_url if stage.photo_url else None

            # Создаём payload
            payload: str = json.dumps(
                {"user_id": user_id, "amount": stage.price, **(stage.payload or {})}
            )

            # Цены должны быть списком LabeledPrice, но Pyrogram принимает dict
            prices: list[dict[str, Any]] = [
                {"label": stage.label, "amount": stage.price}
            ]

            await self.client.send_invoice(
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
        self, payment_callback: Callable[[PaymentResult], Any]
    ) -> None:
        """Setup Pyrogram payment handlers"""
        self._payment_callback = payment_callback
        logger.info("Pyrogram payment handlers configured")

    async def handle_successful_payment(self, message: "Message") -> None:
        """Handle successful payment update from Pyrogram"""
        if not self._payment_callback:
            return

        payment: Optional["SuccessfulPayment"] = getattr(
            message, "successful_payment", None
        )
        if not payment:
            return

        # ⚠️ from_user может быть None, проверим
        if not message.from_user:
            logger.warning("Payment without from_user, skipping")
            return

        user_id: int = message.from_user.id
        payload_data: dict[str, Any] = {}
        try:
            if payment.invoice_payload:
                payload_data = json.loads(payment.invoice_payload)
        except json.JSONDecodeError:
            pass

        result = PaymentResult(
            user_id=user_id,
            amount=payment.total_amount,
            currency=payment.currency,
            status=PaymentStatus.COMPLETED,  # Enum вместо строки
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
                # Если есть активный цикл — запускаем задачу
                loop = asyncio.get_running_loop()
                loop.create_task(self._payment_callback(result))  # type: ignore
            except RuntimeError:
                # Если цикла нет — создаём новый в отдельном потоке
                def run() -> None:
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    try:
                        loop.run_until_complete(self._payment_callback(result))  # type: ignore
                    finally:
                        loop.close()

                thread = threading.Thread(target=run)
                thread.start()
        except Exception as e:
            logger.error(f"Error calling payment callback: {e}")

    def get_library_info(self) -> Dict[str, Any]:
        """Get Pyrogram adapter information"""
        return {
            "library": "pyrogram",
            "version": "2.0+",
            "features": [
                "Telegram Stars payments",
                "Photo support",
                "Payment callbacks",
            ],
        }

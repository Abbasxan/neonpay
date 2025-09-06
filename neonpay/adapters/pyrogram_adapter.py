"""
Pyrogram adapter for NEONPAY

Supports Pyrogram v2.0+ with Telegram Stars payments
"""

import asyncio
import json
import logging
import secrets
import threading
import traceback
from typing import TYPE_CHECKING, Any, Callable, Dict, Optional

if TYPE_CHECKING:
    from pyrogram import Client

from ..core import PaymentAdapter, PaymentResult, PaymentStage, PaymentStatus
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
        """Send payment invoice using Pyrogram raw API"""
        try:
            from pyrogram.raw.functions.messages import SendMedia
            from pyrogram.raw.types import (
                DataJSON,
                InputMediaInvoice,
                InputPeerUser,
                InputWebDocument,
                Invoice,
                LabeledPrice,
            )

            invoice = Invoice(
                currency="XTR",
                prices=[LabeledPrice(label=stage.label, amount=stage.price)],
            )

            payload = json.dumps(
                {"user_id": user_id, "amount": stage.price, **(stage.payload or {})}
            ).encode("utf-8")

            peer = await self.client.resolve_peer(user_id)
            if not isinstance(peer, InputPeerUser):
                raise NeonPayError(f"Cannot resolve user_id {user_id} to InputPeerUser")

            # Всегда передаём InputWebDocument, даже если картинки нет
            if stage.photo_url:
                photo_doc = InputWebDocument(
                    url=stage.photo_url, size=0, mime_type="image/png", attributes=[]
                )
            else:
                photo_doc = InputWebDocument(
                    url="", size=0, mime_type="application/octet-stream", attributes=[]
                )

            await self.client.invoke(
                SendMedia(
                    peer=peer,
                    media=InputMediaInvoice(
                        title=stage.title,
                        description=stage.description,
                        invoice=invoice,
                        payload=payload,  # bytes
                        provider="",  # Telegram Stars
                        provider_data=DataJSON(data="{}"),  # строка
                        photo=photo_doc,
                        start_param=stage.start_parameter or "neonpay_invoice",
                    ),
                    message=f"{stage.title}\n{stage.description}",
                    random_id=secrets.randbits(64),
                )
            )
            return True

        except Exception as e:
            logger.error("Send invoice failed:\n%s", traceback.format_exc())
            raise NeonPayError(f"Telegram API error: {e}") from e

    async def setup_handlers(
        self, payment_callback: Callable[[PaymentResult], Any]
    ) -> None:
        """Setup Pyrogram payment handlers"""
        self._payment_callback = payment_callback
        logger.info("Pyrogram payment handlers configured")

    async def handle_successful_payment(self, message: Any) -> None:
        """Handle successful payment update from Pyrogram"""
        if (
            not self._payment_callback
            or not hasattr(message, "successful_payment")
            or not message.successful_payment
        ):
            return

        payment = message.successful_payment

        if not hasattr(message, "from_user") or not message.from_user:
            logger.warning("Payment without from_user, skipping")
            return

        user_id: int = message.from_user.id
        payload_data: dict[str, Any] = {}
        try:
            if hasattr(payment, "invoice_payload") and payment.invoice_payload:
                payload_data = json.loads(str(payment.invoice_payload))
        except (json.JSONDecodeError, AttributeError) as e:
            logger.warning(f"Failed to parse invoice payload: {e}")

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
            loop = asyncio.get_running_loop()
            if loop.is_running():
                asyncio.create_task(self._payment_callback(result))
            else:
                await self._payment_callback(result)
        except RuntimeError:
            # fallback for sync context
            def run() -> None:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    if self._payment_callback:
                        loop.run_until_complete(self._payment_callback(result))
                finally:
                    loop.close()

            thread = threading.Thread(target=run, daemon=True)
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

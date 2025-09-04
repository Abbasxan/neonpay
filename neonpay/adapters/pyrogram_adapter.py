""" 
Pyrogram adapter for NEONPAY

Supports Pyrogram v2.0+ with Telegram Stars payments
"""

import json
import logging
import mimetypes
from typing import Dict, Callable, Optional, TYPE_CHECKING
import asyncio
import threading

if TYPE_CHECKING:
    from pyrogram import Client

from ..core import PaymentAdapter, PaymentStage, PaymentResult
from ..errors import NeonPayError

logger = logging.getLogger(__name__)


class PyrogramAdapter(PaymentAdapter):
    """Pyrogram library adapter for NEONPAY"""
    
    def __init__(self, client: "Client"):
        """
        Initialize Pyrogram adapter
        Args:
            client: Pyrogram Client instance
        """
        self.client = client
        self._payment_callback: Optional[Callable[[PaymentResult], None]] = None
    
    async def send_invoice(self, user_id: int, stage: PaymentStage) -> bool:
        """Send payment invoice using Pyrogram"""
        try:
            from pyrogram.types import InputWebDocument
            
            photo = None
            if stage.photo_url:
                mime_type, _ = mimetypes.guess_type(stage.photo_url)
                if not mime_type:
                    mime_type = "image/jpeg"
                
                photo = InputWebDocument(
                    url=stage.photo_url,
                    mime_type=mime_type,
                    estimated_size=1024
                )
            
            payload = json.dumps({
                "user_id": user_id,
                "amount": stage.price,
                **stage.payload
            })
            
            await self.client.send_invoice(
                chat_id=user_id,
                title=stage.title,
                description=stage.description,
                payload=payload,
                provider_token="",  # Empty for Telegram Stars
                currency="XTR",
                prices=[{"label": stage.label, "amount": stage.price}],
                photo=photo,
                start_parameter=stage.start_parameter
            )
            return True
        except Exception as e:
            raise NeonPayError(f"Telegram API error: {e}")
    
    async def setup_handlers(self, payment_callback: Callable[[PaymentResult], None]) -> None:
        """Setup Pyrogram payment handlers"""
        self._payment_callback = payment_callback
        logger.info("Pyrogram payment handlers configured")

    async def handle_successful_payment(self, message) -> None:
        """Handle successful payment update from Pyrogram"""
        if not self._payment_callback:
            return

        payment = getattr(message, "successful_payment", None)
        if not payment:
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
            status="COMPLETED",  # Можно использовать Enum, если он нужен
            transaction_id=payment.telegram_payment_charge_id,
            metadata=payload_data
        )

        await self._call_async_callback(result)

    async def _call_async_callback(self, result: PaymentResult) -> None:
        """Safely call async callback from sync context"""
        if not self._payment_callback:
            return

        try:
            try:
                asyncio.get_running_loop()
                asyncio.create_task(self._payment_callback(result))
            except RuntimeError:
                def run():
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    try:
                        loop.run_until_complete(self._payment_callback(result))
                    finally:
                        loop.close()

                thread = threading.Thread(target=run)
                thread.start()
        except Exception as e:
            logger.error(f"Error calling payment callback: {e}")
    
    def get_library_info(self) -> Dict[str, str]:
        """Get Pyrogram adapter information"""
        return {
            "library": "pyrogram",
            "version": "2.0+",
            "features": ["Telegram Stars payments", "Photo support", "Payment callbacks"] 
        }
        

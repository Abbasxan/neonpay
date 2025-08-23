"""
Pyrogram adapter for NEONPAY
Supports Pyrogram v2.0+ with Telegram Stars payments
"""

import json
import random
from typing import Dict, Any, Callable, Optional, Union
from pyrogram import Client
from pyrogram.raw.types import (
    LabeledPrice, Invoice, InputWebDocument,
    InputMediaInvoice, DataJSON,
    UpdateBotPrecheckoutQuery, MessageActionPaymentSentMe
)
from pyrogram.raw.functions.messages import SendMedia, SetBotPrecheckoutResults

from .base import PaymentAdapter
from ..core import PaymentStage, PaymentResult, PaymentStatus
from ..errors import NeonPayError
from ..localization import Language


class PyrogramAdapter(PaymentAdapter):
    """Pyrogram library adapter for NEONPAY"""
    
    def __init__(self, app: Client, language: Union[Language, str] = Language.EN):
        """
        Initialize Pyrogram adapter
        
        Args:
            app: Pyrogram Client instance
            language: Language for payment messages
        """
        super().__init__(language)
        self.app = app
        self._handlers_setup = False
    
    async def send_invoice(self, user_id: int, stage: PaymentStage) -> bool:
        """Send payment invoice using Pyrogram"""
        try:
            peer = await self.app.resolve_peer(user_id)
        except Exception as e:
            raise NeonPayError(self.get_text("errors.api_error", error=str(e)))

        # Create invoice
        invoice = Invoice(
            currency="XTR",
            prices=[LabeledPrice(label=stage.label, amount=stage.price)],
        )

        # Prepare photo
        photo = None
        if stage.photo_url:
            photo = InputWebDocument(
                url=stage.photo_url,
                size=0,
                mime_type="image/png",
                attributes=[]
            )

        payment_message = self.get_text(
            "messages.payment_instructions", 
            amount=stage.price, 
            product_name=stage.title
        )

        # Create media invoice
        media = InputMediaInvoice(
            title=stage.title,
            description=stage.description,
            invoice=invoice,
            payload=json.dumps({
                "user_id": user_id,
                "amount": stage.price,
                **stage.payload
            }).encode(),
            provider="",
            provider_data=DataJSON(data="{}"),
            photo=photo,
            start_param=stage.start_parameter,
        )

        try:
            await self.app.invoke(SendMedia(
                peer=peer,
                media=media,
                message=payment_message,
                random_id=random.getrandbits(64),
            ))
            return True
        except Exception as e:
            raise NeonPayError(self.get_text("errors.api_error", error=str(e)))
    
    async def setup_handlers(self, payment_callback: Callable[[PaymentResult], None]) -> None:
        """Setup Pyrogram payment handlers"""
        if self._handlers_setup:
            return
            
        self._payment_callback = payment_callback
        
        # Add raw update handler
        self.app.add_handler(self._on_raw_update, group=-1)
        self._handlers_setup = True
    
    async def _on_raw_update(self, client, update, users, chats):
        """Handle raw Pyrogram updates for payments"""
        # Handle pre-checkout query
        if isinstance(update, UpdateBotPrecheckoutQuery):
            await client.invoke(SetBotPrecheckoutResults(
                query_id=update.query_id,
                success=True
            ))
        
        # Handle successful payment
        if hasattr(update, "message") and hasattr(update.message, "action"):
            action = update.message.action
            if isinstance(action, MessageActionPaymentSentMe) and action.currency == "XTR":
                user_id = update.message.from_id.user_id
                amount = action.total_amount
                
                # Parse payload
                payload_data = {}
                try:
                    if action.payload:
                        payload_data = json.loads(action.payload.decode())
                except:
                    pass
                
                # Create payment result
                result = PaymentResult(
                    user_id=user_id,
                    amount=amount,
                    currency="XTR",
                    status=PaymentStatus.COMPLETED,
                    metadata=payload_data
                )
                
                # Call payment callback
                await self._payment_callback(result)
    
    def get_library_info(self) -> Dict[str, str]:
        """Get Pyrogram library information"""
        return {
            "library": "pyrogram",
            "version": getattr(self.app, "__version__", "unknown"),
            "adapter": "PyrogramAdapter",
            "language": self.localization.language.value
        }

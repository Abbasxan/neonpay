"""
Pyrogram adapter for NEONPAY
Supports Pyrogram v2.0+ with Telegram Stars payments
"""

import json
import logging
import mimetypes
from typing import Dict, Callable, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from pyrogram import Client
    from pyrogram.types import InputWebDocument

from ..core import PaymentAdapter, PaymentStage, PaymentResult, PaymentStatus
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
            # Import pyrogram types
            from pyrogram.types import InputWebDocument
            
            # Create photo document if provided
            photo = None
            if stage.photo_url:
                # Determine MIME type and estimated size
                mime_type, _ = mimetypes.guess_type(stage.photo_url)
                if not mime_type:
                    mime_type = "image/jpeg"
                
                photo = InputWebDocument(
                    url=stage.photo_url,
                    mime_type=mime_type,
                    estimated_size=1024  # Default estimated size
                )
            
            # Create payload
            payload = json.dumps({
                "user_id": user_id,
                "amount": stage.price,
                **stage.payload
            })
            
            # Send invoice
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
    
    def get_library_info(self) -> Dict[str, str]:
        """Get Pyrogram adapter information"""
        return {
            "library": "pyrogram",
            "version": "2.0+",
            "features": ["Telegram Stars payments", "Photo support", "Payment callbacks"]
        }

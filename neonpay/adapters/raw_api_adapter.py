"""
Raw Telegram Bot API adapter for NEONPAY
Direct integration with Telegram Bot API using HTTP requests
"""

import json
import aiohttp
from typing import Dict, Any, Callable, Optional
import logging

from ..core import PaymentAdapter, PaymentStage, PaymentResult, PaymentStatus
from ..errors import NeonPayError

logger = logging.getLogger(__name__)


class RawAPIAdapter(PaymentAdapter):
    """Raw Telegram Bot API adapter for NEONPAY"""
    
    def __init__(self, bot_token: str, webhook_url: Optional[str] = None):
        """
        Initialize Raw API adapter
        
        Args:
            bot_token: Telegram bot token
            webhook_url: Optional webhook URL for receiving updates
        """
        self.bot_token = bot_token
        self.webhook_url = webhook_url
        self.api_url = f"https://api.telegram.org/bot{bot_token}"
        self._payment_callback: Optional[Callable[[PaymentResult], None]] = None
        self._session: Optional[aiohttp.ClientSession] = None
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session"""
        if not self._session or self._session.closed:
            self._session = aiohttp.ClientSession()
        return self._session
    
    async def send_invoice(self, user_id: int, stage: PaymentStage) -> bool:
        """Send payment invoice using raw API"""
        session = await self._get_session()
        
        # Prepare invoice data
        data = {
            "chat_id": user_id,
            "title": stage.title,
            "description": stage.description,
            "payload": json.dumps({
                "user_id": user_id,
                "amount": stage.price,
                **stage.payload
            }),
            "provider_token": "",  # Empty for Telegram Stars
            "currency": "XTR",
            "prices": json.dumps([{
                "label": stage.label,
                "amount": stage.price
            }]),
            "start_parameter": stage.start_parameter
        }
        
        if stage.photo_url:
            data["photo_url"] = stage.photo_url
        
        try:
            async with session.post(f"{self.api_url}/sendInvoice", data=data) as response:
                result = await response.json()
                if result.get("ok"):
                    return True
                else:
                    raise NeonPayError(f"API Error: {result.get('description', 'Unknown error')}")
        except Exception as e:
            raise NeonPayError(f"Failed to send invoice: {e}")
    
    async def setup_handlers(self, payment_callback: Callable[[PaymentResult], None]) -> None:
        """Setup webhook for payment handling"""
        self._payment_callback = payment_callback
        
        if self.webhook_url:
            await self._set_webhook()
    
    async def _set_webhook(self):
        """Set webhook URL"""
        session = await self._get_session()
        
        data = {"url": self.webhook_url}
        
        try:
            async with session.post(f"{self.api_url}/setWebhook", data=data) as response:
                result = await response.json()
                if not result.get("ok"):
                    logger.error(f"Failed to set webhook: {result.get('description')}")
        except Exception as e:
            logger.error(f"Error setting webhook: {e}")
    
    async def handle_webhook_update(self, update_data: Dict[str, Any]):
        """
        Handle webhook update from Telegram
        
        This method should be called from your webhook handler
        """
        # Handle pre-checkout query
        if "pre_checkout_query" in update_data:
            await self._handle_pre_checkout_query(update_data["pre_checkout_query"])
        
        # Handle successful payment
        if "message" in update_data and "successful_payment" in update_data["message"]:
            await self._handle_successful_payment(update_data["message"])
    
    async def _handle_pre_checkout_query(self, pre_checkout_query: Dict[str, Any]):
        """Handle pre-checkout query"""
        session = await self._get_session()
        
        data = {
            "pre_checkout_query_id": pre_checkout_query["id"],
            "ok": True
        }
        
        try:
            async with session.post(f"{self.api_url}/answerPreCheckoutQuery", data=data) as response:
                result = await response.json()
                if not result.get("ok"):
                    logger.error(f"Failed to answer pre-checkout query: {result.get('description')}")
        except Exception as e:
            logger.error(f"Error answering pre-checkout query: {e}")
    
    async def _handle_successful_payment(self, message: Dict[str, Any]):
        """Handle successful payment"""
        if not self._payment_callback:
            return
            
        payment = message.get("successful_payment")
        if not payment:
            return
        
        user_id = message["from"]["id"]
        
        # Parse payload
        payload_data = {}
        try:
            if payment.get("invoice_payload"):
                payload_data = json.loads(payment["invoice_payload"])
        except:
            pass
        
        # Create payment result
        result = PaymentResult(
            user_id=user_id,
            amount=payment["total_amount"],
            currency=payment["currency"],
            status=PaymentStatus.COMPLETED,
            transaction_id=payment.get("telegram_payment_charge_id"),
            metadata=payload_data
        )
        
        # Call payment callback
        await self._payment_callback(result)
    
    async def close(self):
        """Close HTTP session"""
        if self._session and not self._session.closed:
            await self._session.close()
    
    def get_library_info(self) -> Dict[str, str]:
        """Get Raw API adapter information"""
        return {
            "library": "raw-telegram-api",
            "version": "1.0",
            "adapter": "RawAPIAdapter"
        }

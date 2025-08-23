"""
pyTelegramBotAPI (telebot) adapter for NEONPAY
Supports pyTelegramBotAPI v4.0+ with Telegram Stars payments
"""

from typing import Dict, Any, Callable, Optional, TYPE_CHECKING
import json
import logging

if TYPE_CHECKING:
    from telebot import TeleBot
    from telebot.types import Message, PreCheckoutQuery

from ..core import PaymentAdapter, PaymentStage, PaymentResult, PaymentStatus
from ..errors import NeonPayError

logger = logging.getLogger(__name__)


class TelebotAdapter(PaymentAdapter):
    """pyTelegramBotAPI (telebot) library adapter for NEONPAY"""
    
    def __init__(self, bot: "TeleBot"):
        """
        Initialize telebot adapter
        
        Args:
            bot: TeleBot instance
        """
        self.bot = bot
        self._handlers_setup = False
        self._payment_callback: Optional[Callable[[PaymentResult], None]] = None
    
    async def send_invoice(self, user_id: int, stage: PaymentStage) -> bool:
        """Send payment invoice using telebot"""
        try:
            # Import telebot types
            from telebot.types import LabeledPrice
            
            # Create price list
            prices = [LabeledPrice(label=stage.label, amount=stage.price)]
            
            # Create payload
            payload = json.dumps({
                "user_id": user_id,
                "amount": stage.price,
                **stage.payload
            })
            
            # Send invoice
            self.bot.send_invoice(
                chat_id=user_id,
                title=stage.title,
                description=stage.description,
                invoice_payload=payload,
                provider_token="",  # Empty for Telegram Stars
                currency="XTR",
                prices=prices,
                photo_url=stage.photo_url,
                start_parameter=stage.start_parameter
            )
            return True
            
        except Exception as e:
            raise NeonPayError(f"Failed to send invoice: {e}")
    
    async def setup_handlers(self, payment_callback: Callable[[PaymentResult], None]) -> None:
        """Setup telebot payment handlers"""
        if self._handlers_setup:
            return
            
        self._payment_callback = payment_callback
        
        # Register handlers
        self.bot.pre_checkout_query_handler(func=lambda query: True)(
            self._handle_pre_checkout_query
        )
        self.bot.message_handler(content_types=['successful_payment'])(
            self._handle_successful_payment
        )
        
        self._handlers_setup = True
    
    def _handle_pre_checkout_query(self, pre_checkout_query: "PreCheckoutQuery"):
        """Handle pre-checkout query"""
        self.bot.answer_pre_checkout_query(
            pre_checkout_query.id,
            ok=True
        )
    
    def _handle_successful_payment(self, message: "Message"):
        """Handle successful payment"""
        if not message.successful_payment:
            return
            
        payment = message.successful_payment
        user_id = message.from_user.id
        
        # Parse payload
        payload_data = {}
        try:
            if payment.invoice_payload:
                payload_data = json.loads(payment.invoice_payload)
        except:
            pass
        
        # Create payment result
        result = PaymentResult(
            user_id=user_id,
            amount=payment.total_amount,
            currency=payment.currency,
            status=PaymentStatus.COMPLETED,
            transaction_id=payment.telegram_payment_charge_id,
            metadata=payload_data
        )
        
        # Call payment callback (sync version)
        if self._payment_callback:
            import asyncio
            try:
                loop = asyncio.get_event_loop()
                loop.create_task(self._payment_callback(result))
            except RuntimeError:
                # If no event loop, run in new loop
                asyncio.run(self._payment_callback(result))
    
    def get_library_info(self) -> Dict[str, str]:
        """Get telebot library information"""
        try:
            import telebot
            version = telebot.__version__
        except:
            version = "unknown"
            
        return {
            "library": "pyTelegramBotAPI",
            "version": version,
            "adapter": "TelebotAdapter"
        }

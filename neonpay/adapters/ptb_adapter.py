"""
python-telegram-bot adapter for NEONPAY
Supports python-telegram-bot v20.0+ with Telegram Stars payments
"""

from typing import Dict, Any, Callable, Optional, TYPE_CHECKING
import json
import logging

if TYPE_CHECKING:
    from telegram import Bot, Update
    from telegram.ext import Application, ContextTypes

from ..core import PaymentAdapter, PaymentStage, PaymentResult, PaymentStatus
from ..errors import NeonPayError

logger = logging.getLogger(__name__)


class PythonTelegramBotAdapter(PaymentAdapter):
    """python-telegram-bot library adapter for NEONPAY"""
    
    def __init__(self, application: "Application"):
        """
        Initialize python-telegram-bot adapter
        
        Args:
            application: python-telegram-bot Application instance
        """
        self.application = application
        self.bot = application.bot
        self._handlers_setup = False
        self._payment_callback: Optional[Callable[[PaymentResult], None]] = None
    
    async def send_invoice(self, user_id: int, stage: PaymentStage) -> bool:
        """Send payment invoice using python-telegram-bot"""
        try:
            # Import telegram types
            from telegram import LabeledPrice
            
            # Create price list
            prices = [LabeledPrice(label=stage.label, amount=stage.price)]
            
            # Create payload
            payload = json.dumps({
                "user_id": user_id,
                "amount": stage.price,
                **stage.payload
            })
            
            # Send invoice
            await self.bot.send_invoice(
                chat_id=user_id,
                title=stage.title,
                description=stage.description,
                payload=payload,
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
        """Setup python-telegram-bot payment handlers"""
        if self._handlers_setup:
            return
            
        self._payment_callback = payment_callback
        
        # Import handler types
        from telegram.ext import PreCheckoutQueryHandler, MessageHandler, filters
        
        # Add handlers
        self.application.add_handler(
            PreCheckoutQueryHandler(self._handle_pre_checkout_query)
        )
        self.application.add_handler(
            MessageHandler(
                filters.SUCCESSFUL_PAYMENT,
                self._handle_successful_payment
            )
        )
        
        self._handlers_setup = True
    
    async def _handle_pre_checkout_query(self, update: "Update", context: "ContextTypes.DEFAULT_TYPE"):
        """Handle pre-checkout query"""
        query = update.pre_checkout_query
        await query.answer(ok=True)
    
    async def _handle_successful_payment(self, update: "Update", context: "ContextTypes.DEFAULT_TYPE"):
        """Handle successful payment"""
        message = update.message
        if not message or not message.successful_payment:
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
        
        # Call payment callback
        if self._payment_callback:
            await self._payment_callback(result)
    
    def get_library_info(self) -> Dict[str, str]:
        """Get python-telegram-bot library information"""
        try:
            import telegram
            version = telegram.__version__
        except:
            version = "unknown"
            
        return {
            "library": "python-telegram-bot",
            "version": version,
            "adapter": "PythonTelegramBotAdapter"
        }

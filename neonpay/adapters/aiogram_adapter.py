"""
Aiogram adapter for NEONPAY
Supports Aiogram v3.0+ with Telegram Stars payments
"""

from typing import Dict, Any, Callable, Optional, TYPE_CHECKING, Union
import json
import logging

if TYPE_CHECKING:
    from aiogram import Bot, Dispatcher
    from aiogram.types import LabeledPrice, InputFile, PreCheckoutQuery, Message

from .base import PaymentAdapter
from ..core import PaymentStage, PaymentResult, PaymentStatus
from ..errors import NeonPayError
from ..localization import Language

logger = logging.getLogger(__name__)


class AiogramAdapter(PaymentAdapter):
    """Aiogram library adapter for NEONPAY"""
    
    def __init__(
        self, 
        bot: "Bot", 
        dispatcher: Optional["Dispatcher"] = None,
        language: Union[Language, str] = Language.EN
    ):
        """
        Initialize Aiogram adapter
        
        Args:
            bot: Aiogram Bot instance
            dispatcher: Aiogram Dispatcher instance (optional)
            language: Language for payment messages
        """
        super().__init__(language)
        self.bot = bot
        self.dispatcher = dispatcher
        self._handlers_setup = False
        self._payment_callback: Optional[Callable[[PaymentResult], None]] = None
    
    async def send_invoice(self, user_id: int, stage: PaymentStage) -> bool:
        """Send payment invoice using Aiogram"""
        try:
            # Import aiogram types
            from aiogram.types import LabeledPrice, InputFile
            
            # Create price list
            prices = [LabeledPrice(label=stage.label, amount=stage.price)]
            
            # Prepare photo
            photo = None
            if stage.photo_url:
                photo = stage.photo_url
            
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
                photo_url=photo,
                start_parameter=stage.start_parameter
            )
            return True
            
        except Exception as e:
            raise NeonPayError(self.get_text("errors.api_error", error=str(e)))
    
    async def setup_handlers(self, payment_callback: Callable[[PaymentResult], None]) -> None:
        """Setup Aiogram payment handlers"""
        if self._handlers_setup or not self.dispatcher:
            return
            
        self._payment_callback = payment_callback
        
        # Register handlers
        self.dispatcher.pre_checkout_query.register(self._handle_pre_checkout_query)
        self.dispatcher.message.register(
            self._handle_successful_payment,
            lambda message: message.successful_payment is not None
        )
        
        self._handlers_setup = True
    
    async def _handle_pre_checkout_query(self, pre_checkout_query: "PreCheckoutQuery"):
        """Handle pre-checkout query"""
        await self.bot.answer_pre_checkout_query(
            pre_checkout_query.id,
            ok=True
        )
    
    async def _handle_successful_payment(self, message: "Message"):
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
        
        # Call payment callback
        if self._payment_callback:
            await self._payment_callback(result)
    
    def get_library_info(self) -> Dict[str, str]:
        """Get Aiogram library information"""
        try:
            import aiogram
            version = aiogram.__version__
        except:
            version = "unknown"
            
        return {
            "library": "aiogram",
            "version": version,
            "adapter": "AiogramAdapter",
            "language": self.localization.language.value
        }

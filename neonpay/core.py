"""
NEONPAY Core - Modern payment processing system for Telegram bots
Supports multiple Telegram bot libraries with unified API
"""

import json
import asyncio
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Callable, Union, List
from dataclasses import dataclass, field
from enum import Enum
import logging

from .localization import LocalizationManager, Language, _, get_localization_manager
from ._version import __version__

logger = logging.getLogger(__name__)


class PaymentStatus(Enum):
    """Payment status enumeration"""
    PENDING = "pending"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    FAILED = "failed"
    REFUNDED = "refunded"


class BotLibrary(Enum):
    """Supported bot libraries"""
    PYROGRAM = "pyrogram"
    AIOGRAM = "aiogram"
    PYTHON_TELEGRAM_BOT = "python-telegram-bot"
    TELEBOT = "telebot"


@dataclass
class PaymentStage:
    """
    Payment stage configuration
    
    Represents a complete payment setup with all necessary information
    for processing Telegram Stars payments.
    """
    title: str
    description: str
    price: int  # Price in Telegram Stars
    label: str = "Payment"
    photo_url: Optional[str] = None
    payload: Optional[Dict[str, Any]] = field(default_factory=dict)
    provider_token: str = ""
    start_parameter: str = "neonpay"
    
    def __post_init__(self):
        """Validate payment stage data"""
        if self.price <= 0:
            raise ValueError("Price must be positive")
        if not self.title.strip():
            raise ValueError("Title cannot be empty")
        if not self.description.strip():
            raise ValueError("Description cannot be empty")


@dataclass
class PaymentResult:
    """Payment processing result"""
    user_id: int
    amount: int
    currency: str = "XTR"
    status: PaymentStatus = PaymentStatus.COMPLETED
    stage: Optional[PaymentStage] = None
    transaction_id: Optional[str] = None
    timestamp: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class PaymentAdapter(ABC):
    """Abstract base class for bot library adapters"""
    
    @abstractmethod
    async def send_invoice(self, user_id: int, stage: PaymentStage) -> bool:
        """Send payment invoice to user"""
        pass
    
    @abstractmethod
    async def setup_handlers(self, payment_callback: Callable[[PaymentResult], None]) -> None:
        """Setup payment event handlers"""
        pass
    
    @abstractmethod
    def get_library_info(self) -> Dict[str, str]:
        """Get information about the bot library"""
        pass


class NeonPayCore:
    """
    Core NEONPAY payment processor
    
    Universal payment system that works with multiple Telegram bot libraries
    through adapter pattern.
    """
    
    def __init__(
        self, 
        adapter: PaymentAdapter, 
        thank_you_message: Optional[str] = None,
        language: Union[Language, str] = Language.EN
    ):
        self.adapter = adapter
        self.localization = LocalizationManager(language)

        if thank_you_message:
            self.thank_you_message = thank_you_message
            self._custom_thank_you = True
        else:
            self.thank_you_message = self.localization.get("messages.thank_you")
            self._custom_thank_you = False

        self._payment_stages: Dict[str, PaymentStage] = {}
        self._payment_callbacks: List[Callable[[PaymentResult], None]] = []
        self._setup_complete = False
        
    def set_language(self, language: Union[Language, str]) -> None:
        """
        Change the language for all payment messages
        """
        self.localization.set_language(language)
        if not self._custom_thank_you:
            self.thank_you_message = self.localization.get("messages.thank_you")
        logger.info(f"Language changed to: {self.localization.language.value}")
    
    def get_text(self, key: str, **kwargs) -> str:
        """Get localized text by key"""
        return self.localization.get(key, **kwargs)

    async def setup(self) -> None:
        """Initialize the payment system"""
        if self._setup_complete:
            return
            
        await self.adapter.setup_handlers(self._handle_payment)
        self._setup_complete = True
        logger.info(self.get_text("notifications.payment_started", amount="system"))
    
    def create_payment_stage(self, stage_id: str, stage: PaymentStage) -> None:
        """Create a new payment stage"""
        self._payment_stages[stage_id] = stage
        logger.info(f"Created payment stage: {stage_id}")
    
    def update_payment_stage(self, stage_id: str, **kwargs) -> bool:
        """Update payment stage parameters"""
        stage = self._payment_stages.get(stage_id)
        if not stage:
            return False
        for key, value in kwargs.items():
            if hasattr(stage, key):
                setattr(stage, key, value)
        logger.info(f"Updated payment stage: {stage_id}")
        return True
    
    def get_payment_stage(self, stage_id: str) -> Optional[PaymentStage]:
        """Get payment stage by ID"""
        return self._payment_stages.get(stage_id)
    
    def list_payment_stages(self) -> Dict[str, PaymentStage]:
        """Get all payment stages"""
        return self._payment_stages.copy()
    
    def remove_payment_stage(self, stage_id: str) -> bool:
        """Remove payment stage"""
        if stage_id in self._payment_stages:
            del self._payment_stages[stage_id]
            logger.info(f"Removed payment stage: {stage_id}")
            return True
        return False
    
    async def send_payment(self, user_id: int, stage_id: str) -> bool:
        """Send payment invoice to user"""
        if not self._setup_complete:
            await self.setup()
            
        stage = self.get_payment_stage(stage_id)
        if not stage:
            logger.error(self.get_text("errors.payment_not_found"))
            return False
            
        try:
            result = await self.adapter.send_invoice(user_id, stage)
            if result:
                logger.info(self.get_text("notifications.payment_started", amount=stage.price))
            return result
        except Exception as e:
            logger.error(self.get_text("errors.api_error", error=str(e)))
            return False
    
    def on_payment(self, callback: Callable[[PaymentResult], None]) -> None:
        """Register payment completion callback"""
        self._payment_callbacks.append(callback)
    
    async def _handle_payment(self, result: PaymentResult) -> None:
        """Internal payment handler"""
        logger.info(self.get_text("notifications.payment_completed", amount=result.amount))
        
        for callback in self._payment_callbacks:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(result)
                else:
                    callback(result)
            except Exception as e:
                logger.exception(self.get_text("errors.unknown_error") + f": {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get payment system statistics"""
        return {
            "version": __version__,
            "total_stages": len(self._payment_stages),
            "registered_callbacks": len(self._payment_callbacks),
            "setup_complete": self._setup_complete,
            "adapter_info": self.adapter.get_library_info(),
            "current_language": self.localization.language.value
        }

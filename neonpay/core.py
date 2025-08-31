"""
NEONPAY Core - Modern payment processing system for Telegram bots
Supports multiple Telegram bot libraries with unified API
"""

import json
import asyncio
import re
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Callable, Union, List
from dataclasses import dataclass, field
from enum import Enum
import logging
from urllib.parse import urlparse

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


def validate_url(url: str, require_https: bool = False) -> bool:
    """Validate URL format and security"""
    if not url:
        return False
    
    try:
        parsed = urlparse(url)
        if not parsed.scheme or not parsed.netloc:
            return False
        
        if require_https and parsed.scheme != 'https':
            return False
            
        return True
    except Exception:
        return False


def validate_json_payload(payload: Dict[str, Any]) -> bool:
    """Validate JSON payload structure and size"""
    if not isinstance(payload, dict):
        return False
    
    # Check payload size (max 1024 bytes when serialized)
    try:
        serialized = json.dumps(payload)
        if len(serialized.encode('utf-8')) > 1024:
            return False
        return True
    except Exception:
        return False


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
        """Validate payment stage data with enhanced security"""
        # Validate price
        if not isinstance(self.price, int):
            raise ValueError("Price must be an integer")
        
        if not (1 <= self.price <= 2500):
            raise ValueError("Price must be between 1 and 2500 Telegram Stars")
        
        # Validate title
        if not isinstance(self.title, str) or not self.title.strip():
            raise ValueError("Title must be a non-empty string")
        
        if len(self.title) > 32:
            raise ValueError("Title must be 32 characters or less")
        
        # Validate description
        if not isinstance(self.description, str) or not self.description.strip():
            raise ValueError("Description must be a non-empty string")
        
        if len(self.description) > 255:
            raise ValueError("Description must be 255 characters or less")
        
        # Validate label
        if not isinstance(self.label, str) or not self.label.strip():
            raise ValueError("Label must be a non-empty string")
        
        if len(self.label) > 32:
            raise ValueError("Label must be 32 characters or less")
        
        # Validate photo URL
        if self.photo_url is not None:
            if not isinstance(self.photo_url, str):
                raise ValueError("Photo URL must be a string")
            
            if not validate_url(self.photo_url):
                raise ValueError("Photo URL must be a valid URL")
        
        # Validate payload
        if self.payload is not None:
            if not isinstance(self.payload, dict):
                raise ValueError("Payload must be a dictionary")
            
            if not validate_json_payload(self.payload):
                raise ValueError("Payload must be valid JSON and under 1024 bytes")
        
        # Validate start parameter
        if not isinstance(self.start_parameter, str) or not self.start_parameter.strip():
            raise ValueError("Start parameter must be a non-empty string")
        
        if len(self.start_parameter) > 64:
            raise ValueError("Start parameter must be 64 characters or less")
        
        # Validate start parameter format (alphanumeric + underscore only)
        if not re.match(r'^[a-zA-Z0-9_]+$', self.start_parameter):
            raise ValueError("Start parameter can only contain letters, numbers, and underscores")


@dataclass
class PaymentResult:
    """Payment processing result with enhanced validation"""
    user_id: int
    amount: int
    currency: str = "XTR"
    status: PaymentStatus = PaymentStatus.COMPLETED
    stage: Optional[PaymentStage] = None
    transaction_id: Optional[str] = None
    timestamp: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Validate payment result data"""
        # Validate user_id
        if not isinstance(self.user_id, int) or self.user_id <= 0:
            raise ValueError("User ID must be a positive integer")
        
        # Validate amount
        if not isinstance(self.amount, int) or self.amount <= 0:
            raise ValueError("Amount must be a positive integer")
        
        # Validate currency
        if not isinstance(self.currency, str) or self.currency != "XTR":
            raise ValueError("Currency must be 'XTR' for Telegram Stars")
        
        # Validate status
        if not isinstance(self.status, PaymentStatus):
            raise ValueError("Status must be a valid PaymentStatus")
        
        # Validate transaction_id
        if self.transaction_id is not None:
            if not isinstance(self.transaction_id, str) or not self.transaction_id.strip():
                raise ValueError("Transaction ID must be a non-empty string")
        
        # Validate timestamp
        if self.timestamp is not None:
            if not isinstance(self.timestamp, (int, float)) or self.timestamp <= 0:
                raise ValueError("Timestamp must be a positive number")
        
        # Validate metadata
        if not isinstance(self.metadata, dict):
            raise ValueError("Metadata must be a dictionary")


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
        enable_logging: bool = True,
        max_stages: int = 100
    ):
        self.adapter = adapter
        self.thank_you_message = thank_you_message or "Thank you for your payment!"
        self._payment_stages: Dict[str, PaymentStage] = {}
        self._payment_callbacks: List[Callable[[PaymentResult], None]] = []
        self._setup_complete = False
        self._enable_logging = enable_logging
        self._max_stages = max_stages
        
        if self._enable_logging:
            logger.info(f"NeonPayCore initialized with {adapter.__class__.__name__}")
    
    def create_payment_stage(self, stage_id: str, stage: PaymentStage) -> None:
        """
        Create a new payment stage with validation
        
        Args:
            stage_id: Unique identifier for the payment stage
            stage: PaymentStage configuration
        """
        # Validate stage_id
        if not isinstance(stage_id, str) or not stage_id.strip():
            raise ValueError("Stage ID is required")
        
        if len(stage_id) > 64:
            raise ValueError("Stage ID must be 64 characters or less")
        
        # Check if stage_id already exists
        if stage_id in self._payment_stages:
            raise ValueError(f"Payment stage with ID '{stage_id}' already exists")
        
        # Check maximum stages limit
        if len(self._payment_stages) >= self._max_stages:
            raise ValueError(f"Maximum number of payment stages ({self._max_stages}) reached")
        
        self._payment_stages[stage_id] = stage
        
        if self._enable_logging:
            logger.info(f"Created payment stage: {stage_id}")
    
    def get_payment_stage(self, stage_id: str) -> Optional[PaymentStage]:
        """Get payment stage by ID"""
        if not isinstance(stage_id, str):
            raise ValueError("Stage ID must be a string")
        
        return self._payment_stages.get(stage_id)
    
    def list_payment_stages(self) -> Dict[str, PaymentStage]:
        """Get all payment stages"""
        return self._payment_stages.copy()
    
    def remove_payment_stage(self, stage_id: str) -> bool:
        """Remove payment stage"""
        if not isinstance(stage_id, str):
            raise ValueError("Stage ID must be a string")
        
        if stage_id in self._payment_stages:
            del self._payment_stages[stage_id]
            
            if self._enable_logging:
                logger.info(f"Removed payment stage: {stage_id}")
            return True
        return False
    
    async def setup(self) -> None:
        """Initialize the payment system"""
        if self._setup_complete:
            return
            
        await self.adapter.setup_handlers(self._handle_payment)
        self._setup_complete = True
        
        if self._enable_logging:
            logger.info("Payment system initialized")
    
    async def send_payment(self, user_id: int, stage_id: str) -> bool:
        """
        Send payment invoice to user with validation
        
        Args:
            user_id: Telegram user ID
            stage_id: Payment stage identifier
            
        Returns:
            True if invoice was sent successfully
        """
        # Validate user_id
        if not isinstance(user_id, int) or user_id <= 0:
            raise ValueError("User ID must be a positive integer")
        
        # Validate stage_id
        if not isinstance(stage_id, str) or not stage_id.strip():
            raise ValueError("Stage ID is required")
        
        if not self._setup_complete:
            await self.setup()
            
        stage = self.get_payment_stage(stage_id)
        if not stage:
            logger.error("Payment stage not found")
            return False
            
        try:
            result = await self.adapter.send_invoice(user_id, stage)
            if result:
                if self._enable_logging:
                    logger.info(f"Payment invoice sent: {stage.price} Stars")
            return result
        except Exception as e:
            logger.error(f"Failed to send payment invoice: {e}")
            return False
    
    def on_payment(self, callback: Callable[[PaymentResult], None]) -> None:
        """
        Register payment completion callback
        
        Args:
            callback: Function to call when payment is completed
        """
        if not callable(callback):
            raise ValueError("Callback must be callable")
        
        self._payment_callbacks.append(callback)
        
        if self._enable_logging:
            logger.info(f"Payment callback registered: {callback.__name__}")
    
    async def _handle_payment(self, result: PaymentResult) -> None:
        """Internal payment handler with error handling"""
        if self._enable_logging:
            logger.info(f"Payment completed: {result.amount} Stars")
        
        # Call all registered callbacks
        for callback in self._payment_callbacks:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(result)
                else:
                    callback(result)
            except Exception as e:
                logger.error(f"Error in payment callback {callback.__name__}: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get payment system statistics"""
        return {
            "total_stages": len(self._payment_stages),
            "registered_callbacks": len(self._payment_callbacks),
            "setup_complete": self._setup_complete,
            "adapter_info": self.adapter.get_library_info(),
            "max_stages": self._max_stages,
            "logging_enabled": self._enable_logging
        }

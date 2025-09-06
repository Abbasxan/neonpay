"""Base adapter for bot library integration."""

from abc import ABC, abstractmethod
from typing import Callable, Dict

from ..core import PaymentResult, PaymentStage


class PaymentAdapter(ABC):
    """Abstract base class for bot library adapters"""

    def __init__(self) -> None:
        """Initialize adapter."""
        pass

    @abstractmethod
    async def send_invoice(self, user_id: int, stage: PaymentStage) -> bool:
        """Send payment invoice to user"""
        pass

    @abstractmethod
    async def setup_handlers(
        self, payment_callback: Callable[[PaymentResult], None]
    ) -> None:
        """Setup payment event handlers"""
        pass

    @abstractmethod
    def get_library_info(self) -> Dict[str, str]:
        """Get information about the bot library"""
        pass

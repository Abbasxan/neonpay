"""
NEONPAY Middleware System
Provides flexible payment processing pipeline with hooks and filters.
"""

import logging
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict, List, Optional

from .core import PaymentResult, PaymentStage


class PaymentMiddleware(ABC):
    """Base class for payment middleware."""

    @abstractmethod
    async def before_payment(
        self, stage: PaymentStage, context: Dict[str, Any]
    ) -> Optional[PaymentStage]:
        """Called before payment processing. Return None to stop processing."""
        pass

    @abstractmethod
    async def after_payment(
        self, result: PaymentResult, context: Dict[str, Any]
    ) -> Optional[PaymentResult]:
        """Called after payment processing. Return None to stop processing."""
        pass

    @abstractmethod
    async def on_error(self, error: Exception, context: Dict[str, Any]) -> bool:
        """Called when error occurs. Return True to continue, False to stop."""
        pass


class LoggingMiddleware(PaymentMiddleware):
    """Middleware for logging payment operations."""

    def __init__(self, logger: Optional[logging.Logger] = None):
        self.logger = logger or logging.getLogger("neonpay.payments")

    async def before_payment(
        self, stage: PaymentStage, context: Dict[str, Any]
    ) -> Optional[PaymentStage]:
        self.logger.info(f"Processing payment: {stage.title} - {stage.price} XTR")
        context["start_time"] = datetime.now()
        return stage

    async def after_payment(
        self, result: PaymentResult, context: Dict[str, Any]
    ) -> Optional[PaymentResult]:
        start_time = context.get("start_time")
        if isinstance(start_time, datetime):
            duration = datetime.now() - start_time
            self.logger.info(f"Payment completed in {duration.total_seconds():.2f}s")
        else:
            self.logger.info("Payment completed")
        return result

    async def on_error(self, error: Exception, context: Dict[str, Any]) -> bool:
        self.logger.error(f"Payment error: {error}")
        return True


class ValidationMiddleware(PaymentMiddleware):
    """Middleware for payment validation."""

    def __init__(self, min_price: int = 1, max_price: int = 2500):
        self.min_price = min_price
        self.max_price = max_price

    async def before_payment(
        self, stage: PaymentStage, context: Dict[str, Any]
    ) -> Optional[PaymentStage]:
        if not (self.min_price <= stage.price <= self.max_price):
            raise ValueError(
                f"Price must be between {self.min_price} and {self.max_price} XTR"
            )

        if not stage.title.strip():
            raise ValueError("Payment title cannot be empty")

        return stage

    async def after_payment(
        self, result: PaymentResult, context: Dict[str, Any]
    ) -> Optional[PaymentResult]:
        return result

    async def on_error(self, error: Exception, context: Dict[str, Any]) -> bool:
        return True


class WebhookMiddleware(PaymentMiddleware):
    """Middleware for webhook notifications."""

    def __init__(self, webhook_url: str, secret_key: Optional[str] = None):
        self.webhook_url = webhook_url
        self.secret_key = secret_key

    async def before_payment(
        self, stage: PaymentStage, context: Dict[str, Any]
    ) -> Optional[PaymentStage]:
        return stage

    async def after_payment(
        self, result: PaymentResult, context: Dict[str, Any]
    ) -> Optional[PaymentResult]:
        if hasattr(result, "transaction_id") and result.transaction_id:
            await self._send_webhook(
                "payment_success",
                {
                    "payment_id": result.transaction_id,
                    "user_id": context.get("user_id"),
                    "amount": getattr(result, "amount", 0),
                    "timestamp": datetime.now().isoformat(),
                },
            )
        return result

    async def on_error(self, error: Exception, context: Dict[str, Any]) -> bool:
        await self._send_webhook(
            "payment_error",
            {
                "error": str(error),
                "user_id": context.get("user_id"),
                "timestamp": datetime.now().isoformat(),
            },
        )
        return True

    async def _send_webhook(self, event_type: str, data: Dict[str, Any]) -> None:
        """Send webhook notification."""
        import hashlib
        import hmac

        import aiohttp

        payload = {"event": event_type, "data": data}

        headers = {"Content-Type": "application/json"}

        if self.secret_key:
            signature = hmac.new(
                self.secret_key.encode(), str(payload).encode(), hashlib.sha256
            ).hexdigest()
            headers["X-NeonPay-Signature"] = f"sha256={signature}"

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.webhook_url, json=payload, headers=headers
                ) as response:
                    if response.status != 200:
                        logging.warning(f"Webhook failed: {response.status}")
        except Exception as e:
            logging.error(f"Webhook error: {e}")


class MiddlewareManager:
    """Manages payment middleware pipeline."""

    def __init__(self) -> None:
        self.middlewares: List[PaymentMiddleware] = []
        self.logger: logging.Logger = logging.getLogger(__name__)

    def add_middleware(self, middleware: PaymentMiddleware) -> None:
        """Add middleware to the pipeline."""
        self.middlewares.append(middleware)

    def remove_middleware(self, middleware_class: type) -> None:
        """Remove middleware by class type."""
        self.middlewares = [
            m for m in self.middlewares if not isinstance(m, middleware_class)
        ]

    async def process_before_payment(
        self, stage: PaymentStage, context: Dict[str, Any]
    ) -> Optional[PaymentStage]:
        """Process all before_payment middleware."""
        current_stage = stage

        for middleware in self.middlewares:
            try:
                result = await middleware.before_payment(current_stage, context)
                if result is None:
                    return None
                current_stage = result
            except Exception as e:
                should_continue = await middleware.on_error(e, context)
                if not should_continue:
                    raise

        return current_stage

    async def process_after_payment(
        self, result: PaymentResult, context: Dict[str, Any]
    ) -> Optional[PaymentResult]:
        """Process all after_payment middleware."""
        current_result: Optional[PaymentResult] = result

        for middleware in self.middlewares:
            try:
                if current_result is None:
                    return None
                processed_result = await middleware.after_payment(
                    current_result, context
                )
                current_result = processed_result
            except Exception as e:
                should_continue = await middleware.on_error(e, context)
                if not should_continue:
                    raise

        return current_result

    async def handle_error(self, error: Exception, context: Dict[str, Any]) -> bool:
        """Handle error through all middleware."""
        for middleware in self.middlewares:
            try:
                should_continue = await middleware.on_error(error, context)
                if not should_continue:
                    return False
            except Exception as middleware_error:
                # Log middleware error but continue processing other middlewares
                self.logger.warning(
                    f"Middleware {middleware.__class__.__name__} failed to handle error: {middleware_error}"
                )
                # Continue to next middleware instead of using continue statement
                pass

        return True

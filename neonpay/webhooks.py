"""
Webhook handling and verification for NEONPAY

Secure webhook processing with signature validation

"""

import asyncio
import hashlib
import hmac
import json
import logging
import time
from typing import Any, Callable, Dict, List, Optional

from .errors import NeonPayError

logger = logging.getLogger(__name__)


class WebhookVerifier:
    """Secure webhook verification with signature and timestamp validation"""

    def __init__(self, secret_token: str, max_age: int = 300):
        """
        Initialize webhook verifier

        Args:
            secret_token: Secret token for signature verification
            max_age: Maximum age of webhook in seconds (default: 5 minutes)
        """
        self.secret_token = secret_token
        self.max_age = max_age

    def verify_signature(self, payload: str, signature: str) -> bool:
        """
        Verify webhook signature using HMAC-SHA256

        Args:
            payload: Raw webhook payload
            signature: X-Telegram-Bot-Api-Signature header value

        Returns:
            True if signature is valid
        """
        if not signature:
            return False

        try:
            # Remove 'sha256=' prefix if present
            if signature.startswith("sha256="):
                signature = signature[7:]

            # Calculate expected signature
            expected_signature = hmac.new(
                self.secret_token.encode("utf-8"),
                payload.encode("utf-8"),
                hashlib.sha256,
            ).hexdigest()

            # Compare signatures (constant-time comparison)
            return hmac.compare_digest(signature, expected_signature)

        except Exception as e:
            logger.error(f"Error verifying signature: {e}")
            return False

    def verify_timestamp(self, timestamp: Optional[str] = None) -> bool:
        """
        Verify webhook timestamp is within acceptable range

        Args:
            timestamp: X-Telegram-Bot-Api-Timestamp header value

        Returns:
            True if timestamp is valid
        """
        if not timestamp:
            return False

        try:
            webhook_time = int(timestamp)
            current_time = int(time.time())

            # Check if webhook is too old
            if current_time - webhook_time > self.max_age:
                return False

            # Check if webhook is from the future (allow 60 seconds clock skew)
            if webhook_time > current_time + 60:
                return False

            return True

        except (ValueError, TypeError):
            return False

    def verify_webhook(self, payload: str, signature: str, timestamp: str) -> bool:
        """
        Verify webhook authenticity

        Args:
            payload: Raw webhook payload
            signature: X-Telegram-Bot-Api-Signature header value
            timestamp: X-Telegram-Bot-Api-Timestamp header value

        Returns:
            True if webhook is authentic
        """
        # Verify signature first
        if not self.verify_signature(payload, signature):
            logger.warning("Invalid webhook signature")
            return False

        # Verify timestamp
        if not self.verify_timestamp(timestamp):
            logger.warning("Invalid webhook timestamp")
            return False

        return True


class WebhookHandler:
    """Secure webhook event handler with validation"""

    def __init__(self, verifier: WebhookVerifier):
        """
        Initialize webhook handler

        Args:
            verifier: WebhookVerifier instance
        """
        self.verifier = verifier
        self._event_handlers: Dict[str, List[Callable]] = {}
        self._default_handler: Optional[Callable] = None

    def on_event(self, event_type: str, handler: Callable) -> None:
        """
        Register event handler

        Args:
            event_type: Type of event to handle
            handler: Function to call for this event type
        """
        if not callable(handler):
            raise ValueError("Handler must be callable")

        if event_type not in self._event_handlers:
            self._event_handlers[event_type] = []

        self._event_handlers[event_type].append(handler)
        logger.info(f"Registered handler for event: {event_type}")

    def on_default(self, handler: Callable) -> None:
        """
        Register default handler for unhandled events

        Args:
            handler: Function to call for unhandled events
        """
        if not callable(handler):
            raise ValueError("Handler must be callable")

        self._default_handler = handler
        logger.info("Registered default event handler")

    async def process_webhook(
        self,
        payload: str,
        signature: str,
        timestamp: str,
        headers: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """
        Process incoming webhook with full validation

        Args:
            payload: Raw webhook payload
            signature: X-Telegram-Bot-Api-Signature header value
            timestamp: X-Telegram-Bot-Api-Timestamp header value
            headers: Additional headers for validation

        Returns:
            Processing result

        Raises:
            NeonPayError: If webhook validation fails
        """
        # Validate webhook authenticity
        if not self.verifier.verify_webhook(payload, signature, timestamp):
            raise NeonPayError("Webhook verification failed")

        try:
            # Parse payload
            data = json.loads(payload)

            # Extract event type
            event_type = self._extract_event_type(data)

            # Log webhook receipt
            logger.info("Webhook received and processed")

            # Process event
            result = await self._process_event(event_type, data, headers)

            return {
                "success": True,
                "event_type": event_type,
                "result": result,
                "timestamp": timestamp,
            }

        except json.JSONDecodeError:
            raise NeonPayError("Invalid JSON payload")
        except Exception as e:
            logger.error(f"Error processing webhook: {e}")
            raise NeonPayError("An unknown error occurred")

    def _extract_event_type(self, data: Dict[str, Any]) -> str:
        """Extract event type from webhook data"""
        # Check for common Telegram update types
        if "message" in data:
            if "successful_payment" in data["message"]:
                return "payment_success"
            return "message"
        elif "pre_checkout_query" in data:
            return "pre_checkout"
        elif "callback_query" in data:
            return "callback_query"
        elif "inline_query" in data:
            return "inline_query"
        elif "chosen_inline_result" in data:
            return "chosen_inline_result"
        else:
            return "unknown"

    async def _process_event(
        self,
        event_type: str,
        data: Dict[str, Any],
        headers: Optional[Dict[str, str]] = None,
    ) -> Any:
        """Process specific event type"""
        handlers = self._event_handlers.get(event_type, [])

        if not handlers and self._default_handler:
            # Use default handler
            if asyncio.iscoroutinefunction(self._default_handler):
                return await self._default_handler(event_type, data, headers)
            else:
                return self._default_handler(event_type, data, headers)

        # Call all registered handlers
        results = []
        for handler in handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    result = await handler(event_type, data, headers)
                else:
                    result = handler(event_type, data, headers)
                results.append(result)
            except Exception as e:
                logger.error(f"Error in event handler {handler.__name__}: {e}")
                results.append({"error": str(e)})

        return results if len(results) > 1 else results[0] if results else None

    def get_stats(self) -> Dict[str, Any]:
        """Get webhook handler statistics"""
        return {
            "registered_events": list(self._event_handlers.keys()),
            "total_handlers": sum(
                len(handlers) for handlers in self._event_handlers.values()
            ),
            "has_default_handler": self._default_handler is not None,
            "verifier_max_age": self.verifier.max_age,
        }


# Convenience function for creating secure webhook handler
def create_secure_webhook_handler(
    secret_token: str, max_age: int = 300
) -> WebhookHandler:
    """
    Create a secure webhook handler with verification

    Args:
        secret_token: Secret token for signature verification
        max_age: Maximum age of webhook in seconds

    Returns:
        Configured WebhookHandler instance
    """
    verifier = WebhookVerifier(secret_token, max_age)
    return WebhookHandler(verifier)

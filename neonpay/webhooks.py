"""
NEONPAY Webhook System
Provides webhook handling and verification utilities.
"""

import hashlib
import hmac
import json
from typing import Any, Dict, Optional, Callable
from datetime import datetime, timedelta
import asyncio


class WebhookVerifier:
    """Verifies webhook signatures and timestamps."""
    
    def __init__(self, secret_key: str, tolerance_seconds: int = 300):
        self.secret_key = secret_key
        self.tolerance_seconds = tolerance_seconds
    
    def verify_signature(self, payload: str, signature: str) -> bool:
        """Verify webhook signature."""
        if not signature.startswith("sha256="):
            return False
        
        expected_signature = hmac.new(
            self.secret_key.encode(),
            payload.encode(),
            hashlib.sha256
        ).hexdigest()
        
        provided_signature = signature[7:]  # Remove "sha256=" prefix
        
        return hmac.compare_digest(expected_signature, provided_signature)
    
    def verify_timestamp(self, timestamp: str) -> bool:
        """Verify webhook timestamp is within tolerance."""
        try:
            webhook_time = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            current_time = datetime.now(webhook_time.tzinfo)
            
            time_diff = abs((current_time - webhook_time).total_seconds())
            return time_diff <= self.tolerance_seconds
        except (ValueError, TypeError):
            return False


class WebhookHandler:
    """Handles incoming webhooks."""
    
    def __init__(self, secret_key: Optional[str] = None):
        self.verifier = WebhookVerifier(secret_key) if secret_key else None
        self.handlers: Dict[str, Callable] = {}
    
    def register_handler(self, event_type: str, handler: Callable):
        """Register handler for specific event type."""
        self.handlers[event_type] = handler
    
    def on(self, event_type: str):
        """Decorator for registering event handlers."""
        def decorator(func: Callable):
            self.register_handler(event_type, func)
            return func
        return decorator
    
    async def handle_webhook(self, payload: str, signature: Optional[str] = None) -> Dict[str, Any]:
        """Handle incoming webhook."""
        # Verify signature if verifier is configured
        if self.verifier and signature:
            if not self.verifier.verify_signature(payload, signature):
                raise ValueError("Invalid webhook signature")
        
        try:
            data = json.loads(payload)
        except json.JSONDecodeError:
            raise ValueError("Invalid JSON payload")
        
        event_type = data.get("event")
        if not event_type:
            raise ValueError("Missing event type")
        
        # Verify timestamp if present
        if self.verifier and "timestamp" in data.get("data", {}):
            if not self.verifier.verify_timestamp(data["data"]["timestamp"]):
                raise ValueError("Webhook timestamp too old")
        
        # Handle event
        handler = self.handlers.get(event_type)
        if handler:
            if asyncio.iscoroutinefunction(handler):
                result = await handler(data["data"])
            else:
                result = handler(data["data"])
            
            return {
                "status": "success",
                "event": event_type,
                "result": result
            }
        else:
            return {
                "status": "ignored",
                "event": event_type,
                "message": f"No handler for event: {event_type}"
            }


# Example webhook handlers
def create_webhook_handlers() -> WebhookHandler:
    """Create webhook handler with common event handlers."""
    handler = WebhookHandler()
    
    @handler.on("payment_success")
    async def handle_payment_success(data: Dict[str, Any]):
        """Handle successful payment."""
        print(f"Payment successful: {data.get('payment_id')} for user {data.get('user_id')}")
        # Add your custom logic here
        return {"processed": True}
    
    @handler.on("payment_error")
    async def handle_payment_error(data: Dict[str, Any]):
        """Handle payment error."""
        print(f"Payment error for user {data.get('user_id')}: {data.get('error')}")
        # Add your custom logic here
        return {"processed": True}
    
    return handler

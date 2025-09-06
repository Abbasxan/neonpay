"""
NEONPAY Webhook Server Example
Simple webhook server to handle NEONPAY notifications.
"""

from typing import Optional

import uvicorn
from fastapi import FastAPI, Header, HTTPException, Request

from neonpay.webhooks import WebhookHandler

app = FastAPI(title="NEONPAY Webhook Server", version="1.0.0")

# Initialize webhook handler with secret key
webhook_handler = WebhookHandler(secret_key="your_webhook_secret_key")


# Custom event handlers
@webhook_handler.on("payment_success")
async def handle_payment_success(data):
    """Handle successful payment."""
    user_id = data.get("user_id")
    payment_id = data.get("payment_id")
    amount = data.get("amount")

    print(f"✅ Payment successful: {payment_id}")
    print(f"👤 User: {user_id}")
    print(f"💰 Amount: {amount} XTR")

    # Add your business logic here
    return {"status": "processed", "action": "user_upgraded"}


@webhook_handler.on("payment_error")
async def handle_payment_error(data):
    """Handle payment error."""
    user_id = data.get("user_id")
    error = data.get("error")

    print(f"❌ Payment error for user {user_id}: {error}")

    # Add your error handling logic here
    return {"status": "logged", "action": "error_reported"}


@webhook_handler.on("subscription_renewed")
async def handle_subscription_renewal(data):
    """Handle subscription renewal."""
    user_id = data.get("user_id")
    subscription_id = data.get("subscription_id")

    print(f"🔄 Subscription renewed: {subscription_id} for user {user_id}")

    # Extend user subscription
    return {"status": "renewed", "action": "subscription_extended"}


@app.post("/webhook/neonpay")
async def receive_webhook(
    request: Request, x_neonpay_signature: Optional[str] = Header(None)
):
    """Receive and process NEONPAY webhooks."""
    try:
        payload = await request.body()
        payload_str = payload.decode("utf-8")

        result = await webhook_handler.handle_webhook(payload_str, x_neonpay_signature)

        return result

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")


@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "service": "NEONPAY Webhook Server",
        "status": "running",
        "version": "1.0.0",
    }


@app.get("/health")
async def health_check():
    """Detailed health check."""
    return {
        "status": "healthy",
        "webhook_handler": "configured",
        "registered_events": list(webhook_handler.handlers.keys()),
    }


if __name__ == "__main__":
    print("🚀 Starting NEONPAY Webhook Server...")
    print("📡 Webhook endpoint: http://localhost:8000/webhook/neonpay")
    print("🔍 Health check: http://localhost:8000/health")

    uvicorn.run("webhook_server_example:app", host="0.0.0.0", port=8000, reload=True)

"""
NEONPAY Middleware Example
Demonstrates how to use middleware for payment processing.
"""

import logging

from pyrogram import Client, filters
from pyrogram.types import Message

from neonpay import NeonPay
from neonpay.middleware import (
    LoggingMiddleware,
    MiddlewareManager,
    ValidationMiddleware,
)

# Configure logging
logging.basicConfig(level=logging.INFO)

# Bot configuration
API_ID = "your_api_id"
API_HASH = "your_api_hash"
BOT_TOKEN = "your_bot_token"

app = Client(
    "neonpay_middleware_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN
)

# Initialize NEONPAY with middleware
neonpay = NeonPay(app)

# Setup middleware pipeline
middleware_manager = MiddlewareManager()

# Add logging middleware
middleware_manager.add_middleware(LoggingMiddleware())

# Add validation middleware (1-1000 XTR range)
middleware_manager.add_middleware(ValidationMiddleware(min_price=1, max_price=1000))

# Add webhook middleware (optional)
# middleware_manager.add_middleware(WebhookMiddleware(
#     webhook_url="https://your-server.com/webhook",
#     secret_key="your_secret_key"
# ))

# Integrate middleware with NEONPAY
neonpay.core.middleware_manager = middleware_manager


@app.on_message(filters.command("start"))
async def start_command(client: Client, message: Message):
    """Start command handler."""
    await message.reply_text(
        "🌟 Welcome to NEONPAY Middleware Demo!\n\n"
        "Available commands:\n"
        "• /donate - Make a donation\n"
        "• /premium - Buy premium access\n"
        "• /course - Purchase course"
    )


@app.on_message(filters.command("donate"))
async def donate_command(client: Client, message: Message):
    """Donation with middleware processing."""
    try:
        # Create payment stage
        stage = neonpay.create_stage(
            title="💝 Support Our Project",
            price=50,  # 50 XTR
            description="Thank you for supporting our project! Your donation helps us continue developing.",
            logo_url="https://example.com/donate-logo.png",
        )

        # Process payment with middleware
        context = {
            "user_id": message.from_user.id,
            "username": message.from_user.username,
            "command": "donate",
            "amount": 50,
        }

        # Middleware will handle logging, validation, and webhooks
        processed_stage = await middleware_manager.process_before_payment(
            stage, context
        )
        if processed_stage is None:
            await message.reply_text("❌ Payment was cancelled by middleware.")
            return

        # Send payment
        result = await neonpay.send_payment(message.chat.id, processed_stage)

        # Process result through middleware
        processed_result = await middleware_manager.process_after_payment(
            result, context
        )

        if processed_result and processed_result.success:
            await message.reply_text("✅ Thank you for your donation!")
        else:
            await message.reply_text("❌ Donation failed. Please try again.")

    except Exception as e:
        # Handle error through middleware
        context = {"user_id": message.from_user.id, "command": "donate"}
        should_continue = await middleware_manager.handle_error(e, context)

        if should_continue:
            await message.reply_text(f"❌ Error: {str(e)}")
        else:
            await message.reply_text(
                "❌ Payment processing stopped due to critical error."
            )


@app.on_message(filters.command("premium"))
async def premium_command(client: Client, message: Message):
    """Premium subscription with middleware."""
    try:
        stage = neonpay.create_stage(
            title="⭐ Premium Access",
            price=200,  # 200 XTR
            description="Get premium features:\n• Ad-free experience\n• Priority support\n• Exclusive content",
            logo_url="https://example.com/premium-logo.png",
        )

        context = {
            "user_id": message.from_user.id,
            "username": message.from_user.username,
            "command": "premium",
            "amount": 200,
            "subscription_type": "premium",
        }

        # Process with middleware
        processed_stage = await middleware_manager.process_before_payment(
            stage, context
        )
        if processed_stage is None:
            return

        result = await neonpay.send_payment(message.chat.id, processed_stage)
        processed_result = await middleware_manager.process_after_payment(
            result, context
        )

        if processed_result and processed_result.success:
            await message.reply_text(
                "🎉 Welcome to Premium!\n\n"
                "Your premium features are now active. Enjoy!"
            )

    except Exception as e:
        context = {"user_id": message.from_user.id, "command": "premium"}
        await middleware_manager.handle_error(e, context)
        await message.reply_text("❌ Premium purchase failed.")


@app.on_message(filters.command("course"))
async def course_command(client: Client, message: Message):
    """Course purchase with middleware."""
    try:
        stage = neonpay.create_stage(
            title="📚 Python Mastery Course",
            price=500,  # 500 XTR
            description="Complete Python course:\n• 50+ video lessons\n• Practice projects\n• Certificate\n• Lifetime access",
            logo_url="https://example.com/course-logo.png",
        )

        context = {
            "user_id": message.from_user.id,
            "username": message.from_user.username,
            "command": "course",
            "amount": 500,
            "product_type": "course",
            "course_id": "python_mastery",
        }

        # Process with middleware
        processed_stage = await middleware_manager.process_before_payment(
            stage, context
        )
        if processed_stage is None:
            return

        result = await neonpay.send_payment(message.chat.id, processed_stage)
        processed_result = await middleware_manager.process_after_payment(
            result, context
        )

        if processed_result and processed_result.success:
            await message.reply_text(
                "🎓 Course Purchased Successfully!\n\n"
                "You now have access to the Python Mastery Course.\n"
                "Check your DMs for course access details."
            )

            # Send course access (this would be handled by webhook in production)
            await client.send_message(
                message.from_user.id,
                "🔗 Course Access Link: https://courses.example.com/python-mastery\n"
                "📧 Login details have been sent to your email.",
            )

    except Exception as e:
        context = {"user_id": message.from_user.id, "command": "course"}
        await middleware_manager.handle_error(e, context)
        await message.reply_text("❌ Course purchase failed.")


if __name__ == "__main__":
    print("🚀 Starting NEONPAY Middleware Bot...")
    app.run()

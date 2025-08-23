"""
NEONPAY Pyrogram Example
Complete example showing how to use NEONPAY with Pyrogram v2.0+
"""

import asyncio
from pyrogram import Client, filters
from neonpay import create_neonpay, PaymentStage, PaymentResult, PaymentStatus

# Initialize Pyrogram client
app = Client(
    "neonpay_bot",
    api_id=12345,  # Replace with your API ID
    api_hash="your_api_hash",  # Replace with your API hash
    bot_token="YOUR_BOT_TOKEN"  # Replace with your bot token
)

# Initialize NEONPAY with automatic adapter detection
neonpay = create_neonpay(app, "Thank you for your support! 🌟")

# Create payment stages
async def setup_payment_stages():
    """Setup different payment options"""
    
    # Basic donation
    basic_donation = PaymentStage(
        title="☕ Buy me a coffee",
        description="Support the developer with a small donation",
        price=50,  # 50 Telegram Stars
        label="Donate 50 ⭐",
        photo_url="https://via.placeholder.com/300x200/4CAF50/white?text=Coffee",
        payload={"type": "donation", "tier": "basic"}
    )
    
    # Premium donation
    premium_donation = PaymentStage(
        title="🚀 Premium Support",
        description="Show extra support for the project",
        price=200,  # 200 Telegram Stars
        label="Donate 200 ⭐",
        photo_url="https://via.placeholder.com/300x200/2196F3/white?text=Premium",
        payload={"type": "donation", "tier": "premium"}
    )
    
    # VIP access
    vip_access = PaymentStage(
        title="👑 VIP Access",
        description="Get exclusive VIP features and priority support",
        price=500,  # 500 Telegram Stars
        label="Get VIP 500 ⭐",
        photo_url="https://via.placeholder.com/300x200/FF9800/white?text=VIP",
        payload={"type": "subscription", "plan": "vip", "duration": 30}
    )
    
    # Add stages to NEONPAY
    neonpay.create_payment_stage("coffee", basic_donation)
    neonpay.create_payment_stage("premium", premium_donation)
    neonpay.create_payment_stage("vip", vip_access)
    
    print("✅ Payment stages created successfully!")

# Payment completion handler
@neonpay.on_payment
async def handle_payment(result: PaymentResult):
    """Handle successful payments"""
    user_id = result.user_id
    amount = result.amount
    payment_type = result.metadata.get("type", "unknown")
    
    print(f"🎉 Payment received: {amount} ⭐ from user {user_id}")
    
    if payment_type == "donation":
        tier = result.metadata.get("tier", "basic")
        await app.send_message(
            user_id,
            f"🙏 Thank you for your {tier} donation of {amount} ⭐!\n"
            f"Your support means a lot to us!"
        )
        
    elif payment_type == "subscription":
        plan = result.metadata.get("plan", "unknown")
        duration = result.metadata.get("duration", 0)
        
        # Grant VIP access (implement your logic here)
        await grant_vip_access(user_id, duration)
        
        await app.send_message(
            user_id,
            f"👑 Welcome to {plan.upper()}!\n"
            f"You now have {duration} days of premium access.\n"
            f"Enjoy your exclusive features!"
        )

async def grant_vip_access(user_id: int, days: int):
    """Grant VIP access to user (implement your database logic)"""
    # This is where you would update your database
    print(f"Granted {days} days VIP access to user {user_id}")

# Bot commands
@app.on_message(filters.command("start"))
async def start_command(client, message):
    """Welcome message with available commands"""
    welcome_text = (
        "🌟 Welcome to NEONPAY Demo Bot!\n\n"
        "Available commands:\n"
        "• /donate - Show donation options\n"
        "• /coffee - Buy me a coffee (50 ⭐)\n"
        "• /premium - Premium support (200 ⭐)\n"
        "• /vip - Get VIP access (500 ⭐)\n"
        "• /status - Check your status\n"
        "• /help - Show this help message"
    )
    await message.reply(welcome_text)

@app.on_message(filters.command("donate"))
async def donate_command(client, message):
    """Show donation options"""
    keyboard = [
        [{"text": "☕ Coffee (50 ⭐)", "callback_data": "pay_coffee"}],
        [{"text": "🚀 Premium (200 ⭐)", "callback_data": "pay_premium"}],
        [{"text": "👑 VIP Access (500 ⭐)", "callback_data": "pay_vip"}]
    ]
    
    await message.reply(
        "💝 Choose your support level:",
        reply_markup={"inline_keyboard": keyboard}
    )

@app.on_message(filters.command("coffee"))
async def coffee_command(client, message):
    """Quick coffee donation"""
    try:
        success = await neonpay.send_payment(message.from_user.id, "coffee")
        if not success:
            await message.reply("❌ Failed to create payment. Please try again.")
    except Exception as e:
        await message.reply(f"❌ Error: {e}")

@app.on_message(filters.command("premium"))
async def premium_command(client, message):
    """Premium donation"""
    try:
        success = await neonpay.send_payment(message.from_user.id, "premium")
        if not success:
            await message.reply("❌ Failed to create payment. Please try again.")
    except Exception as e:
        await message.reply(f"❌ Error: {e}")

@app.on_message(filters.command("vip"))
async def vip_command(client, message):
    """VIP access purchase"""
    try:
        success = await neonpay.send_payment(message.from_user.id, "vip")
        if not success:
            await message.reply("❌ Failed to create payment. Please try again.")
    except Exception as e:
        await message.reply(f"❌ Error: {e}")

@app.on_message(filters.command("status"))
async def status_command(client, message):
    """Show user status and bot statistics"""
    stats = neonpay.get_stats()
    status_text = (
        f"📊 Bot Status:\n"
        f"• Payment stages: {stats['total_stages']}\n"
        f"• Active callbacks: {stats['registered_callbacks']}\n"
        f"• System ready: {'✅' if stats['setup_complete'] else '❌'}\n"
        f"• Library: {stats['adapter_info']['library']}"
    )
    await message.reply(status_text)

@app.on_message(filters.command("help"))
async def help_command(client, message):
    """Show help information"""
    help_text = (
        "🆘 NEONPAY Demo Bot Help\n\n"
        "This bot demonstrates NEONPAY payment processing with Pyrogram.\n\n"
        "💫 Telegram Stars Payments:\n"
        "• All payments use Telegram's native Stars (XTR) currency\n"
        "• Payments are processed instantly\n"
        "• No external payment processors needed\n\n"
        "🔧 Commands:\n"
        "• /start - Welcome message\n"
        "• /donate - Show donation options\n"
        "• /coffee, /premium, /vip - Quick payments\n"
        "• /status - Bot statistics\n"
        "• /help - This help message\n\n"
        "💡 Tip: Use inline buttons for better user experience!"
    )
    await message.reply(help_text)

# Callback query handler for inline buttons
@app.on_callback_query()
async def handle_callback(client, callback_query):
    """Handle inline button presses"""
    data = callback_query.data
    user_id = callback_query.from_user.id
    
    try:
        if data == "pay_coffee":
            await neonpay.send_payment(user_id, "coffee")
        elif data == "pay_premium":
            await neonpay.send_payment(user_id, "premium")
        elif data == "pay_vip":
            await neonpay.send_payment(user_id, "vip")
        
        await callback_query.answer("💫 Payment invoice sent!")
        
    except Exception as e:
        await callback_query.answer(f"❌ Error: {e}", show_alert=True)

# Main function
async def main():
    """Initialize and run the bot"""
    print("🚀 Starting NEONPAY Pyrogram Demo Bot...")
    
    # Setup payment stages
    await setup_payment_stages()
    
    # Start the bot
    await app.start()
    print("✅ Bot started successfully!")
    print("💫 NEONPAY is ready to process payments!")
    
    # Keep the bot running
    await asyncio.Event().wait()

if __name__ == "__main__":
    # Run the bot
    app.run(main())

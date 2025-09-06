"""
NEONPAY Pyrogram Example - Real-world Bot Implementation
Complete ready-to-use bot with donation system and digital store
Based on real production usage patterns
"""

import asyncio
import logging
from datetime import datetime

from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from neonpay.core import PaymentStage, PaymentStatus
from neonpay.factory import create_neonpay

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Initialize Pyrogram client
app = Client(
    "neonpay_bot",
    api_id=12345,  # Replace with your API ID
    api_hash="your_api_hash",  # Replace with your API hash
    bot_token="YOUR_BOT_TOKEN",  # Replace with your bot token
)

neonpay = None

# Donation options: amount and description before payment
DONATE_OPTIONS = [
    {
        "amount": 1,
        "symbol": "⭐",
        "desc": "1⭐ support: Will be used for bot server costs",
    },
    {
        "amount": 10,
        "symbol": "⭐",
        "desc": "10⭐ support: Will be spent on developing new features",
    },
    {
        "amount": 50,
        "symbol": "🌟",
        "desc": "50⭐ big support: Will be used for bot development and promotion",
    },
]

# Digital products store
DIGITAL_PRODUCTS = [
    {
        "id": "premium_access",
        "title": "Premium Access",
        "description": "Unlock all premium features for 30 days",
        "price": 25,
        "symbol": "👑",
    },
    {
        "id": "custom_theme",
        "title": "Custom Theme",
        "description": "Personalized bot theme and colors",
        "price": 15,
        "symbol": "🎨",
    },
    {
        "id": "priority_support",
        "title": "Priority Support",
        "description": "24/7 priority customer support",
        "price": 30,
        "symbol": "⚡",
    },
]


async def setup_neonpay():
    """Initialize NEONPAY with real-world configuration"""
    global neonpay
    if neonpay:
        return neonpay

    neonpay = create_neonpay(bot_instance=app)

    # Create payment stages for donations
    for option in DONATE_OPTIONS:
        neonpay.create_payment_stage(
            f"donate_{option['amount']}",
            PaymentStage(
                title=f"Support {option['amount']}{option['symbol']}",
                description=option["desc"],
                price=option["amount"],
            ),
        )

    # Create payment stages for digital products
    for product in DIGITAL_PRODUCTS:
        neonpay.create_payment_stage(
            product["id"],
            PaymentStage(
                title=f"{product['symbol']} {product['title']}",
                description=product["description"],
                price=product["price"],
            ),
        )


@neonpay.on_payment
async def handle_payment(result):
    if result.status == PaymentStatus.COMPLETED:
        try:
            # Determine if it's a donation or product purchase
            if result.stage_id.startswith("donate_"):
                await app.send_message(
                    result.user_id,
                    f"Thank you! Your support: {result.amount}⭐ ❤️\n"
                    f"Your contribution helps keep the bot running!",
                )
            else:
                # Handle digital product delivery
                product = next(
                    (p for p in DIGITAL_PRODUCTS if p["id"] == result.stage_id), None
                )
                if product:
                    await app.send_message(
                        result.user_id,
                        f"🎉 Purchase successful!\n\n"
                        f"Product: {product['symbol']} {product['title']}\n"
                        f"Price: {product['price']}⭐\n\n"
                        f"Your digital product has been activated!\n"
                        f"Thank you for your purchase! 🚀",
                    )

            logger.info(
                f"Payment completed: user={result.user_id}, amount={result.amount}, stage={result.stage_id}"
            )

        except Exception as e:
            logger.exception(f"Failed to send post-payment message: {e}")

    logger.info("✅ NEONPAY payment system initialized")
    return neonpay


# Bot commands
@app.on_message(filters.command("start"))
async def start_command(client, message):
    """Welcome new users"""
    user_name = message.from_user.first_name or "Friend"

    welcome_text = (
        f"👋 Hello {user_name}!\n\n"
        f"🤖 I'm a free bot created with love by an independent developer.\n\n"
        f"📱 **Available Commands:**\n"
        f"• /help - Show all commands\n"
        f"• /donate - Support the developer\n"
        f"• /store - Digital products store\n"
        f"• /status - Bot statistics\n\n"
        f"💡 This bot is completely free to use!\n"
        f"If you find it helpful, consider supporting development."
    )

    keyboard = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("❤️ Support Developer", callback_data="show_donate")],
            [InlineKeyboardButton("🛒 Digital Store", callback_data="show_store")],
            [InlineKeyboardButton("📋 Help", callback_data="show_help")],
        ]
    )

    await message.reply(welcome_text, reply_markup=keyboard)


@app.on_message(filters.command("donate"))
async def donate_command(client, message):
    """Show donation options"""
    logging.info(f"/donate command received: user={message.from_user.id}")

    keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    text=f"{opt['symbol']} {opt['amount']}",
                    callback_data=f"donate:{opt['amount']}",
                )
            ]
            for opt in DONATE_OPTIONS
        ]
    )

    await message.reply(
        "Please choose an amount to support the developer:", reply_markup=keyboard
    )


@app.on_message(filters.command("store"))
async def store_command(client, message):
    """Show digital products store"""
    logging.info(f"/store command received: user={message.from_user.id}")

    keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    text=f"{product['symbol']} {product['title']} - {product['price']}⭐",
                    callback_data=f"buy:{product['id']}",
                )
            ]
            for product in DIGITAL_PRODUCTS
        ]
    )

    store_text = (
        "🛒 **Digital Products Store**\n\n"
        "Choose a product to purchase:\n\n"
        "💡 All products are delivered instantly after payment!"
    )

    await message.reply(store_text, reply_markup=keyboard)


@app.on_message(filters.command("status"))
async def status_command(client, message):
    """Show bot status and statistics"""
    uptime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    status_text = (
        "📊 **Bot Status**\n\n"
        f"✅ Status: Online\n"
        f"⏰ Last restart: {uptime}\n"
        f"💫 Payment system: Active\n"
        f"🔧 Version: 2.0\n\n"
        f"Thank you for using this free bot!"
    )

    await message.reply(status_text)


@app.on_message(filters.command("help"))
async def help_command(client, message):
    """Show help information"""
    help_text = (
        "📋 **Bot Help**\n\n"
        "🆓 **This bot is completely free!**\n\n"
        "**Commands:**\n"
        "• /start - Welcome message\n"
        "• /donate - Support development\n"
        "• /store - Digital products store\n"
        "• /status - Bot statistics\n"
        "• /help - This help message\n\n"
        "**About:**\n"
        "This bot was created by an independent developer.\n"
        "All features are free, donations help keep it running!\n\n"
        "🐛 Found a bug? Contact @your_username"
    )

    await message.reply(help_text)


# Callback query handler for inline buttons
@app.on_callback_query()
async def handle_callback(client, callback_query):
    """Handle inline button presses"""
    data = callback_query.data
    user_id = callback_query.from_user.id

    try:
        if data == "show_donate":
            await callback_query.answer()
            await donate_command(client, callback_query.message)
        elif data == "show_store":
            await callback_query.answer()
            await store_command(client, callback_query.message)
        elif data == "show_help":
            await callback_query.answer()
            await help_command(client, callback_query.message)
        elif data.startswith("donate:"):
            amount = int(data.split(":")[1])
            option = next((o for o in DONATE_OPTIONS if o["amount"] == amount), None)

            if not option:
                await callback_query.answer(
                    "Error: Selected amount not found", show_alert=True
                )
                return

            # Send payment using NeonPay
            await neonpay.send_payment(user_id=user_id, stage_id=f"donate_{amount}")
            logger.info(f"Support started: user={user_id}, amount={amount}")
            await callback_query.answer("✅ Payment message sent")

        elif data.startswith("buy:"):
            product_id = data.split(":")[1]
            product = next((p for p in DIGITAL_PRODUCTS if p["id"] == product_id), None)

            if not product:
                await callback_query.answer("Error: Product not found", show_alert=True)
                return

            # Send payment using NeonPay
            await neonpay.send_payment(user_id=user_id, stage_id=product_id)
            logger.info(
                f"Product purchase started: user={user_id}, product={product_id}"
            )
            await callback_query.answer("✅ Payment message sent")

    except Exception as e:
        logger.exception(f"Failed to handle callback: {e}")
        await callback_query.answer("💥 Error occurred during payment", show_alert=True)


# Main function
async def main():
    """Initialize and run the bot"""
    logger.info("🚀 Starting NEONPAY Pyrogram Bot...")

    try:
        await setup_neonpay()

        # Start the bot
        await app.start()
        logger.info("✅ Bot started successfully!")
        logger.info("💰 Donation system ready!")
        logger.info("🛒 Digital store ready!")
        logger.info("🔄 Bot is running...")

        # Keep the bot running
        await asyncio.Event().wait()

    except Exception as e:
        logger.error(f"Failed to start bot: {e}")
        raise


if __name__ == "__main__":
    try:
        app.run(main())
    except KeyboardInterrupt:
        logger.info("👋 Bot stopped by user")
    except Exception as e:
        logger.error(f"Critical error: {e}")

"""
NEONPAY python-telegram-bot Example - Real-world Bot Implementation
Complete ready-to-use bot with donation system and digital store
Based on real production usage patterns
"""

import logging
from datetime import datetime

try:
    from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
    from telegram.ext import (
        Application,
        CallbackQueryHandler,
        CommandHandler,
        ContextTypes,
    )
except ImportError:
    raise ImportError(
        "python-telegram-bot is required for this example. "
        "Install it with: pip install python-telegram-bot>=20.0"
    )

from neonpay.core import PaymentStage, PaymentStatus
from neonpay.factory import create_neonpay

# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Bot token
BOT_TOKEN = "YOUR_BOT_TOKEN"  # Replace with your bot token

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


async def setup_neonpay(application: Application) -> None:
    """Initialize NEONPAY with real-world configuration"""
    global neonpay
    if neonpay:
        return neonpay

    neonpay = create_neonpay(bot_instance=application.bot)

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
                    await application.bot.send_message(
                        result.user_id,
                        f"Thank you! Your support: {result.amount}⭐ ❤️\n"
                        f"Your contribution helps keep the bot running!",
                    )
                else:
                    # Handle digital product delivery
                    product = next(
                        (p for p in DIGITAL_PRODUCTS if p["id"] == result.stage_id),
                        None,
                    )
                    if product:
                        await application.bot.send_message(
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
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Welcome new users"""
    user_name = update.effective_user.first_name or "Friend"

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

    await update.message.reply_text(welcome_text, reply_markup=keyboard)


async def donate_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show donation options"""
    logging.info(f"/donate command received: user={update.effective_user.id}")

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

    await update.message.reply_text(
        "Please choose an amount to support the developer:", reply_markup=keyboard
    )


async def store_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show digital products store"""
    logging.info(f"/store command received: user={update.effective_user.id}")

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

    await update.message.reply_text(store_text, reply_markup=keyboard)


async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
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

    await update.message.reply_text(status_text)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
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

    await update.message.reply_text(help_text)


# Callback query handlers
async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle inline button presses"""
    query = update.callback_query
    await query.answer()

    data = query.data
    user_id = query.from_user.id

    try:
        if data == "show_donate":
            await donate_command(update, context)
        elif data == "show_store":
            await store_command(update, context)
        elif data == "show_help":
            await help_command(update, context)
        elif data.startswith("donate:"):
            amount = int(data.split(":")[1])
            option = next((o for o in DONATE_OPTIONS if o["amount"] == amount), None)

            if not option:
                await query.answer("Error: Selected amount not found", show_alert=True)
                return

            # Send payment using NeonPay
            await neonpay.send_payment(user_id=user_id, stage_id=f"donate_{amount}")
            logger.info(f"Support started: user={user_id}, amount={amount}")
            await query.answer("✅ Payment message sent")

        elif data.startswith("buy:"):
            product_id = data.split(":")[1]
            product = next((p for p in DIGITAL_PRODUCTS if p["id"] == product_id), None)

            if not product:
                await query.answer("Error: Product not found", show_alert=True)
                return

            # Send payment using NeonPay
            await neonpay.send_payment(user_id=user_id, stage_id=product_id)
            logger.info(
                f"Product purchase started: user={user_id}, product={product_id}"
            )
            await query.answer("✅ Payment message sent")

    except Exception as e:
        logger.exception(f"Failed to handle callback: {e}")
        await query.answer("💥 Error occurred during payment", show_alert=True)


# Main function
async def main() -> None:
    """Initialize and run the bot"""
    logger.info("🚀 Starting NEONPAY PTB Bot...")

    # Create application
    application = Application.builder().token(BOT_TOKEN).build()

    try:
        # Setup NEONPAY
        await setup_neonpay(application)

        # Add handlers
        application.add_handler(CommandHandler("start", start_command))
        application.add_handler(CommandHandler("donate", donate_command))
        application.add_handler(CommandHandler("store", store_command))
        application.add_handler(CommandHandler("status", status_command))
        application.add_handler(CommandHandler("help", help_command))
        application.add_handler(CallbackQueryHandler(callback_handler))

        logger.info("✅ Bot initialized successfully!")
        logger.info("💰 Donation system ready!")
        logger.info("🛒 Digital store ready!")
        logger.info("🔄 Starting polling...")

        # Start polling
        await application.run_polling()

    except Exception as e:
        logger.error(f"Failed to start bot: {e}")
        raise


if __name__ == "__main__":
    try:
        import asyncio

        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("👋 Bot stopped by user")
    except Exception as e:
        logger.error(f"Critical error: {e}")

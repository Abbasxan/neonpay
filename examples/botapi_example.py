"""
NEONPAY Bot API Example - Donation Bot with Telegram Stars
Based on python-telegram-bot (official Bot API library)
"""

import asyncio
import logging
from datetime import datetime

from telegram import (
    Bot,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Update,
)
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    PreCheckoutQueryHandler,
    filters,
)

from neonpay import (
    BotAPIAdapter,
    NeonPayCore,
    PaymentResult,
    PaymentStage,
    PaymentStatus,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Bot configuration
BOT_TOKEN = "YOUR_BOT_TOKEN"  # Replace with your bot token

# Initialize bot + adapter
bot = Bot(token=BOT_TOKEN)
adapter = BotAPIAdapter(bot)
neonpay = NeonPayCore(adapter)

# Donation options
DONATE_OPTIONS = [
    {"amount": 1, "symbol": "⭐", "desc": "1⭐ support: Helps cover server costs"},
    {"amount": 10, "symbol": "⭐", "desc": "10⭐ support: New feature development"},
    {"amount": 50, "symbol": "🌟", "desc": "50⭐ big support: Development & promotion"},
]


async def setup_neonpay():
    """Initialize payment stages and handlers"""
    for option in DONATE_OPTIONS:
        neonpay.create_payment_stage(
            f"donate_{option['amount']}",
            PaymentStage(
                title=f"Support {option['amount']}{option['symbol']}",
                description=option["desc"],
                price=option["amount"],
            ),
        )

    @neonpay.on_payment
    async def handle_payment(result: PaymentResult):
        """Handle successful payments"""
        if result.status == PaymentStatus.COMPLETED:
            try:
                await bot.send_message(
                    result.user_id, f"🎉 Thank you! Your support: {result.amount}⭐ ❤️"
                )
                logger.info(
                    f"✅ Donation completed: user={result.user_id}, amount={result.amount}"
                )
            except Exception as e:
                logger.exception(f"Failed to send thank-you message: {e}")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Welcome message"""
    user_name = update.effective_user.first_name or "Friend"

    welcome_text = (
        f"👋 Hello {user_name}!\n\n"
        f"🤖 I'm a free bot powered by NEONPAY.\n\n"
        f"📱 **Commands:**\n"
        f"• /help - Show all commands\n"
        f"• /donate - Support the developer\n"
        f"• /status - Bot statistics\n\n"
        f"💡 This bot is completely free! Consider supporting if you like it."
    )

    keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    text="❤️ Support Developer", callback_data="show_donate"
                )
            ],
            [InlineKeyboardButton(text="📋 Help", callback_data="show_help")],
        ]
    )

    await update.message.reply_text(welcome_text, reply_markup=keyboard)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Help message"""
    help_text = (
        "📋 **Help**\n\n"
        "🆓 This bot is completely free!\n\n"
        "**Commands:**\n"
        "• /start - Welcome message\n"
        "• /donate - Support development\n"
        "• /status - Bot statistics\n"
        "• /help - This help message\n\n"
        "🐛 Found a bug? Contact @your_username"
    )
    await update.message.reply_text(help_text, parse_mode="Markdown")


async def donate_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Donation options"""
    kb = InlineKeyboardMarkup(
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
    await update.message.reply_text("Please choose an amount:", reply_markup=kb)


async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Bot statistics"""
    uptime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    stats = neonpay.get_stats()
    status_text = (
        "📊 **Bot Status**\n\n"
        f"✅ Status: Online\n"
        f"⏰ Last restart: {uptime}\n"
        f"💫 Payment system: Active\n"
        f"🔧 Version: {stats.get('adapter_info', {}).get('library')}\n\n"
        f"Thank you for using this free bot!"
    )
    await update.message.reply_text(status_text, parse_mode="Markdown")


async def show_donate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Inline button: show donate"""
    await update.callback_query.answer()
    await donate_command(update, context)


async def show_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Inline button: show help"""
    await update.callback_query.answer()
    await help_command(update, context)


async def donate_choose(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Donation amount selection"""
    query = update.callback_query
    await query.answer()

    amount = int(query.data.split(":")[1])
    stage_id = f"donate_{amount}"

    try:
        await neonpay.send_payment(user_id=query.from_user.id, stage_id=stage_id)
        logger.info(f"💰 Donation started: user={query.from_user.id}, amount={amount}")
        await query.answer("✅ Payment invoice sent")
    except Exception as e:
        logger.exception(f"Failed to start donation: {e}")
        await query.answer("💥 Error occurred during payment", show_alert=True)


async def precheckout(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle pre-checkout query"""
    await adapter.handle_pre_checkout_query(update.pre_checkout_query)


async def successful_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle successful payment"""
    await adapter.handle_successful_payment(update.message)


async def main():
    """Main entry point"""
    logger.info("🚀 Starting NEONPAY Bot API Donation Bot...")

    await setup_neonpay()
    await adapter.setup_handlers(lambda r: None)  # Register empty callback

    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("donate", donate_command))
    app.add_handler(CommandHandler("status", status_command))

    app.add_handler(CallbackQueryHandler(show_donate, pattern="^show_donate$"))
    app.add_handler(CallbackQueryHandler(show_help, pattern="^show_help$"))
    app.add_handler(CallbackQueryHandler(donate_choose, pattern="^donate:"))

    app.add_handler(PreCheckoutQueryHandler(precheckout))
    app.add_handler(MessageHandler(filters.SUCCESSFUL_PAYMENT, successful_payment))

    await app.run_polling()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("👋 Bot stopped by user")
    except Exception as e:
        logger.error(f"Critical error: {e}")

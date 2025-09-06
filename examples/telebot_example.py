"""
NEONPAY pyTelegramBotAPI (telebot) Example - Real-world Bot Implementation
Complete ready-to-use bot with donation system and digital store
Based on real production usage patterns
"""

import logging
from datetime import datetime

from telebot import TeleBot
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup

from neonpay.core import PaymentStage, PaymentStatus
from neonpay.factory import create_neonpay

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Bot token
BOT_TOKEN = "YOUR_BOT_TOKEN"  # Replace with your bot token

# Initialize bot
bot = TeleBot(BOT_TOKEN)

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


def setup_neonpay():
    """Initialize NEONPAY with real-world configuration"""
    global neonpay
    if neonpay:
        return neonpay

    neonpay = create_neonpay(bot_instance=bot)

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
                bot.send_message(
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
                    bot.send_message(
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
@bot.message_handler(commands=["start"])
def start_command(message):
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

    keyboard = InlineKeyboardMarkup()
    keyboard.row(
        InlineKeyboardButton("❤️ Support Developer", callback_data="show_donate"),
        InlineKeyboardButton("🛒 Digital Store", callback_data="show_store"),
    )
    keyboard.row(InlineKeyboardButton("📋 Help", callback_data="show_help"))

    bot.reply_to(message, welcome_text, reply_markup=keyboard, parse_mode="Markdown")


@bot.message_handler(commands=["donate"])
def donate_command(message):
    """Show donation options"""
    logging.info(f"/donate command received: user={message.from_user.id}")

    keyboard = InlineKeyboardMarkup()
    for opt in DONATE_OPTIONS:
        keyboard.row(
            InlineKeyboardButton(
                text=f"{opt['symbol']} {opt['amount']}",
                callback_data=f"donate:{opt['amount']}",
            )
        )

    bot.reply_to(
        message,
        "Please choose an amount to support the developer:",
        reply_markup=keyboard,
    )


@bot.message_handler(commands=["store"])
def store_command(message):
    """Show digital products store"""
    logging.info(f"/store command received: user={message.from_user.id}")

    keyboard = InlineKeyboardMarkup()
    for product in DIGITAL_PRODUCTS:
        keyboard.row(
            InlineKeyboardButton(
                text=f"{product['symbol']} {product['title']} - {product['price']}⭐",
                callback_data=f"buy:{product['id']}",
            )
        )

    store_text = (
        "🛒 **Digital Products Store**\n\n"
        "Choose a product to purchase:\n\n"
        "💡 All products are delivered instantly after payment!"
    )

    bot.reply_to(message, store_text, reply_markup=keyboard, parse_mode="Markdown")


@bot.message_handler(commands=["status"])
def status_command(message):
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

    bot.reply_to(message, status_text, parse_mode="Markdown")


@bot.message_handler(commands=["help"])
def help_command(message):
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

    bot.reply_to(message, help_text, parse_mode="Markdown")


# Callback query handlers
@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    """Handle inline button presses"""
    user_id = call.from_user.id
    data = call.data

    try:
        if data == "show_donate":
            bot.answer_callback_query(call.id)
            donate_command(call.message)
        elif data == "show_store":
            bot.answer_callback_query(call.id)
            store_command(call.message)
        elif data == "show_help":
            bot.answer_callback_query(call.id)
            help_command(call.message)
        elif data.startswith("donate:"):
            amount = int(data.split(":")[1])
            option = next((o for o in DONATE_OPTIONS if o["amount"] == amount), None)

            if not option:
                bot.answer_callback_query(
                    call.id, "Error: Selected amount not found", show_alert=True
                )
                return

            # Send payment using NeonPay
            import asyncio

            asyncio.run(
                neonpay.send_payment(user_id=user_id, stage_id=f"donate_{amount}")
            )
            logger.info(f"Support started: user={user_id}, amount={amount}")
            bot.answer_callback_query(call.id, "✅ Payment message sent")

        elif data.startswith("buy:"):
            product_id = data.split(":")[1]
            product = next((p for p in DIGITAL_PRODUCTS if p["id"] == product_id), None)

            if not product:
                bot.answer_callback_query(
                    call.id, "Error: Product not found", show_alert=True
                )
                return

            # Send payment using NeonPay
            asyncio.run(neonpay.send_payment(user_id=user_id, stage_id=product_id))
            logger.info(
                f"Product purchase started: user={user_id}, product={product_id}"
            )
            bot.answer_callback_query(call.id, "✅ Payment message sent")

    except Exception as e:
        logger.exception(f"Failed to handle callback: {e}")
        bot.answer_callback_query(
            call.id, "💥 Error occurred during payment", show_alert=True
        )


# Initialize and run
if __name__ == "__main__":
    logger.info("🚀 Starting NEONPAY Telebot Bot...")

    try:
        # Setup payment stages
        setup_neonpay()

        logger.info("✅ Bot started successfully!")
        logger.info("💰 Donation system ready!")
        logger.info("🛒 Digital store ready!")
        logger.info("🔄 Starting polling...")

        # Start polling
        bot.infinity_polling()

    except Exception as e:
        logger.error(f"Failed to start bot: {e}")
        raise

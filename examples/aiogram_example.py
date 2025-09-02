"""
NEONPAY Aiogram Example - Real-world Bot Implementation
Complete ready-to-use bot with donation system and digital store
Based on real production usage patterns
"""

import asyncio
import logging
from datetime import datetime
from aiogram import Bot, Dispatcher, Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command

from neonpay.factory import create_neonpay
from neonpay.core import PaymentStage, PaymentStatus

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Bot configuration
BOT_TOKEN = "YOUR_BOT_TOKEN"  # Replace with your bot token

# Initialize bot and dispatcher
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
router = Router()

neonpay = None

DONATE_OPTIONS = [
    {"amount": 1, "symbol": "⭐", "desc": "1⭐ support: Will be used for bot server costs"},
    {"amount": 10, "symbol": "⭐", "desc": "10⭐ support: Will be spent on developing new features"},
    {"amount": 50, "symbol": "🌟", "desc": "50⭐ big support: Will be used for bot development and promotion"},
]

async def setup_neonpay():
    """Initialize NEONPAY with real-world configuration"""
    global neonpay
    if neonpay:
        return neonpay
    
    neonpay = create_neonpay(bot_instance=bot, dispatcher=dp)
    
    for option in DONATE_OPTIONS:
        neonpay.create_payment_stage(
            f"donate_{option['amount']}",
            PaymentStage(
                title=f"Support {option['amount']}{option['symbol']}",
                description=option["desc"],
                price=option["amount"],
            )
        )
    
    @neonpay.on_payment
    async def handle_payment(result):
        if result.status == PaymentStatus.COMPLETED:
            try:
                await bot.send_message(
                    result.user_id,
                    f"Thank you! Your support: {result.amount}⭐ ❤️"
                )
                chat_id = getattr(result, "_neonpay_chat_id", None)
                message_id = getattr(result, "_neonpay_message_id", None)
                if chat_id and message_id:
                    await bot.edit_message_reply_markup(
                        chat_id=chat_id,
                        message_id=message_id,
                        reply_markup=None,
                    )
                logger.info(f"Support completed: user={result.user_id}, amount={result.amount}")
            except Exception as e:
                logger.exception(f"Failed to send post-payment message: {e}")
    
    logger.info("✅ NEONPAY donation system initialized")
    return neonpay

@router.message(Command("start"))
async def start_command(message: Message):
    """Welcome new users"""
    user_name = message.from_user.first_name or "Friend"
    
    welcome_text = (
        f"👋 Hello {user_name}!\n\n"
        f"🤖 I'm a free bot created with love by an independent developer.\n\n"
        f"📱 **Available Commands:**\n"
        f"• /help - Show all commands\n"
        f"• /donate - Support the developer\n"
        f"• /status - Bot statistics\n\n"
        f"💡 This bot is completely free to use!\n"
        f"If you find it helpful, consider supporting development."
    )
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❤️ Support Developer", callback_data="show_donate")],
        [InlineKeyboardButton(text="📋 Help", callback_data="show_help")]
    ])
    
    await message.answer(welcome_text, reply_markup=keyboard)

@router.message(Command("help"))
async def help_command(message: Message):
    """Show help information"""
    help_text = (
        "📋 **Bot Help**\n\n"
        "🆓 **This bot is completely free!**\n\n"
        "**Commands:**\n"
        "• /start - Welcome message\n"
        "• /donate - Support development\n"
        "• /status - Bot statistics\n"
        "• /help - This help message\n\n"
        "**About:**\n"
        "This bot was created by an independent developer.\n"
        "All features are free, donations help keep it running!\n\n"
        "🐛 Found a bug? Contact @your_username"
    )
    
    await message.answer(help_text, parse_mode="Markdown")

@router.message(Command("donate"))
async def donate_command(message: Message):
    """Show donation options"""
    logging.info(f"/donate command received: user={message.from_user.id}")
    
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=f"{opt['symbol']} {opt['amount']}",
                    callback_data=f"donate:{opt['amount']}"
                )
            ]
            for opt in DONATE_OPTIONS
        ]
    )
    
    await message.answer(
        "Please choose an amount to support the developer:",
        reply_markup=kb
    )

@router.message(Command("status"))
async def status_command(message: Message):
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
    
    await message.answer(status_text, parse_mode="Markdown")

@router.callback_query(F.data == "show_donate")
async def show_donate_callback(callback: CallbackQuery):
    """Handle donate button press"""
    await callback.answer()
    await donate_command(callback.message)

@router.callback_query(F.data == "show_help")
async def show_help_callback(callback: CallbackQuery):
    """Handle help button press"""
    await callback.answer()
    await help_command(callback.message)

@router.callback_query(F.data.startswith("donate:"))
async def donate_choose(callback: CallbackQuery):
    """Handle donation amount selection"""
    amount = int(callback.data.split(":")[1])
    option = next((o for o in DONATE_OPTIONS if o["amount"] == amount), None)
    
    if not option:
        await callback.answer("Error: Selected amount not found", show_alert=True)
        return
    
    try:
        await neonpay.send_payment(
            user_id=callback.from_user.id,
            stage_id=f"donate_{amount}"
        )
        
        callback.message._neonpay_chat_id = callback.message.chat.id
        callback.message._neonpay_message_id = callback.message.message_id
        
        logger.info(f"Support started: user={callback.from_user.id}, amount={amount}")
        await callback.answer("✅ Payment message sent")
        
    except Exception as e:
        logger.exception(f"Failed to create support: {e}")
        await callback.answer("💥 Error occurred during payment", show_alert=True)

@router.error()
async def error_handler(event, exception):
    """Handle all bot errors"""
    logger.error(f"Bot error: {exception}", exc_info=True)
    return True

async def main():
    """Initialize and run the bot"""
    logger.info("🚀 Starting NEONPAY Donation Bot...")
    
    try:
        await setup_neonpay()
        
        # Include router
        dp.include_router(router)
        
        logger.info("✅ Bot initialized successfully!")
        logger.info("💰 Donation system ready!")
        logger.info("🔄 Starting polling...")
        
        # Start polling
        await dp.start_polling(bot)
        
    except Exception as e:
        logger.error(f"Failed to start bot: {e}")
        raise

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("👋 Bot stopped by user")
    except Exception as e:
        logger.error(f"Critical error: {e}")

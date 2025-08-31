"""
NEONPAY Aiogram Example
Complete example showing how to use NEONPAY with Aiogram v3.0+
"""

import asyncio
import logging
from aiogram import Bot, Dispatcher, Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from neonpay import create_neonpay, PaymentStage, PaymentResult, PaymentStatus

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Bot configuration
BOT_TOKEN = "YOUR_BOT_TOKEN"  # Replace with your bot token

# Initialize bot and dispatcher
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
router = Router()

# Initialize NEONPAY
neonpay = create_neonpay(bot, "Thank you for your purchase! 🎉")

# FSM States for order flow
class OrderStates(StatesGroup):
    selecting_product = State()
    confirming_order = State()

# Product catalog
PRODUCTS = {
    "ebook": {
        "name": "📚 Programming eBook",
        "description": "Complete guide to modern programming",
        "price": 100,
        "emoji": "📚"
    },
    "course": {
        "name": "🎓 Online Course",
        "description": "Full-stack development course",
        "price": 300,
        "emoji": "🎓"
    },
    "consultation": {
        "name": "💼 1-on-1 Consultation",
        "description": "Personal mentoring session",
        "price": 500,
        "emoji": "💼"
    },
    "premium": {
        "name": "⭐ Premium Membership",
        "description": "Access to all premium content",
        "price": 200,
        "emoji": "⭐"
    }
}

async def setup_payment_stages():
    """Initialize payment stages for all products"""
    for product_id, product in PRODUCTS.items():
        stage = PaymentStage(
            title=product["name"],
            description=product["description"],
            price=product["price"],
            label=f"Buy for {product['price']} ⭐",
            photo_url=f"https://via.placeholder.com/400x300/2196F3/white?text={product['emoji']}",
            payload={
                "product_id": product_id,
                "product_name": product["name"],
                "category": "digital_product"
            }
        )
        neonpay.create_payment_stage(product_id, stage)
    
    logger.info("✅ Payment stages initialized")

# Payment completion handler
@neonpay.on_payment
async def handle_payment(result: PaymentResult):
    """Process successful payments"""
    user_id = result.user_id
    amount = result.amount
    product_id = result.metadata.get("product_id")
    product_name = result.metadata.get("product_name", "Unknown Product")
    
    logger.info(f"💰 Payment received: {amount} ⭐ from user {user_id} for {product_name}")
    
    # Send confirmation message
    confirmation_text = (
        f"✅ Payment Successful!\n\n"
        f"Product: {product_name}\n"
        f"Amount: {amount} ⭐\n"
        f"Transaction ID: {result.transaction_id or 'N/A'}\n\n"
        f"🎉 Thank you for your purchase!"
    )
    
    # Create delivery keyboard
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📥 Download", callback_data=f"download_{product_id}")],
        [InlineKeyboardButton(text="📞 Support", callback_data="contact_support")]
    ])
    
    try:
        await bot.send_message(user_id, confirmation_text, reply_markup=keyboard)
        
        # Deliver the product (implement your logic)
        await deliver_product(user_id, product_id)
        
    except Exception as e:
        logger.error(f"Failed to send confirmation to user {user_id}: {e}")

async def deliver_product(user_id: int, product_id: str):
    """Deliver digital product to user"""
    # Implement your product delivery logic here
    # This could involve:
    # - Adding user to database
    # - Sending download links
    # - Granting access to premium features
    # - etc.
    
    logger.info(f"📦 Delivered product {product_id} to user {user_id}")

# Command handlers
@router.message(Command("start"))
async def start_command(message: Message):
    """Welcome message"""
    welcome_text = (
        "🛍️ Welcome to NEONPAY Store!\n\n"
        "We sell digital products using Telegram Stars.\n\n"
        "Available commands:\n"
        "• /shop - Browse products\n"
        "• /cart - View your cart\n"
        "• /orders - Order history\n"
        "• /support - Get help\n\n"
        "💫 All payments are processed securely with Telegram Stars!"
    )
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🛍️ Start Shopping", callback_data="show_shop")]
    ])
    
    await message.answer(welcome_text, reply_markup=keyboard)

@router.message(Command("shop"))
async def shop_command(message: Message):
    """Show product catalog"""
    await show_product_catalog(message.from_user.id)

@router.message(Command("orders"))
async def orders_command(message: Message):
    """Show order history (mock implementation)"""
    # In a real app, you'd fetch from database
    orders_text = (
        "📋 Your Order History:\n\n"
        "No orders found.\n\n"
        "Start shopping with /shop to see your orders here!"
    )
    await message.answer(orders_text)

@router.message(Command("support"))
async def support_command(message: Message):
    """Show support information"""
    support_text = (
        "🆘 Need Help?\n\n"
        "• For technical issues: @support\n"
        "• For refunds: @billing\n"
        "• General questions: @help\n\n"
        "📧 Email: support@example.com\n"
        "⏰ Response time: 24 hours"
    )
    await message.answer(support_text)

async def show_product_catalog(user_id: int):
    """Display product catalog with inline buttons"""
    catalog_text = "🛍️ **Product Catalog**\n\nChoose a product to purchase:"
    
    # Create product buttons
    keyboard_buttons = []
    for product_id, product in PRODUCTS.items():
        button_text = f"{product['emoji']} {product['name']} - {product['price']} ⭐"
        keyboard_buttons.append([
            InlineKeyboardButton(
                text=button_text,
                callback_data=f"product_{product_id}"
            )
        ])
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
    
    try:
        await bot.send_message(user_id, catalog_text, reply_markup=keyboard, parse_mode="Markdown")
    except Exception as e:
        logger.error(f"Failed to send catalog to user {user_id}: {e}")

# Callback query handlers
@router.callback_query(F.data == "show_shop")
async def show_shop_callback(callback: CallbackQuery):
    """Handle shop button press"""
    await callback.answer()
    await show_product_catalog(callback.from_user.id)

@router.callback_query(F.data.startswith("product_"))
async def product_callback(callback: CallbackQuery):
    """Handle product selection"""
    product_id = callback.data.split("_")[1]
    product = PRODUCTS.get(product_id)
    
    if not product:
        await callback.answer("❌ Product not found", show_alert=True)
        return
    
    # Show product details
    product_text = (
        f"{product['emoji']} **{product['name']}**\n\n"
        f"📝 {product['description']}\n\n"
        f"💰 Price: {product['price']} ⭐\n\n"
        f"Ready to purchase?"
    )
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"💳 Buy Now ({product['price']} ⭐)", callback_data=f"buy_{product_id}")],
        [InlineKeyboardButton(text="🔙 Back to Shop", callback_data="show_shop")]
    ])
    
    await callback.message.edit_text(product_text, reply_markup=keyboard, parse_mode="Markdown")
    await callback.answer()

@router.callback_query(F.data.startswith("buy_"))
async def buy_callback(callback: CallbackQuery):
    """Handle purchase button press"""
    product_id = callback.data.split("_")[1]
    user_id = callback.from_user.id
    
    try:
        success = await neonpay.send_payment(user_id, product_id)
        if success:
            await callback.answer("💫 Payment invoice sent! Check your messages.")
        else:
            await callback.answer("❌ Failed to create payment. Please try again.", show_alert=True)
    except Exception as e:
        logger.error(f"Payment error for user {user_id}: {e}")
        await callback.answer(f"❌ Error: {e}", show_alert=True)

@router.callback_query(F.data.startswith("download_"))
async def download_callback(callback: CallbackQuery):
    """Handle download button press"""
    product_id = callback.data.split("_")[1]
    product = PRODUCTS.get(product_id)
    
    if not product:
        await callback.answer("❌ Product not found", show_alert=True)
        return
    
    # Mock download link
    download_text = (
        f"📥 **Download {product['name']}**\n\n"
        f"🔗 Download Link: `https://example.com/download/{product_id}`\n"
        f"🔑 Access Code: `NEONPAY2024`\n\n"
        f"⚠️ This link expires in 24 hours.\n"
        f"💾 Save your files immediately!"
    )
    
    await callback.message.answer(download_text, parse_mode="Markdown")
    await callback.answer("📥 Download information sent!")

@router.callback_query(F.data == "contact_support")
async def support_callback(callback: CallbackQuery):
    """Handle support contact"""
    support_text = (
        "📞 **Contact Support**\n\n"
        "Our support team is here to help!\n\n"
        "📧 Email: support@example.com\n"
        "💬 Telegram: @support_bot\n"
        "⏰ Hours: 9 AM - 6 PM UTC\n\n"
        "Please include your transaction ID when contacting support."
    )
    
    await callback.message.answer(support_text, parse_mode="Markdown")
    await callback.answer()

# Error handler
@router.error()
async def error_handler(event, exception):
    """Handle errors"""
    logger.error(f"Error occurred: {exception}")
    return True

# Main function
async def main():
    """Initialize and run the bot"""
    logger.info("🚀 Starting NEONPAY Aiogram Demo Bot...")
    
    # Setup payment stages
    await setup_payment_stages()
    
    # Include router
    dp.include_router(router)
    
    # Start polling
    logger.info("✅ Bot started successfully!")
    logger.info("💫 NEONPAY is ready to process payments!")
    
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

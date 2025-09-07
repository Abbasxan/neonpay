#!/usr/bin/env python3
"""
NEONPAY Pyrogram Bot Example - Complete donation bot with digital store
Demonstrates payment processing, digital product delivery, and user management
"""

import asyncio
import logging

from pyrogram import Client, filters
from pyrogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup

# Import NEONPAY
from neonpay import PaymentResult, PaymentStage, PaymentStatus, create_neonpay

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Bot configuration
BOT_TOKEN = "YOUR_BOT_TOKEN"  # Replace with your bot token
API_ID = 12345  # Replace with your API ID
API_HASH = "your_api_hash"  # Replace with your API hash

# Initialize Pyrogram client
app = Client("neonpay_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# Initialize NEONPAY
neonpay = create_neonpay(app)

# User data storage (in production, use a database)
user_data = {}
purchases = {}


def setup_payment_stages():
    """Setup payment stages for the bot"""

    # Donation stages
    donation_1 = PaymentStage(
        title="❤️ Support Developer",
        description="Small donation to support development",
        price=1,  # 1 Telegram Star
        photo_url="https://via.placeholder.com/512x512/FF6B6B/FFFFFF?text=❤️",
        payload={"type": "donation", "amount": 1},
    )

    donation_10 = PaymentStage(
        title="❤️❤️ Support Developer",
        description="Medium donation to support development",
        price=10,  # 10 Telegram Stars
        photo_url="https://via.placeholder.com/512x512/4ECDC4/FFFFFF?text=❤️❤️",
        payload={"type": "donation", "amount": 10},
    )

    donation_50 = PaymentStage(
        title="❤️❤️❤️ Support Developer",
        description="Large donation to support development",
        price=50,  # 50 Telegram Stars
        photo_url="https://via.placeholder.com/512x512/45B7D1/FFFFFF?text=❤️❤️❤️",
        payload={"type": "donation", "amount": 50},
    )

    # Digital product stages
    premium_access = PaymentStage(
        title="🚀 Premium Access",
        description="Get access to premium features and priority support",
        price=100,  # 100 Telegram Stars
        photo_url="https://via.placeholder.com/512x512/96CEB4/FFFFFF?text=🚀",
        payload={"type": "product", "product": "premium_access"},
    )

    custom_theme = PaymentStage(
        title="🎨 Custom Theme",
        description="Exclusive custom theme for your bot",
        price=200,  # 200 Telegram Stars
        photo_url="https://via.placeholder.com/512x512/FFEAA7/FFFFFF?text=🎨",
        payload={"type": "product", "product": "custom_theme"},
    )

    priority_support = PaymentStage(
        title="⚡ Priority Support",
        description="Get priority support and faster response times",
        price=150,  # 150 Telegram Stars
        photo_url="https://via.placeholder.com/512x512/DDA0DD/FFFFFF?text=⚡",
        payload={"type": "product", "product": "priority_support"},
    )

    # Add payment stages to NEONPAY
    neonpay.create_payment_stage("donation_1", donation_1)
    neonpay.create_payment_stage("donation_10", donation_10)
    neonpay.create_payment_stage("donation_50", donation_50)
    neonpay.create_payment_stage("premium_access", premium_access)
    neonpay.create_payment_stage("custom_theme", custom_theme)
    neonpay.create_payment_stage("priority_support", priority_support)


@neonpay.on_payment
async def handle_payment(result: PaymentResult):
    """Handle successful payments"""
    user_id = result.user_id
    amount = result.amount
    metadata = result.metadata

    logger.info(f"Payment received: {amount} stars from user {user_id}")

    if result.status == PaymentStatus.COMPLETED:
        if metadata.get("type") == "donation":
            # Handle donation
            await handle_donation(user_id, amount)
        elif metadata.get("type") == "product":
            # Handle product purchase
            await handle_product_purchase(user_id, metadata.get("product"))

        # Store purchase record
        purchases[user_id] = {
            "amount": amount,
            "product": metadata.get("product", "donation"),
            "timestamp": result.timestamp,
        }

        # Send confirmation
        await app.send_message(
            user_id,
            f"✅ Payment successful!\n"
            f"Amount: {amount} Telegram Stars\n"
            f"Thank you for your support! 🙏",
        )


async def handle_donation(user_id: int, amount: int):
    """Handle donation payments"""
    if user_id not in user_data:
        user_data[user_id] = {"total_donated": 0, "donation_count": 0}

    user_data[user_id]["total_donated"] += amount
    user_data[user_id]["donation_count"] += 1

    # Send thank you message
    await app.send_message(
        user_id,
        f"🙏 Thank you for your donation of {amount} stars!\n"
        f"Total donated: {user_data[user_id]['total_donated']} stars\n"
        f"Donation count: {user_data[user_id]['donation_count']}",
    )


async def handle_product_purchase(user_id: int, product: str):
    """Handle digital product purchases"""
    if product == "premium_access":
        await deliver_premium_access(user_id)
    elif product == "custom_theme":
        await deliver_custom_theme(user_id)
    elif product == "priority_support":
        await deliver_priority_support(user_id)


async def deliver_premium_access(user_id: int):
    """Deliver premium access"""
    await app.send_message(
        user_id,
        "🚀 Premium Access Activated!\n\n"
        "You now have access to:\n"
        "• Advanced features\n"
        "• Priority support\n"
        "• Exclusive content\n"
        "• Beta testing access\n\n"
        "Thank you for your support! 🎉",
    )


async def deliver_custom_theme(user_id: int):
    """Deliver custom theme"""
    await app.send_message(
        user_id,
        "🎨 Custom Theme Delivered!\n\n"
        "Your exclusive custom theme is now available.\n"
        "Download link: https://example.com/themes/custom_theme.zip\n\n"
        "Installation instructions:\n"
        "1. Download the theme file\n"
        "2. Extract to your bot's theme folder\n"
        "3. Restart your bot\n\n"
        "Enjoy your new theme! ✨",
    )


async def deliver_priority_support(user_id: int):
    """Deliver priority support"""
    await app.send_message(
        user_id,
        "⚡ Priority Support Activated!\n\n"
        "You now have:\n"
        "• Faster response times (under 1 hour)\n"
        "• Direct access to support team\n"
        "• Priority bug fixes\n"
        "• Exclusive support channel access\n\n"
        "Contact: @support_team for immediate assistance! 🚀",
    )


@app.on_message(filters.command("start"))
async def start_command(client, message):
    """Handle /start command"""
    # user_id = message.from_user.id  # Not used in this function

    keyboard = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("❤️ Support Developer", callback_data="donate")],
            [InlineKeyboardButton("🛒 Digital Store", callback_data="store")],
            [InlineKeyboardButton("📊 My Stats", callback_data="stats")],
            [InlineKeyboardButton("ℹ️ About", callback_data="about")],
        ]
    )

    await message.reply_text(
        "🎉 Welcome to NEONPAY Demo Bot!\n\n"
        "This bot demonstrates Telegram Stars payments using NEONPAY library.\n\n"
        "Choose an option below:",
        reply_markup=keyboard,
    )


@app.on_callback_query()
async def handle_callback(client, callback_query: CallbackQuery):
    """Handle callback queries"""
    user_id = callback_query.from_user.id
    data = callback_query.data

    if data == "donate":
        await show_donation_options(callback_query)
    elif data == "store":
        await show_store_options(callback_query)
    elif data == "stats":
        await show_user_stats(callback_query)
    elif data == "about":
        await show_about(callback_query)
    elif data.startswith("donate_"):
        stage_id = data
        await neonpay.send_payment(user_id, stage_id)
    elif data.startswith("buy_"):
        stage_id = data
        await neonpay.send_payment(user_id, stage_id)


async def show_donation_options(callback_query: CallbackQuery):
    """Show donation options"""
    keyboard = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("❤️ 1 Star", callback_data="donate_donation_1")],
            [InlineKeyboardButton("❤️❤️ 10 Stars", callback_data="donate_donation_10")],
            [InlineKeyboardButton("❤️❤️❤️ 50 Stars", callback_data="donate_donation_50")],
            [InlineKeyboardButton("🔙 Back", callback_data="back_main")],
        ]
    )

    await callback_query.edit_message_text(
        "❤️ Support Developer\n\n"
        "Choose donation amount:\n"
        "• 1 Star - Small donation\n"
        "• 10 Stars - Medium donation\n"
        "• 50 Stars - Large donation\n\n"
        "Thank you for supporting development! 🙏",
        reply_markup=keyboard,
    )


async def show_store_options(callback_query: CallbackQuery):
    """Show digital store options"""
    keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "🚀 Premium Access - 100⭐", callback_data="buy_premium_access"
                )
            ],
            [
                InlineKeyboardButton(
                    "🎨 Custom Theme - 200⭐", callback_data="buy_custom_theme"
                )
            ],
            [
                InlineKeyboardButton(
                    "⚡ Priority Support - 150⭐", callback_data="buy_priority_support"
                )
            ],
            [InlineKeyboardButton("🔙 Back", callback_data="back_main")],
        ]
    )

    await callback_query.edit_message_text(
        "🛒 Digital Store\n\n"
        "Available products:\n"
        "• Premium Access - Advanced features and priority support\n"
        "• Custom Theme - Exclusive custom theme for your bot\n"
        "• Priority Support - Faster response times and direct access\n\n"
        "All products are delivered instantly after payment! ⚡",
        reply_markup=keyboard,
    )


async def show_user_stats(callback_query: CallbackQuery):
    """Show user statistics"""
    user_id = callback_query.from_user.id

    if user_id in user_data:
        total_donated = user_data[user_id]["total_donated"]
        donation_count = user_data[user_id]["donation_count"]
    else:
        total_donated = 0
        donation_count = 0

    if user_id in purchases:
        purchase_count = len(
            [p for p in purchases.values() if p.get("product") != "donation"]
        )
    else:
        purchase_count = 0

    keyboard = InlineKeyboardMarkup(
        [[InlineKeyboardButton("🔙 Back", callback_data="back_main")]]
    )

    await callback_query.edit_message_text(
        f"📊 Your Statistics\n\n"
        f"💰 Total Donated: {total_donated} Stars\n"
        f"❤️ Donation Count: {donation_count}\n"
        f"🛒 Products Purchased: {purchase_count}\n\n"
        f"Thank you for your support! 🙏",
        reply_markup=keyboard,
    )


async def show_about(callback_query: CallbackQuery):
    """Show about information"""
    keyboard = InlineKeyboardMarkup(
        [[InlineKeyboardButton("🔙 Back", callback_data="back_main")]]
    )

    await callback_query.edit_message_text(
        "ℹ️ About NEONPAY Demo Bot\n\n"
        "This bot demonstrates the NEONPAY library capabilities:\n"
        "• Telegram Stars payment processing\n"
        "• Digital product delivery\n"
        "• User management and statistics\n"
        "• Multi-stage payment support\n\n"
        "Built with:\n"
        "• Pyrogram - Modern Telegram client\n"
        "• NEONPAY - Payment processing library\n\n"
        "GitHub: https://github.com/Abbasxan/neonpay",
        reply_markup=keyboard,
    )


async def main():
    """Main function"""
    print("🚀 Starting NEONPAY Pyrogram Bot...")

    # Setup payment stages
    setup_payment_stages()

    print("✅ Payment stages configured")
    print("✅ Bot ready to receive payments")

    # Start the bot
    await app.start()
    print("🤖 Bot started successfully!")

    # Keep the bot running
    await app.idle()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Bot stopped by user")
    except Exception as e:
        logger.error(f"Bot error: {e}")
        print(f"❌ Bot error: {e}")

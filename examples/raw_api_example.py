"""
NEONPAY Raw Telegram Bot API Example
Complete example showing how to use NEONPAY with direct HTTP requests
"""

import asyncio
import json
import logging
from aiohttp import web, ClientSession
from neonpay import RawAPIAdapter, NeonPayCore, PaymentStage, PaymentResult

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
BOT_TOKEN = "YOUR_BOT_TOKEN"  # Replace with your bot token
WEBHOOK_URL = "https://yourdomain.com/webhook"  # Replace with your webhook URL
WEBHOOK_PATH = "/webhook"
WEBAPP_HOST = "0.0.0.0"
WEBAPP_PORT = 8080

# Digital products catalog
DIGITAL_PRODUCTS = {
    "ebook_python": {
        "name": "🐍 Python Mastery eBook",
        "description": "Complete Python programming guide with 500+ pages",
        "price": 150,
        "file_url": "https://example.com/downloads/python-mastery.pdf",
        "category": "programming",
    },
    "course_webdev": {
        "name": "🌐 Web Development Course",
        "description": "Full-stack web development video course (20+ hours)",
        "price": 400,
        "file_url": "https://example.com/courses/webdev-complete",
        "category": "course",
    },
    "template_react": {
        "name": "⚛️ React Template Pack",
        "description": "10 professional React.js templates for modern apps",
        "price": 200,
        "file_url": "https://example.com/downloads/react-templates.zip",
        "category": "template",
    },
    "plugin_wordpress": {
        "name": "🔌 WordPress Plugin Bundle",
        "description": "5 premium WordPress plugins for business websites",
        "price": 300,
        "file_url": "https://example.com/downloads/wp-plugins.zip",
        "category": "plugin",
    },
}

# Initialize NEONPAY with Raw API adapter
adapter = RawAPIAdapter(BOT_TOKEN, WEBHOOK_URL + WEBHOOK_PATH)
neonpay = NeonPayCore(adapter, "Thank you for your purchase! 🎉")

# Purchase database (in production, use a real database)
user_purchases = {}


async def setup_digital_store():
    """Initialize digital product payment stages"""
    for product_id, product in DIGITAL_PRODUCTS.items():
        stage = PaymentStage(
            title=product["name"],
            description=product["description"],
            price=product["price"],
            label=f"Buy for {product['price']} ⭐",
            photo_url=f"https://via.placeholder.com/400x300/673AB7/white?text={product['category'].upper()}",
            payload={
                "product_id": product_id,
                "product_name": product["name"],
                "file_url": product["file_url"],
                "category": product["category"],
            },
        )
        neonpay.create_payment_stage(product_id, stage)

    logger.info("✅ Digital store initialized with payment stages")


# Payment completion handler
@neonpay.on_payment
async def handle_digital_purchase(result: PaymentResult):
    """Process digital product purchases"""
    user_id = result.user_id
    amount = result.amount
    product_id = result.metadata.get("product_id")
    product_name = result.metadata.get("product_name", "Unknown Product")
    file_url = result.metadata.get("file_url")
    category = result.metadata.get("category", "digital")

    logger.info(
        f"💰 Digital purchase: {product_name} by user {user_id} for {amount} ⭐"
    )

    # Record purchase
    if user_id not in user_purchases:
        user_purchases[user_id] = []

    purchase_record = {
        "product_id": product_id,
        "product_name": product_name,
        "amount": amount,
        "file_url": file_url,
        "category": category,
        "transaction_id": result.transaction_id,
        "timestamp": result.timestamp or asyncio.get_event_loop().time(),
    }
    user_purchases[user_id].append(purchase_record)

    # Send download information
    download_text = (
        f"✅ **Purchase Successful!**\n\n"
        f"📦 Product: {product_name}\n"
        f"💰 Amount: {amount} ⭐\n"
        f"📋 Order ID: #{result.transaction_id or f'RAW{user_id}'}\n\n"
        f"📥 **Download Information:**\n"
        f"🔗 Download Link: `{file_url}`\n"
        f"🔑 Access Code: `NEONPAY2024`\n\n"
        f"⚠️ **Important:**\n"
        f"• Download link expires in 7 days\n"
        f"• Save files to your device immediately\n"
        f"• Contact support if you have issues\n\n"
        f"🎉 Thank you for your purchase!"
    )

    # Create inline keyboard for additional actions
    keyboard = {
        "inline_keyboard": [
            [
                {"text": "📥 Download Now", "url": file_url},
                {"text": "📞 Support", "callback_data": "contact_support"},
            ],
            [
                {"text": "📋 My Purchases", "callback_data": "my_purchases"},
                {"text": "🛍️ Shop More", "callback_data": "show_catalog"},
            ],
        ]
    }

    try:
        await send_message(user_id, download_text, keyboard)

        # Send receipt
        await send_purchase_receipt(user_id, purchase_record)

    except Exception as e:
        logger.error(f"Failed to send download info to user {user_id}: {e}")


async def send_purchase_receipt(user_id: int, purchase: dict):
    """Send detailed purchase receipt"""
    receipt_text = (
        f"🧾 **Purchase Receipt**\n\n"
        f"📅 Date: {asyncio.get_event_loop().time()}\n"
        f"👤 Customer ID: {user_id}\n"
        f"📦 Product: {purchase['product_name']}\n"
        f"🏷️ Category: {purchase['category'].title()}\n"
        f"💰 Amount: {purchase['amount']} ⭐\n"
        f"🆔 Transaction: {purchase['transaction_id']}\n\n"
        f"📧 Receipt sent to your Telegram account\n"
        f"💾 Keep this for your records\n\n"
        f"Thank you for choosing our digital store! 🙏"
    )

    try:
        await send_message(user_id, receipt_text)
    except Exception as e:
        logger.error(f"Failed to send receipt to user {user_id}: {e}")


async def send_message(chat_id: int, text: str, reply_markup: dict = None):
    """Send message using raw API"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    data = {"chat_id": chat_id, "text": text, "parse_mode": "Markdown"}

    if reply_markup:
        data["reply_markup"] = json.dumps(reply_markup)

    async with ClientSession() as session:
        async with session.post(url, data=data) as response:
            result = await response.json()
            if not result.get("ok"):
                logger.error(f"Failed to send message: {result}")
            return result


async def send_catalog(user_id: int):
    """Send product catalog"""
    catalog_text = "🛍️ **Digital Store Catalog**\n\nChoose a product to purchase:"

    # Create product buttons
    keyboard_buttons = []
    for product_id, product in DIGITAL_PRODUCTS.items():
        button_text = f"{product['name']} - {product['price']} ⭐"
        keyboard_buttons.append(
            [{"text": button_text, "callback_data": f"product_{product_id}"}]
        )

    keyboard_buttons.append(
        [{"text": "📋 My Purchases", "callback_data": "my_purchases"}]
    )

    keyboard = {"inline_keyboard": keyboard_buttons}

    await send_message(user_id, catalog_text, keyboard)


async def show_product_details(user_id: int, product_id: str):
    """Show detailed product information"""
    product = DIGITAL_PRODUCTS.get(product_id)
    if not product:
        await send_message(user_id, "❌ Product not found")
        return

    details_text = (
        f"{product['name']}\n\n"
        f"📝 **Description:**\n{product['description']}\n\n"
        f"💰 **Price:** {product['price']} ⭐\n"
        f"🏷️ **Category:** {product['category'].title()}\n\n"
        f"📦 **What You Get:**\n"
        f"• Instant download access\n"
        f"• Lifetime updates (if applicable)\n"
        f"• Customer support\n"
        f"• Money-back guarantee\n\n"
        f"Ready to purchase?"
    )

    keyboard = {
        "inline_keyboard": [
            [
                {
                    "text": f"💳 Buy Now ({product['price']} ⭐)",
                    "callback_data": f"buy_{product_id}",
                }
            ],
            [{"text": "🔙 Back to Catalog", "callback_data": "show_catalog"}],
        ]
    }

    await send_message(user_id, details_text, keyboard)


async def show_user_purchases(user_id: int):
    """Show user's purchase history"""
    purchases = user_purchases.get(user_id, [])

    if not purchases:
        purchases_text = (
            "📋 **Your Purchases**\n\n"
            "You haven't made any purchases yet.\n\n"
            "Browse our catalog to find amazing digital products!"
        )
        keyboard = {
            "inline_keyboard": [
                [{"text": "🛍️ Browse Catalog", "callback_data": "show_catalog"}]
            ]
        }
    else:
        purchases_text = f"📋 **Your Purchases ({len(purchases)} items)**\n\n"

        for i, purchase in enumerate(purchases[-5:], 1):  # Show last 5 purchases
            purchases_text += (
                f"{i}. {purchase['product_name']}\n"
                f"   💰 {purchase['amount']} ⭐ | 📥 [Download]({purchase['file_url']})\n\n"
            )

        keyboard = {
            "inline_keyboard": [
                [{"text": "🛍️ Shop More", "callback_data": "show_catalog"}],
                [{"text": "📞 Support", "callback_data": "contact_support"}],
            ]
        }

    await send_message(user_id, purchases_text, keyboard)


async def handle_callback_query(callback_query: dict):
    """Handle inline button presses"""
    user_id = callback_query["from"]["id"]
    data = callback_query["data"]
    callback_id = callback_query["id"]

    try:
        if data == "show_catalog":
            await send_catalog(user_id)
            await answer_callback_query(callback_id, "📱 Catalog loaded!")

        elif data.startswith("product_"):
            product_id = data.split("_")[1]
            await show_product_details(user_id, product_id)
            await answer_callback_query(callback_id)

        elif data.startswith("buy_"):
            product_id = data.split("_")[1]
            success = await neonpay.send_payment(user_id, product_id)
            if success:
                await answer_callback_query(callback_id, "💫 Payment invoice sent!")
            else:
                await answer_callback_query(
                    callback_id, "❌ Failed to create payment", True
                )

        elif data == "my_purchases":
            await show_user_purchases(user_id)
            await answer_callback_query(callback_id)

        elif data == "contact_support":
            support_text = (
                "📞 **Customer Support**\n\n"
                "Need help with your purchase?\n\n"
                "📧 Email: support@digitalstore.com\n"
                "💬 Telegram: @store_support\n"
                "📞 Phone: +1 (555) 123-4567\n\n"
                "⏰ Response time: 2-4 hours\n"
                "🕘 Business hours: 9 AM - 6 PM UTC"
            )
            await send_message(user_id, support_text)
            await answer_callback_query(callback_id, "📞 Support info sent!")

    except Exception as e:
        logger.error(f"Callback error: {e}")
        await answer_callback_query(callback_id, "❌ An error occurred", True)


async def answer_callback_query(
    callback_query_id: str, text: str = "", show_alert: bool = False
):
    """Answer callback query"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/answerCallbackQuery"

    data = {
        "callback_query_id": callback_query_id,
        "text": text,
        "show_alert": show_alert,
    }

    async with ClientSession() as session:
        async with session.post(url, data=data) as response:
            result = await response.json()
            return result


async def handle_command(message: dict):
    """Handle bot commands"""
    text = message.get("text", "")
    user_id = message["from"]["id"]
    first_name = message["from"].get("first_name", "User")

    if text == "/start":
        welcome_text = (
            f"🌟 **Welcome to Digital Store, {first_name}!**\n\n"
            f"We sell premium digital products:\n"
            f"• Programming eBooks & Courses\n"
            f"• Web Templates & Themes\n"
            f"• WordPress Plugins\n"
            f"• Design Resources\n\n"
            f"💫 All payments via Telegram Stars - instant & secure!\n\n"
            f"Ready to explore our catalog?"
        )

        keyboard = {
            "inline_keyboard": [
                [{"text": "🛍️ Browse Catalog", "callback_data": "show_catalog"}],
                [{"text": "📋 My Purchases", "callback_data": "my_purchases"}],
            ]
        }

        await send_message(user_id, welcome_text, keyboard)

    elif text == "/catalog":
        await send_catalog(user_id)

    elif text == "/purchases":
        await show_user_purchases(user_id)

    elif text == "/help":
        help_text = (
            "🆘 **Help & Commands**\n\n"
            "**Available Commands:**\n"
            "• /start - Welcome message\n"
            "• /catalog - Browse products\n"
            "• /purchases - View your purchases\n"
            "• /help - This help message\n\n"
            "**How to Buy:**\n"
            "1. Browse catalog with /catalog\n"
            "2. Select a product\n"
            "3. Pay with Telegram Stars\n"
            "4. Get instant download access\n\n"
            "**Support:**\n"
            "📧 support@digitalstore.com\n"
            "💬 @store_support\n\n"
            "Happy shopping! 🛍️"
        )

        await send_message(user_id, help_text)


# Webhook handler
async def webhook_handler(request):
    """Handle incoming webhook updates"""
    try:
        update_data = await request.json()
        logger.info(f"Received update: {update_data}")

        # Handle different update types
        if "message" in update_data:
            message = update_data["message"]
            if "text" in message and message["text"].startswith("/"):
                await handle_command(message)

        elif "callback_query" in update_data:
            await handle_callback_query(update_data["callback_query"])

        # Let NEONPAY handle payment updates
        await adapter.handle_webhook_update(update_data)

        return web.Response(text="OK")

    except Exception as e:
        logger.error(f"Webhook error: {e}")
        return web.Response(text="Error", status=500)


# Web application setup
async def init_webapp():
    """Initialize web application"""
    app = web.Application()
    app.router.add_post(WEBHOOK_PATH, webhook_handler)

    return app


async def main():
    """Main function"""
    logger.info("🚀 Starting NEONPAY Raw API Demo...")

    # Setup digital store
    await setup_digital_store()

    # Setup NEONPAY
    await neonpay.setup()

    # Create web application
    app = await init_webapp()

    logger.info("✅ Digital store initialized!")
    logger.info(f"💫 Webhook URL: {WEBHOOK_URL + WEBHOOK_PATH}")
    logger.info("🛍️ NEONPAY is ready to process payments!")

    # Start web server
    runner = web.AppRunner(app)
    await runner.setup()

    site = web.TCPSite(runner, WEBAPP_HOST, WEBAPP_PORT)
    await site.start()

    logger.info(f"🌐 Webhook server started on {WEBAPP_HOST}:{WEBAPP_PORT}")

    # Keep running
    try:
        await asyncio.Event().wait()
    except KeyboardInterrupt:
        logger.info("🛑 Shutting down...")
    finally:
        await adapter.close()
        await runner.cleanup()


if __name__ == "__main__":
    asyncio.run(main())

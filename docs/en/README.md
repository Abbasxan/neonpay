# NEONPAY Documentation (English)

Welcome to the complete NEONPAY documentation. This guide will help you integrate Telegram Stars payments into your bot quickly and efficiently.

## Table of Contents

1. [Installation](#installation)
2. [Quick Start](#quick-start)
3. [Library Support](#library-support)
4. [Core Concepts](#core-concepts)
5. [API Reference](#api-reference)
6. [Real-world Examples](#real-world-examples)
7. [Best Practices](#best-practices)
8. [Production Deployment](#production-deployment)
9. [Troubleshooting](#troubleshooting)
10. [Support](#support)

## Installation

Install NEONPAY using pip:

\`\`\`bash
pip install neonpay
\`\`\`

For specific bot libraries, install the required dependencies:

\`\`\`bash
# For Pyrogram
pip install neonpay pyrogram

# For Aiogram
pip install neonpay aiogram

# For python-telegram-bot
pip install neonpay python-telegram-bot

# For pyTelegramBotAPI
pip install neonpay pyTelegramBotAPI
\`\`\`

## Quick Start

### 1. Install Dependencies

\`\`\`bash
# For Aiogram (Recommended)
pip install neonpay aiogram

# For Pyrogram
pip install neonpay pyrogram

# For pyTelegramBotAPI
pip install neonpay pyTelegramBotAPI
\`\`\`

### 2. Import and Initialize

\`\`\`python
from neonpay.factory import create_neonpay
from neonpay.core import PaymentStage, PaymentStatus

# Automatic adapter detection
neonpay = create_neonpay(bot_instance=your_bot_instance)
\`\`\`

### 3. Create Payment Stage

\`\`\`python
stage = PaymentStage(
    title="Premium Access",
    description="Unlock premium features for 30 days",
    price=25,  # 25 Telegram Stars
)

neonpay.create_payment_stage("premium_access", stage)
\`\`\`

### 4. Send Payment

\`\`\`python
await neonpay.send_payment(user_id=12345, stage_id="premium_access")
\`\`\`

### 5. Handle Payments

\`\`\`python
@neonpay.on_payment
async def handle_payment(result):
    if result.status == PaymentStatus.COMPLETED:
        print(f"Received {result.amount} stars from user {result.user_id}")
        # Deliver your product/service here
\`\`\`

## Library Support

### Aiogram Integration (Recommended)

\`\`\`python
from aiogram import Bot, Dispatcher, Router
from aiogram.filters import Command
from neonpay.factory import create_neonpay
from neonpay.core import PaymentStage, PaymentStatus

bot = Bot(token="YOUR_TOKEN")
dp = Dispatcher()
router = Router()

neonpay = create_neonpay(bot_instance=bot, dispatcher=dp)

# Create payment stage
stage = PaymentStage(
    title="Premium Access",
    description="Unlock premium features for 30 days",
    price=25,
)
neonpay.create_payment_stage("premium_access", stage)

# Handle payments
@neonpay.on_payment
async def handle_payment(result):
    if result.status == PaymentStatus.COMPLETED:
        await bot.send_message(
            result.user_id, 
            f"Thank you! Your premium access is now active! 🎉"
        )

@router.message(Command("buy"))
async def buy_handler(message: Message):
    await neonpay.send_payment(message.from_user.id, "premium_access")

dp.include_router(router)
\`\`\`

### Pyrogram Integration

\`\`\`python
from pyrogram import Client, filters
from neonpay.factory import create_neonpay
from neonpay.core import PaymentStage, PaymentStatus

app = Client("my_bot", bot_token="YOUR_TOKEN")
neonpay = create_neonpay(bot_instance=app)

# Create payment stage
stage = PaymentStage(
    title="Premium Access",
    description="Unlock premium features for 30 days",
    price=25,
)
neonpay.create_payment_stage("premium_access", stage)

# Handle payments
@neonpay.on_payment
async def handle_payment(result):
    if result.status == PaymentStatus.COMPLETED:
        await app.send_message(
            result.user_id, 
            f"Thank you! Your premium access is now active! 🎉"
        )

@app.on_message(filters.command("buy"))
async def buy_handler(client, message):
    await neonpay.send_payment(message.from_user.id, "premium_access")

app.run()
\`\`\`

### pyTelegramBotAPI Integration

\`\`\`python
from telebot import TeleBot
from neonpay.factory import create_neonpay
from neonpay.core import PaymentStage, PaymentStatus

bot = TeleBot("YOUR_TOKEN")
neonpay = create_neonpay(bot_instance=bot)

# Create payment stage
stage = PaymentStage(
    title="Premium Access",
    description="Unlock premium features for 30 days",
    price=25,
)
neonpay.create_payment_stage("premium_access", stage)

# Handle payments
@neonpay.on_payment
async def handle_payment(result):
    if result.status == PaymentStatus.COMPLETED:
        bot.send_message(
            result.user_id, 
            f"Thank you! Your premium access is now active! 🎉"
        )

@bot.message_handler(commands=['buy'])
def buy_handler(message):
    import asyncio
    asyncio.run(neonpay.send_payment(message.from_user.id, "premium_access"))

bot.infinity_polling()
\`\`\`

## Core Concepts

### Payment Stages

Payment stages define what users are buying:

\`\`\`python
stage = PaymentStage(
    title="Product Name",           # Required: Display name
    description="Product details",  # Required: Description
    price=100,                     # Required: Price in stars
    label="Buy Now",               # Optional: Button label
    photo_url="https://...",       # Optional: Product image
    payload={"custom": "data"},    # Optional: Custom data
    start_parameter="ref_code"     # Optional: Deep linking
)
\`\`\`

### Payment Results

When payments complete, you receive a `PaymentResult`:

\`\`\`python
@neonpay.on_payment
async def handle_payment(result: PaymentResult):
    print(f"User ID: {result.user_id}")
    print(f"Amount: {result.amount}")
    print(f"Currency: {result.currency}")
    print(f"Status: {result.status}")
    print(f"Metadata: {result.metadata}")
\`\`\`

### Error Handling

\`\`\`python
from neonpay import NeonPayError, PaymentError

try:
    await neonpay.send_payment(user_id, "stage_id")
except PaymentError as e:
    print(f"Payment failed: {e}")
except NeonPayError as e:
    print(f"System error: {e}")
\`\`\`

## API Reference

### NeonPayCore Class

#### Methods

- `create_payment_stage(stage_id: str, stage: PaymentStage)` - Create payment stage
- `get_payment_stage(stage_id: str)` - Get payment stage by ID
- `list_payment_stages()` - Get all payment stages
- `remove_payment_stage(stage_id: str)` - Remove payment stage
- `send_payment(user_id: int, stage_id: str)` - Send payment invoice
- `on_payment(callback)` - Register payment callback
- `get_stats()` - Get system statistics

### PaymentStage Class

#### Parameters

- `title: str` - Payment title (required)
- `description: str` - Payment description (required)
- `price: int` - Price in Telegram Stars (required)
- `label: str` - Button label (default: "Payment")
- `photo_url: str` - Product image URL (optional)
- `payload: dict` - Custom data (optional)
- `start_parameter: str` - Deep linking parameter (optional)

### PaymentResult Class

#### Attributes

- `user_id: int` - User who made payment
- `amount: int` - Payment amount
- `currency: str` - Payment currency (XTR)
- `status: PaymentStatus` - Payment status
- `transaction_id: str` - Transaction ID (optional)
- `metadata: dict` - Custom metadata

## Real-world Examples

All examples are based on **real working bots** and are production-ready. Check the [examples directory](../../examples/) for complete implementations.

### Donation Bot

\`\`\`python
from neonpay.factory import create_neonpay
from neonpay.core import PaymentStage, PaymentStatus

# Donation options
DONATE_OPTIONS = [
    {"amount": 1, "symbol": "⭐", "desc": "1⭐ support: Will be used for bot server costs"},
    {"amount": 10, "symbol": "⭐", "desc": "10⭐ support: Will be spent on developing new features"},
    {"amount": 50, "symbol": "🌟", "desc": "50⭐ big support: Will be used for bot development and promotion"},
]

neonpay = create_neonpay(bot_instance=bot)

# Create donation stages
for option in DONATE_OPTIONS:
    neonpay.create_payment_stage(
        f"donate_{option['amount']}",
        PaymentStage(
            title=f"Support {option['amount']}{option['symbol']}",
            description=option["desc"],
            price=option["amount"],
        ),
    )

# Handle donations
@neonpay.on_payment
async def handle_payment(result):
    if result.status == PaymentStatus.COMPLETED:
        if result.stage_id.startswith("donate_"):
            await bot.send_message(
                result.user_id,
                f"Thank you! Your support: {result.amount}⭐ ❤️\n"
                f"Your contribution helps keep the bot running!"
            )
\`\`\`

### Digital Store

\`\`\`python
# Digital products
DIGITAL_PRODUCTS = [
    {
        "id": "premium_access",
        "title": "Premium Access",
        "description": "Unlock all premium features for 30 days",
        "price": 25,
        "symbol": "👑"
    },
    {
        "id": "custom_theme",
        "title": "Custom Theme",
        "description": "Personalized bot theme and colors",
        "price": 15,
        "symbol": "🎨"
    },
]

# Create product stages
for product in DIGITAL_PRODUCTS:
    neonpay.create_payment_stage(
        product["id"],
        PaymentStage(
            title=f"{product['symbol']} {product['title']}",
            description=product["description"],
            price=product["price"],
        ),
    )

# Handle product purchases
@neonpay.on_payment
async def handle_payment(result):
    if result.status == PaymentStatus.COMPLETED:
        if not result.stage_id.startswith("donate_"):
            product = next((p for p in DIGITAL_PRODUCTS if p["id"] == result.stage_id), None)
            if product:
                await bot.send_message(
                    result.user_id,
                    f"🎉 Purchase successful!\n\n"
                    f"Product: {product['symbol']} {product['title']}\n"
                    f"Price: {product['price']}⭐\n\n"
                    f"Your digital product has been activated!\n"
                    f"Thank you for your purchase! 🚀"
                )
\`\`\`

## Best Practices

### 1. Validate Payment Data

\`\`\`python
@neonpay.on_payment
async def handle_payment(result):
    # Verify payment amount
    expected_amount = get_expected_amount(result.metadata)
    if result.amount != expected_amount:
        logger.warning(f"Amount mismatch: expected {expected_amount}, got {result.amount}")
        return
    
    # Process payment
    await process_payment(result)
\`\`\`

### 2. Handle Errors Gracefully

\`\`\`python
async def safe_send_payment(user_id, stage_id):
    try:
        await neonpay.send_payment(user_id, stage_id)
    except PaymentError as e:
        await bot.send_message(user_id, f"Payment failed: {e}")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        await bot.send_message(user_id, "Something went wrong. Please try again.")
\`\`\`

### 3. Use Meaningful Stage IDs

\`\`\`python
# Good
neonpay.create_payment_stage("premium_monthly_subscription", stage)
neonpay.create_payment_stage("coffee_large_size", stage)

# Bad
neonpay.create_payment_stage("stage1", stage)
neonpay.create_payment_stage("payment", stage)
\`\`\`

### 4. Log Payment Events

\`\`\`python
import logging

logger = logging.getLogger(__name__)

@neonpay.on_payment
async def handle_payment(result):
    logger.info(f"Payment received: {result.user_id} paid {result.amount} stars")
    
    try:
        await process_payment(result)
        logger.info(f"Payment processed successfully for user {result.user_id}")
    except Exception as e:
        logger.error(f"Failed to process payment for user {result.user_id}: {e}")
\`\`\`

## Production Deployment

### 1. Environment Variables

\`\`\`python
import os

# Store sensitive data securely
BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
DATABASE_URL = os.getenv("DATABASE_URL")
\`\`\`

### 2. Database Integration

\`\`\`python
# Replace in-memory storage with database
import asyncpg

async def save_payment(user_id: int, amount: int, stage_id: str):
    conn = await asyncpg.connect(DATABASE_URL)
    await conn.execute(
        "INSERT INTO payments (user_id, amount, stage_id, created_at) VALUES ($1, $2, $3, NOW())",
        user_id, amount, stage_id
    )
    await conn.close()
\`\`\`

### 3. Error Monitoring

\`\`\`python
import logging
from logging.handlers import RotatingFileHandler

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        RotatingFileHandler("bot.log", maxBytes=10*1024*1024, backupCount=5),
        logging.StreamHandler()
    ]
)
\`\`\`

### 4. Health Checks

\`\`\`python
@router.message(Command("status"))
async def status_command(message: Message):
    """Health check endpoint"""
    stats = neonpay.get_stats()
    status_text = (
        f"📊 **Bot Status**\n\n"
        f"✅ Status: Online\n"
        f"💫 Payment system: Active\n"
        f"🔧 Version: 2.0\n"
        f"📈 Payment stages: {stats['total_stages']}\n"
        f"🔄 Callbacks: {stats['registered_callbacks']}\n\n"
        f"Thank you for using this free bot!"
    )
    await message.answer(status_text)
\`\`\`

### 5. Webhook Setup (for Raw API)

\`\`\`python
from aiohttp import web

async def webhook_handler(request):
    """Handle incoming webhook updates"""
    try:
        data = await request.json()
        
        # Process update
        await process_update(data)
        
        return web.Response(text="OK")
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        return web.Response(text="Error", status=500)

app = web.Application()
app.router.add_post("/webhook", webhook_handler)
\`\`\`

## Troubleshooting

### Common Issues

#### 1. "Payment stage not found"

\`\`\`python
# Check if stage exists
stage = neonpay.get_payment_stage("my_stage")
if not stage:
    print("Stage doesn't exist!")
    
# List all stages
stages = neonpay.list_payment_stages()
print(f"Available stages: {list(stages.keys())}")
\`\`\`

#### 2. "Failed to send invoice"

- Verify bot token is correct
- Check if user has started the bot
- Ensure user ID is valid
- Verify payment stage configuration

#### 3. Payment callbacks not working

\`\`\`python
# Make sure setup is called
await neonpay.setup()

# Check if handlers are registered
stats = neonpay.get_stats()
print(f"Callbacks registered: {stats['registered_callbacks']}")
\`\`\`

### Debug Mode

\`\`\`python
import logging

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)
logging.getLogger("neonpay").setLevel(logging.DEBUG)
\`\`\`

## Support

### Getting Help

If you need help:

1. 📚 **Documentation**: Check the [examples](../../examples/) directory for complete working examples
2. 💬 **Community**: Join our [Telegram community](https://t.me/neonpay_community)
3. 🐛 **Issues**: Open an issue on [GitHub](https://github.com/Abbasxan/neonpay/issues)
4. 📧 **Email**: Contact support at [support@neonpay.com](mailto:support@neonpay.com)
5. 💬 **Telegram**: Contact [@neonsahib](https://t.me/neonsahib)

### Resources

- 📖 **Complete Examples**: [examples/](../../examples/) - Production-ready bot examples
- 🔧 **API Reference**: [API.md](API.md) - Complete API documentation
- 🔒 **Security**: [SECURITY.md](SECURITY.md) - Security best practices
- 📝 **Changelog**: [CHANGELOG.md](../../CHANGELOG.md) - Version history

### Quick Links

- 🚀 **Get Started**: [Quick Start Guide](#quick-start)
- 📚 **Examples**: [Real-world Examples](#real-world-examples)
- 🏗️ **Deployment**: [Production Deployment](#production-deployment)
- 🐛 **Troubleshooting**: [Common Issues](#troubleshooting)

---

[← Back to Main README](../../README.md) | [Russian Documentation →](../ru/README.md) | [Azerbaijani Documentation →](../az/README.md)

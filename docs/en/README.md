# NEONPAY Documentation (English)

Welcome to the complete NEONPAY documentation. This guide will help you integrate Telegram Stars payments into your bot quickly and efficiently.

## Table of Contents

1. [Installation](#installation)
2. [Quick Start](#quick-start)
3. [Library Support](#library-support)
4. [Core Concepts](#core-concepts)
5. [API Reference](#api-reference)
6. [Examples](#examples)
7. [Best Practices](#best-practices)
8. [Troubleshooting](#troubleshooting)

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

### 1. Import and Initialize

\`\`\`python
from neonpay import create_neonpay, PaymentStage

# Automatic adapter detection
neonpay = create_neonpay(your_bot_instance)
\`\`\`

### 2. Create Payment Stage

\`\`\`python
stage = PaymentStage(
    title="Premium Access",
    description="Unlock premium features",
    price=100,  # 100 Telegram Stars
    photo_url="https://example.com/logo.png"
)

neonpay.create_payment_stage("premium", stage)
\`\`\`

### 3. Send Payment

\`\`\`python
await neonpay.send_payment(user_id=12345, stage_id="premium")
\`\`\`

### 4. Handle Payments

\`\`\`python
@neonpay.on_payment
async def handle_payment(result):
    print(f"Received {result.amount} stars from user {result.user_id}")
\`\`\`

## Library Support

### Pyrogram Integration

\`\`\`python
from pyrogram import Client
from neonpay import create_neonpay

app = Client("my_bot", bot_token="YOUR_TOKEN")
neonpay = create_neonpay(app)

@app.on_message()
async def handle_message(client, message):
    if message.text == "/buy":
        await neonpay.send_payment(message.from_user.id, "premium")

app.run()
\`\`\`

### Aiogram Integration

\`\`\`python
from aiogram import Bot, Dispatcher, Router
from neonpay import create_neonpay

bot = Bot(token="YOUR_TOKEN")
dp = Dispatcher()
router = Router()

neonpay = create_neonpay(bot)

@router.message(Command("buy"))
async def buy_handler(message: Message):
    await neonpay.send_payment(message.from_user.id, "premium")

dp.include_router(router)
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

## Examples

### E-commerce Bot

\`\`\`python
from neonpay import create_neonpay, PaymentStage

# Product catalog
products = {
    "coffee": PaymentStage("Coffee", "Premium coffee beans", 50),
    "tea": PaymentStage("Tea", "Organic tea leaves", 30),
    "cake": PaymentStage("Cake", "Delicious chocolate cake", 100)
}

neonpay = create_neonpay(bot)

# Add all products
for product_id, stage in products.items():
    neonpay.create_payment_stage(product_id, stage)

# Handle orders
@neonpay.on_payment
async def process_order(result):
    user_id = result.user_id
    product = result.metadata.get("product")
    
    # Process the order
    await fulfill_order(user_id, product)
    await bot.send_message(user_id, "Order confirmed! Thank you!")
\`\`\`

### Subscription Service

\`\`\`python
subscription_plans = {
    "monthly": PaymentStage(
        "Monthly Plan", 
        "1 month premium access", 
        100,
        payload={"duration": 30}
    ),
    "yearly": PaymentStage(
        "Yearly Plan", 
        "12 months premium access (2 months free!)", 
        1000,
        payload={"duration": 365}
    )
}

@neonpay.on_payment
async def handle_subscription(result):
    user_id = result.user_id
    duration = result.metadata.get("duration", 30)
    
    # Grant subscription
    await grant_premium(user_id, days=duration)
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

### Getting Help

If you need help:

1. Check the [examples](../../examples/) directory
2. Read the [FAQ](FAQ.md)
3. Open an issue on [GitHub](https://github.com/Abbasxan/neonpay/issues)
4. Contact support: [@neonsahib](https://t.me/neonsahib)

---

[← Back to Main README](../../README.md) | [Russian Documentation →](../ru/README.md)

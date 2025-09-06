# Frequently Asked Questions (FAQ) - NEONPAY

Common questions and answers about NEONPAY library.

## Table of Contents

1. [General Questions](#general-questions)
2. [Installation & Setup](#installation--setup)
3. [Payment Processing](#payment-processing)
4. [Error Handling](#error-handling)
5. [Security](#security)
6. [Production Deployment](#production-deployment)
7. [Troubleshooting](#troubleshooting)

## General Questions

### What is NEONPAY?

NEONPAY is a Python library that simplifies Telegram Stars payments integration for bot developers. It provides a unified API for multiple bot libraries (Aiogram, Pyrogram, pyTelegramBotAPI, etc.) and handles payment processing automatically.

### Which bot libraries are supported?

NEONPAY supports:
- **Aiogram** (Recommended) - Modern async library
- **Pyrogram** - Popular MTProto library
- **pyTelegramBotAPI** - Simple synchronous library
- **python-telegram-bot** - Comprehensive library
- **Raw Telegram Bot API** - Direct HTTP requests

### What are Telegram Stars?

Telegram Stars is Telegram's built-in virtual currency that users can purchase and use to pay for digital goods and services within bots. It's officially supported by Telegram and provides a seamless payment experience.

### Is NEONPAY free to use?

Yes, NEONPAY is completely free and open-source. You only pay Telegram's fees for processing Stars payments (typically 5% of the transaction amount).

## Installation & Setup

### How do I install NEONPAY?

```bash
# Basic installation
pip install neonpay

# With specific bot library
pip install neonpay aiogram  # For Aiogram
pip install neonpay pyrogram  # For Pyrogram
```

### How do I get started quickly?

```python
from neonpay.factory import create_neonpay
from neonpay.core import PaymentStage, PaymentStatus

# Initialize
neonpay = create_neonpay(bot_instance=your_bot)

# Create payment stage
stage = PaymentStage(
    title="Premium Access",
    description="Unlock premium features",
    price=25,  # 25 Telegram Stars
)
neonpay.create_payment_stage("premium", stage)

# Handle payments
@neonpay.on_payment
async def handle_payment(result):
    if result.status == PaymentStatus.COMPLETED:
        print(f"Payment received: {result.amount} stars")
```

### Do I need to configure webhooks?

No, NEONPAY handles webhook configuration automatically for supported libraries. For Raw API, you need to set up webhooks manually.

### How do I choose the right bot library?

**For new projects:** Use **Aiogram** - it's modern, well-documented, and has excellent async support.

**For existing projects:** Use whatever library you're already using. NEONPAY works with all major libraries.

## Payment Processing

### How do I create different payment options?

```python
# Donation options
donation_stages = [
    PaymentStage("Support 1⭐", "Help keep the bot running", 1),
    PaymentStage("Support 10⭐", "Support development", 10),
    PaymentStage("Support 50⭐", "Big support", 50),
]

# Digital products
product_stages = [
    PaymentStage("Premium Access", "30 days premium", 25),
    PaymentStage("Custom Theme", "Personalized theme", 15),
]

# Add all stages
for i, stage in enumerate(donation_stages):
    neonpay.create_payment_stage(f"donate_{i}", stage)

for i, stage in enumerate(product_stages):
    neonpay.create_payment_stage(f"product_{i}", stage)
```

### How do I handle different types of payments?

```python
@neonpay.on_payment
async def handle_payment(result):
    if result.status == PaymentStatus.COMPLETED:
        if result.stage_id.startswith("donate_"):
            # Handle donation
            await handle_donation(result)
        elif result.stage_id.startswith("product_"):
            # Handle product purchase
            await handle_product_purchase(result)
        else:
            # Handle other payments
            await handle_other_payment(result)
```

### Can I customize payment messages?

Yes, you can customize the thank you message:

```python
neonpay = create_neonpay(
    bot_instance=bot,
    thank_you_message="🎉 Thank you for your purchase! Your product is now active."
)
```

### How do I validate payment amounts?

```python
@neonpay.on_payment
async def handle_payment(result):
    # Get expected amount for this stage
    stage = neonpay.get_payment_stage(result.stage_id)
    expected_amount = stage.price
    
    if result.amount != expected_amount:
        logger.warning(f"Amount mismatch: expected {expected_amount}, got {result.amount}")
        return
    
    # Process payment
    await process_payment(result)
```

## Error Handling

### What happens if a payment fails?

NEONPAY automatically handles payment failures and provides detailed error information:

```python
@neonpay.on_payment
async def handle_payment(result):
    if result.status == PaymentStatus.COMPLETED:
        # Payment successful
        await process_successful_payment(result)
    elif result.status == PaymentStatus.FAILED:
        # Payment failed
        await handle_payment_failure(result)
    elif result.status == PaymentStatus.PENDING:
        # Payment pending
        await handle_pending_payment(result)
```

### How do I handle network errors?

```python
async def safe_send_payment(user_id: int, stage_id: str):
    try:
        await neonpay.send_payment(user_id, stage_id)
    except PaymentError as e:
        logger.error(f"Payment error: {e}")
        await bot.send_message(user_id, "Payment failed. Please try again.")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        await bot.send_message(user_id, "Something went wrong. Please try again later.")
```

### What if the bot token is invalid?

NEONPAY will raise a `ConfigurationError` if the bot token is invalid:

```python
try:
    neonpay = create_neonpay(bot_instance=bot)
except ConfigurationError as e:
    print(f"Configuration error: {e}")
    # Check your bot token
```

## Security

### How do I protect my bot token?

Never hardcode tokens in your source code:

```python
# ❌ Wrong
BOT_TOKEN = "1234567890:ABCdefGHIjklMNOpqrsTUVwxyz"

# ✅ Correct
import os
BOT_TOKEN = os.getenv("BOT_TOKEN")
```

### How do I validate user permissions?

```python
async def safe_send_payment(user_id: int, stage_id: str):
    # Check if user can make payments
    if not await user_can_pay(user_id):
        await bot.send_message(user_id, "You don't have permission to make payments.")
        return
    
    # Check if user has reached payment limit
    if await user_payment_limit_reached(user_id):
        await bot.send_message(user_id, "You've reached your payment limit.")
        return
    
    # Send payment
    await neonpay.send_payment(user_id, stage_id)
```

### How do I prevent payment fraud?

```python
class PaymentValidator:
    def __init__(self):
        self.user_payments = defaultdict(list)
        self.max_payments_per_hour = 5
    
    async def validate_payment(self, user_id: int, stage_id: str) -> bool:
        # Check payment frequency
        now = time.time()
        recent_payments = [
            t for t in self.user_payments[user_id] 
            if now - t < 3600  # Last hour
        ]
        
        if len(recent_payments) >= self.max_payments_per_hour:
            return False
        
        # Check for suspicious patterns
        if await self.is_suspicious_user(user_id):
            return False
        
        return True
    
    async def record_payment(self, user_id: int):
        self.user_payments[user_id].append(time.time())
```

## Production Deployment

### How do I deploy to production?

1. **Use environment variables:**
```python
import os
BOT_TOKEN = os.getenv("BOT_TOKEN")
DATABASE_URL = os.getenv("DATABASE_URL")
```

2. **Set up proper logging:**
```python
import logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
```

3. **Use a production database:**
```python
# Replace in-memory storage with database
import asyncpg

async def store_payment(payment_data):
    conn = await asyncpg.connect(DATABASE_URL)
    await conn.execute(
        "INSERT INTO payments (user_id, amount, stage_id, created_at) VALUES ($1, $2, $3, NOW())",
        payment_data['user_id'], payment_data['amount'], payment_data['stage_id']
    )
    await conn.close()
```

### How do I monitor payments?

```python
class PaymentMonitor:
    def __init__(self):
        self.payment_stats = defaultdict(int)
    
    async def log_payment(self, result):
        self.payment_stats['total_payments'] += 1
        self.payment_stats['total_amount'] += result.amount
        
        # Log to database
        await self.store_payment_log(result)
        
        # Send alerts for high volume
        if self.payment_stats['total_payments'] % 100 == 0:
            await self.send_volume_alert()
    
    async def get_stats(self):
        return dict(self.payment_stats)
```

### How do I handle high traffic?

```python
# Use connection pooling
import asyncpg

class DatabasePool:
    def __init__(self, database_url: str):
        self.pool = None
        self.database_url = database_url
    
    async def initialize(self):
        self.pool = await asyncpg.create_pool(
            self.database_url,
            min_size=10,
            max_size=20
        )
    
    async def execute(self, query, *args):
        async with self.pool.acquire() as conn:
            return await conn.execute(query, *args)
```

## Troubleshooting

### Payment not being sent

**Check:**
1. Bot token is valid
2. User has started the bot
3. Payment stage exists
4. User ID is correct

```python
# Debug payment sending
async def debug_send_payment(user_id: int, stage_id: str):
    # Check if stage exists
    stage = neonpay.get_payment_stage(stage_id)
    if not stage:
        print(f"Stage {stage_id} not found")
        return
    
    # Check if user exists
    try:
        user = await bot.get_chat(user_id)
        print(f"User found: {user.first_name}")
    except Exception as e:
        print(f"User not found: {e}")
        return
    
    # Send payment
    try:
        await neonpay.send_payment(user_id, stage_id)
        print("Payment sent successfully")
    except Exception as e:
        print(f"Payment failed: {e}")
```

### Payment callback not working

**Check:**
1. `@neonpay.on_payment` decorator is properly applied
2. Function is async
3. Bot is running and receiving updates

```python
# Test payment callback
@neonpay.on_payment
async def test_payment_handler(result):
    print(f"Payment callback triggered: {result}")
    # Add breakpoint here to debug
```

### Bot not responding to commands

**Check:**
1. Bot token is correct
2. Bot is running
3. Commands are properly registered
4. Network connectivity

```python
# Test bot connectivity
async def test_bot():
    try:
        me = await bot.get_me()
        print(f"Bot is running: {me.first_name}")
    except Exception as e:
        print(f"Bot connection failed: {e}")
```

### Database connection issues

```python
# Test database connection
async def test_database():
    try:
        conn = await asyncpg.connect(DATABASE_URL)
        result = await conn.fetchval("SELECT 1")
        print(f"Database connected: {result}")
        await conn.close()
    except Exception as e:
        print(f"Database connection failed: {e}")
```

## Common Issues

### "Payment stage not found"

This happens when you try to send a payment for a stage that doesn't exist:

```python
# Check available stages
stages = neonpay.list_payment_stages()
print(f"Available stages: {list(stages.keys())}")

# Create stage if missing
if "premium" not in stages:
    stage = PaymentStage("Premium", "Premium access", 25)
    neonpay.create_payment_stage("premium", stage)
```

### "Failed to send invoice"

This usually means:
1. Bot token is invalid
2. User hasn't started the bot
3. User ID is incorrect

```python
# Debug invoice sending
async def debug_invoice(user_id: int, stage_id: str):
    try:
        # Check bot info
        me = await bot.get_me()
        print(f"Bot: {me.first_name} (@{me.username})")
        
        # Check user
        user = await bot.get_chat(user_id)
        print(f"User: {user.first_name} (@{user.username})")
        
        # Send payment
        await neonpay.send_payment(user_id, stage_id)
    except Exception as e:
        print(f"Error: {e}")
```

### "Payment callback not triggered"

Make sure:
1. Function is decorated with `@neonpay.on_payment`
2. Function is async
3. Bot is receiving updates

```python
# Test callback registration
stats = neonpay.get_stats()
print(f"Callbacks registered: {stats['registered_callbacks']}")
```

## Getting Help

### Where can I get help?

1. **Documentation**: Check the [examples](../../examples/) directory
2. **Community**: Join our [Telegram community](https://t.me/neonpay_community)
3. **Issues**: Open an issue on [GitHub](https://github.com/Abbasxan/neonpay/issues)
4. **Email**: Contact support at [support@neonpay.com](mailto:support@neonpay.com)

### How do I report bugs?

When reporting bugs, please include:
1. Python version
2. NEONPAY version
3. Bot library and version
4. Error message and stack trace
5. Steps to reproduce

### How do I request features?

Feature requests are welcome! Please:
1. Check if the feature already exists
2. Describe the use case
3. Provide example code if possible
4. Open an issue on GitHub

---

**Still have questions? Check the [examples](../../examples/) directory or contact support!**

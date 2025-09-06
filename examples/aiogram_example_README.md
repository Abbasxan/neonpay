# Aiogram Example - NEONPAY Donation Bot

This is a complete, production-ready Telegram bot built with **Aiogram** and **NEONPAY** for processing Telegram Stars payments.

## Features

- ❤️ **Donation System**: Support the developer with 1⭐, 10⭐, or 50⭐ donations
- 🛒 **Digital Store**: Sell digital products (Premium Access, Custom Theme, Priority Support)
- 💫 **Telegram Stars**: Native Telegram payment processing
- 🎯 **Real-world Code**: Based on actual working bot implementation
- 🔄 **Auto-delivery**: Instant digital product delivery after payment

## Quick Start

### 1. Install Dependencies
```bash
pip install aiogram neonpay
```

### 2. Configure Bot
1. Get bot token from [@BotFather](https://t.me/BotFather)
2. Replace `YOUR_BOT_TOKEN` in the code
3. Run the bot:

```bash
python aiogram_example.py
```

### 3. Test Payments
1. Start conversation with your bot
2. Use `/donate` to test donations
3. Use `/store` to test digital products
4. Complete payment with Telegram Stars

## Code Structure

```python
# Donation options
DONATE_OPTIONS = [
    {"amount": 1, "symbol": "⭐", "desc": "1⭐ support: Will be used for bot server costs"},
    {"amount": 10, "symbol": "⭐", "desc": "10⭐ support: Will be spent on developing new features"},
    {"amount": 50, "symbol": "🌟", "desc": "50⭐ big support: Will be used for bot development and promotion"},
]

# Digital products
DIGITAL_PRODUCTS = [
    {
        "id": "premium_access",
        "title": "Premium Access",
        "description": "Unlock all premium features for 30 days",
        "price": 25,
        "symbol": "👑"
    },
    # ... more products
]
```

## Key Components

### Payment Setup
```python
async def setup_neonpay():
    neonpay = create_neonpay(bot_instance=bot, dispatcher=dp)
    
    # Create payment stages
    for option in DONATE_OPTIONS:
        neonpay.create_payment_stage(
            f"donate_{option['amount']}",
            PaymentStage(
                title=f"Support {option['amount']}{option['symbol']}",
                description=option["desc"],
                price=option["amount"],
            ),
        )
```

### Payment Handler
```python
@neonpay.on_payment
async def handle_payment(result):
    if result.status == PaymentStatus.COMPLETED:
        if result.stage_id.startswith("donate_"):
            # Handle donation
            await bot.send_message(result.user_id, "Thank you! ❤️")
        else:
            # Handle product delivery
            await bot.send_message(result.user_id, "Product activated! 🚀")
```

### Commands
- `/start` - Welcome message with inline buttons
- `/donate` - Show donation options
- `/store` - Show digital products
- `/status` - Bot statistics
- `/help` - Help information

## Customization

### Adding New Products
```python
new_product = {
    "id": "new_product",
    "title": "New Product",
    "description": "Product description",
    "price": 20,
    "symbol": "🆕"
}

# Add to DIGITAL_PRODUCTS list
DIGITAL_PRODUCTS.append(new_product)

# Create payment stage
neonpay.create_payment_stage(
    new_product["id"],
    PaymentStage(
        title=f"{new_product['symbol']} {new_product['title']}",
        description=new_product["description"],
        price=new_product["price"],
    ),
)
```

### Custom Payment Logic
```python
@neonpay.on_payment
async def handle_payment(result):
    if result.status == PaymentStatus.COMPLETED:
        # Your custom logic here
        await process_payment(result.user_id, result.stage_id, result.amount)
        
        # Send confirmation
        await bot.send_message(result.user_id, "Payment successful! 🎉")
```

## Production Deployment

### Environment Variables
```python
import os
BOT_TOKEN = os.getenv("BOT_TOKEN")
```

### Database Integration
```python
# Replace in-memory storage with database
async def save_payment(user_id, amount, stage_id):
    # Save to PostgreSQL, MongoDB, etc.
    pass
```

### Error Handling
```python
@router.error()
async def error_handler(event, exception):
    logger.error(f"Bot error: {exception}", exc_info=True)
    return True
```

## Testing

### Test Payments
1. Use Telegram's test environment
2. Create test bot with @BotFather
3. Use test Telegram Stars
4. Verify payment flow

### Debug Mode
```python
import logging
logging.getLogger("neonpay").setLevel(logging.DEBUG)
```

## Support

- 📚 [NEONPAY Documentation](../docs/en/README.md)
- 💬 [Community](https://t.me/neonpay_community)
- 🐛 [Report Issues](https://github.com/Abbasxan/neonpay/issues)

---

**Ready to build your own payment bot? Start with this example! 🚀**

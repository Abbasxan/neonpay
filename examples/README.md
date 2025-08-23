# NEONPAY Examples

This directory contains complete working examples for all supported Telegram bot libraries.

## Available Examples

### 1. [Pyrogram Example](pyrogram_example.py)
**Complete donation bot with multiple payment tiers**
- ☕ Coffee donation (50 ⭐)
- 🚀 Premium support (200 ⭐)  
- 👑 VIP access (500 ⭐)
- Interactive inline keyboards
- Payment confirmation system
- User status tracking

**Features:**
- Automatic payment processing
- Custom payment stages
- Callback query handling
- Error handling and logging
- User-friendly interface

### 2. [Aiogram Example](aiogram_example.py)
**Digital products store with shopping cart**
- 📚 Programming eBooks
- 🎓 Online courses
- 💼 Consultation services
- ⭐ Premium memberships
- Download delivery system
- Purchase history

**Features:**
- FSM (Finite State Machine) support
- Product catalog management
- Automatic file delivery
- Receipt generation
- Customer support integration

### 3. [python-telegram-bot Example](ptb_example.py)
**Professional services marketplace**
- 🎨 Web design services
- 🎯 Logo design
- 📈 SEO audits
- ✍️ Content writing
- Project management workflow
- Client communication system

**Features:**
- Service booking system
- Project brief collection
- Manager assignment
- Status tracking
- Portfolio showcase

### 4. [pyTelegramBotAPI Example](telebot_example.py)
**Subscription service with multiple plans**
- 📱 Basic plan (99 ⭐)
- 💼 Pro plan (299 ⭐)
- 🏢 Enterprise plan (599 ⭐)
- User dashboard
- Subscription management
- Feature comparison

**Features:**
- Multi-tier subscriptions
- User access control
- Plan comparison tools
- Renewal notifications
- Usage analytics

### 5. [Raw API Example](raw_api_example.py)
**Digital store with webhook integration**
- 🐍 Programming eBooks
- 🌐 Development courses
- ⚛️ React templates
- 🔌 WordPress plugins
- Direct download links
- Purchase receipts

**Features:**
- Webhook-based updates
- File delivery system
- Purchase tracking
- Receipt generation
- Customer support

## Quick Start

### 1. Choose Your Library
Pick the example that matches your preferred bot library:

\`\`\`bash
# For Pyrogram
pip install pyrogram neonpay

# For Aiogram  
pip install aiogram neonpay

# For python-telegram-bot
pip install python-telegram-bot neonpay

# For pyTelegramBotAPI
pip install pyTelegramBotAPI neonpay

# For Raw API
pip install aiohttp neonpay
\`\`\`

### 2. Configure Your Bot
Replace the placeholder values in each example:

\`\`\`python
BOT_TOKEN = "YOUR_BOT_TOKEN"  # Get from @BotFather
API_ID = 12345                # Get from my.telegram.org
API_HASH = "your_api_hash"    # Get from my.telegram.org
\`\`\`

### 3. Run the Example
\`\`\`bash
python pyrogram_example.py
\`\`\`

## Common Features

All examples include:

✅ **Payment Processing**
- Telegram Stars integration
- Multiple payment stages
- Automatic confirmation
- Error handling

✅ **User Interface**
- Inline keyboards
- Command handlers
- Callback queries
- Status messages

✅ **Business Logic**
- Product/service delivery
- User management
- Purchase tracking
- Support integration

## Customization Guide

### Adding New Payment Stages

\`\`\`python
# Create payment stage
new_stage = PaymentStage(
    title="Your Product",
    description="Product description",
    price=100,  # 100 Telegram Stars
    photo_url="https://example.com/image.png",
    payload={"custom": "data"}
)

# Add to NEONPAY
neonpay.create_payment_stage("product_id", new_stage)
\`\`\`

### Handling Payments

\`\`\`python
@neonpay.on_payment
async def handle_payment(result: PaymentResult):
    user_id = result.user_id
    amount = result.amount
    custom_data = result.metadata
    
    # Your business logic here
    await deliver_product(user_id, custom_data)
\`\`\`

### Error Handling

\`\`\`python
try:
    await neonpay.send_payment(user_id, "stage_id")
except PaymentError as e:
    await bot.send_message(user_id, f"Payment failed: {e}")
except NeonPayError as e:
    logger.error(f"NEONPAY error: {e}")
\`\`\`

## Testing

### 1. Test Payments
Use Telegram's test environment for development:
- Create test bot with @BotFather
- Use test Telegram Stars
- Verify payment flow

### 2. Debug Mode
Enable detailed logging:

\`\`\`python
import logging
logging.getLogger("neonpay").setLevel(logging.DEBUG)
\`\`\`

### 3. Error Simulation
Test error scenarios:
- Invalid payment stages
- Network failures
- User cancellations

## Production Deployment

### 1. Environment Variables
Store sensitive data securely:

\`\`\`python
import os
BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
\`\`\`

### 2. Database Integration
Replace in-memory storage:

\`\`\`python
# Instead of dictionaries, use:
# - PostgreSQL
# - MongoDB  
# - Redis
# - SQLite
\`\`\`

### 3. Monitoring
Add monitoring and analytics:

\`\`\`python
# Track payments
# Monitor errors
# Analyze user behavior
# Performance metrics
\`\`\`

## Support

Need help with the examples?

- 📚 Read the [documentation](../docs/en/README.md)
- 💬 Join our [community](https://t.me/neonpay_community)
- 📧 Contact [support](mailto:support@neonpay.com)
- 🐛 Report [issues](https://github.com/Abbasxan/neonpay/issues)

## Contributing

Want to improve the examples?

1. Fork the repository
2. Create your feature branch
3. Add/improve examples
4. Submit a pull request

---

**Happy coding with NEONPAY! 🚀**

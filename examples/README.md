# NEONPAY Examples

This directory contains complete working examples for all supported Telegram bot libraries. All examples are based on real-world usage patterns and are ready to use in production.

## 🆕 New in v2.6.0

The examples now include comprehensive demonstrations of all new enterprise features:

- **Advanced Features Example** - Complete enterprise features demo
- **Multi-Bot Analytics Example** - Analytics dashboard setup
- **Multi-Bot Sync Example** - Bot synchronization
- **Webhook Server Example** - Web interface setup

## Available Examples

### 1. [Aiogram Example](aiogram_example.py) ⭐ **RECOMMENDED**
**Complete donation bot with digital store**
- ❤️ Support Developer (1⭐, 10⭐, 50⭐)
- 🛒 Digital Products Store (Premium Access, Custom Theme, Priority Support)
- Interactive inline keyboards
- Payment confirmation system
- Real-world production code

**Features:**
- Automatic payment processing
- Digital product delivery
- Callback query handling
- Error handling and logging
- User-friendly interface
- Based on real working bot

### 2. [Pyrogram Example](pyrogram_example.py)
**Complete donation bot with digital store**
- ❤️ Support Developer (1⭐, 10⭐, 50⭐)
- 🛒 Digital Products Store (Premium Access, Custom Theme, Priority Support)
- Interactive inline keyboards
- Payment confirmation system
- Real-world production code

**Features:**
- Automatic payment processing
- Digital product delivery
- Callback query handling
- Error handling and logging
- User-friendly interface
- Based on real working bot

### 3. [pyTelegramBotAPI Example](telebot_example.py)
**Complete donation bot with digital store**
- ❤️ Support Developer (1⭐, 10⭐, 50⭐)
- 🛒 Digital Products Store (Premium Access, Custom Theme, Priority Support)
- Interactive inline keyboards
- Payment confirmation system
- Real-world production code

**Features:**
- Automatic payment processing
- Digital product delivery
- Callback query handling
- Error handling and logging
- User-friendly interface
- Based on real working bot

### 4. [python-telegram-bot Example](ptb_example.py)
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

## 🆕 New Feature Examples (v2.6.0)

### 6. [Advanced Features Example](advanced_features_example.py) 🚀 **ENTERPRISE**
**Complete enterprise features demonstration**
- 🌐 Web Analytics Dashboard
- 🔔 Multi-channel Notifications
- 💾 Automated Backup System
- 📋 Template Generation
- 🔗 Multi-Bot Management
- 📈 Event Collection

**Features:**
- Real-time analytics dashboard
- Email, Telegram, SMS notifications
- Automated backup scheduling
- Bot template generation
- Cross-bot synchronization
- Centralized event management

### 7. [Multi-Bot Analytics Example](multi_bot_analytics_example.py)
**Analytics dashboard setup**
- 📊 Network-wide performance tracking
- 📈 Real-time metrics
- 📋 Export capabilities
- 🔍 Detailed insights

**Features:**
- Multi-bot analytics collection
- Web dashboard interface
- Performance metrics
- Revenue tracking

### 8. [Multi-Bot Sync Example](multi_bot_sync_example.py)
**Bot synchronization**
- 🔄 Cross-bot data sync
- ⚡ Conflict resolution
- 📊 Unified analytics
- 🛡️ Secure synchronization

**Features:**
- Automated bot synchronization
- Conflict detection and resolution
- Centralized data management
- Secure sync protocols

### 9. [Webhook Server Example](webhook_server_example.py)
**Web interface setup**
- 🌐 RESTful API endpoints
- 📊 Web analytics interface
- 🔄 Sync management
- 🛡️ Security features

**Features:**
- Web-based management interface
- REST API for external integration
- Real-time monitoring
- Secure authentication

## Quick Start

### 1. Choose Your Library
Pick the example that matches your preferred bot library:

\`\`\`bash
# For Aiogram (Recommended)
pip install aiogram neonpay

# For Pyrogram
pip install pyrogram neonpay

# For pyTelegramBotAPI
pip install pyTelegramBotAPI neonpay

# For python-telegram-bot
pip install python-telegram-bot neonpay

# For Raw API
pip install aiohttp neonpay
\`\`\`

### 2. Configure Your Bot
Replace the placeholder values in each example:

\`\`\`python
# For all examples
BOT_TOKEN = "YOUR_BOT_TOKEN"  # Get from @BotFather

# For Pyrogram only
API_ID = 12345                # Get from my.telegram.org
API_HASH = "your_api_hash"    # Get from my.telegram.org
\`\`\`

### 3. Run the Example
\`\`\`bash
# Recommended: Aiogram example
python aiogram_example.py

# Or Pyrogram example
python pyrogram_example.py

# Or Telebot example
python telebot_example.py
\`\`\`

### 4. 🆕 Try New Features (v2.6.0)
\`\`\`bash
# Enterprise features demo
python advanced_features_example.py

# Analytics dashboard
python multi_bot_analytics_example.py

# Bot synchronization
python multi_bot_sync_example.py

# Web interface
python webhook_server_example.py
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

## Real-world Examples

All examples are based on **real working bots** and include:

- ❤️ **Donation System**: Support developer with 1⭐, 10⭐, 50⭐
- 🛒 **Digital Store**: Premium Access, Custom Theme, Priority Support
- 💫 **Telegram Stars**: Native payment processing
- 🎯 **Production Ready**: Error handling, logging, user management
- 🔄 **Auto-delivery**: Instant digital product delivery

## Example Comparison

| Library | Best For | Complexity | Features |
|---------|----------|------------|----------|
| **Aiogram** | Modern bots, FSM | Medium | ⭐⭐⭐⭐⭐ |
| **Pyrogram** | Advanced features | Medium | ⭐⭐⭐⭐⭐ |
| **Telebot** | Simple bots | Low | ⭐⭐⭐⭐ |
| **PTB** | Enterprise bots | High | ⭐⭐⭐⭐ |
| **Raw API** | Custom solutions | High | ⭐⭐⭐ |

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

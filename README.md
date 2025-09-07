# NEONPAY - Modern Telegram Stars Payment Library

[![PyPI version](https://img.shields.io/pypi/v/neonpay.svg)](https://pypi.org/project/neonpay/)
[![PyPI downloads](https://img.shields.io/pypi/dm/neonpay.svg)](https://pypi.org/project/neonpay/)
[![Python Support](https://img.shields.io/pypi/pyversions/neonpay.svg)](https://pypi.org/project/neonpay/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Build Status](https://github.com/Abbasxan/neonpay/workflows/CI/badge.svg)](https://github.com/Abbasxan/neonpay/actions)
[![Code Quality](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

**Current Version: [2.6.0](https://pypi.org/project/neonpay/2.6.0/) - Published on PyPI** 🚀

**NEONPAY** is a modern, universal payment processing library for Telegram bots that makes integrating Telegram Stars payments incredibly simple. With support for all major bot libraries and a clean, intuitive API, you can add payments to your bot in just a few lines of code.

## ✨ Features

### Core Payment Features
- 🚀 **Universal Support** - Works with Pyrogram, Aiogram, python-telegram-bot, pyTelegramBotAPI, and raw Bot API
- 💫 **Telegram Stars Integration** - Native support for Telegram's XTR currency
- 🎨 **Custom Payment Stages** - Create branded payment experiences with custom logos and descriptions
- 🔧 **Simple Setup** - Get started with just 2-3 lines of code
- 📱 **Modern Architecture** - Built with async/await and type hints
- 🛡️ **Error Handling** - Comprehensive error handling and validation
- 📦 **Zero Dependencies** - Only requires your chosen bot library

### 🆕 New in v2.6.0 - Enterprise Features
- 🌐 **Web Analytics Dashboard** - Real-time bot performance monitoring via web interface
- 🔄 **Web Sync Interface** - Multi-bot synchronization through REST API
- 📊 **Advanced Analytics** - Comprehensive payment analytics and reporting
- 🔔 **Notification System** - Multi-channel notifications (Email, Telegram, SMS, Webhook)
- 💾 **Backup & Restore** - Automated data protection and recovery
- 📋 **Template System** - Pre-built bot templates and generators
- 🔗 **Multi-Bot Analytics** - Network-wide performance tracking
- 📈 **Event Collection** - Centralized event management and processing

## 🚀 Quick Start

### Installation

```bash
# Install latest version from PyPI
pip install neonpay

# Or install specific version
pip install neonpay==2.5.0

# Install with optional dependencies
pip install neonpay[all]  # All bot libraries
pip install neonpay[ptb]   # python-telegram-bot only
pip install neonpay[aiogram]  # Aiogram only
```

**📦 Available on PyPI:** [neonpay 2.5.0](https://pypi.org/project/neonpay/2.5.0/)

### Basic Usage

```python
from neonpay import create_neonpay, PaymentStage

# Works with any bot library - automatic detection!
neonpay = create_neonpay(your_bot_instance)

# Create a payment stage
stage = PaymentStage(
    title="Premium Features",
    description="Unlock all premium features",
    price=100,  # 100 Telegram Stars
    photo_url="https://example.com/logo.png"
)

# Add the payment stage
neonpay.create_payment_stage("premium", stage)

# Send payment to user
await neonpay.send_payment(user_id=12345, stage_id="premium")

# Handle successful payments
@neonpay.on_payment
async def handle_payment(result):
    print(f"Payment received: {result.amount} stars from user {result.user_id}")
```

## 📚 Library Support

NEONPAY automatically detects your bot library and creates the appropriate adapter:

### Pyrogram

```python
from pyrogram import Client
from neonpay import create_neonpay

app = Client("my_bot", bot_token="YOUR_TOKEN")
neonpay = create_neonpay(app)
```

### Aiogram

```python
from aiogram import Bot, Dispatcher
from neonpay import create_neonpay

bot = Bot(token="YOUR_TOKEN")
dp = Dispatcher()
neonpay = create_neonpay(bot, dp)  # Pass dispatcher for aiogram
```

### python-telegram-bot

```python
from telegram.ext import Application
from neonpay import create_neonpay

application = Application.builder().token("YOUR_TOKEN").build()
neonpay = create_neonpay(application)
```

### pyTelegramBotAPI

```python
import telebot
from neonpay import create_neonpay

bot = telebot.TeleBot("YOUR_TOKEN")
neonpay = create_neonpay(bot)
```

### Raw Bot API

```python
from neonpay import RawAPIAdapter, NeonPayCore

adapter = RawAPIAdapter("YOUR_TOKEN", webhook_url="https://yoursite.com/webhook")
neonpay = NeonPayCore(adapter)
```

## 🎯 Advanced Usage

### Custom Payment Stages

```python
from neonpay import PaymentStage

# Create detailed payment stage
premium_stage = PaymentStage(
    title="Premium Subscription",
    description="Get access to exclusive features and priority support",
    price=500,  # 500 Telegram Stars
    label="Premium Plan",
    photo_url="https://yoursite.com/premium-logo.png",
    payload={"plan": "premium", "duration": "monthly"}
)

neonpay.create_payment_stage("premium_monthly", premium_stage)
```

### Payment Callbacks

```python
from neonpay import PaymentResult, PaymentStatus

@neonpay.on_payment
async def handle_payment(result: PaymentResult):
    if result.status == PaymentStatus.COMPLETED:
        # Grant premium access
        user_id = result.user_id
        amount = result.amount
        metadata = result.metadata
        
        print(f"User {user_id} paid {amount} stars")
        print(f"Plan: {metadata.get('plan')}")
        
        # Your business logic here
        await grant_premium_access(user_id, metadata.get('plan'))
```

### Multiple Payment Stages

```python
# Create multiple payment options
stages = {
    "basic": PaymentStage("Basic Plan", "Essential features", 100),
    "premium": PaymentStage("Premium Plan", "All features + support", 300),
    "enterprise": PaymentStage("Enterprise", "Custom solutions", 1000)
}

for stage_id, stage in stages.items():
    neonpay.create_payment_stage(stage_id, stage)

# Send different payments based on user choice
await neonpay.send_payment(user_id, "premium")
```

## 🔧 Configuration

### Error Handling

```python
from neonpay import NeonPayError, PaymentError

try:
    await neonpay.send_payment(user_id, "nonexistent_stage")
except PaymentError as e:
    print(f"Payment error: {e}")
except NeonPayError as e:
    print(f"NEONPAY error: {e}")
```

### Logging

```python
import logging

# Enable NEONPAY logging
logging.getLogger("neonpay").setLevel(logging.INFO)
```

## 🆕 New Features in v2.6.0

### Web Analytics Dashboard
```python
from neonpay import MultiBotAnalyticsManager, run_analytics_server

# Initialize analytics
analytics = MultiBotAnalyticsManager()

# Start web dashboard
await run_analytics_server(analytics, host="localhost", port=8081)
# Access dashboard at http://localhost:8081
```

### Notification System
```python
from neonpay import NotificationManager, NotificationConfig

# Configure notifications
config = NotificationConfig(
    telegram_bot_token="YOUR_ADMIN_BOT_TOKEN",
    telegram_admin_chat_id="YOUR_CHAT_ID"
)

notifications = NotificationManager(config)
await notifications.send_notification(message)
```

### Backup System
```python
from neonpay import BackupManager, BackupConfig

# Setup automated backups
backup_config = BackupConfig(
    backup_type=BackupType.JSON,
    schedule="daily"
)

backup_manager = BackupManager(backup_config)
await backup_manager.create_backup()
```

### Template System
```python
from neonpay import TemplateManager

# Generate bot from template
templates = TemplateManager()
await templates.generate_template("digital_store", output_file="my_bot.py")
```

### Multi-Bot Sync
```python
from neonpay import MultiBotSyncManager

# Sync multiple bots
sync_manager = MultiBotSyncManager()
await sync_manager.sync_bots([bot1, bot2, bot3])
```

## 📖 Documentation

- **[English Documentation](docs/en/README.md)** - Complete guide in English
- **[Russian Documentation](docs/ru/README.md)** - Полное руководство на русском
- **[Azerbaijani Documentation](docs/az/README.md)** - Azərbaycan dilində tam bələdçi

## 🤝 Examples

Check out the [examples](examples/) directory for complete working examples:

### Core Payment Examples
- [Pyrogram Bot Example](examples/pyrogram_example.py)
- [Aiogram Bot Example](examples/aiogram_example.py)
- [python-telegram-bot Example](examples/ptb_example.py)
- [pyTelegramBotAPI Example](examples/telebot_example.py)
- [Raw API Example](examples/raw_api_example.py)

### 🆕 New Feature Examples (v2.6.0)
- [Advanced Features Example](examples/advanced_features_example.py) - Complete enterprise features demo
- [Multi-Bot Analytics Example](examples/multi_bot_analytics_example.py) - Analytics dashboard setup
- [Multi-Bot Sync Example](examples/multi_bot_sync_example.py) - Bot synchronization
- [Webhook Server Example](examples/webhook_server_example.py) - Web interface setup

## 🛠️ Development Tools

The project includes automated scripts in `.github/scripts/`:

- **Cleanup**: `python .github/scripts/cleanup.py` - Remove cache files
- **Version Update**: `python .github/scripts/update_readme_version.py` - Update README version
- **PyPI Check**: `python .github/scripts/check_pypi_version.py` - Check PyPI version

## 🛠️ Requirements

- Python 3.9+
- One of the supported bot libraries:
  - `pyrogram>=2.0.106` for Pyrogram
  - `aiogram>=3.0.0` for Aiogram
  - `python-telegram-bot>=20.0` for python-telegram-bot
  - `pyTelegramBotAPI>=4.0.0` for pyTelegramBotAPI
  - `aiohttp>=3.8.0` for Raw API (optional)

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📞 Support

- **Telegram**: [@neonsahib](https://t.me/neonsahib)
- **Issues**: [GitHub Issues](https://github.com/Abbasxan/neonpay/issues)
- **Email**: sultanov.abas@outlook.com

## ⭐ Star History

If you find NEONPAY useful, please consider giving it a star on GitHub!

---

Made with ❤️ by [Abbas Sultanov](https://github.com/Abbasxan)

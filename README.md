# NEONPAY - Modern Telegram Stars Payment Library

[![PyPI version](https://badge.fury.io/py/neonpay.svg)](https://badge.fury.io/py/neonpay)
[![Python Support](https://img.shields.io/pypi/pyversions/neonpay.svg)](https://pypi.org/project/neonpay/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**NEONPAY** is a modern, universal payment processing library for Telegram bots that makes integrating Telegram Stars payments incredibly simple. With support for all major bot libraries and a clean, intuitive API, you can add payments to your bot in just a few lines of code.

## ✨ Features

- 🚀 **Universal Support** - Works with Pyrogram, Aiogram, python-telegram-bot, pyTelegramBotAPI, and raw Bot API
- 💫 **Telegram Stars Integration** - Native support for Telegram's XTR currency
- 🎨 **Custom Payment Stages** - Create branded payment experiences with custom logos and descriptions
- 🔧 **Simple Setup** - Get started with just 2-3 lines of code
- 📱 **Modern Architecture** - Built with async/await and type hints
- 🛡️ **Error Handling** - Comprehensive error handling and validation
- 📦 **Zero Dependencies** - Only requires your chosen bot library

## 🚀 Quick Start

### Installation

```bash
pip install neonpay
```

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

## 📖 Documentation

- **[English Documentation](docs/en/README.md)** - Complete guide in English
- **[Russian Documentation](docs/ru/README.md)** - Полное руководство на русском
- **[Azerbaijani Documentation](docs/az/README.md)** - Azərbaycan dilində tam bələdçi

## 🤝 Examples

Check out the [examples](examples/) directory for complete working examples:

- [Pyrogram Bot Example](examples/pyrogram_example.py)
- [Aiogram Bot Example](examples/aiogram_example.py)
- [python-telegram-bot Example](examples/ptb_example.py)
- [pyTelegramBotAPI Example](examples/telebot_example.py)
- [Raw API Example](examples/raw_api_example.py)

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

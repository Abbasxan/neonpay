# NeonPay Library Structure Documentation

## Project Structure

```
neonpay/
├── neonpay/                    # Core Library
│   ├── __init__.py            # Main exports and lazy loading
│   ├── _version.py            # Version info (2.2.0)
│   ├── core.py                # Core classes and logic
│   ├── factory.py             # Auto-detection factory
│   ├── errors.py              # Exception system
│   ├── payments.py            # Legacy NeonStars class
│   ├── webhooks.py            # Webhook processing
│   ├── middleware.py          # Framework middleware
│   ├── utils.py               # Helper utilities
│   ├── py.typed               # Type hints marker
│   └── adapters/              # Bot library adapters
│       ├── base.py            # Base adapter class
│       ├── aiogram_adapter.py # Aiogram 3.x support
│       ├── pyrogram_adapter.py# Pyrogram 2.x support
│       ├── ptb_adapter.py     # python-telegram-bot 20.x
│       ├── telebot_adapter.py # pyTelegramBotAPI 4.x
│       └── raw_api_adapter.py # Direct API access
├── examples/                   # Usage Examples
├── tests/                      # Test Suite
├── setup.py                   # Classic setup
├── pyproject.toml             # Modern config
└── README.md                  # Documentation
```

## Quick Start Guide

### 1. Basic Import Pattern

```python
# Recommended: Factory approach (auto-detection)
from neonpay.factory import create_neonpay
from neonpay.core import PaymentStage, PaymentStatus

# Alternative: Direct imports
from neonpay import NeonPayCore, PaymentStage, PaymentResult
from neonpay import AiogramAdapter  # Lazy loaded
```

### 2. Initialization Methods

#### Method A: Factory (Recommended)
```python
# Auto-detects bot library and creates appropriate adapter
neonpay = create_neonpay(bot_instance=bot, dispatcher=dp)
```

#### Method B: Manual Adapter
```python
from neonpay import AiogramAdapter, NeonPayCore

adapter = AiogramAdapter(bot, dispatcher)
neonpay = NeonPayCore(adapter)
```

## Core Classes Reference

### NeonPayCore
**Location:** `neonpay/core.py`  
**Import:** `from neonpay import NeonPayCore`

Main payment processor class that handles all payment operations.

**Key Methods:**
- `create_payment_stage(stage_id, stage)` - Create payment configuration
- `send_payment(user_id, stage_id)` - Send invoice to user
- `on_payment(callback)` - Register payment completion handler
- `setup()` - Initialize payment system

### PaymentStage
**Location:** `neonpay/core.py`  
**Import:** `from neonpay import PaymentStage`

Payment configuration with validation.

**Required Fields:**
- `title: str` - Payment title (max 32 chars)
- `description: str` - Payment description (max 255 chars)  
- `price: int` - Price in Telegram Stars (1-2500)

**Optional Fields:**
- `label: str` - Button label (default: "Payment")
- `photo_url: str` - Payment image URL
- `payload: dict` - Custom data (max 1024 bytes)

### PaymentResult
**Location:** `neonpay/core.py`  
**Import:** `from neonpay import PaymentResult`

Payment completion result with user and transaction data.

### PaymentStatus
**Location:** `neonpay/core.py`  
**Import:** `from neonpay import PaymentStatus`

Payment status enumeration: `PENDING`, `COMPLETED`, `CANCELLED`, `FAILED`, `REFUNDED`

## Adapter System

### Supported Bot Libraries

| Library | Adapter Class | Import Path | Required Params |
|---------|---------------|-------------|-----------------|
| **Aiogram 3.x** | `AiogramAdapter` | `from neonpay import AiogramAdapter` | `bot, dispatcher` |
| **Pyrogram 2.x** | `PyrogramAdapter` | `from neonpay import PyrogramAdapter` | `client` |
| **python-telegram-bot 20.x** | `PythonTelegramBotAdapter` | `from neonpay import PythonTelegramBotAdapter` | `bot, application` |
| **pyTelegramBotAPI 4.x** | `TelebotAdapter` | `from neonpay import TelebotAdapter` | `bot` |
| **Raw API** | `RawAPIAdapter` | `from neonpay import RawAPIAdapter` | `bot_token` |

### Adapter Usage Examples

#### Aiogram 3.x
```python
from aiogram import Bot, Dispatcher
from neonpay.factory import create_neonpay

bot = Bot(token="YOUR_TOKEN")
dp = Dispatcher()

# Factory method (recommended)
neonpay = create_neonpay(bot_instance=bot, dispatcher=dp)

# Manual method
from neonpay import AiogramAdapter, NeonPayCore
adapter = AiogramAdapter(bot, dp)
neonpay = NeonPayCore(adapter)
```

#### Pyrogram 2.x
```python
from pyrogram import Client
from neonpay.factory import create_neonpay

app = Client("my_bot", bot_token="YOUR_TOKEN")
neonpay = create_neonpay(bot_instance=app)
```

## Complete Usage Pattern

### 1. Setup Payment Stages
```python
# Create payment configurations
neonpay.create_payment_stage(
    "donate_1", 
    PaymentStage(
        title="Support 1 Star",
        description="Help with server costs",
        price=1
    )
)

neonpay.create_payment_stage(
    "donate_10",
    PaymentStage(
        title="Support 10 Stars", 
        description="Support new features",
        price=10
    )
)
```

### 2. Register Payment Handler
```python
@neonpay.on_payment
async def handle_payment(result: PaymentResult):
    if result.status == PaymentStatus.COMPLETED:
        await bot.send_message(
            result.user_id,
            f"Thank you! Payment: {result.amount} Stars"
        )
```

### 3. Send Payment Invoice
```python
# In your command handler
@router.message(Command("donate"))
async def donate_cmd(message: types.Message):
    # Send payment invoice
    await neonpay.send_payment(
        user_id=message.from_user.id,
        stage_id="donate_1"
    )
```

## Advanced Features

### Error Handling
```python
from neonpay import PaymentError, ConfigurationError, ValidationError

try:
    await neonpay.send_payment(user_id, "invalid_stage")
except PaymentError as e:
    logger.error(f"Payment failed: {e}")
except ValidationError as e:
    logger.error(f"Invalid data: {e}")
```

### Custom Configuration
```python
neonpay = create_neonpay(
    bot_instance=bot,
    dispatcher=dp,
    thank_you_message="Custom thank you!",
    enable_logging=True,
    max_stages=50
)
```

### Payment Statistics
```python
stats = neonpay.get_stats()
print(f"Total stages: {stats['total_stages']}")
print(f"Callbacks: {stats['registered_callbacks']}")
```

## Best Practices

### Do's
- Use factory method `create_neonpay()` for automatic detection
- Validate payment data before creating stages
- Handle payment callbacks with try-catch blocks
- Use descriptive stage IDs and titles
- Enable logging for production debugging

### Don'ts  
- Don't create stages with duplicate IDs
- Don't exceed 2500 Stars per payment
- Don't forget to register payment handlers
- Don't use invalid URLs for photo_url
- Don't exceed payload size limits (1024 bytes)

## Debugging Tips

### Enable Detailed Logging
```python
import logging
logging.basicConfig(level=logging.INFO)

neonpay = create_neonpay(bot_instance=bot, enable_logging=True)
```

### Check System Status
```python
# Verify setup
stats = neonpay.get_stats()
print(f"Setup complete: {stats['setup_complete']}")

# List all stages
stages = neonpay.list_payment_stages()
for stage_id, stage in stages.items():
    print(f"{stage_id}: {stage.price} Stars")
```

### Common Issues
1. **Import Error**: Install required dependencies `pip install neonpay[aiogram]`
2. **Adapter Error**: Check bot instance type and required parameters
3. **Payment Failed**: Verify stage exists and user_id is valid
4. **Validation Error**: Check PaymentStage field limits and formats

## Version Information

**Current Version:** 2.2.0  
**Author:** Abbas Sultanov  
**Email:** sultanov.abas@outlook.com

For more examples, check the `/examples` directory in the repository.

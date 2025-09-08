# NEONPAY - Современная библиотека платежей Telegram Stars

[![PyPI version](https://img.shields.io/pypi/v/neonpay.svg)](https://pypi.org/project/neonpay/)
[![PyPI downloads](https://img.shields.io/pypi/dm/neonpay.svg)](https://pypi.org/project/neonpay/)
[![Python Support](https://img.shields.io/pypi/pyversions/neonpay.svg)](https://pypi.org/project/neonpay/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**NEONPAY** — это современная, универсальная библиотека обработки платежей для Telegram ботов, которая делает интеграцию платежей Telegram Stars невероятно простой. С поддержкой всех основных библиотек ботов и чистым, интуитивным API, вы можете добавить платежи в свой бот всего несколькими строками кода.

## ✨ Возможности

- 🚀 **Универсальная поддержка** - Работает с Pyrogram, Aiogram, python-telegram-bot, pyTelegramBotAPI и raw Bot API
- 💫 **Интеграция Telegram Stars** - Нативная поддержка валюты XTR от Telegram
- 🎨 **Пользовательские этапы платежей** - Создавайте брендовые платежные процессы с пользовательскими логотипами и описаниями
- 🔧 **Простая настройка** - Начните всего с 2-3 строк кода
- 📱 **Современная архитектура** - Построена с async/await и type hints
- 🛡️ **Обработка ошибок** - Комплексная обработка ошибок и валидация
- 📦 **Нулевые зависимости** - Требует только выбранную вами библиотеку ботов

## 🚀 Быстрый старт

### Установка

```bash
# Установите последнюю версию с PyPI
pip install neonpay

# Или установите конкретную версию
pip install neonpay==2.5.0

# Установите с дополнительными зависимостями
pip install neonpay[all]  # Все библиотеки ботов
pip install neonpay[ptb]   # только python-telegram-bot
pip install neonpay[aiogram]  # только Aiogram
```

### Базовое использование

```python
from neonpay import create_neonpay, PaymentStage

# Работает с любой библиотекой ботов - автоматическое определение!
neonpay = create_neonpay(your_bot_instance)

# Создайте этап платежа
stage = PaymentStage(
    title="Премиум функции",
    description="Разблокируйте все премиум функции",
    price=100,  # 100 Telegram Stars
    photo_url="https://example.com/logo.png"
)

# Добавьте этап платежа
neonpay.create_payment_stage("premium", stage)

# Отправьте платеж пользователю
await neonpay.send_payment(user_id=12345, stage_id="premium")

# Обрабатывайте успешные платежи
@neonpay.on_payment
async def handle_payment(result):
    print(f"Платеж получен: {result.amount} stars от пользователя {result.user_id}")
```

## 📚 Поддержка библиотек

NEONPAY автоматически определяет вашу библиотеку ботов и создает соответствующий адаптер:

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
neonpay = create_neonpay(bot, dp)  # Передайте диспетчер для aiogram
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

## 🎯 Продвинутое использование

### Пользовательские этапы платежей

```python
from neonpay import PaymentStage

# Создайте детальный этап платежа
premium_stage = PaymentStage(
    title="Премиум подписка",
    description="Получите доступ к эксклюзивным функциям и приоритетной поддержке",
    price=500,  # 500 Telegram Stars
    label="Премиум план",
    photo_url="https://yoursite.com/premium-logo.png",
    payload={"plan": "premium", "duration": "monthly"}
)

neonpay.create_payment_stage("premium_monthly", premium_stage)
```

### Callback'и платежей

```python
from neonpay import PaymentResult, PaymentStatus

@neonpay.on_payment
async def handle_payment(result: PaymentResult):
    if result.status == PaymentStatus.COMPLETED:
        # Предоставьте премиум доступ
        user_id = result.user_id
        amount = result.amount
        metadata = result.metadata
        
        print(f"Пользователь {user_id} заплатил {amount} stars")
        print(f"План: {metadata.get('plan')}")
        
        # Ваша бизнес-логика здесь
        await grant_premium_access(user_id, metadata.get('plan'))
```

### Множественные этапы платежей

```python
# Создайте несколько вариантов платежей
stages = {
    "basic": PaymentStage("Базовый план", "Основные функции", 100),
    "premium": PaymentStage("Премиум план", "Все функции + поддержка", 300),
    "enterprise": PaymentStage("Корпоративный", "Пользовательские решения", 1000)
}

for stage_id, stage in stages.items():
    neonpay.create_payment_stage(stage_id, stage)

# Отправляйте разные платежи на основе выбора пользователя
await neonpay.send_payment(user_id, "premium")
```

## 🔧 Конфигурация

### Обработка ошибок

```python
from neonpay import NeonPayError, PaymentError

try:
    await neonpay.send_payment(user_id, "nonexistent_stage")
except PaymentError as e:
    print(f"Ошибка платежа: {e}")
except NeonPayError as e:
    print(f"Ошибка NEONPAY: {e}")
```

### Логирование

```python
import logging

# Включите логирование NEONPAY
logging.getLogger("neonpay").setLevel(logging.INFO)
```

## 📖 Документация

- **[Английская документация](en/README.md)** - Полное руководство на английском
- **[Русская документация](ru/README.md)** - Полное руководство на русском
- **[Азербайджанская документация](az/README.md)** - Полное руководство на азербайджанском

## 🤝 Примеры

Посмотрите папку [examples](../examples/) для полных рабочих примеров:

- [Пример бота Pyrogram](../examples/pyrogram_example.py)
- [Пример бота Aiogram](../examples/aiogram_example.py)
- [Пример python-telegram-bot](../examples/ptb_example.py)
- [Пример pyTelegramBotAPI](../examples/telebot_example.py)
- [Пример Raw API](../examples/raw_api_example.py)

## 🛠️ Требования

- Python 3.9+
- Одна из поддерживаемых библиотек ботов:
  - `pyrogram>=2.0.106` для Pyrogram
  - `aiogram>=3.0.0` для Aiogram
  - `python-telegram-bot>=20.0` для python-telegram-bot
  - `pyTelegramBotAPI>=4.0.0` для pyTelegramBotAPI
  - `aiohttp>=3.8.0` для Raw API (опционально)

## 📄 Лицензия

Этот проект лицензирован под лицензией MIT - подробности см. в файле [LICENSE](../../LICENSE).

## 🤝 Вклад в проект

Вклад в проект приветствуется! Пожалуйста, не стесняйтесь отправлять Pull Request.

## 📞 Поддержка

- **Telegram**: [@neonsahib](https://t.me/neonsahib)
- **Issues**: [GitHub Issues](https://github.com/Abbasxan/neonpay/issues)
- **Email**: sultanov.abas@outlook.com

## ⭐ История звезд

Если вы считаете NEONPAY полезным, пожалуйста, рассмотрите возможность поставить звезду на GitHub!

---

Сделано с ❤️ [Abbas Sultanov](https://github.com/Abbasxan)


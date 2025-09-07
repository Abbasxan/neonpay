# NEONPAY - Modern Telegram Stars Payment Library

[![PyPI version](https://img.shields.io/pypi/v/neonpay.svg)](https://pypi.org/project/neonpay/)
[![PyPI downloads](https://img.shields.io/pypi/dm/neonpay.svg)](https://pypi.org/project/neonpay/)
[![Python Support](https://img.shields.io/pypi/pyversions/neonpay.svg)](https://pypi.org/project/neonpay/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**NEONPAY** Telegram botları üçün müasir, universal ödəniş emalı kitabxanasıdır ki, Telegram Stars ödənişlərini inteqrasiya etməyi inanılmaz dərəcədə sadə edir. Bütün əsas bot kitabxanalarına dəstək və təmiz, intuitiv API ilə ödənişləri botunuza yalnız bir neçə sətir kodla əlavə edə bilərsiniz.

## ✨ Xüsusiyyətlər

- 🚀 **Universal Dəstək** - Pyrogram, Aiogram, python-telegram-bot, pyTelegramBotAPI və raw Bot API ilə işləyir
- 💫 **Telegram Stars İnteqrasiyası** - Telegram-ın XTR valyutasına native dəstək
- 🎨 **Fərdi Ödəniş Mərhələləri** - Fərdi logolar və təsvirlərlə brend ödəniş təcrübələri yaradın
- 🔧 **Sadə Quraşdırma** - Yalnız 2-3 sətir kodla başlayın
- 📱 **Müasir Arxitektura** - async/await və type hints ilə qurulmuş
- 🛡️ **Xəta İdarəetməsi** - Hərtərəfli xəta idarəetməsi və validasiya
- 📦 **Sıfır Asılılıqlar** - Yalnız seçdiyiniz bot kitabxanasını tələb edir

## 🚀 Sürətli Başlanğıc

### Quraşdırma

```bash
# PyPI-dən ən son versiyanı quraşdırın
pip install neonpay

# Və ya müəyyən versiyanı quraşdırın
pip install neonpay==2.5.0

# İsteğe bağlı asılılıqlarla quraşdırın
pip install neonpay[all]  # Bütün bot kitabxanaları
pip install neonpay[ptb]   # yalnız python-telegram-bot
pip install neonpay[aiogram]  # yalnız Aiogram
```

### Əsas İstifadə

```python
from neonpay import create_neonpay, PaymentStage

# Hər hansı bot kitabxanası ilə işləyir - avtomatik aşkarlama!
neonpay = create_neonpay(your_bot_instance)

# Ödəniş mərhələsi yaradın
stage = PaymentStage(
    title="Premium Xüsusiyyətlər",
    description="Bütün premium xüsusiyyətləri açın",
    price=100,  # 100 Telegram Stars
    photo_url="https://example.com/logo.png"
)

# Ödəniş mərhələsini əlavə edin
neonpay.create_payment_stage("premium", stage)

# İstifadəçiyə ödəniş göndərin
await neonpay.send_payment(user_id=12345, stage_id="premium")

# Uğurlu ödənişləri idarə edin
@neonpay.on_payment
async def handle_payment(result):
    print(f"Ödəniş alındı: {result.amount} stars istifadəçidən {result.user_id}")
```

## 📚 Kitabxana Dəstəyi

NEONPAY avtomatik olaraq bot kitabxananızı aşkar edir və uyğun adapter yaradır:

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
neonpay = create_neonpay(bot, dp)  # Aiogram üçün dispatcher keçin
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

## 🎯 Təkmilləşdirilmiş İstifadə

### Fərdi Ödəniş Mərhələləri

```python
from neonpay import PaymentStage

# Ətraflı ödəniş mərhələsi yaradın
premium_stage = PaymentStage(
    title="Premium Abunə",
    description="Ekskluziv xüsusiyyətlərə və prioritet dəstəyə giriş əldə edin",
    price=500,  # 500 Telegram Stars
    label="Premium Plan",
    photo_url="https://yoursite.com/premium-logo.png",
    payload={"plan": "premium", "duration": "monthly"}
)

neonpay.create_payment_stage("premium_monthly", premium_stage)
```

### Ödəniş Callback-ləri

```python
from neonpay import PaymentResult, PaymentStatus

@neonpay.on_payment
async def handle_payment(result: PaymentResult):
    if result.status == PaymentStatus.COMPLETED:
        # Premium girişi verin
        user_id = result.user_id
        amount = result.amount
        metadata = result.metadata
        
        print(f"İstifadəçi {user_id} {amount} stars ödədi")
        print(f"Plan: {metadata.get('plan')}")
        
        # Burada biznes məntiqiniz
        await grant_premium_access(user_id, metadata.get('plan'))
```

### Çoxlu Ödəniş Mərhələləri

```python
# Çoxlu ödəniş seçimləri yaradın
stages = {
    "basic": PaymentStage("Əsas Plan", "Əsas xüsusiyyətlər", 100),
    "premium": PaymentStage("Premium Plan", "Bütün xüsusiyyətlər + dəstək", 300),
    "enterprise": PaymentStage("Enterprise", "Fərdi həllər", 1000)
}

for stage_id, stage in stages.items():
    neonpay.create_payment_stage(stage_id, stage)

# İstifadəçi seçiminə əsasən müxtəlif ödənişlər göndərin
await neonpay.send_payment(user_id, "premium")
```

## 🔧 Konfiqurasiya

### Xəta İdarəetməsi

```python
from neonpay import NeonPayError, PaymentError

try:
    await neonpay.send_payment(user_id, "nonexistent_stage")
except PaymentError as e:
    print(f"Ödəniş xətası: {e}")
except NeonPayError as e:
    print(f"NEONPAY xətası: {e}")
```

### Logging

```python
import logging

# NEONPAY logging-i aktivləşdirin
logging.getLogger("neonpay").setLevel(logging.INFO)
```

## 📖 Sənədləşmə

- **[İngilis Sənədləşməsi](en/README.md)** - İngilis dilində tam bələdçi
- **[Rus Sənədləşməsi](ru/README.md)** - Rus dilində tam bələdçi
- **[Azərbaycan Sənədləşməsi](az/README.md)** - Azərbaycan dilində tam bələdçi

## 🤝 Nümunələr

Tam işləyən nümunələr üçün [examples](../examples/) qovluğuna baxın:

- [Pyrogram Bot Nümunəsi](../examples/pyrogram_example.py)
- [Aiogram Bot Nümunəsi](../examples/aiogram_example.py)
- [python-telegram-bot Nümunəsi](../examples/ptb_example.py)
- [pyTelegramBotAPI Nümunəsi](../examples/telebot_example.py)
- [Raw API Nümunəsi](../examples/raw_api_example.py)

## 🛠️ Tələblər

- Python 3.9+
- Dəstəklənən bot kitabxanalarından biri:
  - `pyrogram>=2.0.106` Pyrogram üçün
  - `aiogram>=3.0.0` Aiogram üçün
  - `python-telegram-bot>=20.0` python-telegram-bot üçün
  - `pyTelegramBotAPI>=4.0.0` pyTelegramBotAPI üçün
  - `aiohttp>=3.8.0` Raw API üçün (isteğe bağlı)

## 📄 Lisenziya

Bu layihə MIT Lisenziyası altında lisenziyalaşdırılmışdır - ətraflı məlumat üçün [LICENSE](../../LICENSE) faylına baxın.

## 🤝 Töhfə Vermə

Töhfələr xoş gəlinir! Zəhmət olmasa Pull Request göndərməkdən çəkinməyin.

## 📞 Dəstək

- **Telegram**: [@neonsahib](https://t.me/neonsahib)
- **Issues**: [GitHub Issues](https://github.com/Abbasxan/neonpay/issues)
- **Email**: sultanov.abas@outlook.com

## ⭐ Star Tarixi

Əgər NEONPAY-i faydalı hesab edirsinizsə, zəhmət olmasa GitHub-da ona star verin!

---

[Abbas Sultanov](https://github.com/Abbasxan) tərəfindən ❤️ ilə hazırlanmışdır


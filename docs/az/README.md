# NEONPAY Sənədləri (Azərbaycan)

NEONPAY-ın tam sənədlərinə xoş gəlmisiniz. Bu bələdçi sizə Telegram Stars ödənişlərini botunuza tez və səmərəli şəkildə inteqrasiya etməyə kömək edəcək.

## Mündəricat

1. [Quraşdırma](#quraşdırma)
2. [Sürətli başlanğıc](#sürətli-başlanğıc)
3. [Kitabxana dəstəyi](#kitabxana-dəstəyi)
4. [Əsas konsepsiyalar](#əsas-konsepsiyalar)
5. [API arayışı](#api-arayışı)
6. [Həqiqi nümunələr](#həqiqi-nümunələr)
7. [Ən yaxşı təcrübələr](#ən-yaxşı-təcrübələr)
8. [İstehsal yerləşdirilməsi](#istehsal-yerləşdirilməsi)
9. [Problem həlli](#problem-həlli)
10. [Dəstək](#dəstək)

## Quraşdırma

NEONPAY-ı pip ilə quraşdırın:

\`\`\`bash
pip install neonpay
\`\`\`

Xüsusi bot kitabxanaları üçün lazımi asılılıqları quraşdırın:

\`\`\`bash
# Pyrogram üçün
pip install neonpay pyrogram

# Aiogram üçün
pip install neonpay aiogram

# python-telegram-bot üçün
pip install neonpay python-telegram-bot

# pyTelegramBotAPI üçün
pip install neonpay pyTelegramBotAPI
\`\`\`

## Sürətli başlanğıc

### 1. İmport və inisializasiya

\`\`\`python
from neonpay import create_neonpay, PaymentStage

# Avtomatik adapter aşkarlanması
neonpay = create_neonpay(sizin_bot_nümunəniz)
\`\`\`

### 2. Ödəniş mərhələsi yaradın

\`\`\`python
stage = PaymentStage(
    title="Premium giriş",
    description="Premium funksiyaları açın",
    price=100,  # 100 Telegram Stars
    photo_url="https://example.com/logo.png"
)

neonpay.create_payment_stage("premium", stage)
\`\`\`

### 3. Ödəniş göndərin

\`\`\`python
await neonpay.send_payment(user_id=12345, stage_id="premium")
\`\`\`

### 4. Ödənişləri idarə edin

\`\`\`python
@neonpay.on_payment
async def handle_payment(result):
    print(f"İstifadəçi {result.user_id}-dən {result.amount} ulduz alındı")
\`\`\`

## Kitabxana dəstəyi

### Pyrogram inteqrasiyası

\`\`\`python
from pyrogram import Client
from neonpay import create_neonpay

app = Client("my_bot", bot_token="SİZİN_TOKENİNİZ")
neonpay = create_neonpay(app)

@app.on_message()
async def handle_message(client, message):
    if message.text == "/al":
        await neonpay.send_payment(message.from_user.id, "premium")

app.run()
\`\`\`

### Aiogram inteqrasiyası

\`\`\`python
from aiogram import Bot, Dispatcher, Router
from neonpay import create_neonpay

bot = Bot(token="SİZİN_TOKENİNİZ")
dp = Dispatcher()
router = Router()

neonpay = create_neonpay(bot)

@router.message(Command("al"))
async def buy_handler(message: Message):
    await neonpay.send_payment(message.from_user.id, "premium")

dp.include_router(router)
\`\`\`

## Əsas konsepsiyalar

### Ödəniş mərhələləri

Ödəniş mərhələləri istifadəçilərin nə aldığını müəyyən edir:

\`\`\`python
stage = PaymentStage(
    title="Məhsul adı",              # Məcburi: göstərilən ad
    description="Məhsul təfərrüatı", # Məcburi: təsvir
    price=100,                      # Məcburi: ulduzlarla qiymət
    label="İndi al",                # İstəyə bağlı: düymə etiketi
    photo_url="https://...",        # İstəyə bağlı: məhsul şəkli
    payload={"custom": "data"},     # İstəyə bağlı: xüsusi məlumat
    start_parameter="ref_code"      # İstəyə bağlı: dərin əlaqə parametri
)
\`\`\`

### Ödəniş nəticələri

Ödənişlər tamamlandıqda `PaymentResult` alırsınız:

\`\`\`python
@neonpay.on_payment
async def handle_payment(result: PaymentResult):
    print(f"İstifadəçi ID: {result.user_id}")
    print(f"Məbləğ: {result.amount}")
    print(f"Valyuta: {result.currency}")
    print(f"Status: {result.status}")
    print(f"Metadata: {result.metadata}")
\`\`\`

### Xəta idarəetməsi

\`\`\`python
from neonpay import NeonPayError, PaymentError

try:
    await neonpay.send_payment(user_id, "stage_id")
except PaymentError as e:
    print(f"Ödəniş xətası: {e}")
except NeonPayError as e:
    print(f"Sistem xətası: {e}")
\`\`\`

## API arayışı

### NeonPayCore sinfi

#### Metodlar

- `create_payment_stage(stage_id: str, stage: PaymentStage)` - Ödəniş mərhələsi yarat
- `get_payment_stage(stage_id: str)` - ID ilə ödəniş mərhələsini al
- `list_payment_stages()` - Bütün ödəniş mərhələlərini al
- `remove_payment_stage(stage_id: str)` - Ödəniş mərhələsini sil
- `send_payment(user_id: int, stage_id: str)` - Ödəniş hesabı göndər
- `on_payment(callback)` - Ödəniş callback-ini qeydiyyatdan keçir
- `get_stats()` - Sistem statistikasını al

### PaymentStage sinfi

#### Parametrlər

- `title: str` - Ödəniş başlığı (məcburi)
- `description: str` - Ödəniş təsviri (məcburi)
- `price: int` - Telegram Stars-da qiymət (məcburi)
- `label: str` - Düymə etiketi (standart: "Payment")
- `photo_url: str` - Məhsul şəkli URL-i (istəyə bağlı)
- `payload: dict` - Xüsusi məlumat (istəyə bağlı)
- `start_parameter: str` - Dərin əlaqə parametri (istəyə bağlı)

## Nümunələr

### E-ticarət botu

\`\`\`python
from neonpay import create_neonpay, PaymentStage

# Məhsul kataloqu
products = {
    "coffee": PaymentStage("Qəhvə", "Premium qəhvə dənələri", 50),
    "tea": PaymentStage("Çay", "Üzvi çay yarpaqları", 30),
    "cake": PaymentStage("Tort", "Dadlı şokolad tortu", 100)
}

neonpay = create_neonpay(bot)

# Bütün məhsulları əlavə et
for product_id, stage in products.items():
    neonpay.create_payment_stage(product_id, stage)

# Sifarişləri emal et
@neonpay.on_payment
async def process_order(result):
    user_id = result.user_id
    product = result.metadata.get("product")
    
    # Sifarişi emal et
    await fulfill_order(user_id, product)
    await bot.send_message(user_id, "Sifariş təsdiqləndi! Təşəkkür edirik!")
\`\`\`

### Abunəlik xidməti

\`\`\`python
subscription_plans = {
    "monthly": PaymentStage(
        "Aylıq plan", 
        "1 ay premium giriş", 
        100,
        payload={"duration": 30}
    ),
    "yearly": PaymentStage(
        "İllik plan", 
        "12 ay premium giriş (2 ay pulsuz!)", 
        1000,
        payload={"duration": 365}
    )
}

@neonpay.on_payment
async def handle_subscription(result):
    user_id = result.user_id
    duration = result.metadata.get("duration", 30)
    
    # Abunəlik ver
    await grant_premium(user_id, days=duration)
\`\`\`

## Ən yaxşı təcrübələr

### 1. Ödəniş məlumatlarını yoxlayın

\`\`\`python
@neonpay.on_payment
async def handle_payment(result):
    # Ödəniş məbləğini yoxla
    expected_amount = get_expected_amount(result.metadata)
    if result.amount != expected_amount:
        logger.warning(f"Məbləğ uyğunsuzluğu: gözlənilən {expected_amount}, alınan {result.amount}")
        return
    
    # Ödənişi emal et
    await process_payment(result)
\`\`\`

### 2. Xətaları düzgün idarə edin

\`\`\`python
async def safe_send_payment(user_id, stage_id):
    try:
        await neonpay.send_payment(user_id, stage_id)
    except PaymentError as e:
        await bot.send_message(user_id, f"Ödəniş xətası: {e}")
    except Exception as e:
        logger.error(f"Gözlənilməz xəta: {e}")
        await bot.send_message(user_id, "Nəsə səhv getdi. Yenidən cəhd edin.")
\`\`\`

## Problem həlli

### Ümumi problemlər

#### 1. "Payment stage not found"

\`\`\`python
# Mərhələnin mövcudluğunu yoxla
stage = neonpay.get_payment_stage("my_stage")
if not stage:
    print("Mərhələ mövcud deyil!")
    
# Bütün mərhələlərin siyahısı
stages = neonpay.list_payment_stages()
print(f"Mövcud mərhələlər: {list(stages.keys())}")
\`\`\`

#### 2. "Failed to send invoice"

- Bot tokeninin düzgünlüyünü yoxlayın
- İstifadəçinin botu başlatdığından əmin olun
- İstifadəçi ID-sinin etibarlılığını yoxlayın
- Ödəniş mərhələsi konfiqurasiyasını yoxlayın

### Debug rejimi

\`\`\`python
import logging

# Debug loqlaşdırmasını aktiv et
logging.basicConfig(level=logging.DEBUG)
logging.getLogger("neonpay").setLevel(logging.DEBUG)
\`\`\`

### Kömək almaq

Kömək lazımdırsa:

1. [examples](../../examples/) qovluğunu yoxlayın
2. [FAQ](FAQ.md)-ı oxuyun
3. [GitHub](https://github.com/Abbasxan/neonpay/issues)-da issue yaradın
4. Dəstəklə əlaqə saxlayın: [@neonsahib](https://t.me/neonsahib)

---

[← Əsas README-yə qayıt](../../README.md) | [English Documentation →](../en/README.md)

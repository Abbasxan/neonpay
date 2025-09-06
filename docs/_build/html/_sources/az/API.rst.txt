# NEONPAY API Arayışı

## Ümumi Baxış

NEONPAY Telegram Stars vasitəsilə ödənişləri botlarınıza inteqrasiya etmək üçün sadə və güclü API təqdim edir. API bütün məşhur Telegram bot kitabxanalarını dəstəkləyir.

## Əsas Siniflər

### NeonPayCore

Ödənişləri idarə etmək üçün əsas sinif.


python
```
from neonpay import NeonPayCore
```
# İnisializasiya
```
neonpay = NeonPayCore(bot_instance)
```

#### Metodlar
```
create_payment_stage(name, price, description=None, logo_url=None)
```
Göstərilən parametrlərlə ödəniş mərhələsi yaradır.

**Parametrlər:**
- `name` (str): Məhsul/xidmətin adı
- `price` (int): Telegram Stars-da qiymət
- `description` (str, optional): Məhsulun təsviri
- `logo_url` (str, optional): Loqo URL-i

**Qaytarır:** `PaymentStage`

**Nümunə:**
python
```
stage = neonpay.create_payment_stage(
    name="Premium abunəlik",
    price=100,
    description="Bir ay premium funksiyalara giriş",
    logo_url="https://example.com/logo.png"
)
```

##### 
```
send_invoice(chat_id, payment_stage)
```

İstifadəçiyə faktura göndərir.

**Parametrlər:**
- `chat_id` (int): İstifadəçi çat ID-si
- `payment_stage` (PaymentStage): Ödəniş mərhələsi

**Qaytarır:** `PaymentResult`

**Nümunə:**
python
```
result = await neonpay.send_invoice(user_id, stage)
if result.success:
    print("Faktura uğurla göndərildi")
```

#####
```
handle_successful_payment(payment_data)
```

Uğurlu ödənişi işləyir.

**Parametrlər:**
- `payment_data`: Telegram-dan ödəniş məlumatları

**Qaytarır:** `PaymentResult`

##### `refund_payment(payment_id, reason=None)`

Ödənişi geri qaytarır (dəstəklənərsə).

**Parametrlər:**
- `payment_id` (str): Ödəniş ID-si
- `reason` (str, optional): Geri qaytarma səbəbi

**Qaytarır:** `PaymentResult`

### PaymentStage

Ödəniş mərhələsini təmsil edən sinif.

**Atributlar:**
- `name` (str): Məhsulun adı
- `price` (int): Stars-da qiymət
- `description` (str): Təsvir
- `logo_url` (str): Loqo URL-i
- `created_at` (datetime): Yaradılma vaxtı

### PaymentResult

Ödəniş əməliyyatının nəticəsi üçün sinif.

**Atributlar:**
- `success` (bool): Əməliyyatın uğurluluğu
- `payment_id` (str): Ödəniş ID-si
- `message` (str): Nəticə mesajı
- `data` (dict): Əlavə məlumatlar

## Adapter Fabriki

### AdapterFactory

Botunuz üçün uyğun adapteri avtomatik yaradır.

python
```
from neonpay import AdapterFactory

# Bot tipinin avtomatik təyini
neonpay = AdapterFactory.create_neonpay(bot_instance)
```

#### Dəstəklənən Kitabxanalar

- **Aiogram v3**: `Bot` tipinə görə avtomatik təyin edilir
- **Pyrogram v2+**: `Client` tipinə görə avtomatik təyin edilir
- **python-telegram-bot**: `Application` tipinə görə avtomatik təyin edilir
- **pyTelegramBotAPI**: `TeleBot` tipinə görə avtomatik təyin edilir
- **Raw API**: `RawApiAdapter`-i birbaşa istifadə edin

## Xəta İşləmə

### İstisnalar

python
```
from neonpay.errors import (
    NeonPayError,
    PaymentError,
    InvalidPaymentStageError,
    UnsupportedBotTypeError
)

try:
    result = await neonpay.send_invoice(user_id, stage)
except PaymentError as e:
    print(f"Ödəniş xətası: {e}")
except NeonPayError as e:
    print(f"Ümumi NEONPAY xətası: {e}")
```

## Yardımçı Vasitələr

### PaymentValidator

Ödəniş məlumatlarının yoxlanması.

python
```
from neonpay.utils import PaymentValidator

# Qiymətin yoxlanması
if PaymentValidator.validate_price(100):
    print("Qiymət düzgündür")

# Ödəniş mərhələsinin yoxlanması
if PaymentValidator.validate_payment_stage(stage):
    print("Ödəniş mərhələsi düzgündür")
```

### NeonPayLogger

Loqlama sistemi.

python
```
from neonpay.utils import NeonPayLogger

logger = NeonPayLogger("MyBot")
logger.log_payment_attempt(user_id, stage.name, stage.price)
logger.log_payment_success(payment_id, user_id)
```

### PaymentHelper

Yardımçı funksiyalar.

python
```
from neonpay.utils import PaymentHelper

# Qiymətin formatlanması
formatted = PaymentHelper.format_price(100)  # "100 ⭐"

# Ödəniş ID-sinin yaradılması
payment_id = PaymentHelper.generate_payment_id()

# URL yoxlanması
if PaymentHelper.is_valid_url("https://example.com/logo.png"):
    print("URL düzgündür")
```

## Middleware Sistemi

### PaymentMiddleware

Middleware üçün əsas sinif.

python
```
from neonpay.middleware import PaymentMiddleware

class LoggingMiddleware(PaymentMiddleware):
    async def before_payment(self, payment_stage, context):
        print(f"Ödəniş başlayır: {payment_stage.name}")
        return payment_stage, context
    
    async def after_payment(self, result, context):
        print(f"Ödəniş tamamlandı: {result.success}")
        return result

# İstifadə

neonpay.add_middleware(LoggingMiddleware())
```

### Daxili Middleware

python
```
from neonpay.middleware import (
    LoggingMiddleware,
    ValidationMiddleware,
    WebhookMiddleware
)

# Middleware əlavə etmə
neonpay.add_middleware(LoggingMiddleware())
neonpay.add_middleware(ValidationMiddleware())
neonpay.add_middleware(WebhookMiddleware("https://mysite.com/webhook"))
```

## Webhook İnteqrasiyası

### WebhookHandler

Webhook bildirişlərinin işlənməsi.

python
```
from neonpay.webhooks import WebhookHandler

handler = WebhookHandler(secret_key="your_secret_key")

# Webhook işləmə
@app.post("/webhook")
async def handle_webhook(request):
    if handler.verify_signature(request.headers, request.body):
        event = handler.parse_event(request.body)
        if event.type == "payment.successful":
            # Uğurlu ödənişin işlənməsi
            print(f"Ödəniş {event.payment_id} uğurludur")
    return {"status": "ok"}
```

## İstifadə Nümunələri

### Aiogram ilə Sadə Nümunə

python
```
from aiogram import Bot, Dispatcher, types
from neonpay import AdapterFactory

bot = Bot(token="YOUR_BOT_TOKEN")
dp = Dispatcher()
neonpay = AdapterFactory.create_neonpay(bot)

@dp.message(commands=["buy"])
async def buy_handler(message: types.Message):
    stage = neonpay.create_payment_stage(
        name="Premium giriş",
        price=50,
        description="Premium funksiyalara giriş"
    )
    
    result = await neonpay.send_invoice(message.chat.id, stage)
    if not result.success:
        await message.answer("Ödəniş yaradılmasında xəta")

@dp.pre_checkout_query()
async def pre_checkout_handler(query: types.PreCheckoutQuery):
    await query.answer(ok=True)

@dp.message(content_types=types.ContentType.SUCCESSFUL_PAYMENT)
async def successful_payment_handler(message: types.Message):
    result = await neonpay.handle_successful_payment(message.successful_payment)
    await message.answer("Alış üçün təşəkkürlər! 🎉")
```

### Pyrogram ilə Nümunə
python
```
from pyrogram import Client, filters
from neonpay import AdapterFactory

app = Client("my_bot", bot_token="YOUR_BOT_TOKEN")
neonpay = AdapterFactory.create_neonpay(app)

@app.on_message(filters.command("buy"))
async def buy_handler(client, message):
    stage = neonpay.create_payment_stage(
        name="VIP status",
        price=100,
        description="Bir ay VIP status"
    )
    
    result = await neonpay.send_invoice(message.chat.id, stage)
    if result.success:
        await message.reply("Faktura göndərildi!")

@app.on_message(filters.successful_payment)
async def payment_handler(client, message):
    result = await neonpay.handle_successful_payment(message.successful_payment)
    await message.reply("Ödəniş alındı! ✅")
```

## Ən Yaxşı Təcrübələr

### Təhlükəsizlik

1. **Məlumat yoxlanması**: Həmişə giriş məlumatlarını yoxlayın
2. **Xəta işləmə**: try-catch blokları istifadə edin
3. **Loqlama**: Bütün əməliyyatların loqlarını aparın
4. **Webhook təhlükəsizliyi**: Webhook imzalarını yoxlayın

### Performans

1. **Asinxronluq**: async/await istifadə edin
2. **Keşləmə**: Ödəniş mərhələlərini keşləyin
3. **Middleware**: Ümumi məntiq üçün middleware istifadə edin
4. **Monitorinq**: Performansı izləyin

### İstifadəçi Təcrübəsi

1. **Aydın təsvirlər**: Məhsulların aydın təsvirlərini istifadə edin
2. **Loqolar**: Tanınma üçün loqolar əlavə edin
3. **Geri əlaqə**: İstifadəçiləri status haqqında məlumatlandırın
4. **Xəta işləmə**: Xətalar haqqında aydın mesajlar göstərin

# NEONPAY API Sənədləşməsi

Bu sənəd NEONPAY kitabxanasının API-ni ətraflı şəkildə təsvir edir.

## Əsas Siniflər

### PaymentStage

Ödəniş mərhələsini təmsil edən sinif.

```python
class PaymentStage:
    def __init__(
        self,
        title: str,
        description: str,
        price: int,
        label: Optional[str] = None,
        photo_url: Optional[str] = None,
        payload: Optional[Dict[str, Any]] = None
    ):
        pass
```

**Parametrlər:**
- `title` (str): Ödəniş mərhələsinin başlığı (maksimum 32 simvol)
- `description` (str): Ödəniş mərhələsinin təsviri (maksimum 255 simvol)
- `price` (int): Telegram Stars-da qiymət
- `label` (Optional[str]): Ödəniş etiketi
- `photo_url` (Optional[str]): Foto URL-i
- `payload` (Optional[Dict]): Əlavə məlumatlar

### PaymentResult

Ödəniş nəticəsini təmsil edən sinif.

```python
class PaymentResult:
    user_id: int
    amount: int
    status: PaymentStatus
    metadata: Dict[str, Any]
    timestamp: datetime
```

### PaymentStatus

Ödəniş statusunu təmsil edən enum.

```python
class PaymentStatus(Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
```

## Əsas Funksiyalar

### create_neonpay

NEONPAY instansını yaradır.

```python
def create_neonpay(bot_instance, dispatcher=None):
    pass
```

**Parametrlər:**
- `bot_instance`: Bot instansı (Pyrogram, Aiogram, və s.)
- `dispatcher` (Optional): Dispatcher (Aiogram üçün)

**Qaytarır:** NeonPayCore instansı

### NeonPayCore

Əsas NEONPAY sinfi.

```python
class NeonPayCore:
    def create_payment_stage(self, stage_id: str, stage: PaymentStage):
        pass
    
    async def send_payment(self, user_id: int, stage_id: str):
        pass
    
    def on_payment(self, handler):
        pass
```

## Adapter-lər

### PyrogramAdapter

Pyrogram üçün adapter.

```python
class PyrogramAdapter(PaymentAdapter):
    def __init__(self, client: Client):
        pass
```

### AiogramAdapter

Aiogram üçün adapter.

```python
class AiogramAdapter(PaymentAdapter):
    def __init__(self, bot: Bot, dispatcher: Dispatcher):
        pass
```

### TelebotAdapter

pyTelegramBotAPI üçün adapter.

```python
class TelebotAdapter(PaymentAdapter):
    def __init__(self, bot: TeleBot):
        pass
```

### PTBAdapter

python-telegram-bot üçün adapter.

```python
class PTBAdapter(PaymentAdapter):
    def __init__(self, application: Application):
        pass
```

### RawAPIAdapter

Raw Bot API üçün adapter.

```python
class RawAPIAdapter(PaymentAdapter):
    def __init__(self, token: str, webhook_url: Optional[str] = None):
        pass
```

## Xəta Sinifləri

### NeonPayError

Əsas NEONPAY xətası.

```python
class NeonPayError(Exception):
    pass
```

### PaymentError

Ödəniş xətası.

```python
class PaymentError(NeonPayError):
    pass
```

### ValidationError

Validasiya xətası.

```python
class ValidationError(NeonPayError):
    pass
```

## Nümunələr

### Əsas İstifadə

```python
from neonpay import create_neonpay, PaymentStage

# Bot instansını yaradın
neonpay = create_neonpay(your_bot)

# Ödəniş mərhələsi yaradın
stage = PaymentStage(
    title="Premium",
    description="Premium xüsusiyyətlər",
    price=100
)

# Mərhələni əlavə edin
neonpay.create_payment_stage("premium", stage)

# Ödəniş göndərin
await neonpay.send_payment(user_id, "premium")
```

### Callback İdarəetməsi

```python
@neonpay.on_payment
async def handle_payment(result: PaymentResult):
    if result.status == PaymentStatus.COMPLETED:
        print(f"Ödəniş alındı: {result.amount} stars")
```

### Xəta İdarəetməsi

```python
try:
    await neonpay.send_payment(user_id, "premium")
except PaymentError as e:
    print(f"Ödəniş xətası: {e}")
except NeonPayError as e:
    print(f"NEONPAY xətası: {e}")
```


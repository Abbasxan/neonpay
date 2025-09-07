# Документация API NEONPAY

Этот документ подробно описывает API библиотеки NEONPAY.

## Основные классы

### PaymentStage

Класс, представляющий этап платежа.

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

**Параметры:**
- `title` (str): Заголовок этапа платежа (максимум 32 символа)
- `description` (str): Описание этапа платежа (максимум 255 символов)
- `price` (int): Цена в Telegram Stars
- `label` (Optional[str]): Метка платежа
- `photo_url` (Optional[str]): URL фотографии
- `payload` (Optional[Dict]): Дополнительные данные

### PaymentResult

Класс, представляющий результат платежа.

```python
class PaymentResult:
    user_id: int
    amount: int
    status: PaymentStatus
    metadata: Dict[str, Any]
    timestamp: datetime
```

### PaymentStatus

Enum, представляющий статус платежа.

```python
class PaymentStatus(Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
```

## Основные функции

### create_neonpay

Создает экземпляр NEONPAY.

```python
def create_neonpay(bot_instance, dispatcher=None):
    pass
```

**Параметры:**
- `bot_instance`: Экземпляр бота (Pyrogram, Aiogram, и т.д.)
- `dispatcher` (Optional): Диспетчер (для Aiogram)

**Возвращает:** Экземпляр NeonPayCore

### NeonPayCore

Основной класс NEONPAY.

```python
class NeonPayCore:
    def create_payment_stage(self, stage_id: str, stage: PaymentStage):
        pass
    
    async def send_payment(self, user_id: int, stage_id: str):
        pass
    
    def on_payment(self, handler):
        pass
```

## Адаптеры

### PyrogramAdapter

Адаптер для Pyrogram.

```python
class PyrogramAdapter(PaymentAdapter):
    def __init__(self, client: Client):
        pass
```

### AiogramAdapter

Адаптер для Aiogram.

```python
class AiogramAdapter(PaymentAdapter):
    def __init__(self, bot: Bot, dispatcher: Dispatcher):
        pass
```

### TelebotAdapter

Адаптер для pyTelegramBotAPI.

```python
class TelebotAdapter(PaymentAdapter):
    def __init__(self, bot: TeleBot):
        pass
```

### PTBAdapter

Адаптер для python-telegram-bot.

```python
class PTBAdapter(PaymentAdapter):
    def __init__(self, application: Application):
        pass
```

### RawAPIAdapter

Адаптер для Raw Bot API.

```python
class RawAPIAdapter(PaymentAdapter):
    def __init__(self, token: str, webhook_url: Optional[str] = None):
        pass
```

## Классы ошибок

### NeonPayError

Основная ошибка NEONPAY.

```python
class NeonPayError(Exception):
    pass
```

### PaymentError

Ошибка платежа.

```python
class PaymentError(NeonPayError):
    pass
```

### ValidationError

Ошибка валидации.

```python
class ValidationError(NeonPayError):
    pass
```

## Примеры

### Базовое использование

```python
from neonpay import create_neonpay, PaymentStage

# Создайте экземпляр бота
neonpay = create_neonpay(your_bot)

# Создайте этап платежа
stage = PaymentStage(
    title="Premium",
    description="Премиум функции",
    price=100
)

# Добавьте этап
neonpay.create_payment_stage("premium", stage)

# Отправьте платеж
await neonpay.send_payment(user_id, "premium")
```

### Обработка callback'ов

```python
@neonpay.on_payment
async def handle_payment(result: PaymentResult):
    if result.status == PaymentStatus.COMPLETED:
        print(f"Платеж получен: {result.amount} stars")
```

### Обработка ошибок

```python
try:
    await neonpay.send_payment(user_id, "premium")
except PaymentError as e:
    print(f"Ошибка платежа: {e}")
except NeonPayError as e:
    print(f"Ошибка NEONPAY: {e}")
```


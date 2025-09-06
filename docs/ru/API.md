# NEONPAY API Справочник

## Обзор

NEONPAY предоставляет простой и мощный API для интеграции платежей через Telegram Stars в ваши боты. API поддерживает все популярные библиотеки для Telegram ботов.

## Основные классы

### NeonPayCore

Основной класс для управления платежами.

\`\`\`python
from neonpay import NeonPayCore

# Инициализация
neonpay = NeonPayCore(bot_instance)
\`\`\`

#### Методы

##### `create_payment_stage(name, price, description=None, logo_url=None)`

Создает этап оплаты с указанными параметрами.

**Параметры:**
- `name` (str): Название продукта/услуги
- `price` (int): Цена в Telegram Stars
- `description` (str, optional): Описание продукта
- `logo_url` (str, optional): URL логотипа

**Возвращает:** `PaymentStage`

**Пример:**
\`\`\`python
stage = neonpay.create_payment_stage(
    name="Премиум подписка",
    price=100,
    description="Доступ к премиум функциям на месяц",
    logo_url="https://example.com/logo.png"
)
\`\`\`

##### `send_invoice(chat_id, payment_stage)`

Отправляет инвойс пользователю.

**Параметры:**
- `chat_id` (int): ID чата пользователя
- `payment_stage` (PaymentStage): Этап оплаты

**Возвращает:** `PaymentResult`

**Пример:**
\`\`\`python
result = await neonpay.send_invoice(user_id, stage)
if result.success:
    print("Инвойс отправлен успешно")
\`\`\`

##### `handle_successful_payment(payment_data)`

Обрабатывает успешный платеж.

**Параметры:**
- `payment_data`: Данные платежа от Telegram

**Возвращает:** `PaymentResult`

##### `refund_payment(payment_id, reason=None)`

Возвращает платеж (если поддерживается).

**Параметры:**
- `payment_id` (str): ID платежа
- `reason` (str, optional): Причина возврата

**Возвращает:** `PaymentResult`

### PaymentStage

Класс для представления этапа оплаты.

**Атрибуты:**
- `name` (str): Название продукта
- `price` (int): Цена в Stars
- `description` (str): Описание
- `logo_url` (str): URL логотипа
- `created_at` (datetime): Время создания

### PaymentResult

Класс для результата операции платежа.

**Атрибуты:**
- `success` (bool): Успешность операции
- `payment_id` (str): ID платежа
- `message` (str): Сообщение о результате
- `data` (dict): Дополнительные данные

## Фабрика адаптеров

### AdapterFactory

Автоматически создает подходящий адаптер для вашего бота.

\`\`\`python
from neonpay import AdapterFactory

# Автоматическое определение типа бота
neonpay = AdapterFactory.create_neonpay(bot_instance)
\`\`\`

#### Поддерживаемые библиотеки

- **Aiogram v3**: Автоматически определяется по типу `Bot`
- **Pyrogram v2+**: Автоматически определяется по типу `Client`
- **python-telegram-bot**: Автоматически определяется по типу `Application`
- **pyTelegramBotAPI**: Автоматически определяется по типу `TeleBot`
- **Raw API**: Используйте `RawApiAdapter` напрямую

## Обработка ошибок

### Исключения

\`\`\`python
from neonpay.errors import (
    NeonPayError,
    PaymentError,
    InvalidPaymentStageError,
    UnsupportedBotTypeError
)

try:
    result = await neonpay.send_invoice(user_id, stage)
except PaymentError as e:
    print(f"Ошибка платежа: {e}")
except NeonPayError as e:
    print(f"Общая ошибка NEONPAY: {e}")
\`\`\`

## Утилиты

### PaymentValidator

Валидация данных платежей.

\`\`\`python
from neonpay.utils import PaymentValidator

# Валидация цены
if PaymentValidator.validate_price(100):
    print("Цена корректна")

# Валидация этапа оплаты
if PaymentValidator.validate_payment_stage(stage):
    print("Этап оплаты корректен")
\`\`\`

### NeonPayLogger

Система логирования.

\`\`\`python
from neonpay.utils import NeonPayLogger

logger = NeonPayLogger("MyBot")
logger.log_payment_attempt(user_id, stage.name, stage.price)
logger.log_payment_success(payment_id, user_id)
\`\`\`

### PaymentHelper

Вспомогательные функции.

\`\`\`python
from neonpay.utils import PaymentHelper

# Форматирование цены
formatted = PaymentHelper.format_price(100)  # "100 ⭐"

# Генерация ID платежа
payment_id = PaymentHelper.generate_payment_id()

# Валидация URL
if PaymentHelper.is_valid_url("https://example.com/logo.png"):
    print("URL корректен")
\`\`\`

## Middleware система

### PaymentMiddleware

Базовый класс для middleware.

\`\`\`python
from neonpay.middleware import PaymentMiddleware

class LoggingMiddleware(PaymentMiddleware):
    async def before_payment(self, payment_stage, context):
        print(f"Начинается платеж: {payment_stage.name}")
        return payment_stage, context
    
    async def after_payment(self, result, context):
        print(f"Платеж завершен: {result.success}")
        return result

# Использование
neonpay.add_middleware(LoggingMiddleware())
\`\`\`

### Встроенные middleware

\`\`\`python
from neonpay.middleware import (
    LoggingMiddleware,
    ValidationMiddleware,
    WebhookMiddleware
)

# Добавление middleware
neonpay.add_middleware(LoggingMiddleware())
neonpay.add_middleware(ValidationMiddleware())
neonpay.add_middleware(WebhookMiddleware("https://mysite.com/webhook"))
\`\`\`

## Webhook интеграция

### WebhookHandler

Обработка webhook уведомлений.

\`\`\`python
from neonpay.webhooks import WebhookHandler

handler = WebhookHandler(secret_key="your_secret_key")

# Обработка webhook
@app.post("/webhook")
async def handle_webhook(request):
    if handler.verify_signature(request.headers, request.body):
        event = handler.parse_event(request.body)
        if event.type == "payment.successful":
            # Обработка успешного платежа
            print(f"Платеж {event.payment_id} успешен")
    return {"status": "ok"}
\`\`\`

## Примеры использования

### Простой пример с Aiogram

\`\`\`python
from aiogram import Bot, Dispatcher, types
from neonpay import AdapterFactory

bot = Bot(token="YOUR_BOT_TOKEN")
dp = Dispatcher()
neonpay = AdapterFactory.create_neonpay(bot)

@dp.message(commands=["buy"])
async def buy_handler(message: types.Message):
    stage = neonpay.create_payment_stage(
        name="Премиум доступ",
        price=50,
        description="Доступ к премиум функциям"
    )
    
    result = await neonpay.send_invoice(message.chat.id, stage)
    if not result.success:
        await message.answer("Ошибка при создании платежа")

@dp.pre_checkout_query()
async def pre_checkout_handler(query: types.PreCheckoutQuery):
    await query.answer(ok=True)

@dp.message(content_types=types.ContentType.SUCCESSFUL_PAYMENT)
async def successful_payment_handler(message: types.Message):
    result = await neonpay.handle_successful_payment(message.successful_payment)
    await message.answer("Спасибо за покупку! 🎉")
\`\`\`

### Пример с Pyrogram

\`\`\`python
from pyrogram import Client, filters
from neonpay import AdapterFactory

app = Client("my_bot", bot_token="YOUR_BOT_TOKEN")
neonpay = AdapterFactory.create_neonpay(app)

@app.on_message(filters.command("buy"))
async def buy_handler(client, message):
    stage = neonpay.create_payment_stage(
        name="VIP статус",
        price=100,
        description="VIP статус на месяц"
    )
    
    result = await neonpay.send_invoice(message.chat.id, stage)
    if result.success:
        await message.reply("Инвойс отправлен!")

@app.on_message(filters.successful_payment)
async def payment_handler(client, message):
    result = await neonpay.handle_successful_payment(message.successful_payment)
    await message.reply("Платеж получен! ✅")
\`\`\`

## Лучшие практики

### Безопасность

1. **Валидация данных**: Всегда валидируйте входные данные
2. **Обработка ошибок**: Используйте try-catch блоки
3. **Логирование**: Ведите логи всех операций
4. **Webhook безопасность**: Проверяйте подписи webhook

### Производительность

1. **Асинхронность**: Используйте async/await
2. **Кэширование**: Кэшируйте этапы оплаты
3. **Middleware**: Используйте middleware для общей логики
4. **Мониторинг**: Отслеживайте производительность

### Пользовательский опыт

1. **Понятные описания**: Используйте четкие описания продуктов
2. **Логотипы**: Добавляйте логотипы для узнаваемости
3. **Обратная связь**: Информируйте пользователей о статусе
4. **Обработка ошибок**: Показывайте понятные сообщения об ошибках

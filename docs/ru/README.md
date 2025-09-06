# Документация NEONPAY (Русский)

Добро пожаловать в полную документацию NEONPAY. Это руководство поможет вам быстро и эффективно интегрировать платежи Telegram Stars в ваш бот.

## Содержание

1. [Установка](#установка)
2. [Быстрый старт](#быстрый-старт)
3. [Поддержка библиотек](#поддержка-библиотек)
4. [Основные концепции](#основные-концепции)
5. [Справочник API](#справочник-api)
6. [Реальные примеры](#реальные-примеры)
7. [Лучшие практики](#лучшие-практики)
8. [Продакшн развертывание](#продакшн-развертывание)
9. [Решение проблем](#решение-проблем)
10. [Поддержка](#поддержка)

## Установка

Установите NEONPAY с помощью pip:

\`\`\`bash
pip install neonpay
\`\`\`

Для конкретных библиотек ботов установите необходимые зависимости:

\`\`\`bash
# Для Pyrogram
pip install neonpay pyrogram

# Для Aiogram
pip install neonpay aiogram

# Для python-telegram-bot
pip install neonpay python-telegram-bot

# Для pyTelegramBotAPI
pip install neonpay pyTelegramBotAPI
\`\`\`

## Быстрый старт

### 1. Установка зависимостей

\`\`\`bash
# Для Aiogram (Рекомендуется)
pip install neonpay aiogram

# Для Pyrogram
pip install neonpay pyrogram

# Для pyTelegramBotAPI
pip install neonpay pyTelegramBotAPI
\`\`\`

### 2. Импорт и инициализация

\`\`\`python
from neonpay.factory import create_neonpay
from neonpay.core import PaymentStage, PaymentStatus

# Автоматическое определение адаптера
neonpay = create_neonpay(bot_instance=ваш_экземпляр_бота)
\`\`\`

### 3. Создание этапа платежа

\`\`\`python
stage = PaymentStage(
    title="Премиум доступ",
    description="Разблокировать премиум функции на 30 дней",
    price=25,  # 25 Telegram Stars
)

neonpay.create_payment_stage("premium_access", stage)
\`\`\`

### 4. Отправка платежа

\`\`\`python
await neonpay.send_payment(user_id=12345, stage_id="premium_access")
\`\`\`

### 5. Обработка платежей

\`\`\`python
@neonpay.on_payment
async def handle_payment(result):
    if result.status == PaymentStatus.COMPLETED:
        print(f"Получено {result.amount} звезд от пользователя {result.user_id}")
        # Доставьте ваш продукт/услугу здесь
\`\`\`

## Поддержка библиотек

### Интеграция с Pyrogram

\`\`\`python
from pyrogram import Client
from neonpay import create_neonpay

app = Client("my_bot", bot_token="ВАШ_ТОКЕН")
neonpay = create_neonpay(app)

@app.on_message()
async def handle_message(client, message):
    if message.text == "/купить":
        await neonpay.send_payment(message.from_user.id, "premium")

app.run()
\`\`\`

### Интеграция с Aiogram

\`\`\`python
from aiogram import Bot, Dispatcher, Router
from neonpay import create_neonpay

bot = Bot(token="ВАШ_ТОКЕН")
dp = Dispatcher()
router = Router()

neonpay = create_neonpay(bot)

@router.message(Command("купить"))
async def buy_handler(message: Message):
    await neonpay.send_payment(message.from_user.id, "premium")

dp.include_router(router)
\`\`\`

## Основные концепции

### Этапы оплаты

Этапы оплаты определяют, что покупают пользователи:

\`\`\`python
stage = PaymentStage(
    title="Название товара",         # Обязательно: отображаемое имя
    description="Описание товара",   # Обязательно: описание
    price=100,                      # Обязательно: цена в звездах
    label="Купить сейчас",          # Опционально: текст кнопки
    photo_url="https://...",        # Опционально: изображение товара
    payload={"custom": "data"},     # Опционально: пользовательские данные
    start_parameter="ref_code"      # Опционально: параметр для deep linking
)
\`\`\`

### Результаты платежей

Когда платежи завершаются, вы получаете `PaymentResult`:

\`\`\`python
@neonpay.on_payment
async def handle_payment(result: PaymentResult):
    print(f"ID пользователя: {result.user_id}")
    print(f"Сумма: {result.amount}")
    print(f"Валюта: {result.currency}")
    print(f"Статус: {result.status}")
    print(f"Метаданные: {result.metadata}")
\`\`\`

### Обработка ошибок

\`\`\`python
from neonpay import NeonPayError, PaymentError

try:
    await neonpay.send_payment(user_id, "stage_id")
except PaymentError as e:
    print(f"Ошибка платежа: {e}")
except NeonPayError as e:
    print(f"Системная ошибка: {e}")
\`\`\`

## Справочник API

### Класс NeonPayCore

#### Методы

- `create_payment_stage(stage_id: str, stage: PaymentStage)` - Создать этап оплаты
- `get_payment_stage(stage_id: str)` - Получить этап оплаты по ID
- `list_payment_stages()` - Получить все этапы оплаты
- `remove_payment_stage(stage_id: str)` - Удалить этап оплаты
- `send_payment(user_id: int, stage_id: str)` - Отправить счет на оплату
- `on_payment(callback)` - Зарегистрировать callback для платежей
- `get_stats()` - Получить статистику системы

### Класс PaymentStage

#### Параметры

- `title: str` - Название платежа (обязательно)
- `description: str` - Описание платежа (обязательно)
- `price: int` - Цена в Telegram Stars (обязательно)
- `label: str` - Текст кнопки (по умолчанию: "Payment")
- `photo_url: str` - URL изображения товара (опционально)
- `payload: dict` - Пользовательские данные (опционально)
- `start_parameter: str` - Параметр для deep linking (опционально)

## Примеры

### Бот интернет-магазина

\`\`\`python
from neonpay import create_neonpay, PaymentStage

# Каталог товаров
products = {
    "coffee": PaymentStage("Кофе", "Премиум кофейные зерна", 50),
    "tea": PaymentStage("Чай", "Органические чайные листья", 30),
    "cake": PaymentStage("Торт", "Вкусный шоколадный торт", 100)
}

neonpay = create_neonpay(bot)

# Добавляем все товары
for product_id, stage in products.items():
    neonpay.create_payment_stage(product_id, stage)

# Обрабатываем заказы
@neonpay.on_payment
async def process_order(result):
    user_id = result.user_id
    product = result.metadata.get("product")
    
    # Обрабатываем заказ
    await fulfill_order(user_id, product)
    await bot.send_message(user_id, "Заказ подтвержден! Спасибо!")
\`\`\`

### Сервис подписок

\`\`\`python
subscription_plans = {
    "monthly": PaymentStage(
        "Месячный план", 
        "1 месяц премиум доступа", 
        100,
        payload={"duration": 30}
    ),
    "yearly": PaymentStage(
        "Годовой план", 
        "12 месяцев премиум доступа (2 месяца в подарок!)", 
        1000,
        payload={"duration": 365}
    )
}

@neonpay.on_payment
async def handle_subscription(result):
    user_id = result.user_id
    duration = result.metadata.get("duration", 30)
    
    # Предоставляем подписку
    await grant_premium(user_id, days=duration)
\`\`\`

## Лучшие практики

### 1. Проверяйте данные платежей

\`\`\`python
@neonpay.on_payment
async def handle_payment(result):
    # Проверяем сумму платежа
    expected_amount = get_expected_amount(result.metadata)
    if result.amount != expected_amount:
        logger.warning(f"Несоответствие суммы: ожидалось {expected_amount}, получено {result.amount}")
        return
    
    # Обрабатываем платеж
    await process_payment(result)
\`\`\`

### 2. Обрабатывайте ошибки корректно

\`\`\`python
async def safe_send_payment(user_id, stage_id):
    try:
        await neonpay.send_payment(user_id, stage_id)
    except PaymentError as e:
        await bot.send_message(user_id, f"Ошибка платежа: {e}")
    except Exception as e:
        logger.error(f"Неожиданная ошибка: {e}")
        await bot.send_message(user_id, "Что-то пошло не так. Попробуйте еще раз.")
\`\`\`

### 3. Используйте осмысленные ID этапов

\`\`\`python
# Хорошо
neonpay.create_payment_stage("premium_monthly_subscription", stage)
neonpay.create_payment_stage("coffee_large_size", stage)

# Плохо
neonpay.create_payment_stage("stage1", stage)
neonpay.create_payment_stage("payment", stage)
\`\`\`

## Решение проблем

### Частые проблемы

#### 1. "Payment stage not found"

\`\`\`python
# Проверяем, существует ли этап
stage = neonpay.get_payment_stage("my_stage")
if not stage:
    print("Этап не существует!")
    
# Список всех этапов
stages = neonpay.list_payment_stages()
print(f"Доступные этапы: {list(stages.keys())}")
\`\`\`

#### 2. "Failed to send invoice"

- Проверьте правильность токена бота
- Убедитесь, что пользователь запустил бота
- Проверьте валидность ID пользователя
- Проверьте конфигурацию этапа оплаты

### Режим отладки

\`\`\`python
import logging

# Включаем отладочное логирование
logging.basicConfig(level=logging.DEBUG)
logging.getLogger("neonpay").setLevel(logging.DEBUG)
\`\`\`

### Получение помощи

Если вам нужна помощь:

1. Проверьте директорию [examples](../../examples/)
2. Прочитайте [FAQ](FAQ.md)
3. Создайте issue на [GitHub](https://github.com/Abbasxan/neonpay/issues)
4. Обратитесь в поддержку: [@neonsahib](https://t.me/neonsahib)

---

[← Назад к основному README](../../README.md) | [English Documentation →](../en/README.md)

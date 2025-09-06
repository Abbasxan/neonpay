Документация NEONPAY (Русский)
===============================

Добро пожаловать в полную документацию NEONPAY. Это руководство поможет вам быстро и эффективно интегрировать платежи Telegram Stars в вашего бота.

Содержание
----------

1. Установка
2. Быстрый старт
3. Поддержка библиотек
4. Основные концепции
5. Справочник API
6. Реальные примеры
7. Лучшие практики
8. Развертывание в продакшене
9. Устранение неполадок
10. Поддержка

Установка
---------

Установите NEONPAY с помощью pip:

.. code-block:: bash

   pip install neonpay

Для конкретных библиотек ботов установите необходимые зависимости:

.. code-block:: bash

   # Для Pyrogram
   pip install neonpay pyrogram
   
   # Для Aiogram
   pip install neonpay aiogram
   
   # Для python-telegram-bot
   pip install neonpay python-telegram-bot
   
   # Для pyTelegramBotAPI
   pip install neonpay pyTelegramBotAPI

Быстрый старт
-------------

1. Установка зависимостей
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Для Aiogram (Рекомендуется)
   pip install neonpay aiogram
   
   # Для Pyrogram
   pip install neonpay pyrogram
   
   # Для pyTelegramBotAPI
   pip install neonpay pyTelegramBotAPI

2. Импорт и инициализация
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from neonpay.factory import create_neonpay
   from neonpay.core import PaymentStage, PaymentStatus
   
   # Автоматическое определение адаптера
   neonpay = create_neonpay(bot_instance=ваш_экземпляр_бота)

3. Создание этапа платежа
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   stage = PaymentStage(
       title="Премиум доступ",
       description="Разблокируйте премиум функции на 30 дней",
       price=25,  # 25 Telegram Stars
   )
   
   neonpay.create_payment_stage("premium_access", stage)

4. Отправка платежа
~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   await neonpay.send_payment(user_id=12345, stage_id="premium_access")

5. Обработка платежей
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   @neonpay.on_payment
   async def handle_payment(result):
       if result.status == PaymentStatus.COMPLETED:
           print(f"Получено {result.amount} звезд от пользователя {result.user_id}")
           # Доставьте ваш продукт/услугу здесь

Поддержка библиотек
-------------------

Интеграция с Aiogram (Рекомендуется)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from aiogram import Bot, Dispatcher, Router
   from aiogram.filters import Command
   from neonpay.factory import create_neonpay
   from neonpay.core import PaymentStage, PaymentStatus
   
   bot = Bot(token="ВАШ_ТОКЕН")
   dp = Dispatcher()
   router = Router()
   
   neonpay = create_neonpay(bot_instance=bot, dispatcher=dp)
   
   # Создание этапа платежа
   stage = PaymentStage(
       title="Премиум доступ",
       description="Разблокируйте премиум функции на 30 дней",
       price=25,
   )
   neonpay.create_payment_stage("premium_access", stage)
   
   # Обработка платежей
   @neonpay.on_payment
   async def handle_payment(result):
       if result.status == PaymentStatus.COMPLETED:
           await bot.send_message(
               result.user_id, 
               f"Спасибо! Ваш премиум доступ теперь активен! 🎉"
           )
   
   @router.message(Command("buy"))
   async def buy_handler(message: Message):
       await neonpay.send_payment(message.from_user.id, "premium_access")
   
   dp.include_router(router)

Интеграция с Pyrogram
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from pyrogram import Client, filters
   from neonpay.factory import create_neonpay
   from neonpay.core import PaymentStage, PaymentStatus
   
   app = Client("my_bot", bot_token="ВАШ_ТОКЕН")
   neonpay = create_neonpay(bot_instance=app)
   
   # Создание этапа платежа
   stage = PaymentStage(
       title="Премиум доступ",
       description="Разблокируйте премиум функции на 30 дней",
       price=25,
   )
   neonpay.create_payment_stage("premium_access", stage)
   
   # Обработка платежей
   @neonpay.on_payment
   async def handle_payment(result):
       if result.status == PaymentStatus.COMPLETED:
           await app.send_message(
               result.user_id, 
               f"Спасибо! Ваш премиум доступ теперь активен! 🎉"
           )
   
   @app.on_message(filters.command("buy"))
   async def buy_handler(client, message):
       await neonpay.send_payment(message.from_user.id, "premium_access")
   
   app.run()

Интеграция с pyTelegramBotAPI
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from telebot import TeleBot
   from neonpay.factory import create_neonpay
   from neonpay.core import PaymentStage, PaymentStatus
   
   bot = TeleBot("ВАШ_ТОКЕН")
   neonpay = create_neonpay(bot_instance=bot)
   
   # Создание этапа платежа
   stage = PaymentStage(
       title="Премиум доступ",
       description="Разблокируйте премиум функции на 30 дней",
       price=25,
   )
   neonpay.create_payment_stage("premium_access", stage)
   
   # Обработка платежей
   @neonpay.on_payment
   async def handle_payment(result):
       if result.status == PaymentStatus.COMPLETED:
           bot.send_message(
               result.user_id, 
               f"Спасибо! Ваш премиум доступ теперь активен! 🎉"
           )
   
   @bot.message_handler(commands=['buy'])
   def buy_handler(message):
       import asyncio
       asyncio.run(neonpay.send_payment(message.from_user.id, "premium_access"))
   
   bot.infinity_polling()

Основные концепции
------------------

Этапы платежей
~~~~~~~~~~~~~~~

Этапы платежей определяют, что покупают пользователи:

.. code-block:: python

   stage = PaymentStage(
       title="Название продукта",           # Обязательно: Отображаемое имя
       description="Детали продукта",      # Обязательно: Описание
       price=100,                          # Обязательно: Цена в звездах
       label="Купить сейчас",             # Опционально: Метка кнопки
       photo_url="https://...",            # Опционально: Изображение продукта
       payload={"custom": "data"},         # Опционально: Пользовательские данные
       start_parameter="ref_code"          # Опционально: Параметр глубокой ссылки
   )

Результаты платежей
~~~~~~~~~~~~~~~~~~~

Когда платежи завершаются, вы получаете `PaymentResult`:

.. code-block:: python

   @neonpay.on_payment
   async def handle_payment(result: PaymentResult):
       print(f"ID пользователя: {result.user_id}")
       print(f"Сумма: {result.amount}")
       print(f"Валюта: {result.currency}")
       print(f"Статус: {result.status}")
       print(f"Метаданные: {result.metadata}")

Обработка ошибок
~~~~~~~~~~~~~~~~~

.. code-block:: python

   from neonpay import NeonPayError, PaymentError
   
   try:
       await neonpay.send_payment(user_id, "stage_id")
   except PaymentError as e:
       print(f"Платеж не удался: {e}")
   except NeonPayError as e:
       print(f"Системная ошибка: {e}")

Справочник API
--------------

Класс NeonPayCore
~~~~~~~~~~~~~~~~~~

Методы:

- `create_payment_stage(stage_id: str, stage: PaymentStage)` - Создать этап платежа
- `get_payment_stage(stage_id: str)` - Получить этап платежа по ID
- `list_payment_stages()` - Получить все этапы платежей
- `remove_payment_stage(stage_id: str)` - Удалить этап платежа
- `send_payment(user_id: int, stage_id: str)` - Отправить счет на оплату
- `on_payment(callback)` - Зарегистрировать callback платежа
- `get_stats()` - Получить статистику системы

Класс PaymentStage
~~~~~~~~~~~~~~~~~~~

Параметры:

- `title: str` - Заголовок платежа (обязательно)
- `description: str` - Описание платежа (обязательно)
- `price: int` - Цена в Telegram Stars (обязательно)
- `label: str` - Метка кнопки (по умолчанию: "Платеж")
- `photo_url: str` - URL изображения продукта (опционально)
- `payload: dict` - Пользовательские данные (опционально)
- `start_parameter: str` - Параметр глубокой ссылки (опционально)

Класс PaymentResult
~~~~~~~~~~~~~~~~~~~~

Атрибуты:

- `user_id: int` - Пользователь, совершивший платеж
- `amount: int` - Сумма платежа
- `currency: str` - Валюта платежа (XTR)
- `status: PaymentStatus` - Статус платежа
- `transaction_id: str` - ID транзакции (опционально)
- `metadata: dict` - Пользовательские метаданные

Реальные примеры
----------------

Все примеры основаны на **реально работающих ботах** и готовы к продакшену. Проверьте папку examples для полных реализаций.

Бот для пожертвований
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from neonpay.factory import create_neonpay
   from neonpay.core import PaymentStage, PaymentStatus
   
   # Варианты пожертвований
   DONATE_OPTIONS = [
       {"amount": 1, "symbol": "⭐", "desc": "1⭐ поддержка: Будет использовано для серверных расходов бота"},
       {"amount": 10, "symbol": "⭐", "desc": "10⭐ поддержка: Будет потрачено на разработку новых функций"},
       {"amount": 50, "symbol": "🌟", "desc": "50⭐ большая поддержка: Будет использовано для разработки и продвижения бота"},
   ]
   
   neonpay = create_neonpay(bot_instance=bot)
   
   # Создание этапов пожертвований
   for option in DONATE_OPTIONS:
       neonpay.create_payment_stage(
           f"donate_{option['amount']}",
           PaymentStage(
               title=f"Поддержка {option['amount']}{option['symbol']}",
               description=option["desc"],
               price=option["amount"],
           ),
       )
   
   # Обработка пожертвований
   @neonpay.on_payment
   async def handle_payment(result):
       if result.status == PaymentStatus.COMPLETED:
           if result.stage_id.startswith("donate_"):
               await bot.send_message(
                   result.user_id,
                   f"Спасибо! Ваша поддержка: {result.amount}⭐ ❤️\n"
                   f"Ваш вклад помогает поддерживать работу бота!"
               )

Цифровой магазин
~~~~~~~~~~~~~~~~

.. code-block:: python

   # Цифровые продукты
   DIGITAL_PRODUCTS = [
       {
           "id": "premium_access",
           "title": "Премиум доступ",
           "description": "Разблокируйте все премиум функции на 30 дней",
           "price": 25,
           "symbol": "👑"
       },
       {
           "id": "custom_theme",
           "title": "Пользовательская тема",
           "description": "Персонализированная тема и цвета бота",
           "price": 15,
           "symbol": "🎨"
       },
   ]
   
   # Создание этапов продуктов
   for product in DIGITAL_PRODUCTS:
       neonpay.create_payment_stage(
           product["id"],
           PaymentStage(
               title=f"{product['symbol']} {product['title']}",
               description=product["description"],
               price=product["price"],
           ),
       )
   
   # Обработка покупок продуктов
   @neonpay.on_payment
   async def handle_payment(result):
       if result.status == PaymentStatus.COMPLETED:
           if not result.stage_id.startswith("donate_"):
               product = next((p for p in DIGITAL_PRODUCTS if p["id"] == result.stage_id), None)
               if product:
                   await bot.send_message(
                       result.user_id,
                       f"🎉 Покупка успешна!\n\n"
                       f"Продукт: {product['symbol']} {product['title']}\n"
                       f"Цена: {product['price']}⭐\n\n"
                       f"Ваш цифровой продукт активирован!\n"
                       f"Спасибо за покупку! 🚀"
                   )

Лучшие практики
---------------

1. Проверяйте данные платежа
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   @neonpay.on_payment
   async def handle_payment(result):
       # Проверьте сумму платежа
       expected_amount = get_expected_amount(result.metadata)
       if result.amount != expected_amount:
           logger.warning(f"Несоответствие суммы: ожидалось {expected_amount}, получено {result.amount}")
           return
       
       # Обработайте платеж
       await process_payment(result)

2. Обрабатывайте ошибки корректно
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   async def safe_send_payment(user_id, stage_id):
       try:
           await neonpay.send_payment(user_id, stage_id)
       except PaymentError as e:
           await bot.send_message(user_id, f"Платеж не удался: {e}")
       except Exception as e:
           logger.error(f"Неожиданная ошибка: {e}")
           await bot.send_message(user_id, "Что-то пошло не так. Попробуйте еще раз.")

3. Используйте осмысленные ID этапов
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Хорошо
   neonpay.create_payment_stage("premium_monthly_subscription", stage)
   neonpay.create_payment_stage("coffee_large_size", stage)
   
   # Плохо
   neonpay.create_payment_stage("stage1", stage)
   neonpay.create_payment_stage("payment", stage)

4. Логируйте события платежей
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   import logging
   
   logger = logging.getLogger(__name__)
   
   @neonpay.on_payment
   async def handle_payment(result):
       logger.info(f"Получен платеж: {result.user_id} заплатил {result.amount} звезд")
       
       try:
           await process_payment(result)
           logger.info(f"Платеж успешно обработан для пользователя {result.user_id}")
       except Exception as e:
           logger.error(f"Не удалось обработать платеж для пользователя {result.user_id}: {e}")

Развертывание в продакшене
-------------------------

1. Переменные окружения
~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   import os
   
   # Храните чувствительные данные безопасно
   BOT_TOKEN = os.getenv("BOT_TOKEN")
   WEBHOOK_URL = os.getenv("WEBHOOK_URL")
   DATABASE_URL = os.getenv("DATABASE_URL")

2. Интеграция с базой данных
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Замените хранение в памяти на базу данных
   import asyncpg
   
   async def save_payment(user_id: int, amount: int, stage_id: str):
       conn = await asyncpg.connect(DATABASE_URL)
       await conn.execute(
           "INSERT INTO payments (user_id, amount, stage_id, created_at) VALUES ($1, $2, $3, NOW())",
           user_id, amount, stage_id
       )
       await conn.close()

3. Мониторинг ошибок
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   import logging
   from logging.handlers import RotatingFileHandler
   
   # Настройка логирования
   logging.basicConfig(
       level=logging.INFO,
       format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
       handlers=[
           RotatingFileHandler("bot.log", maxBytes=10*1024*1024, backupCount=5),
           logging.StreamHandler()
       ]
   )

4. Проверки здоровья
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   @router.message(Command("status"))
   async def status_command(message: Message):
       """Эндпоинт проверки здоровья"""
       stats = neonpay.get_stats()
       status_text = (
           f"📊 **Статус бота**\n\n"
           f"✅ Статус: Онлайн\n"
           f"💫 Платежная система: Активна\n"
           f"🔧 Версия: 2.0\n"
           f"📈 Этапы платежей: {stats['total_stages']}\n"
           f"🔄 Callback-функции: {stats['registered_callbacks']}\n\n"
           f"Спасибо за использование этого бесплатного бота!"
       )
       await message.answer(status_text)

5. Настройка Webhook (для Raw API)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from aiohttp import web
   
   async def webhook_handler(request):
       """Обработка входящих обновлений webhook"""
       try:
           data = await request.json()
           
           # Обработайте обновление
           await process_update(data)
           
           return web.Response(text="OK")
       except Exception as e:
           logger.error(f"Ошибка webhook: {e}")
           return web.Response(text="Ошибка", status=500)
   
   app = web.Application()
   app.router.add_post("/webhook", webhook_handler)

Устранение неполадок
--------------------

Общие проблемы
~~~~~~~~~~~~~~~

1. "Этап платежа не найден"

.. code-block:: python

   # Проверьте, существует ли этап
   stage = neonpay.get_payment_stage("my_stage")
   if not stage:
       print("Этап не существует!")
       
   # Список всех этапов
   stages = neonpay.list_payment_stages()
   print(f"Доступные этапы: {list(stages.keys())}")

2. "Не удалось отправить счет"

- Убедитесь, что токен бота правильный
- Проверьте, что пользователь запустил бота
- Убедитесь, что ID пользователя действительный
- Проверьте конфигурацию этапа платежа

3. Callback-функции платежей не работают

.. code-block:: python

   # Убедитесь, что setup вызван
   await neonpay.setup()
   
   # Проверьте, зарегистрированы ли обработчики
   stats = neonpay.get_stats()
   print(f"Зарегистрированные callback-функции: {stats['registered_callbacks']}")

Режим отладки
~~~~~~~~~~~~~

.. code-block:: python

   import logging
   
   # Включите отладочное логирование
   logging.basicConfig(level=logging.DEBUG)
   logging.getLogger("neonpay").setLevel(logging.DEBUG)

Поддержка
---------

Получение помощи
~~~~~~~~~~~~~~~~~

Если вам нужна помощь:

1. 📚 **Документация**: Проверьте папку examples для полных рабочих примеров
2. 💬 **Сообщество**: Присоединяйтесь к нашему Telegram сообществу
3. 🐛 **Проблемы**: Откройте проблему на GitHub
4. 📧 **Email**: Обратитесь в поддержку по адресу support@neonpay.com
5. 💬 **Telegram**: Обратитесь к @neonsahib

Ресурсы
~~~~~~~~

- 📖 **Полные примеры**: examples/ - Готовые к продакшену примеры ботов
- 🔧 **Справочник API**: API.md - Полная документация API
- 🔒 **Безопасность**: SECURITY.md - Лучшие практики безопасности
- 📝 **Журнал изменений**: CHANGELOG.md - История версий

Быстрые ссылки
~~~~~~~~~~~~~~~

- 🚀 **Начать**: Руководство по быстрому старту
- 📚 **Примеры**: Реальные примеры
- 🏗️ **Развертывание**: Развертывание в продакшене
- 🐛 **Устранение неполадок**: Общие проблемы

Документация NEONPAY (Русский)
===============================

Добро пожаловать в полную документацию NEONPAY. Это руководство поможет вам быстро и эффективно интегрировать платежи Telegram Stars в вашего бота.

.. toctree::
   :maxdepth: 2
   :caption: Содержание:

   README
   API
   FAQ
   SECURITY

Возможности
-----------

* **Поддержка множественных фреймворков**: Работает с Aiogram, Pyrogram, python-telegram-bot и другими
* **Интеграция с Telegram Stars**: Нативная поддержка платежей Telegram Stars
* **Безопасность**: Встроенные функции безопасности и валидация
* **Простая интеграция**: Простой API для быстрой реализации
* **Подробная документация**: Детальные руководства и примеры

Быстрый старт
-------------

Установите NEONPAY:

.. code-block:: bash

   pip install neonpay

Базовое использование с Aiogram:

.. code-block:: python

   from neonpay.factory import create_neonpay
   from neonpay.core import PaymentStage, PaymentStatus
   from aiogram import Bot, Dispatcher
   
   bot = Bot(token="ВАШ_ТОКЕН")
   dp = Dispatcher()
   
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

Поддерживаемые языки
--------------------

* :doc:`English <../en/README>`
* :doc:`Русский <../ru/README>` (Текущий)
* :doc:`Azerbaijani <../az/README>`

Индексы и таблицы
=================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

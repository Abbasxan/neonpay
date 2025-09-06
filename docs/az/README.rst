NEONPAY Sənədləri (Azərbaycan)
===============================

NEONPAY-ın tam sənədlərinə xoş gəlmisiniz. Bu bələdçi Telegram Stars ödənişlərini botunuza tez və effektiv şəkildə inteqrasiya etməyə kömək edəcək.

Mündəricat
----------

1. Quraşdırma
2. Sürətli Başlanğıc
3. Kitabxana Dəstəyi
4. Əsas Anlayışlar
5. API İstinadı
6. Real Dünya Nümunələri
7. Ən Yaxşı Təcrübələr
8. İstehsal Yerləşdirməsi
9. Problemlərin Həlli
10. Dəstək

Quraşdırma
----------

NEONPAY-ı pip ilə quraşdırın:

.. code-block:: bash

   pip install neonpay

Müəyyən bot kitabxanaları üçün tələb olunan asılılıqları quraşdırın:

.. code-block:: bash

   # Pyrogram üçün
   pip install neonpay pyrogram
   
   # Aiogram üçün
   pip install neonpay aiogram
   
   # python-telegram-bot üçün
   pip install neonpay python-telegram-bot
   
   # pyTelegramBotAPI üçün
   pip install neonpay pyTelegramBotAPI

Sürətli Başlanğıc
-----------------

1. Asılılıqları Quraşdırın
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Aiogram üçün (Tövsiyə olunan)
   pip install neonpay aiogram
   
   # Pyrogram üçün
   pip install neonpay pyrogram
   
   # pyTelegramBotAPI üçün
   pip install neonpay pyTelegramBotAPI

2. İmport və İnitializasiya
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from neonpay.factory import create_neonpay
   from neonpay.core import PaymentStage, PaymentStatus
   
   # Avtomatik adapter aşkarlama
   neonpay = create_neonpay(bot_instance=sizin_bot_instance)

3. Ödəniş Mərhələsi Yaradın
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   stage = PaymentStage(
       title="Premium Giriş",
       description="30 gün üçün premium funksiyaları açın",
       price=25,  # 25 Telegram Stars
   )
   
   neonpay.create_payment_stage("premium_access", stage)

4. Ödəniş Göndərin
~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   await neonpay.send_payment(user_id=12345, stage_id="premium_access")

5. Ödənişləri İdarə Edin
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   @neonpay.on_payment
   async def handle_payment(result):
       if result.status == PaymentStatus.COMPLETED:
           print(f"İstifadəçi {result.user_id}-dən {result.amount} ulduz alındı")
           # Məhsulunuzu/xidmətinizi burada təhvil verin

Kitabxana Dəstəyi
-----------------

Aiogram İnteqrasiyası (Tövsiyə olunan)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from aiogram import Bot, Dispatcher, Router
   from aiogram.filters import Command
   from neonpay.factory import create_neonpay
   from neonpay.core import PaymentStage, PaymentStatus
   
   bot = Bot(token="SIZIN_TOKEN")
   dp = Dispatcher()
   router = Router()
   
   neonpay = create_neonpay(bot_instance=bot, dispatcher=dp)
   
   # Ödəniş mərhələsi yaradın
   stage = PaymentStage(
       title="Premium Giriş",
       description="30 gün üçün premium funksiyaları açın",
       price=25,
   )
   neonpay.create_payment_stage("premium_access", stage)
   
   # Ödənişləri idarə edin
   @neonpay.on_payment
   async def handle_payment(result):
       if result.status == PaymentStatus.COMPLETED:
           await bot.send_message(
               result.user_id, 
               f"Təşəkkürlər! Premium girişiniz indi aktivdir! 🎉"
           )
   
   @router.message(Command("buy"))
   async def buy_handler(message: Message):
       await neonpay.send_payment(message.from_user.id, "premium_access")
   
   dp.include_router(router)

Pyrogram İnteqrasiyası
~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from pyrogram import Client, filters
   from neonpay.factory import create_neonpay
   from neonpay.core import PaymentStage, PaymentStatus
   
   app = Client("my_bot", bot_token="SIZIN_TOKEN")
   neonpay = create_neonpay(bot_instance=app)
   
   # Ödəniş mərhələsi yaradın
   stage = PaymentStage(
       title="Premium Giriş",
       description="30 gün üçün premium funksiyaları açın",
       price=25,
   )
   neonpay.create_payment_stage("premium_access", stage)
   
   # Ödənişləri idarə edin
   @neonpay.on_payment
   async def handle_payment(result):
       if result.status == PaymentStatus.COMPLETED:
           await app.send_message(
               result.user_id, 
               f"Təşəkkürlər! Premium girişiniz indi aktivdir! 🎉"
           )
   
   @app.on_message(filters.command("buy"))
   async def buy_handler(client, message):
       await neonpay.send_payment(message.from_user.id, "premium_access")
   
   app.run()

pyTelegramBotAPI İnteqrasiyası
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from telebot import TeleBot
   from neonpay.factory import create_neonpay
   from neonpay.core import PaymentStage, PaymentStatus
   
   bot = TeleBot("SIZIN_TOKEN")
   neonpay = create_neonpay(bot_instance=bot)
   
   # Ödəniş mərhələsi yaradın
   stage = PaymentStage(
       title="Premium Giriş",
       description="30 gün üçün premium funksiyaları açın",
       price=25,
   )
   neonpay.create_payment_stage("premium_access", stage)
   
   # Ödənişləri idarə edin
   @neonpay.on_payment
   async def handle_payment(result):
       if result.status == PaymentStatus.COMPLETED:
           bot.send_message(
               result.user_id, 
               f"Təşəkkürlər! Premium girişiniz indi aktivdir! 🎉"
           )
   
   @bot.message_handler(commands=['buy'])
   def buy_handler(message):
       import asyncio
       asyncio.run(neonpay.send_payment(message.from_user.id, "premium_access"))
   
   bot.infinity_polling()

Əsas Anlayışlar
---------------

Ödəniş Mərhələləri
~~~~~~~~~~~~~~~~~~~

Ödəniş mərhələləri istifadəçilərin nə aldığını müəyyən edir:

.. code-block:: python

   stage = PaymentStage(
       title="Məhsul Adı",           # Tələb olunan: Görünən ad
       description="Məhsul təfərrüatları",  # Tələb olunan: Təsvir
       price=100,                     # Tələb olunan: Ulduzlarla qiymət
       label="İndi Al",               # İstəyə bağlı: Düymə etiketi
       photo_url="https://...",       # İstəyə bağlı: Məhsul şəkli
       payload={"custom": "data"},    # İstəyə bağlı: Fərdi məlumatlar
       start_parameter="ref_code"     # İstəyə bağlı: Dərin bağlantı
   )

Ödəniş Nəticələri
~~~~~~~~~~~~~~~~~~

Ödənişlər tamamlandıqda, `PaymentResult` alırsınız:

.. code-block:: python

   @neonpay.on_payment
   async def handle_payment(result: PaymentResult):
       print(f"İstifadəçi ID: {result.user_id}")
       print(f"Məbləğ: {result.amount}")
       print(f"Valyuta: {result.currency}")
       print(f"Status: {result.status}")
       print(f"Metadata: {result.metadata}")

Xəta İdarəetməsi
~~~~~~~~~~~~~~~~~

.. code-block:: python

   from neonpay import NeonPayError, PaymentError
   
   try:
       await neonpay.send_payment(user_id, "stage_id")
   except PaymentError as e:
       print(f"Ödəniş uğursuz: {e}")
   except NeonPayError as e:
       print(f"Sistem xətası: {e}")

API İstinadı
------------

NeonPayCore Sinifi
~~~~~~~~~~~~~~~~~~

Metodlar:

- `create_payment_stage(stage_id: str, stage: PaymentStage)` - Ödəniş mərhələsi yaradın
- `get_payment_stage(stage_id: str)` - ID-yə görə ödəniş mərhələsini alın
- `list_payment_stages()` - Bütün ödəniş mərhələlərini alın
- `remove_payment_stage(stage_id: str)` - Ödəniş mərhələsini silin
- `send_payment(user_id: int, stage_id: str)` - Ödəniş hesab-fakturası göndərin
- `on_payment(callback)` - Ödəniş callback-ini qeydiyyatdan keçirin
- `get_stats()` - Sistem statistikalarını alın

PaymentStage Sinifi
~~~~~~~~~~~~~~~~~~~

Parametrlər:

- `title: str` - Ödəniş başlığı (tələb olunan)
- `description: str` - Ödəniş təsviri (tələb olunan)
- `price: int` - Telegram Stars-da qiymət (tələb olunan)
- `label: str` - Düymə etiketi (default: "Ödəniş")
- `photo_url: str` - Məhsul şəkli URL (istəyə bağlı)
- `payload: dict` - Fərdi məlumatlar (istəyə bağlı)
- `start_parameter: str` - Dərin bağlantı parametri (istəyə bağlı)

PaymentResult Sinifi
~~~~~~~~~~~~~~~~~~~~

Atributlar:

- `user_id: int` - Ödəniş edən istifadəçi
- `amount: int` - Ödəniş məbləği
- `currency: str` - Ödəniş valyutası (XTR)
- `status: PaymentStatus` - Ödəniş statusu
- `transaction_id: str` - Tranzaksiya ID (istəyə bağlı)
- `metadata: dict` - Fərdi metadata

Real Dünya Nümunələri
---------------------

Bütün nümunələr **real işləyən botlar** əsasında hazırlanmışdır və istehsala hazırdır. Tam implementasiyalar üçün nümunələr qovluğuna baxın.

Donasiya Botu
~~~~~~~~~~~~~~

.. code-block:: python

   from neonpay.factory import create_neonpay
   from neonpay.core import PaymentStage, PaymentStatus
   
   # Donasiya seçimləri
   DONATE_OPTIONS = [
       {"amount": 1, "symbol": "⭐", "desc": "1⭐ dəstək: Bot server xərcləri üçün istifadə olunacaq"},
       {"amount": 10, "symbol": "⭐", "desc": "10⭐ dəstək: Yeni funksiyaların inkişafı üçün xərclənəcək"},
       {"amount": 50, "symbol": "🌟", "desc": "50⭐ böyük dəstək: Bot inkişafı və təbliği üçün istifadə olunacaq"},
   ]
   
   neonpay = create_neonpay(bot_instance=bot)
   
   # Donasiya mərhələləri yaradın
   for option in DONATE_OPTIONS:
       neonpay.create_payment_stage(
           f"donate_{option['amount']}",
           PaymentStage(
               title=f"Dəstək {option['amount']}{option['symbol']}",
               description=option["desc"],
               price=option["amount"],
           ),
       )
   
   # Donasiyaları idarə edin
   @neonpay.on_payment
   async def handle_payment(result):
       if result.status == PaymentStatus.COMPLETED:
           if result.stage_id.startswith("donate_"):
               await bot.send_message(
                   result.user_id,
                   f"Təşəkkürlər! Dəstəyiniz: {result.amount}⭐ ❤️\n"
                   f"Dəstəyiniz botun işləməsində kömək edir!"
               )

Rəqəmsal Mağaza
~~~~~~~~~~~~~~~~

.. code-block:: python

   # Rəqəmsal məhsullar
   DIGITAL_PRODUCTS = [
       {
           "id": "premium_access",
           "title": "Premium Giriş",
           "description": "30 gün üçün bütün premium funksiyaları açın",
           "price": 25,
           "symbol": "👑"
       },
       {
           "id": "custom_theme",
           "title": "Fərdi Tema",
           "description": "Şəxsi bot teması və rəngləri",
           "price": 15,
           "symbol": "🎨"
       },
   ]
   
   # Məhsul mərhələləri yaradın
   for product in DIGITAL_PRODUCTS:
       neonpay.create_payment_stage(
           product["id"],
           PaymentStage(
               title=f"{product['symbol']} {product['title']}",
               description=product["description"],
               price=product["price"],
           ),
       )
   
   # Məhsul alışlarını idarə edin
   @neonpay.on_payment
   async def handle_payment(result):
       if result.status == PaymentStatus.COMPLETED:
           if not result.stage_id.startswith("donate_"):
               product = next((p for p in DIGITAL_PRODUCTS if p["id"] == result.stage_id), None)
               if product:
                   await bot.send_message(
                       result.user_id,
                       f"🎉 Alış uğurlu!\n\n"
                       f"Məhsul: {product['symbol']} {product['title']}\n"
                       f"Qiymət: {product['price']}⭐\n\n"
                       f"Rəqəmsal məhsulunuz aktivləşdirildi!\n"
                       f"Alışınız üçün təşəkkürlər! 🚀"
                   )

Ən Yaxşı Təcrübələr
-------------------

1. Ödəniş Məlumatlarını Doğrulayın
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   @neonpay.on_payment
   async def handle_payment(result):
       # Ödəniş məbləğini yoxlayın
       expected_amount = get_expected_amount(result.metadata)
       if result.amount != expected_amount:
           logger.warning(f"Məbləğ uyğunsuzluğu: gözlənilən {expected_amount}, alınan {result.amount}")
           return
       
       # Ödənişi emal edin
       await process_payment(result)

2. Xətaları Zərif Şəkildə İdarə Edin
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   async def safe_send_payment(user_id, stage_id):
       try:
           await neonpay.send_payment(user_id, stage_id)
       except PaymentError as e:
           await bot.send_message(user_id, f"Ödəniş uğursuz: {e}")
       except Exception as e:
           logger.error(f"Gözlənilməz xəta: {e}")
           await bot.send_message(user_id, "Nəsə səhv getdi. Yenidən cəhd edin.")

3. Mənalı Mərhələ ID-lərindən İstifadə Edin
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Yaxşı
   neonpay.create_payment_stage("premium_monthly_subscription", stage)
   neonpay.create_payment_stage("coffee_large_size", stage)
   
   # Pis
   neonpay.create_payment_stage("stage1", stage)
   neonpay.create_payment_stage("payment", stage)

4. Ödəniş Hadisələrini Qeyd Edin
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   import logging
   
   logger = logging.getLogger(__name__)
   
   @neonpay.on_payment
   async def handle_payment(result):
       logger.info(f"Ödəniş alındı: {result.user_id} {result.amount} ulduz ödədi")
       
       try:
           await process_payment(result)
           logger.info(f"İstifadəçi {result.user_id} üçün ödəniş uğurla emal edildi")
       except Exception as e:
           logger.error(f"İstifadəçi {result.user_id} üçün ödənişi emal etmək uğursuz: {e}")

İstehsal Yerləşdirməsi
---------------------

1. Mühit Dəyişənləri
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   import os
   
   # Həssas məlumatları təhlükəsiz saxlayın
   BOT_TOKEN = os.getenv("BOT_TOKEN")
   WEBHOOK_URL = os.getenv("WEBHOOK_URL")
   DATABASE_URL = os.getenv("DATABASE_URL")

2. Verilənlər Bazası İnteqrasiyası
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Yaddaşda saxlanma əvəzinə verilənlər bazasından istifadə edin
   import asyncpg
   
   async def save_payment(user_id: int, amount: int, stage_id: str):
       conn = await asyncpg.connect(DATABASE_URL)
       await conn.execute(
           "INSERT INTO payments (user_id, amount, stage_id, created_at) VALUES ($1, $2, $3, NOW())",
           user_id, amount, stage_id
       )
       await conn.close()

3. Xəta Monitorinqi
~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   import logging
   from logging.handlers import RotatingFileHandler
   
   # Logging konfiqurasiyası
   logging.basicConfig(
       level=logging.INFO,
       format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
       handlers=[
           RotatingFileHandler("bot.log", maxBytes=10*1024*1024, backupCount=5),
           logging.StreamHandler()
       ]
   )

4. Sağlamlıq Yoxlamaları
~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   @router.message(Command("status"))
   async def status_command(message: Message):
       """Sağlamlıq yoxlama endpoint-i"""
       stats = neonpay.get_stats()
       status_text = (
           f"📊 **Bot Statusu**\n\n"
           f"✅ Status: Onlayn\n"
           f"💫 Ödəniş sistemi: Aktiv\n"
           f"🔧 Versiya: 2.0\n"
           f"📈 Ödəniş mərhələləri: {stats['total_stages']}\n"
           f"🔄 Callback-lər: {stats['registered_callbacks']}\n\n"
           f"Bu pulsuz botu istifadə etdiyiniz üçün təşəkkürlər!"
       )
       await message.answer(status_text)

5. Webhook Quraşdırması (Raw API üçün)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from aiohttp import web
   
   async def webhook_handler(request):
       """Gələn webhook yeniləmələrini idarə edin"""
       try:
           data = await request.json()
           
           # Yeniləməni emal edin
           await process_update(data)
           
           return web.Response(text="OK")
       except Exception as e:
           logger.error(f"Webhook xətası: {e}")
           return web.Response(text="Xəta", status=500)
   
   app = web.Application()
   app.router.add_post("/webhook", webhook_handler)

Problemlərin Həlli
------------------

Ümumi Problemlər
~~~~~~~~~~~~~~~~~

1. "Ödəniş mərhələsi tapılmadı"

.. code-block:: python

   # Mərhələnin mövcud olub-olmadığını yoxlayın
   stage = neonpay.get_payment_stage("my_stage")
   if not stage:
       print("Mərhələ mövcud deyil!")
       
   # Bütün mərhələləri siyahıya alın
   stages = neonpay.list_payment_stages()
   print(f"Mövcud mərhələlər: {list(stages.keys())}")

2. "Hesab-faktura göndərmək uğursuz"

- Bot tokeninin düzgün olduğunu yoxlayın
- İstifadəçinin botu başlatdığını yoxlayın
- İstifadəçi ID-sinin etibarlı olduğunu yoxlayın
- Ödəniş mərhələsi konfiqurasiyasını yoxlayın

3. Ödəniş callback-ləri işləmir

.. code-block:: python

   # Setup çağrıldığından əmin olun
   await neonpay.setup()
   
   # Handler-lərin qeydiyyatdan keçdiyini yoxlayın
   stats = neonpay.get_stats()
   print(f"Qeydiyyatdan keçmiş callback-lər: {stats['registered_callbacks']}")

Debug Rejimi
~~~~~~~~~~~~~

.. code-block:: python

   import logging
   
   # Debug logging-i aktivləşdirin
   logging.basicConfig(level=logging.DEBUG)
   logging.getLogger("neonpay").setLevel(logging.DEBUG)

Dəstək
-------

Kömək Almaq
~~~~~~~~~~~~

Köməyə ehtiyacınız varsa:

1. 📚 **Sənədlər**: Tam işləyən nümunələr üçün nümunələr qovluğuna baxın
2. 💬 **İcma**: Telegram icmamıza qoşulun
3. 🐛 **Problemlər**: GitHub-da problem açın
4. 📧 **Email**: Dəstək üçün support@neonpay.com-a müraciət edin
5. 💬 **Telegram**: @neonsahib-ə müraciət edin

Resurslar
~~~~~~~~~

- 📖 **Tam Nümunələr**: examples/ - İstehsala hazır bot nümunələri
- 🔧 **API İstinadı**: API.md - Tam API sənədləri
- 🔒 **Təhlükəsizlik**: SECURITY.md - Təhlükəsizlik ən yaxşı təcrübələri
- 📝 **Dəyişikliklər**: CHANGELOG.md - Versiya tarixi

Sürətli Keçidlər
~~~~~~~~~~~~~~~~~

- 🚀 **Başlanğıc**: Sürətli Başlanğıc Bələdçisi
- 📚 **Nümunələr**: Real Dünya Nümunələri
- 🏗️ **Yerləşdirmə**: İstehsal Yerləşdirməsi
- 🐛 **Problemlərin Həlli**: Ümumi Problemlər

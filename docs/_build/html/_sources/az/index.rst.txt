NEONPAY Sənədləri (Azərbaycan)
===============================

NEONPAY-ın tam sənədlərinə xoş gəlmisiniz. Bu bələdçi Telegram Stars ödənişlərini botunuza tez və effektiv şəkildə inteqrasiya etməyə kömək edəcək.

.. toctree::
   :maxdepth: 2
   :caption: Mündəricat:

   README
   API
   FAQ
   SECURITY

Xüsusiyyətlər
-------------

* **Çoxlu Freymvork Dəstəyi**: Aiogram, Pyrogram, python-telegram-bot və digərləri ilə işləyir
* **Telegram Stars İnteqrasiyası**: Telegram Stars ödənişləri üçün yerli dəstək
* **Təhlükəsizlik**: Daxili təhlükəsizlik funksiyaları və doğrulama
* **Asan İnteqrasiya**: Sürətli tətbiq üçün sadə API
* **Hərtərəfli Sənədlər**: Ətraflı bələdçilər və nümunələr

Sürətli Başlanğıc
-----------------

NEONPAY-ı quraşdırın:

.. code-block:: bash

   pip install neonpay

Aiogram ilə əsas istifadə:

.. code-block:: python

   from neonpay.factory import create_neonpay
   from neonpay.core import PaymentStage, PaymentStatus
   from aiogram import Bot, Dispatcher
   
   bot = Bot(token="SIZIN_TOKEN")
   dp = Dispatcher()
   
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

Dəstəklənən Dillər
------------------

* :doc:`English <../en/README>`
* :doc:`Русский <../ru/README>`
* :doc:`Azərbaycan <../az/README>` (Cari)

İndekslər və Cədvəllər
======================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

NEONPAY Documentation (English)
================================

Welcome to the complete NEONPAY documentation. This guide will help you integrate Telegram Stars payments into your bot quickly and efficiently.

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   README
   API
   FAQ
   SECURITY

Features
--------

* **Multi-framework Support**: Works with Aiogram, Pyrogram, python-telegram-bot, and more
* **Telegram Stars Integration**: Native support for Telegram Stars payments
* **Security**: Built-in security features and validation
* **Easy Integration**: Simple API for quick implementation
* **Comprehensive Documentation**: Detailed guides and examples

Quick Start
-----------

Install NEONPAY:

.. code-block:: bash

   pip install neonpay

Basic usage with Aiogram:

.. code-block:: python

   from neonpay.factory import create_neonpay
   from neonpay.core import PaymentStage, PaymentStatus
   from aiogram import Bot, Dispatcher
   
   bot = Bot(token="YOUR_BOT_TOKEN")
   dp = Dispatcher()
   
   neonpay = create_neonpay(bot_instance=bot, dispatcher=dp)
   
   # Create payment stage
   stage = PaymentStage(
       title="Premium Access",
       description="Unlock premium features for 30 days",
       price=25,
   )
   neonpay.create_payment_stage("premium_access", stage)
   
   # Handle payments
   @neonpay.on_payment
   async def handle_payment(result):
       if result.status == PaymentStatus.COMPLETED:
           await bot.send_message(
               result.user_id, 
               f"Thank you! Your premium access is now active! 🎉"
           )

Supported Languages
-------------------

* :doc:`English <../en/README>` (Current)
* :doc:`Russian <../ru/README>`
* :doc:`Azerbaijani <../az/README>`

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

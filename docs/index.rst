NEONPAY Documentation v2.6.0
==============================

Welcome to NEONPAY documentation! NEONPAY is a comprehensive payment processing library for Telegram bots with support for multiple bot frameworks and enterprise features.

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   en/README
   en/API
   en/FAQ
   en/SECURITY
   NEW_FEATURES_v2.6.0
   CHANGELOG

Features
--------

Core Features:
* **Multi-framework Support**: Works with Aiogram, Pyrogram, python-telegram-bot, and more
* **Telegram Stars Integration**: Native support for Telegram Stars payments
* **Security**: Built-in security features and validation
* **Easy Integration**: Simple API for quick implementation

🆕 New in v2.6.0:
* **Web Analytics Dashboard**: Real-time bot performance monitoring
* **Notification System**: Multi-channel notifications (Email, Telegram, SMS, Webhook)
* **Backup & Restore**: Automated data protection and recovery
* **Template System**: Pre-built bot templates and generators
* **Multi-Bot Analytics**: Network-wide performance tracking
* **Event Collection**: Centralized event management and processing
* **Web Sync Interface**: Multi-bot synchronization via REST API

Quick Start
-----------

Install NEONPAY:

.. code-block:: bash

   pip install neonpay

Basic usage with Aiogram:

.. code-block:: python

   from neonpay import NeonPay
   from aiogram import Bot, Dispatcher
   
   bot = Bot(token="YOUR_BOT_TOKEN")
   dp = Dispatcher()
   
   neonpay = NeonPay(bot)
   
   @dp.message_handler(commands=['donate'])
   async def send_donation(message):
       await neonpay.send_donate(
           user_id=message.from_user.id,
           amount=100,  # 100 stars
           label="Support Development",
           title="Donation",
           description="Thank you for supporting our project!"
       )

Supported Languages
-------------------

* :doc:`English <en/README>`
* :doc:`Russian <ru/README>`
* :doc:`Azerbaijani <az/README>`

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

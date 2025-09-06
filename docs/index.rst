NEONPAY Documentation
=====================

Welcome to NEONPAY documentation! NEONPAY is a comprehensive payment processing library for Telegram bots with support for multiple bot frameworks.

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   en/README
   CHANGELOG

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

Documentation Changelog
========================

Version 2.0 - Complete Documentation Update
--------------------------------------------

Major Updates
~~~~~~~~~~~~~

All documentation has been completely rewritten and updated to reflect the new NEONPAY 2.0 API and real-world examples.

Updated Documentation
~~~~~~~~~~~~~~~~~~~~~~

1. English Documentation (docs/en/)
   - ✅ README.md - Complete rewrite with new API
   - ✅ API.md - Updated with factory function and new methods
   - ✅ SECURITY.md - New comprehensive security guide

2. Russian Documentation (docs/ru/)
   - ✅ README.md - Updated with new API and examples
   - ✅ API.md - Updated with factory function and new methods

3. Azerbaijani Documentation (docs/az/)
   - ✅ README.md - Updated with new API and examples
   - ✅ API.md - Updated with factory function and new methods

New Features
~~~~~~~~~~~~

- 🚀 **Factory Function**: New `create_neonpay()` function for automatic adapter detection
- 🔧 **Simplified API**: Cleaner, more intuitive API design
- 📚 **Real Examples**: All examples based on production bots
- 🛡️ **Security Guide**: Comprehensive security best practices
- 🌍 **Multi-language**: Updated documentation in English, Russian, and Azerbaijani

Breaking Changes
~~~~~~~~~~~~~~~~~

- ⚠️ **API Changes**: Some method signatures have changed
- 🔄 **Import Changes**: New import structure with factory function
- 📦 **Dependencies**: Updated dependency requirements

Migration Guide
~~~~~~~~~~~~~~~

For users upgrading from NEONPAY 1.x:

1. Update imports:

.. code-block:: python

   # Old way
   from neonpay import NeonPayCore
   
   # New way
   from neonpay.factory import create_neonpay

2. Update initialization:

.. code-block:: python

   # Old way
   neonpay = NeonPayCore(bot_instance=bot)
   
   # New way
   neonpay = create_neonpay(bot_instance=bot)

3. Update method calls:

.. code-block:: python

   # Old way
   neonpay.create_stage("stage_id", stage_data)
   
   # New way
   neonpay.create_payment_stage("stage_id", stage_data)

Version 1.0 - Initial Release
------------------------------

Initial Documentation
~~~~~~~~~~~~~~~~~~~~~~

- 📖 Basic documentation structure
- 🔧 API reference
- 📝 Installation guide
- 💡 Basic examples

Supported Frameworks
~~~~~~~~~~~~~~~~~~~~

- ✅ Aiogram
- ✅ Pyrogram
- ✅ python-telegram-bot
- ✅ pyTelegramBotAPI
- ✅ Raw API

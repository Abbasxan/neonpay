NEONPAY Complete Guide v2.6.0
===============================

Welcome to the complete NEONPAY documentation! This comprehensive guide covers all features, from basic usage to advanced enterprise capabilities.

Table of Contents
-----------------

1. `Quick Start <#quick-start>`_
2. `Core Features <#core-features>`_
3. `New Features v2.6.0 <#new-features-v260>`_
4. `Advanced Features <#advanced-features>`_
5. `Multi-Bot Analytics <#multi-bot-analytics>`_
6. `Multi-Bot Synchronization <#multi-bot-synchronization>`_
7. `API Reference <#api-reference>`_
8. `Best Practices <#best-practices>`_
9. `Production Deployment <#production-deployment>`_
10. `Troubleshooting <#troubleshooting>`_

Quick Start
-----------

Installation
~~~~~~~~~~~~

.. code-block:: bash

   pip install neonpay

Basic Usage
~~~~~~~~~~~

.. code-block:: python

   from neonpay import create_neonpay, PaymentStage, PaymentStatus

   # Automatic adapter detection
   neonpay = create_neonpay(bot_instance=your_bot_instance)

   # Create payment stage
   stage = PaymentStage(
       title="Premium Access",
       description="Unlock premium features for 30 days",
       price=25,  # 25 Telegram Stars
   )

   neonpay.create_payment_stage("premium_access", stage)

   # Send payment
   await neonpay.send_payment(user_id=12345, stage_id="premium_access")

   # Handle payments
   @neonpay.on_payment
   async def handle_payment(result):
       if result.status == PaymentStatus.COMPLETED:
           print(f"Received {result.amount} stars from user {result.user_id}")

Core Features
-------------

Library Support
~~~~~~~~~~~~~~~

NEONPAY automatically detects your bot library and creates the appropriate adapter:

- **Pyrogram**: Full async support
- **Aiogram**: Native integration with dispatcher
- **python-telegram-bot**: Complete PTB support
- **pyTelegramBotAPI**: Telebot compatibility
- **Raw Bot API**: Direct API integration

Payment Stages
~~~~~~~~~~~~~~

Payment stages define what users are buying:

.. code-block:: python

   stage = PaymentStage(
       title="Product Name",           # Required: Display name
       description="Product details",  # Required: Description
       price=100,                     # Required: Price in stars
       label="Buy Now",               # Optional: Button label
       photo_url="https://...",       # Optional: Product image
       payload={"custom": "data"},    # Optional: Custom data
       start_parameter="ref_code"     # Optional: Deep linking
   )

Error Handling
~~~~~~~~~~~~~~

.. code-block:: python

   from neonpay import NeonPayError, PaymentError

   try:
       await neonpay.send_payment(user_id, "stage_id")
   except PaymentError as e:
       print(f"Payment failed: {e}")
   except NeonPayError as e:
       print(f"System error: {e}")

New Features v2.6.0
-------------------

Web Analytics Dashboard
~~~~~~~~~~~~~~~~~~~~~~~

Real-time bot performance monitoring via web interface.

Setup
^^^^^

.. code-block:: python

   from neonpay import MultiBotAnalyticsManager, run_analytics_server

   # Initialize analytics manager
   analytics = MultiBotAnalyticsManager()

   # Start web dashboard
   await run_analytics_server(
       analytics, 
       host="localhost", 
       port=8081
   )

Access Dashboard
^^^^^^^^^^^^^^^^

Open your browser and navigate to: ``http://localhost:8081``

Features
^^^^^^^^

- Real-time payment analytics
- Revenue tracking
- User behavior analysis
- Performance metrics
- Export capabilities

Notification System
~~~~~~~~~~~~~~~~~~~

Multi-channel notification system for administrators.

Setup
^^^^^

.. code-block:: python

   from neonpay import NotificationManager, NotificationConfig

   # Configure notifications
   config = NotificationConfig(
       # Telegram notifications
       telegram_bot_token="YOUR_ADMIN_BOT_TOKEN",
       telegram_admin_chat_id="YOUR_CHAT_ID",
       
       # Email notifications
       smtp_host="smtp.gmail.com",
       smtp_port=587,
       smtp_username="your_email@gmail.com",
       smtp_password="your_app_password",
       
       # Webhook notifications
       webhook_url="https://your-webhook-url.com/notifications"
   )

   # Initialize notification manager
   notifications = NotificationManager(config, enable_notifications=True)

Sending Notifications
^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   from neonpay import NotificationMessage, NotificationType, NotificationPriority

   # Create notification message
   message = NotificationMessage(
       notification_type=NotificationType.TELEGRAM,
       recipient="admin_chat_id",
       subject="Payment Alert",
       body="New payment received: 100⭐",
       priority=NotificationPriority.HIGH
   )

   # Send notification
   await notifications.send_notification(message)

Notification Types
^^^^^^^^^^^^^^^^^^

- **Email**: SMTP-based email notifications
- **Telegram**: Bot-to-chat notifications
- **SMS**: SMS notifications (requires provider)
- **Webhook**: HTTP webhook notifications
- **Slack**: Slack channel notifications

Backup & Restore System
~~~~~~~~~~~~~~~~~~~~~~~

Automated data protection and recovery.

Setup
^^^^^

.. code-block:: python

   from neonpay import BackupManager, BackupConfig, BackupType

   # Configure backup
   backup_config = BackupConfig(
       backup_type=BackupType.JSON,
       backup_path="./backups/",
       schedule="daily",
       max_backups=30
   )

   # Initialize backup manager
   backup_manager = BackupManager(backup_config)

Creating Backups
^^^^^^^^^^^^^^^^

.. code-block:: python

   # Manual backup
   backup_info = await backup_manager.create_backup(
       description="Weekly backup"
   )

   # Scheduled backups
   await backup_manager.start_scheduled_backups()

Restoring Data
^^^^^^^^^^^^^^

.. code-block:: python

   # List available backups
   backups = await backup_manager.list_backups()

   # Restore from backup
   await backup_manager.restore_backup(backup_id="backup_2025_09_07")

Backup Types
^^^^^^^^^^^^

- **JSON**: Human-readable JSON format
- **SQLite**: SQLite database format
- **PostgreSQL**: PostgreSQL database format

Template System
~~~~~~~~~~~~~~~

Pre-built bot templates and generators.

Available Templates
^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   from neonpay import TemplateManager

   templates = TemplateManager()

   # List available templates
   available_templates = await templates.list_templates()
   print(available_templates)

Generate Bot from Template
^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   # Generate digital store bot
   await templates.generate_template(
       template_name="digital_store",
       output_file="my_store_bot.py",
       custom_data={
           "store_name": "My Digital Store",
           "products": [
               {"name": "Premium Access", "price": 25},
               {"name": "Custom Theme", "price": 15}
           ]
       }
   )

Creating Custom Templates
^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   from neonpay import TemplateProduct, TemplateConfig

   # Define template products
   products = [
       TemplateProduct(
           name="Premium Access",
           description="Unlock all premium features",
           price=25,
           category="subscription"
       ),
       TemplateProduct(
           name="Custom Theme",
           description="Personalized bot theme",
           price=15,
           category="customization"
       )
   ]

   # Create template configuration
   template_config = TemplateConfig(
       name="my_custom_template",
       description="My custom bot template",
       products=products
   )

   # Save template
   await templates.create_template(template_config)

CLI Commands
~~~~~~~~~~~~

New CLI commands for all enterprise features.

Analytics Commands
^^^^^^^^^^^^^^^^^^

.. code-block:: bash

   # Start analytics dashboard
   neonpay analytics --start-dashboard --port 8081

   # Export analytics data
   neonpay analytics --export --format json --output analytics.json

   # Get analytics summary
   neonpay analytics --summary --period 30days

Backup Commands
^^^^^^^^^^^^^^^

.. code-block:: bash

   # Create backup
   neonpay backup create --description "Weekly backup"

   # List backups
   neonpay backup list

   # Restore backup
   neonpay backup restore --backup-id backup_2025_09_07

Template Commands
^^^^^^^^^^^^^^^^^

.. code-block:: bash

   # List available templates
   neonpay template list

   # Generate bot from template
   neonpay template generate digital_store --output my_bot.py

   # Create custom template
   neonpay template create --name my_template --products products.json

Notification Commands
^^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

   # Test notifications
   neonpay notifications test --type telegram \
     --telegram-bot-token ADMIN_BOT_TOKEN \
     --telegram-chat-id ADMIN_CHAT_ID

   # Send notification
   neonpay notifications send --type email \
     --recipient admin@example.com \
     --subject "Test" \
     --body "Test notification"

Migration from v2.5.x
~~~~~~~~~~~~~~~~~~~~~

Import Updates
^^^^^^^^^^^^^^

.. code-block:: python

   # Old imports (still work)
   from neonpay import NeonPayCore, PaymentStage

   # New imports (optional)
   from neonpay import (
       MultiBotAnalyticsManager,
       NotificationManager,
       BackupManager,
       TemplateManager,
       CentralEventCollector,
       MultiBotSyncManager
   )

Configuration Updates
^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   # Existing code continues to work
   neonpay = NeonPayCore(adapter)

   # New features are optional
   analytics = MultiBotAnalyticsManager()  # Optional
   notifications = NotificationManager(config)  # Optional

CLI Updates
^^^^^^^^^^^

.. code-block:: bash

   # Existing commands work as before
   neonpay --help

   # New commands are available
   neonpay analytics --help
   neonpay backup --help
   neonpay template --help
   neonpay notifications --help

Advanced Features
----------------

Analytics System
~~~~~~~~~~~~~~~

The analytics system provides comprehensive insights into your bot's performance and user behavior.

Features
^^^^^^^^

- **Revenue Tracking**: Monitor total revenue, transaction counts, and average transaction values
- **Conversion Analysis**: Track conversion rates and identify drop-off points in your sales funnel
- **Product Performance**: See which products are performing best
- **User Insights**: Understand user behavior and engagement patterns
- **Real-time Monitoring**: Track events as they happen
- **Export Options**: Export data in JSON, CSV, or table format

Usage
^^^^^

.. code-block:: python

   from neonpay import AnalyticsManager, AnalyticsPeriod

   # Initialize analytics
   analytics = AnalyticsManager(enable_analytics=True)

   # Track events
   analytics.track_event("product_view", user_id=12345, stage_id="premium_access")
   analytics.track_event("payment_completed", user_id=12345, amount=100, stage_id="premium_access")

   # Get analytics data
   revenue_data = analytics.get_revenue_analytics(AnalyticsPeriod.DAY, days=30)
   conversion_data = analytics.get_conversion_analytics(AnalyticsPeriod.DAY, days=30)
   product_data = analytics.get_product_analytics(AnalyticsPeriod.DAY, days=30)

   # Generate comprehensive report
   report = analytics.get_dashboard_report(AnalyticsPeriod.DAY, days=30)
   print(json.dumps(report, indent=2))

CLI Usage
^^^^^^^^^

.. code-block:: bash

   # Get analytics for last 30 days
   neonpay analytics --period 30days --format json

   # Export analytics to file
   neonpay analytics --period 7days --format csv --output analytics.csv

Notification System
~~~~~~~~~~~~~~~~~~

The notification system allows you to send notifications through multiple channels when important events occur.

Supported Channels
^^^^^^^^^^^^^^^^^^

- **Email**: SMTP-based email notifications
- **Telegram**: Direct messages to admin chat
- **SMS**: Text message notifications (requires provider integration)
- **Webhook**: HTTP POST to external services
- **Slack**: Messages to Slack channels
- **Discord**: Messages to Discord channels

Features
^^^^^^^^

- **Template System**: Pre-built notification templates for common events
- **Priority Levels**: Low, Normal, High, Critical priority levels
- **Multiple Recipients**: Send to multiple channels simultaneously
- **Custom Templates**: Create your own notification templates
- **Event-driven**: Automatic notifications based on payment events

Usage
^^^^^

.. code-block:: python

   from neonpay import NotificationManager, NotificationConfig, NotificationType

   # Configure notifications
   config = NotificationConfig(
       smtp_host="smtp.gmail.com",
       smtp_port=587,
       smtp_username="your_email@gmail.com",
       smtp_password="your_password",
       telegram_bot_token="YOUR_BOT_TOKEN",
       telegram_admin_chat_id="YOUR_CHAT_ID",
       webhook_url="https://your-webhook-url.com/notifications"
   )

   notifications = NotificationManager(config, enable_notifications=True)

   # Send notification using template
   await notifications.send_template_notification(
       "payment_completed",
       recipient="admin@example.com",
       variables={
           "user_id": 12345,
           "amount": 100,
           "product_name": "Premium Access"
       },
       notification_type=NotificationType.EMAIL
   )

   # Send custom notification
   await notifications.send_notification(
       NotificationMessage(
           notification_type=NotificationType.TELEGRAM,
           recipient="admin_chat_id",
           subject="🚨 Security Alert",
           body="Suspicious activity detected for user 12345",
           priority=NotificationPriority.HIGH
       )
   )

CLI Usage
^^^^^^^^^

.. code-block:: bash

   # Test notifications
   neonpay notifications test --type telegram --recipient "your_chat_id"

   # Send custom notification
   neonpay notifications send --type email --recipient "admin@example.com" \
     --subject "Daily Report" --body "Revenue: 1000 stars"

Template System
~~~~~~~~~~~~~~~

The template system provides pre-built bot configurations for common use cases, making it easy to get started quickly.

Available Templates
^^^^^^^^^^^^^^^^^^^

- **Digital Store**: Complete e-commerce bot with products and categories
- **Subscription Service**: Subscription-based service with multiple plans
- **Donation Bot**: Bot for accepting donations and support
- **Course Platform**: Online learning platform with courses
- **Premium Features**: Bot with premium feature unlocks

Features
^^^^^^^^

- **Ready-to-use**: Pre-configured payment stages and bot logic
- **Customizable**: Modify themes, colors, and content
- **Code Generation**: Generate complete bot code from templates
- **Multiple Libraries**: Support for Aiogram, Pyrogram, and more
- **Export Options**: Export templates in JSON format

Usage
^^^^^

.. code-block:: python

   from neonpay import TemplateManager, TemplateType, ThemeColor

   # Initialize template manager
   templates = TemplateManager()

   # Get available templates
   template_list = templates.list_templates()
   for template in template_list:
       print(f"{template.name}: {template.description}")

   # Use a template
   digital_store = templates.get_template("digital_store")
   if digital_store:
       # Convert to payment stages
       stages = templates.convert_to_payment_stages(digital_store)
       for stage_id, stage in stages.items():
           neonpay.create_payment_stage(stage_id, stage)

   # Generate bot code
   bot_code = templates.generate_bot_code(digital_store, "aiogram")
   with open("generated_bot.py", "w") as f:
       f.write(bot_code)

   # Create custom template
   custom_template = templates.create_custom_template(
       name="My Custom Store",
       description="Custom store template",
       products=[
           TemplateProduct(
               id="custom_product",
               name="Custom Product",
               description="A custom product",
               price=50,
               features=["Feature 1", "Feature 2"]
           )
       ]
   )

CLI Usage
^^^^^^^^^

.. code-block:: bash

   # List available templates
   neonpay template list

   # Generate bot code from template
   neonpay template generate digital_store --library aiogram --output my_bot.py

   # Create custom template
   neonpay template create "My Store" --description "Custom store" --products products.json

Backup System
~~~~~~~~~~~~~

The backup system provides automatic data backup, restoration, and synchronization capabilities.

Features
^^^^^^^^

- **Automatic Backups**: Scheduled backups with configurable intervals
- **Multiple Backup Types**: Full, incremental, and differential backups
- **Compression**: Optional compression to save space
- **Encryption**: Optional encryption for sensitive data
- **Restoration**: Easy restoration from any backup
- **Synchronization**: Sync data between multiple bots
- **Cleanup**: Automatic cleanup of old backups

Usage
^^^^^

.. code-block:: python

   from neonpay import BackupManager, BackupConfig, BackupType

   # Configure backup
   config = BackupConfig(
       backup_directory="./backups",
       max_backups=10,
       compression=True,
       auto_backup=True,
       backup_interval_hours=24
   )

   backup = BackupManager(neonpay, config)

   # Create manual backup
   backup_info = await backup.create_backup(
       backup_type=BackupType.FULL,
       description="Weekly backup"
   )

   # List backups
   backups = backup.list_backups()
   for backup_info in backups:
       print(f"{backup_info.backup_id}: {backup_info.created_at}")

   # Restore from backup
   success = await backup.restore_backup("backup_1234567890")

   # Delete old backup
   await backup.delete_backup("old_backup_id")

CLI Usage
^^^^^^^^^

.. code-block:: bash

   # Create backup
   neonpay backup create --description "Weekly backup" --type full

   # List backups
   neonpay backup list

   # Restore backup
   neonpay backup restore backup_1234567890

   # Delete backup
   neonpay backup delete old_backup_id

CLI Tool
~~~~~~~~

The NEONPAY CLI provides command-line access to all advanced features.

Installation
^^^^^^^^^^^^

.. code-block:: bash

   pip install neonpay[cli]

Available Commands
^^^^^^^^^^^^^^^^^^

.. code-block:: bash

   # Analytics
   neonpay analytics --period 30days --format json
   neonpay analytics --period 7days --format csv --output report.csv

   # Backups
   neonpay backup create --description "Manual backup"
   neonpay backup list
   neonpay backup restore backup_id
   neonpay backup delete backup_id

   # Templates
   neonpay template list
   neonpay template generate digital_store --library aiogram --output bot.py
   neonpay template create "My Store" --description "Custom store"

   # Notifications
   neonpay notifications test --type telegram --recipient "chat_id"
   neonpay notifications send --type email --recipient "admin@example.com" \
     --subject "Alert" --body "Something happened"

Integration Examples
~~~~~~~~~~~~~~~~~~~

Complete Bot with All Features
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   import asyncio
   from neonpay import (
       create_neonpay, PaymentStage, PaymentStatus,
       AnalyticsManager, NotificationManager, NotificationConfig,
       TemplateManager, BackupManager, BackupConfig
   )

   # Initialize bot
   bot = Bot(token="YOUR_BOT_TOKEN")
   dp = Dispatcher()
   neonpay = create_neonpay(bot_instance=bot, dispatcher=dp)

   # Initialize advanced features
   analytics = AnalyticsManager(enable_analytics=True)

   notification_config = NotificationConfig(
       telegram_bot_token="YOUR_BOT_TOKEN",
       telegram_admin_chat_id="YOUR_CHAT_ID"
   )
   notifications = NotificationManager(notification_config, enable_notifications=True)

   templates = TemplateManager()
   backup = BackupManager(neonpay, BackupConfig(auto_backup=True))

   # Setup using template
   digital_store = templates.get_template("digital_store")
   stages = templates.convert_to_payment_stages(digital_store)
   for stage_id, stage in stages.items():
       neonpay.create_payment_stage(stage_id, stage)

   # Enhanced payment handler
   @neonpay.on_payment
   async def handle_payment(result):
       if result.status == PaymentStatus.COMPLETED:
           # Track analytics
           analytics.track_event("payment_completed", result.user_id, 
                               amount=result.amount, stage_id=result.stage_id)
           
           # Send notifications
           await notifications.send_template_notification(
               "payment_completed",
               recipient="admin@example.com",
               variables={
                   "user_id": result.user_id,
                   "amount": result.amount,
                   "product_name": result.stage.title
               }
           )
           
           # Send user confirmation
           await bot.send_message(
               result.user_id,
               f"🎉 Thank you for your purchase!\n"
               f"Product: {result.stage.title}\n"
               f"Amount: {result.amount} stars"
           )

   # Start bot
   async def main():
       dp.include_router(router)
       await dp.start_polling(bot)

   if __name__ == "__main__":
       asyncio.run(main())

Performance Considerations
~~~~~~~~~~~~~~~~~~~~~~~~~

Analytics
^^^^^^^^^

- Events are stored in memory by default (configurable max_events)
- Use `cleanup_old_data()` to remove old analytics data
- Export data regularly to prevent memory issues

Notifications
^^^^^^^^^^^^^

- Notifications are sent asynchronously to avoid blocking
- Use connection pooling for high-volume notifications
- Implement retry logic for failed notifications

Backups
^^^^^^^

- Compression reduces backup size by 60-80%
- Incremental backups are faster for large datasets
- Schedule backups during low-activity periods

Templates
^^^^^^^^^

- Templates are loaded once and cached
- Generated code is optimized for the target library
- Custom templates are stored in memory

Security Best Practices
~~~~~~~~~~~~~~~~~~~~~~~

Analytics
^^^^^^^^^

- Don't store sensitive user data in analytics events
- Use data anonymization for privacy compliance
- Implement data retention policies

Notifications
^^^^^^^^^^^^^

- Use secure channels (HTTPS, TLS) for webhooks
- Implement signature verification for webhook security
- Store credentials securely (environment variables, key vaults)

Backups
^^^^^^^

- Encrypt sensitive backup data
- Store backups in secure locations
- Implement access controls for backup files
- Regular backup integrity checks

Templates
^^^^^^^^^

- Validate template data before processing
- Sanitize user input in custom templates
- Use secure file handling for template exports

Getting Started
~~~~~~~~~~~~~~~

1. **Install NEONPAY with advanced features**:

   .. code-block:: bash

      pip install neonpay[all]

2. **Choose your features**:

   - Analytics for insights
   - Notifications for alerts
   - Templates for quick setup
   - Backups for data safety

3. **Configure your bot**:

   .. code-block:: python

      from neonpay import create_neonpay, AnalyticsManager, NotificationManager
      
      neonpay = create_neonpay(bot_instance=your_bot)
      analytics = AnalyticsManager(enable_analytics=True)
      notifications = NotificationManager(config, enable_notifications=True)

4. **Start tracking and improving**:

   - Monitor analytics for insights
   - Set up notifications for important events
   - Use templates for rapid development
   - Schedule regular backups

The advanced features make NEONPAY not just a payment library, but a complete platform for building and managing Telegram payment bots!

Multi-Bot Analytics
-------------------

**Automatic tracking of all bot events** - this is a revolutionary analytics system that collects data from all synchronized bots in a single center.

What does this give you?
~~~~~~~~~~~~~~~~~~~~~~~~

Before multi-bot analytics:
^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   # Users had to:
   # 1. Set up analytics in bot A (50+ lines)
   # 2. Set up analytics in bot B (50+ lines)
   # 3. Set up analytics in bot C (50+ lines)
   # 4. Collect data from each bot separately
   # 5. Analyze data manually
   # TOTAL: ~200+ lines of code + manual work

After multi-bot analytics:
^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   # Now it's enough:
   from neonpay import MultiBotAnalyticsManager, MultiBotEventCollector, EventCollectorConfig

   # Initialize analytics
   multi_analytics = MultiBotAnalyticsManager(enable_analytics=True)

   # Register bots
   multi_analytics.register_bot("store_bot", "Main Store Bot")
   multi_analytics.register_bot("support_bot", "Support Bot")

   # Set up event collection
   collector_config = EventCollectorConfig(
       central_analytics_url="http://localhost:8081",
       enable_real_time=True,
       enable_batch_collection=True
   )
   event_collector = MultiBotEventCollector(collector_config)

   # ALL events from ALL bots are automatically collected!
   # TOTAL: ~10 lines of code!

Real Benefits
~~~~~~~~~~~~~~

1. Centralized Analytics
^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   # Get analytics for the entire bot network
   network_analytics = multi_analytics.get_network_analytics(days=30)

   print(f"Total revenue: {network_analytics.total_revenue} stars")
   print(f"Total users: {network_analytics.total_users}")
   print(f"Network conversion: {network_analytics.network_conversion_rate:.1f}%")

   # Top bots by revenue
   for bot in network_analytics.top_performing_bots:
       print(f"{bot['bot_name']}: {bot['revenue']} stars")

2. Automatic Event Tracking
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   # Events are automatically tracked:
   # - Product views
   # - Purchases
   # - Promo code usage
   # - Subscriptions
   # - Bot errors
   # - Inter-bot synchronization

   # All events are collected in real-time!

3. Detailed Bot Analytics
^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   # Analytics for a specific bot
   bot_analytics = multi_analytics.get_bot_analytics("store_bot", days=30)

   print(f"Events: {bot_analytics.total_events}")
   print(f"Users: {bot_analytics.total_users}")
   print(f"Revenue: {bot_analytics.total_revenue} stars")
   print(f"Conversion: {bot_analytics.conversion_rate:.1f}%")

   # Events by type
   for event_type, count in bot_analytics.events_by_type.items():
       print(f"{event_type}: {count}")

Setup in 2 Minutes
~~~~~~~~~~~~~~~~~~

Step 1: Installation
^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

   pip install neonpay[analytics,sync]

Step 2: Analytics Setup
^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   from neonpay import (
       MultiBotAnalyticsManager, 
       MultiBotEventCollector, 
       EventCollectorConfig
   )

   # Initialize analytics
   multi_analytics = MultiBotAnalyticsManager(enable_analytics=True)

   # Register bots
   multi_analytics.register_bot("main_bot", "Main Store Bot")
   multi_analytics.register_bot("support_bot", "Support Bot")
   multi_analytics.register_bot("analytics_bot", "Analytics Bot")

Step 3: Event Collection Setup
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   # Event collection configuration
   collector_config = EventCollectorConfig(
       central_analytics_url="http://localhost:8081",
       collection_interval_seconds=30,
       enable_real_time=True,
       enable_batch_collection=True
   )

   # Initialize collector
   event_collector = MultiBotEventCollector(collector_config)

   # Add bots for collection
   event_collector.add_bot("main_bot", "Main Store Bot", "https://main-bot.com")
   event_collector.add_bot("support_bot", "Support Bot", "https://support-bot.com")

Step 4: Launch
^^^^^^^^^^^^^^

.. code-block:: python

   # Start event collection
   await event_collector.start()

   # Track events
   multi_analytics.track_event(
       event_type="payment_completed",
       bot_id="main_bot",
       user_id=12345,
       amount=100,
       product_id="premium_access"
   )

What is Tracked?
~~~~~~~~~~~~~~~~

User Events
^^^^^^^^^^^

- `user_started` - user started the bot
- `user_message` - user sent a message
- `user_callback` - user clicked a button

Product Events
^^^^^^^^^^^^^^

- `product_view` - product view
- `product_click` - product click
- `product_share` - product share

Payment Events
^^^^^^^^^^^^^^

- `payment_started` - payment started
- `payment_completed` - payment completed
- `payment_failed` - payment failed
- `payment_cancelled` - payment cancelled

Promo Events
^^^^^^^^^^^^

- `promo_code_used` - promo code used
- `promo_code_invalid` - invalid promo code

Subscription Events
^^^^^^^^^^^^^^^^^^^

- `subscription_created` - subscription created
- `subscription_renewed` - subscription renewed
- `subscription_expired` - subscription expired
- `subscription_cancelled` - subscription cancelled

Bot Events
^^^^^^^^^^

- `bot_started` - bot started
- `bot_sync` - bot synchronization
- `bot_error` - bot error

Real-time Monitoring
~~~~~~~~~~~~~~~~~~~~

Automatic Event Collection
^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   # Events are collected automatically every 30 seconds
   collector_config = EventCollectorConfig(
       collection_interval_seconds=30,
       enable_real_time=True
   )

   # Real-time events are processed instantly
   await event_collector.receive_realtime_event({
       "event_type": "payment_completed",
       "bot_id": "store_bot",
       "user_id": 12345,
       "amount": 100,
       "timestamp": time.time()
   })

Real-time Monitoring
^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   # Get current statistics
   stats = multi_analytics.get_stats()

   print(f"Registered bots: {stats['registered_bots']}")
   print(f"Total events: {stats['total_events']}")
   print(f"Total users: {stats['total_users']}")

Ready Reports
~~~~~~~~~~~~~

Network Report
^^^^^^^^^^^^^^

.. code-block:: python

   # Get full network report
   report = multi_analytics.get_network_report(days=30)

   print("📊 Network Report:")
   print(f"Bots: {report['network']['total_bots']}")
   print(f"Events: {report['network']['total_events']}")
   print(f"Users: {report['network']['total_users']}")
   print(f"Revenue: {report['network']['total_revenue']} stars")
   print(f"Transactions: {report['network']['total_transactions']}")
   print(f"Conversion: {report['network']['network_conversion_rate']:.1f}%")

Bot Reports
^^^^^^^^^^^

.. code-block:: python

   # Report for each bot
   for bot_id, bot_data in report['bots'].items():
       print(f"\n🤖 {bot_data['bot_name']}:")
       print(f"  Events: {bot_data['total_events']}")
       print(f"  Users: {bot_data['total_users']}")
       print(f"  Revenue: {bot_data['total_revenue']} stars")
       print(f"  Conversion: {bot_data['conversion_rate']:.1f}%")

Data Export
~~~~~~~~~~~

JSON Export
^^^^^^^^^^^

.. code-block:: python

   # Export to JSON
   json_data = multi_analytics.export_network_analytics(
       format_type="json",
       days=30
   )

   with open("analytics.json", "w") as f:
       f.write(json_data)

CSV Export
^^^^^^^^^^

.. code-block:: python

   # Export to CSV
   csv_data = multi_analytics.export_network_analytics(
       format_type="csv",
       days=30
   )

   with open("analytics.csv", "w") as f:
       f.write(csv_data)

CLI Commands
~~~~~~~~~~~~

.. code-block:: bash

   # Network analytics
   neonpay multi-analytics network --period 30days --format table

   # Specific bot analytics
   neonpay multi-analytics bot store_bot --period 7days --format json

   # Data export
   neonpay multi-analytics export --format csv --period 30days --output analytics.csv

   # Analytics status
   neonpay multi-analytics status

Web Interface
~~~~~~~~~~~~~

Starting Analytics Web Server
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   from neonpay.web_analytics import run_analytics_server

   # Start analytics server
   await run_analytics_server(
       multi_analytics,
       event_collector,
       host="0.0.0.0",
       port=8081
   )

Available Endpoints
^^^^^^^^^^^^^^^^^^^

- `POST /analytics/collect` - collect events from bots
- `POST /analytics/realtime` - real-time events
- `GET /analytics/query` - analytics queries
- `GET /analytics/export` - data export
- `GET /analytics/status` - system status

Improvement Statistics
~~~~~~~~~~~~~~~~~~~~~~

Time Savings:
^^^^^^^^^^^^^

- **Analytics Setup**: from 200+ lines to 10 lines (**95% savings**)
- **Data Collection**: from manual to automatic
- **Data Analysis**: from manual to ready reports
- **Monitoring**: from scattered to centralized

Benefits:
^^^^^^^^^

- **Centralization**: all data in one place
- **Real-time**: events in real-time
- **Automation**: no manual work
- **Scalability**: easy to add new bots
- **Export**: data in any format

Real Use Cases
~~~~~~~~~~~~~~

1. Store Network
^^^^^^^^^^^^^^^^

.. code-block:: python

   # Main store + 5 branches
   # Automatically tracked:
   # - Total network revenue
   # - Popular products
   # - Conversion by branches
   # - User behavior

2. Partner Program
^^^^^^^^^^^^^^^^^^

.. code-block:: python

   # Your bot + partner bots
   # Automatically tracked:
   # - Partner sales
   # - Commissions
   # - Partner effectiveness
   # - Overall statistics

3. A/B Testing
^^^^^^^^^^^^^^

.. code-block:: python

   # Bot A (test version) + Bot B (control version)
   # Automatically tracked:
   # - Conversion by versions
   # - Feature popularity
   # - User behavior
   # - Test results

Start Right Now!
~~~~~~~~~~~~~~~~~

.. code-block:: python

   # 1. Install NEONPAY
   pip install neonpay[analytics,sync]

   # 2. Copy this code
   from neonpay import MultiBotAnalyticsManager, MultiBotEventCollector, EventCollectorConfig

   # 3. Initialize analytics
   multi_analytics = MultiBotAnalyticsManager(enable_analytics=True)

   # 4. Register bots
   multi_analytics.register_bot("main_bot", "Main Store Bot")
   multi_analytics.register_bot("support_bot", "Support Bot")

   # 5. Set up event collection
   collector_config = EventCollectorConfig(central_analytics_url="http://localhost:8081")
   event_collector = MultiBotEventCollector(collector_config)

   # 6. Start collection
   await event_collector.start()

   # Done! Now all events are automatically tracked! 🎉

**Multi-bot analytics** - this is not just event tracking, it's a **complete data management system** for entire Telegram bot ecosystems!

No more manual data collection, no more scattered analysis, no more scaling problems.

**All events → automatically → in a single center!** 🚀

Multi-Bot Synchronization
-------------------------

The multi-bot synchronization system allows you to synchronize data between multiple Telegram bots, creating a unified ecosystem where changes in one bot are automatically reflected in others.

Features
~~~~~~~~

- **Real-time Synchronization**: Automatic sync of payment stages, promo codes, templates, and settings
- **Multiple Sync Directions**: Push, Pull, or Bidirectional synchronization
- **Conflict Resolution**: Smart conflict resolution with multiple strategies
- **Webhook Integration**: HTTP endpoints for receiving sync data
- **Auto-sync**: Scheduled automatic synchronization
- **Multi-bot Management**: Manage multiple bots from a single interface
- **Sync Statistics**: Detailed statistics and monitoring

Supported Data Types
~~~~~~~~~~~~~~~~~~~~

Payment Stages
^^^^^^^^^^^^^^

- Product titles, descriptions, and prices
- Payment configurations and payloads
- Photo URLs and start parameters

Promo Codes
^^^^^^^^^^^

- Discount codes and values
- Usage limits and expiration dates
- User restrictions and descriptions

Templates
^^^^^^^^^

- Complete template configurations
- Product catalogs and categories
- Theme settings and customizations

Settings
^^^^^^^^

- Bot configuration parameters
- Thank you messages
- Logging and stage limits

Setup
~~~~~

1. Basic Setup
^^^^^^^^^^^^^^

.. code-block:: python

   from neonpay import create_neonpay, MultiBotSyncManager, BotSyncConfig, SyncDirection

   # Initialize your main bot
   neonpay = create_neonpay(bot_instance=your_bot)

   # Initialize multi-bot sync manager
   multi_sync = MultiBotSyncManager(neonpay)

2. Configure Target Bots
^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   # Bot 1: Store Bot (Bidirectional sync)
   store_config = BotSyncConfig(
       target_bot_token="STORE_BOT_TOKEN",
       target_bot_name="Main Store Bot",
       sync_payment_stages=True,
       sync_promo_codes=True,
       sync_templates=True,
       sync_settings=True,
       direction=SyncDirection.BIDIRECTIONAL,
       auto_sync=True,
       sync_interval_minutes=30,
       webhook_url="https://store-bot.example.com/sync"
   )

   # Bot 2: Support Bot (Push only)
   support_config = BotSyncConfig(
       target_bot_token="SUPPORT_BOT_TOKEN",
       target_bot_name="Support Bot",
       sync_payment_stages=False,
       sync_promo_codes=True,
       sync_templates=True,
       direction=SyncDirection.PUSH,
       auto_sync=False,
       webhook_url="https://support-bot.example.com/sync"
   )

   # Add bots to sync manager
   multi_sync.add_bot(store_config)
   multi_sync.add_bot(support_config)

3. Start Auto-sync
^^^^^^^^^^^^^^^^^^

.. code-block:: python

   # Start automatic synchronization
   await multi_sync.start_auto_sync_all()

Sync Directions
~~~~~~~~~~~~~~~

Push (Source → Target)
^^^^^^^^^^^^^^^^^^^^^^^

Send data from your bot to target bots.

.. code-block:: python

   config = BotSyncConfig(
       target_bot_token="TARGET_TOKEN",
       target_bot_name="Target Bot",
       direction=SyncDirection.PUSH,
       webhook_url="https://target-bot.com/sync"
   )

Pull (Target → Source)
^^^^^^^^^^^^^^^^^^^^^^

Receive data from target bots to your bot.

.. code-block:: python

   config = BotSyncConfig(
       target_bot_token="SOURCE_TOKEN",
       target_bot_name="Source Bot",
       direction=SyncDirection.PULL,
       webhook_url="https://source-bot.com/sync"
   )

Bidirectional (Source ↔ Target)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Synchronize data in both directions.

.. code-block:: python

   config = BotSyncConfig(
       target_bot_token="PARTNER_TOKEN",
       target_bot_name="Partner Bot",
       direction=SyncDirection.BIDIRECTIONAL,
       webhook_url="https://partner-bot.com/sync"
   )

Conflict Resolution
~~~~~~~~~~~~~~~~~~~

Source Wins
^^^^^^^^^^^

Source data overwrites target data.

.. code-block:: python

   from neonpay import ConflictResolution

   config = BotSyncConfig(
       conflict_resolution=ConflictResolution.SOURCE_WINS
   )

Target Wins
^^^^^^^^^^^

Target data overwrites source data.

.. code-block:: python

   config = BotSyncConfig(
       conflict_resolution=ConflictResolution.TARGET_WINS
   )

Merge
^^^^^

Attempt to merge conflicting data.

.. code-block:: python

   config = BotSyncConfig(
       conflict_resolution=ConflictResolution.MERGE
   )

Ask User
^^^^^^^^

Prompt user to resolve conflicts (requires custom implementation).

.. code-block:: python

   config = BotSyncConfig(
       conflict_resolution=ConflictResolution.ASK_USER
   )

Webhook Integration
~~~~~~~~~~~~~~~~~~~

Setting up Webhook Endpoints
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   from neonpay.web_sync import create_sync_app, run_sync_server

   # Create web application for sync endpoints
   app = create_sync_app(neonpay, webhook_secret="your_secret")

   # Run sync server
   await run_sync_server(neonpay, host="0.0.0.0", port=8080)

Available Endpoints
^^^^^^^^^^^^^^^^^^^

- `POST/GET /sync/payment_stages` - Payment stages synchronization
- `POST/GET /sync/promo_codes` - Promo codes synchronization
- `POST/GET /sync/templates` - Templates synchronization
- `POST/GET /sync/settings` - Settings synchronization
- `GET /sync/status` - Sync status and bot information
- `GET /health` - Health check endpoint

Webhook Security
^^^^^^^^^^^^^^^^

.. code-block:: python

   # Verify webhook signature
   config = BotSyncConfig(
       webhook_url="https://target-bot.com/sync",
       webhook_secret="your_webhook_secret"
   )

Monitoring and Statistics
~~~~~~~~~~~~~~~~~~~~~~~~~~

Get Sync Statistics
^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   # Get statistics for all bots
   all_stats = multi_sync.get_all_sync_stats()

   for bot_name, stats in all_stats.items():
       print(f"Bot: {bot_name}")
       print(f"  Total Syncs: {stats['total_syncs']}")
       print(f"  Success Rate: {stats['success_rate']:.1f}%")
       print(f"  Items Synced: {stats['total_items_synced']}")
       print(f"  Conflicts: {stats['total_conflicts']}")

Manual Synchronization
^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   # Sync with specific bot
   result = await multi_sync.sync_all_bots()

   for bot_name, sync_result in result.items():
       print(f"Bot: {bot_name}")
       print(f"Status: {sync_result.status}")
       print(f"Items Synced: {sync_result.items_synced}")
       print(f"Conflicts: {len(sync_result.conflicts)}")

CLI Commands
~~~~~~~~~~~~

Add Bot for Sync
^^^^^^^^^^^^^^^^

.. code-block:: bash

   neonpay sync add-bot --token "BOT_TOKEN" --name "Store Bot" \
     --webhook "https://store-bot.com/sync" --direction bidirectional \
     --auto-sync --interval 30

List Configured Bots
^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

   neonpay sync list-bots

Sync with All Bots
^^^^^^^^^^^^^^^^^^

.. code-block:: bash

   neonpay sync sync-all

Show Sync Statistics
^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

   neonpay sync stats

Remove Bot from Sync
^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

   neonpay sync remove-bot "Store Bot"

Advanced Configuration
~~~~~~~~~~~~~~~~~~~~~~

Custom Conflict Resolution
^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   from neonpay.sync import ConflictResolver

   class CustomConflictResolver(ConflictResolver):
       def resolve_conflict(self, conflict):
           # Custom conflict resolution logic
           if conflict.item_type == "payment_stage":
               # Always use the higher price
               if conflict.source_data.get("price", 0) > conflict.target_data.get("price", 0):
                   return conflict.source_data
               else:
                   return conflict.target_data
           else:
               return super().resolve_conflict(conflict)

   # Use custom resolver
   sync_manager = SyncManager(neonpay, config)
   sync_manager.conflict_resolver = CustomConflictResolver()

Selective Synchronization
^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   # Sync only specific data types
   config = BotSyncConfig(
       target_bot_token="TARGET_TOKEN",
       target_bot_name="Target Bot",
       sync_payment_stages=True,
       sync_promo_codes=False,  # Skip promo codes
       sync_templates=True,
       sync_settings=False,     # Skip settings
       sync_analytics=False     # Skip analytics
   )

Conditional Auto-sync
^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   # Enable auto-sync only during business hours
   import asyncio
   from datetime import datetime

   async def conditional_auto_sync():
       while True:
           now = datetime.now()
           if 9 <= now.hour <= 18:  # Business hours
               await multi_sync.sync_all_bots()
           await asyncio.sleep(3600)  # Check every hour

   # Start conditional sync
   asyncio.create_task(conditional_auto_sync())

Error Handling
~~~~~~~~~~~~~~

Sync Error Handling
^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   async def safe_sync():
       try:
           results = await multi_sync.sync_all_bots()
           
           for bot_name, result in results.items():
               if result.status == SyncStatus.FAILED:
                   logger.error(f"Sync failed with {bot_name}: {result.errors}")
                   # Send notification about failed sync
                   await notifications.send_template_notification(
                       "sync_failed",
                       recipient="admin@example.com",
                       variables={"bot_name": bot_name, "errors": result.errors}
                   )
               elif result.conflicts:
                   logger.warning(f"Conflicts detected with {bot_name}: {len(result.conflicts)}")
                   
       except Exception as e:
           logger.error(f"Sync error: {e}")

Webhook Error Handling
^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   # Handle webhook failures gracefully
   async def robust_webhook_sync():
       max_retries = 3
       retry_delay = 5
       
       for attempt in range(max_retries):
           try:
               success = await connector.send_data(endpoint, data)
               if success:
                   return True
           except Exception as e:
               logger.warning(f"Webhook attempt {attempt + 1} failed: {e}")
               if attempt < max_retries - 1:
                   await asyncio.sleep(retry_delay)
                   retry_delay *= 2  # Exponential backoff
                   
       return False

Performance Optimization
~~~~~~~~~~~~~~~~~~~~~~~~

Batch Synchronization
^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   # Sync multiple items in batches
   async def batch_sync_payment_stages(stages_data):
       batch_size = 10
       batches = [stages_data[i:i + batch_size] 
                  for i in range(0, len(stages_data), batch_size)]
       
       for batch in batches:
           await connector.send_data("/sync/payment_stages", {"data": batch})
           await asyncio.sleep(0.1)  # Small delay between batches

Compression
^^^^^^^^^^^

.. code-block:: python

   import gzip
   import json

   # Compress large sync data
   def compress_sync_data(data):
       json_data = json.dumps(data).encode('utf-8')
       compressed = gzip.compress(json_data)
       return compressed

   # Decompress received data
   def decompress_sync_data(compressed_data):
       decompressed = gzip.decompress(compressed_data)
       return json.loads(decompressed.decode('utf-8'))

Security Best Practices
~~~~~~~~~~~~~~~~~~~~~~~~

Webhook Authentication
^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   import hmac
   import hashlib

   def verify_webhook_signature(payload, signature, secret):
       expected_signature = hmac.new(
           secret.encode('utf-8'),
           payload.encode('utf-8'),
           hashlib.sha256
       ).hexdigest()
       
       return hmac.compare_digest(signature, expected_signature)

Token Security
^^^^^^^^^^^^^^

.. code-block:: python

   # Store bot tokens securely
   import os

   bot_tokens = {
       "store_bot": os.getenv("STORE_BOT_TOKEN"),
       "support_bot": os.getenv("SUPPORT_BOT_TOKEN"),
       "analytics_bot": os.getenv("ANALYTICS_BOT_TOKEN")
   }

   # Use environment variables or secure key management
   config = BotSyncConfig(
       target_bot_token=bot_tokens["store_bot"],
       target_bot_name="Store Bot"
   )

Use Cases
~~~~~~~~~

1. Multi-Store Management
^^^^^^^^^^^^^^^^^^^^^^^^^^

Synchronize products and prices across multiple store bots.

2. Franchise Operations
^^^^^^^^^^^^^^^^^^^^^^^^

Share templates and configurations across franchise bots.

3. A/B Testing
^^^^^^^^^^^^^^

Test different configurations across multiple bots.

4. Backup and Recovery
^^^^^^^^^^^^^^^^^^^^^^

Use sync as a backup mechanism for critical data.

5. Development and Production
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Sync configurations from development to production bots.

Getting Started
~~~~~~~~~~~~~~~

1. **Install NEONPAY with sync support**:

   .. code-block:: bash

      pip install neonpay[sync]

2. **Set up your main bot**:

   .. code-block:: python

      from neonpay import create_neonpay, MultiBotSyncManager
      
      neonpay = create_neonpay(bot_instance=your_bot)
      multi_sync = MultiBotSyncManager(neonpay)

3. **Configure target bots**:

   .. code-block:: python

      config = BotSyncConfig(
          target_bot_token="TARGET_TOKEN",
          target_bot_name="Target Bot",
          webhook_url="https://target-bot.com/sync"
      )
      multi_sync.add_bot(config)

4. **Start synchronization**:

   .. code-block:: python

      await multi_sync.start_auto_sync_all()

5. **Monitor and manage**:

   .. code-block:: bash

      neonpay sync list-bots
      neonpay sync stats
      neonpay sync sync-all

The multi-bot synchronization system transforms NEONPAY from a single-bot library into a comprehensive multi-bot management platform, enabling you to build and manage entire bot ecosystems with ease!

API Reference
-------------

NeonPayCore Class
~~~~~~~~~~~~~~~~~

Methods:

- `create_payment_stage(stage_id: str, stage: PaymentStage)` - Create payment stage
- `get_payment_stage(stage_id: str)` - Get payment stage by ID
- `list_payment_stages()` - Get all payment stages
- `remove_payment_stage(stage_id: str)` - Remove payment stage
- `send_payment(user_id: int, stage_id: str)` - Send payment invoice
- `on_payment(callback)` - Register payment callback
- `get_stats()` - Get system statistics

PaymentStage Class
~~~~~~~~~~~~~~~~~~

Parameters:

- `title: str` - Payment title (required)
- `description: str` - Payment description (required)
- `price: int` - Price in Telegram Stars (required)
- `label: str` - Button label (default: "Payment")
- `photo_url: str` - Product image URL (optional)
- `payload: dict` - Custom data (optional)
- `start_parameter: str` - Deep linking parameter (optional)

PaymentResult Class
~~~~~~~~~~~~~~~~~~~

Attributes:

- `user_id: int` - User who made payment
- `amount: int` - Payment amount
- `currency: str` - Payment currency (XTR)
- `status: PaymentStatus` - Payment status
- `transaction_id: str` - Transaction ID (optional)
- `metadata: dict` - Custom metadata

Best Practices
--------------

1. Validate Payment Data
~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   @neonpay.on_payment
   async def handle_payment(result):
       # Verify payment amount
       expected_amount = get_expected_amount(result.metadata)
       if result.amount != expected_amount:
           logger.warning(f"Amount mismatch: expected {expected_amount}, got {result.amount}")
           return
       
       # Process payment
       await process_payment(result)

2. Handle Errors Gracefully
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   async def safe_send_payment(user_id, stage_id):
       try:
           await neonpay.send_payment(user_id, stage_id)
       except PaymentError as e:
           await bot.send_message(user_id, f"Payment failed: {e}")
       except Exception as e:
           logger.error(f"Unexpected error: {e}")
           await bot.send_message(user_id, "Something went wrong. Please try again.")

3. Use Meaningful Stage IDs
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Good
   neonpay.create_payment_stage("premium_monthly_subscription", stage)
   neonpay.create_payment_stage("coffee_large_size", stage)

   # Bad
   neonpay.create_payment_stage("stage1", stage)
   neonpay.create_payment_stage("payment", stage)

4. Log Payment Events
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   import logging

   logger = logging.getLogger(__name__)

   @neonpay.on_payment
   async def handle_payment(result):
       logger.info(f"Payment received: {result.user_id} paid {result.amount} stars")
       
       try:
           await process_payment(result)
           logger.info(f"Payment processed successfully for user {result.user_id}")
       except Exception as e:
           logger.error(f"Failed to process payment for user {result.user_id}: {e}")

Production Deployment
---------------------

1. Environment Variables
~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   import os

   # Store sensitive data securely
   BOT_TOKEN = os.getenv("BOT_TOKEN")
   WEBHOOK_URL = os.getenv("WEBHOOK_URL")
   DATABASE_URL = os.getenv("DATABASE_URL")

2. Database Integration
~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Replace in-memory storage with database
   import asyncpg

   async def save_payment(user_id: int, amount: int, stage_id: str):
       conn = await asyncpg.connect(DATABASE_URL)
       await conn.execute(
           "INSERT INTO payments (user_id, amount, stage_id, created_at) VALUES ($1, $2, $3, NOW())",
           user_id, amount, stage_id
       )
       await conn.close()

3. Error Monitoring
~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   import logging
   from logging.handlers import RotatingFileHandler

   # Configure logging
   logging.basicConfig(
       level=logging.INFO,
       format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
       handlers=[
           RotatingFileHandler("bot.log", maxBytes=10*1024*1024, backupCount=5),
           logging.StreamHandler()
       ]
   )

4. Health Checks
~~~~~~~~~~~~~~~~~

.. code-block:: python

   @router.message(Command("status"))
   async def status_command(message: Message):
       """Health check endpoint"""
       stats = neonpay.get_stats()
       status_text = (
           f"📊 **Bot Status**\n\n"
           f"✅ Status: Online\n"
           f"💫 Payment system: Active\n"
           f"🔧 Version: 2.6.0\n"
           f"📈 Payment stages: {stats['total_stages']}\n"
           f"🔄 Callbacks: {stats['registered_callbacks']}\n\n"
           f"Thank you for using this free bot!"
       )
       await message.answer(status_text)

5. Webhook Setup (for Raw API)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from aiohttp import web

   async def webhook_handler(request):
       """Handle incoming webhook updates"""
       try:
           data = await request.json()
           
           # Process update
           await process_update(data)
           
           return web.Response(text="OK")
       except Exception as e:
           logger.error(f"Webhook error: {e}")
           return web.Response(text="Error", status=500)

   app = web.Application()
   app.router.add_post("/webhook", webhook_handler)

Troubleshooting
---------------

Common Issues
~~~~~~~~~~~~~

1. "Payment stage not found"

.. code-block:: python

   # Check if stage exists
   stage = neonpay.get_payment_stage("my_stage")
   if not stage:
       print("Stage doesn't exist!")
       
   # List all stages
   stages = neonpay.list_payment_stages()
   print(f"Available stages: {list(stages.keys())}")

2. "Failed to send invoice"

- Verify bot token is correct
- Check if user has started the bot
- Ensure user ID is valid
- Verify payment stage configuration

3. Payment callbacks not working

.. code-block:: python

   # Make sure setup is called
   await neonpay.setup()

   # Check if handlers are registered
   stats = neonpay.get_stats()
   print(f"Callbacks registered: {stats['registered_callbacks']}")

Debug Mode
~~~~~~~~~~

.. code-block:: python

   import logging

   # Enable debug logging
   logging.basicConfig(level=logging.DEBUG)
   logging.getLogger("neonpay").setLevel(logging.DEBUG)

Support
-------

Getting Help
~~~~~~~~~~~~

If you need help:

1. 📚 **Documentation**: Check the examples directory for complete working examples
2. 💬 **Community**: Join our Telegram community
3. 🐛 **Issues**: Open an issue on GitHub
4. 📧 **Email**: Contact support at support@neonpay.com
5. 💬 **Telegram**: Contact @neonsahib

Resources
~~~~~~~~~

- 📖 **Complete Examples**: examples/ - Production-ready bot examples
- 🔧 **API Reference**: API.md - Complete API documentation
- 🔒 **Security**: SECURITY.md - Security best practices
- 📝 **Changelog**: CHANGELOG.md - Version history

Quick Links
~~~~~~~~~~~

- 🚀 **Get Started**: Quick Start Guide
- 📚 **Examples**: Real-world Examples
- 🏗️ **Deployment**: Production Deployment
- 🐛 **Troubleshooting**: Common Issues

---

This complete guide covers all aspects of NEONPAY v2.6.0, from basic usage to advanced enterprise features. Whether you're building a simple donation bot or managing a complex multi-bot ecosystem, NEONPAY provides all the tools you need for success!

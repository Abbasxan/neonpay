# NEONPAY Advanced Features

This document describes the advanced features available in NEONPAY that make it even more powerful and user-friendly.

## 📊 Analytics System

The analytics system provides comprehensive insights into your bot's performance and user behavior.

### Features

- **Revenue Tracking**: Monitor total revenue, transaction counts, and average transaction values
- **Conversion Analysis**: Track conversion rates and identify drop-off points in your sales funnel
- **Product Performance**: See which products are performing best
- **User Insights**: Understand user behavior and engagement patterns
- **Real-time Monitoring**: Track events as they happen
- **Export Options**: Export data in JSON, CSV, or table format

### Usage

```python
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
```

### CLI Usage

```bash
# Get analytics for last 30 days
neonpay analytics --period 30days --format json

# Export analytics to file
neonpay analytics --period 7days --format csv --output analytics.csv
```

## 🔔 Notification System

The notification system allows you to send notifications through multiple channels when important events occur.

### Supported Channels

- **Email**: SMTP-based email notifications
- **Telegram**: Direct messages to admin chat
- **SMS**: Text message notifications (requires provider integration)
- **Webhook**: HTTP POST to external services
- **Slack**: Messages to Slack channels
- **Discord**: Messages to Discord channels

### Features

- **Template System**: Pre-built notification templates for common events
- **Priority Levels**: Low, Normal, High, Critical priority levels
- **Multiple Recipients**: Send to multiple channels simultaneously
- **Custom Templates**: Create your own notification templates
- **Event-driven**: Automatic notifications based on payment events

### Usage

```python
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
```

### CLI Usage

```bash
# Test notifications
neonpay notifications test --type telegram --recipient "your_chat_id"

# Send custom notification
neonpay notifications send --type email --recipient "admin@example.com" \
  --subject "Daily Report" --body "Revenue: 1000 stars"
```

## 🎨 Template System

The template system provides pre-built bot configurations for common use cases, making it easy to get started quickly.

### Available Templates

- **Digital Store**: Complete e-commerce bot with products and categories
- **Subscription Service**: Subscription-based service with multiple plans
- **Donation Bot**: Bot for accepting donations and support
- **Course Platform**: Online learning platform with courses
- **Premium Features**: Bot with premium feature unlocks

### Features

- **Ready-to-use**: Pre-configured payment stages and bot logic
- **Customizable**: Modify themes, colors, and content
- **Code Generation**: Generate complete bot code from templates
- **Multiple Libraries**: Support for Aiogram, Pyrogram, and more
- **Export Options**: Export templates in JSON format

### Usage

```python
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
```

### CLI Usage

```bash
# List available templates
neonpay template list

# Generate bot code from template
neonpay template generate digital_store --library aiogram --output my_bot.py

# Create custom template
neonpay template create "My Store" --description "Custom store" --products products.json
```

## 💾 Backup System

The backup system provides automatic data backup, restoration, and synchronization capabilities.

### Features

- **Automatic Backups**: Scheduled backups with configurable intervals
- **Multiple Backup Types**: Full, incremental, and differential backups
- **Compression**: Optional compression to save space
- **Encryption**: Optional encryption for sensitive data
- **Restoration**: Easy restoration from any backup
- **Synchronization**: Sync data between multiple bots
- **Cleanup**: Automatic cleanup of old backups

### Usage

```python
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
```

### CLI Usage

```bash
# Create backup
neonpay backup create --description "Weekly backup" --type full

# List backups
neonpay backup list

# Restore backup
neonpay backup restore backup_1234567890

# Delete backup
neonpay backup delete old_backup_id
```

## 🛠️ CLI Tool

The NEONPAY CLI provides command-line access to all advanced features.

### Installation

```bash
pip install neonpay[cli]
```

### Available Commands

```bash
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
```

## 🔧 Integration Examples

### Complete Bot with All Features

```python
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
```

## 📈 Performance Considerations

### Analytics

- Events are stored in memory by default (configurable max_events)
- Use `cleanup_old_data()` to remove old analytics data
- Export data regularly to prevent memory issues

### Notifications

- Notifications are sent asynchronously to avoid blocking
- Use connection pooling for high-volume notifications
- Implement retry logic for failed notifications

### Backups

- Compression reduces backup size by 60-80%
- Incremental backups are faster for large datasets
- Schedule backups during low-activity periods

### Templates

- Templates are loaded once and cached
- Generated code is optimized for the target library
- Custom templates are stored in memory

## 🔒 Security Best Practices

### Analytics

- Don't store sensitive user data in analytics events
- Use data anonymization for privacy compliance
- Implement data retention policies

### Notifications

- Use secure channels (HTTPS, TLS) for webhooks
- Implement signature verification for webhook security
- Store credentials securely (environment variables, key vaults)

### Backups

- Encrypt sensitive backup data
- Store backups in secure locations
- Implement access controls for backup files
- Regular backup integrity checks

### Templates

- Validate template data before processing
- Sanitize user input in custom templates
- Use secure file handling for template exports

## 🚀 Getting Started

1. **Install NEONPAY with advanced features**:
   ```bash
   pip install neonpay[all]
   ```

2. **Choose your features**:
   - Analytics for insights
   - Notifications for alerts
   - Templates for quick setup
   - Backups for data safety

3. **Configure your bot**:
   ```python
   from neonpay import create_neonpay, AnalyticsManager, NotificationManager
   
   neonpay = create_neonpay(bot_instance=your_bot)
   analytics = AnalyticsManager(enable_analytics=True)
   notifications = NotificationManager(config, enable_notifications=True)
   ```

4. **Start tracking and improving**:
   - Monitor analytics for insights
   - Set up notifications for important events
   - Use templates for rapid development
   - Schedule regular backups

The advanced features make NEONPAY not just a payment library, but a complete platform for building and managing Telegram payment bots!

# NEONPAY v2.6.0 - New Features Guide

This guide covers all the new enterprise features added in NEONPAY v2.6.0.

## 🌐 Web Analytics Dashboard

Real-time bot performance monitoring via web interface.

### Setup

```python
from neonpay import MultiBotAnalyticsManager, run_analytics_server

# Initialize analytics manager
analytics = MultiBotAnalyticsManager()

# Start web dashboard
await run_analytics_server(
    analytics, 
    host="localhost", 
    port=8081
)
```

### Access Dashboard

Open your browser and navigate to: `http://localhost:8081`

### Features

- Real-time payment analytics
- Revenue tracking
- User behavior analysis
- Performance metrics
- Export capabilities

## 🔔 Notification System

Multi-channel notification system for administrators.

### Setup

```python
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
```

### Sending Notifications

```python
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
```

### Notification Types

- **Email**: SMTP-based email notifications
- **Telegram**: Bot-to-chat notifications
- **SMS**: SMS notifications (requires provider)
- **Webhook**: HTTP webhook notifications
- **Slack**: Slack channel notifications

## 💾 Backup & Restore System

Automated data protection and recovery.

### Setup

```python
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
```

### Creating Backups

```python
# Manual backup
backup_info = await backup_manager.create_backup(
    description="Weekly backup"
)

# Scheduled backups
await backup_manager.start_scheduled_backups()
```

### Restoring Data

```python
# List available backups
backups = await backup_manager.list_backups()

# Restore from backup
await backup_manager.restore_backup(backup_id="backup_2025_09_07")
```

### Backup Types

- **JSON**: Human-readable JSON format
- **SQLite**: SQLite database format
- **PostgreSQL**: PostgreSQL database format

## 📋 Template System

Pre-built bot templates and generators.

### Available Templates

```python
from neonpay import TemplateManager

templates = TemplateManager()

# List available templates
available_templates = await templates.list_templates()
print(available_templates)
```

### Generate Bot from Template

```python
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
```

### Creating Custom Templates

```python
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
```

## 🔗 Multi-Bot Analytics

Network-wide performance tracking across multiple bots.

### Setup

```python
from neonpay import MultiBotAnalyticsManager, BotAnalytics

# Initialize multi-bot analytics
multi_analytics = MultiBotAnalyticsManager()

# Add bots to analytics
bot1_analytics = BotAnalytics(bot_id="bot1", bot_name="Store Bot")
bot2_analytics = BotAnalytics(bot_id="bot2", bot_name="Support Bot")

await multi_analytics.add_bot(bot1_analytics)
await multi_analytics.add_bot(bot2_analytics)
```

### Network Analytics

```python
# Get network-wide statistics
network_stats = await multi_analytics.get_network_analytics()

# Get cross-bot insights
insights = await multi_analytics.get_cross_bot_insights()

# Export network report
await multi_analytics.export_network_report("network_report.json")
```

## 📈 Event Collection System

Centralized event management and processing.

### Setup

```python
from neonpay import CentralEventCollector, EventCollectorConfig

# Configure event collection
config = EventCollectorConfig(
    storage_type="sqlite",
    storage_path="./events.db",
    batch_size=100,
    flush_interval=30
)

# Initialize event collector
event_collector = CentralEventCollector(config)
```

### Collecting Events

```python
from neonpay import EventType

# Collect payment events
await event_collector.collect_event(
    event_type=EventType.PAYMENT_SUCCESS,
    bot_id="bot1",
    user_id=12345,
    data={"amount": 100, "currency": "stars"}
)

# Collect user events
await event_collector.collect_event(
    event_type=EventType.USER_REGISTRATION,
    bot_id="bot1",
    user_id=12345,
    data={"registration_date": "2025-09-07"}
)
```

### Querying Events

```python
# Get events by type
payment_events = await event_collector.get_events_by_type(EventType.PAYMENT_SUCCESS)

# Get events by bot
bot_events = await event_collector.get_events_by_bot("bot1")

# Get events by date range
recent_events = await event_collector.get_events_by_date_range(
    start_date="2025-09-01",
    end_date="2025-09-07"
)
```

## 🔄 Web Sync Interface

Multi-bot synchronization through REST API.

### Setup

```python
from neonpay import MultiBotSyncManager, run_sync_server

# Initialize sync manager
sync_manager = MultiBotSyncManager()

# Start web sync interface
await run_sync_server(
    sync_manager,
    host="localhost",
    port=8080
)
```

### API Endpoints

- `GET /health` - Health check
- `POST /sync/bots` - Sync multiple bots
- `GET /sync/status` - Get sync status
- `POST /sync/resolve-conflicts` - Resolve conflicts

### Using Sync API

```python
import aiohttp

async with aiohttp.ClientSession() as session:
    # Sync bots
    async with session.post('http://localhost:8080/sync/bots', 
                           json={'bot_ids': ['bot1', 'bot2']}) as response:
        result = await response.json()
    
    # Get sync status
    async with session.get('http://localhost:8080/sync/status') as response:
        status = await response.json()
```

## 🛠️ CLI Commands

New CLI commands for all enterprise features.

### Analytics Commands

```bash
# Start analytics dashboard
neonpay analytics --start-dashboard --port 8081

# Export analytics data
neonpay analytics --export --format json --output analytics.json

# Get analytics summary
neonpay analytics --summary --period 30days
```

### Backup Commands

```bash
# Create backup
neonpay backup create --description "Weekly backup"

# List backups
neonpay backup list

# Restore backup
neonpay backup restore --backup-id backup_2025_09_07
```

### Template Commands

```bash
# List available templates
neonpay template list

# Generate bot from template
neonpay template generate digital_store --output my_bot.py

# Create custom template
neonpay template create --name my_template --products products.json
```

### Notification Commands

```bash
# Test notifications
neonpay notifications test --type telegram \
  --telegram-bot-token ADMIN_BOT_TOKEN \
  --telegram-chat-id ADMIN_CHAT_ID

# Send notification
neonpay notifications send --type email \
  --recipient admin@example.com \
  --subject "Test" \
  --body "Test notification"
```

## 🔧 Migration from v2.5.x

### Import Updates

```python
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
```

### Configuration Updates

```python
# Existing code continues to work
neonpay = NeonPayCore(adapter)

# New features are optional
analytics = MultiBotAnalyticsManager()  # Optional
notifications = NotificationManager(config)  # Optional
```

### CLI Updates

```bash
# Existing commands work as before
neonpay --help

# New commands are available
neonpay analytics --help
neonpay backup --help
neonpay template --help
neonpay notifications --help
```

## 📚 Additional Resources

- [Complete API Reference](docs/en/API.md)
- [Security Best Practices](docs/en/SECURITY.md)
- [FAQ](docs/en/FAQ.md)
- [Examples](examples/)
- [Changelog](CHANGELOG.md)

## 🆘 Support

- **GitHub Issues**: [Report bugs or request features](https://github.com/Abbasxan/neonpay/issues)
- **Documentation**: [Complete documentation](docs/)
- **Examples**: [Working examples](examples/)

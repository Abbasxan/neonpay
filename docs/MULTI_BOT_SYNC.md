# NEONPAY Multi-Bot Synchronization

The multi-bot synchronization system allows you to synchronize data between multiple Telegram bots, creating a unified ecosystem where changes in one bot are automatically reflected in others.

## 🚀 Features

- **Real-time Synchronization**: Automatic sync of payment stages, promo codes, templates, and settings
- **Multiple Sync Directions**: Push, Pull, or Bidirectional synchronization
- **Conflict Resolution**: Smart conflict resolution with multiple strategies
- **Webhook Integration**: HTTP endpoints for receiving sync data
- **Auto-sync**: Scheduled automatic synchronization
- **Multi-bot Management**: Manage multiple bots from a single interface
- **Sync Statistics**: Detailed statistics and monitoring

## 📋 Supported Data Types

### Payment Stages
- Product titles, descriptions, and prices
- Payment configurations and payloads
- Photo URLs and start parameters

### Promo Codes
- Discount codes and values
- Usage limits and expiration dates
- User restrictions and descriptions

### Templates
- Complete template configurations
- Product catalogs and categories
- Theme settings and customizations

### Settings
- Bot configuration parameters
- Thank you messages
- Logging and stage limits

## 🔧 Setup

### 1. Basic Setup

```python
from neonpay import create_neonpay, MultiBotSyncManager, BotSyncConfig, SyncDirection

# Initialize your main bot
neonpay = create_neonpay(bot_instance=your_bot)

# Initialize multi-bot sync manager
multi_sync = MultiBotSyncManager(neonpay)
```

### 2. Configure Target Bots

```python
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
```

### 3. Start Auto-sync

```python
# Start automatic synchronization
await multi_sync.start_auto_sync_all()
```

## 🔄 Sync Directions

### Push (Source → Target)
Send data from your bot to target bots.

```python
config = BotSyncConfig(
    target_bot_token="TARGET_TOKEN",
    target_bot_name="Target Bot",
    direction=SyncDirection.PUSH,
    webhook_url="https://target-bot.com/sync"
)
```

### Pull (Target → Source)
Receive data from target bots to your bot.

```python
config = BotSyncConfig(
    target_bot_token="SOURCE_TOKEN",
    target_bot_name="Source Bot",
    direction=SyncDirection.PULL,
    webhook_url="https://source-bot.com/sync"
)
```

### Bidirectional (Source ↔ Target)
Synchronize data in both directions.

```python
config = BotSyncConfig(
    target_bot_token="PARTNER_TOKEN",
    target_bot_name="Partner Bot",
    direction=SyncDirection.BIDIRECTIONAL,
    webhook_url="https://partner-bot.com/sync"
)
```

## ⚙️ Conflict Resolution

### Source Wins
Source data overwrites target data.

```python
from neonpay import ConflictResolution

config = BotSyncConfig(
    conflict_resolution=ConflictResolution.SOURCE_WINS
)
```

### Target Wins
Target data overwrites source data.

```python
config = BotSyncConfig(
    conflict_resolution=ConflictResolution.TARGET_WINS
)
```

### Merge
Attempt to merge conflicting data.

```python
config = BotSyncConfig(
    conflict_resolution=ConflictResolution.MERGE
)
```

### Ask User
Prompt user to resolve conflicts (requires custom implementation).

```python
config = BotSyncConfig(
    conflict_resolution=ConflictResolution.ASK_USER
)
```

## 🌐 Webhook Integration

### Setting up Webhook Endpoints

```python
from neonpay.web_sync import create_sync_app, run_sync_server

# Create web application for sync endpoints
app = create_sync_app(neonpay, webhook_secret="your_secret")

# Run sync server
await run_sync_server(neonpay, host="0.0.0.0", port=8080)
```

### Available Endpoints

- `POST/GET /sync/payment_stages` - Payment stages synchronization
- `POST/GET /sync/promo_codes` - Promo codes synchronization
- `POST/GET /sync/templates` - Templates synchronization
- `POST/GET /sync/settings` - Settings synchronization
- `GET /sync/status` - Sync status and bot information
- `GET /health` - Health check endpoint

### Webhook Security

```python
# Verify webhook signature
config = BotSyncConfig(
    webhook_url="https://target-bot.com/sync",
    webhook_secret="your_webhook_secret"
)
```

## 📊 Monitoring and Statistics

### Get Sync Statistics

```python
# Get statistics for all bots
all_stats = multi_sync.get_all_sync_stats()

for bot_name, stats in all_stats.items():
    print(f"Bot: {bot_name}")
    print(f"  Total Syncs: {stats['total_syncs']}")
    print(f"  Success Rate: {stats['success_rate']:.1f}%")
    print(f"  Items Synced: {stats['total_items_synced']}")
    print(f"  Conflicts: {stats['total_conflicts']}")
```

### Manual Synchronization

```python
# Sync with specific bot
result = await multi_sync.sync_all_bots()

for bot_name, sync_result in result.items():
    print(f"Bot: {bot_name}")
    print(f"Status: {sync_result.status}")
    print(f"Items Synced: {sync_result.items_synced}")
    print(f"Conflicts: {len(sync_result.conflicts)}")
```

## 🛠️ CLI Commands

### Add Bot for Sync

```bash
neonpay sync add-bot --token "BOT_TOKEN" --name "Store Bot" \
  --webhook "https://store-bot.com/sync" --direction bidirectional \
  --auto-sync --interval 30
```

### List Configured Bots

```bash
neonpay sync list-bots
```

### Sync with All Bots

```bash
neonpay sync sync-all
```

### Show Sync Statistics

```bash
neonpay sync stats
```

### Remove Bot from Sync

```bash
neonpay sync remove-bot "Store Bot"
```

## 🔧 Advanced Configuration

### Custom Conflict Resolution

```python
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
```

### Selective Synchronization

```python
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
```

### Conditional Auto-sync

```python
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
```

## 🚨 Error Handling

### Sync Error Handling

```python
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
```

### Webhook Error Handling

```python
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
```

## 📈 Performance Optimization

### Batch Synchronization

```python
# Sync multiple items in batches
async def batch_sync_payment_stages(stages_data):
    batch_size = 10
    batches = [stages_data[i:i + batch_size] 
               for i in range(0, len(stages_data), batch_size)]
    
    for batch in batches:
        await connector.send_data("/sync/payment_stages", {"data": batch})
        await asyncio.sleep(0.1)  # Small delay between batches
```

### Compression

```python
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
```

## 🔒 Security Best Practices

### Webhook Authentication

```python
import hmac
import hashlib

def verify_webhook_signature(payload, signature, secret):
    expected_signature = hmac.new(
        secret.encode('utf-8'),
        payload.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(signature, expected_signature)
```

### Token Security

```python
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
```

## 🎯 Use Cases

### 1. Multi-Store Management
Synchronize products and prices across multiple store bots.

### 2. Franchise Operations
Share templates and configurations across franchise bots.

### 3. A/B Testing
Test different configurations across multiple bots.

### 4. Backup and Recovery
Use sync as a backup mechanism for critical data.

### 5. Development and Production
Sync configurations from development to production bots.

## 🚀 Getting Started

1. **Install NEONPAY with sync support**:
   ```bash
   pip install neonpay[sync]
   ```

2. **Set up your main bot**:
   ```python
   from neonpay import create_neonpay, MultiBotSyncManager
   
   neonpay = create_neonpay(bot_instance=your_bot)
   multi_sync = MultiBotSyncManager(neonpay)
   ```

3. **Configure target bots**:
   ```python
   config = BotSyncConfig(
       target_bot_token="TARGET_TOKEN",
       target_bot_name="Target Bot",
       webhook_url="https://target-bot.com/sync"
   )
   multi_sync.add_bot(config)
   ```

4. **Start synchronization**:
   ```python
   await multi_sync.start_auto_sync_all()
   ```

5. **Monitor and manage**:
   ```bash
   neonpay sync list-bots
   neonpay sync stats
   neonpay sync sync-all
   ```

The multi-bot synchronization system transforms NEONPAY from a single-bot library into a comprehensive multi-bot management platform, enabling you to build and manage entire bot ecosystems with ease!

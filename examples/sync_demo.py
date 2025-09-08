#!/usr/bin/env python3
"""
NEONPAY Sync Demo - Multi-bot synchronization demonstration
Shows how to synchronize payment stages across multiple bots
"""

import asyncio
import logging

# Import NEONPAY sync functionality
from neonpay import PaymentStage, create_neonpay
from neonpay.sync import BotSyncConfig, MultiBotSyncManager, SyncDirection

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MockBot:
    """Mock bot class for demonstration"""

    def __init__(self, name: str, token: str):
        self.name = name
        self.token = token
        self.payment_stages = {}

    def list_payment_stages(self):
        """List payment stages"""
        return self.payment_stages

    def create_payment_stage(self, stage_id: str, stage: PaymentStage):
        """Create payment stage"""
        self.payment_stages[stage_id] = stage
        logger.info(f"[{self.name}] Created payment stage: {stage_id}")


async def demo_multi_bot_sync():
    """Demonstrate multi-bot synchronization"""

    print("🔄 NEONPAY Multi-Bot Sync Demo")
    print("=" * 50)

    # Create mock bots
    main_bot = MockBot("Main Bot", "main_bot_token")
    backup_bot = MockBot("Backup Bot", "backup_bot_token")
    # analytics_bot = MockBot("Analytics Bot", "analytics_bot_token")  # Not used in this demo

    # Create NEONPAY instances
    main_neonpay = create_neonpay(main_bot)
    backup_neonpay = create_neonpay(backup_bot)
    # analytics_neonpay = create_neonpay(analytics_bot)  # Not used in this demo

    # Create multi-bot sync manager
    multi_sync = MultiBotSyncManager(main_neonpay)

    print("\n📋 Setting up payment stages...")

    # Create payment stages for main bot
    premium_stage = PaymentStage(
        title="🚀 Premium Access",
        description="Get access to premium features",
        price=100,
        photo_url="https://via.placeholder.com/512x512/96CEB4/FFFFFF?text=🚀",
    )

    theme_stage = PaymentStage(
        title="🎨 Custom Theme",
        description="Exclusive custom theme",
        price=200,
        photo_url="https://via.placeholder.com/512x512/FFEAA7/FFFFFF?text=🎨",
    )

    support_stage = PaymentStage(
        title="⚡ Priority Support",
        description="Get priority support",
        price=150,
        photo_url="https://via.placeholder.com/512x512/DDA0DD/FFFFFF?text=⚡",
    )

    # Add stages to main bot
    main_neonpay.create_payment_stage("premium", premium_stage)
    main_neonpay.create_payment_stage("theme", theme_stage)
    main_neonpay.create_payment_stage("support", support_stage)

    print("✅ Main bot stages created")

    # Configure bot synchronization
    print("\n🔧 Configuring bot synchronization...")

    # Add backup bot for bidirectional sync
    backup_config = BotSyncConfig(
        target_bot_token="backup_bot_token",
        target_bot_name="Backup Bot",
        webhook_url="https://backup.example.com/webhook",
        direction=SyncDirection.BIDIRECTIONAL,
        auto_sync=True,
        sync_interval_minutes=5,
    )

    backup_sync_manager = multi_sync.add_bot(backup_config)
    print("✅ Backup bot added for synchronization")

    # Add analytics bot for pull-only sync
    analytics_config = BotSyncConfig(
        target_bot_token="analytics_bot_token",
        target_bot_name="Analytics Bot",
        webhook_url="https://analytics.example.com/webhook",
        direction=SyncDirection.PULL,
        auto_sync=False,
        sync_interval_minutes=10,
    )

    analytics_sync_manager = multi_sync.add_bot(analytics_config)
    print("✅ Analytics bot added for synchronization")

    # List configured bots
    print("\n📋 Configured bots:")
    configured_bots = multi_sync.list_configured_bots()
    for bot_name in configured_bots:
        print(f"  • {bot_name}")

    # Demonstrate sync operations
    print("\n🔄 Performing synchronization...")

    # Sync with backup bot
    print("Syncing with Backup Bot...")
    backup_result = await backup_sync_manager.sync_bot()
    print(f"Backup sync result: {backup_result.status.value}")
    if backup_result.items_synced:
        for item_type, count in backup_result.items_synced.items():
            print(f"  • {item_type}: {count} items")

    # Sync with analytics bot
    print("\nSyncing with Analytics Bot...")
    analytics_result = await analytics_sync_manager.sync_bot()
    print(f"Analytics sync result: {analytics_result.status.value}")
    if analytics_result.items_synced:
        for item_type, count in analytics_result.items_synced.items():
            print(f"  • {item_type}: {count} items")

    # Sync all bots
    print("\n🔄 Syncing all bots...")
    all_results = await multi_sync.sync_all_bots()

    print("📊 All sync results:")
    for bot_name, result in all_results.items():
        status_emoji = "✅" if result.status.value == "completed" else "❌"
        print(f"  {status_emoji} {bot_name}: {result.status.value}")
        if result.items_synced:
            for item_type, count in result.items_synced.items():
                print(f"    • {item_type}: {count}")

        # Show sync statistics
    print("\n📈 Sync Statistics:")
    all_stats = multi_sync.get_all_sync_stats()
    for bot_name, stats in all_stats.items():
        print(f"\n🤖 {bot_name}:")
        print(f"  Total Syncs: {stats.get('total_syncs', 0)}")
        print(f"  Successful: {stats.get('successful_syncs', 0)}")
        print(f"  Failed: {stats.get('failed_syncs', 0)}")
        print(f"  Success Rate: {stats.get('success_rate', 0):.1f}%")
        print(f"  Items Synced: {stats.get('total_items_synced', 0)}")
        print(f"  Conflicts: {stats.get('total_conflicts', 0)}")
        print(
            f"  Auto Sync: {'Enabled' if stats.get('auto_sync_enabled') else 'Disabled'}"
        )

    # Demonstrate conflict resolution
    print("\n⚠️ Demonstrating conflict resolution...")

    # Simulate a conflict by modifying a stage in backup bot
    print("Simulating conflict scenario...")

    # Create conflicting stage in backup bot
    conflicting_stage = PaymentStage(
        title="🚀 Premium Access (Modified)",
        description="Modified premium access with different price",
        price=120,  # Different price
        photo_url="https://via.placeholder.com/512x512/96CEB4/FFFFFF?text=🚀",
    )

    backup_neonpay.create_payment_stage("premium", conflicting_stage)
    print("✅ Conflict created: Premium stage has different price")

    # Attempt sync to trigger conflict resolution
    print("Attempting sync with conflict...")
    conflict_result = await backup_sync_manager.sync_bot()

    if conflict_result.conflicts:
        print(f"⚠️ Conflicts detected: {len(conflict_result.conflicts)}")
        for conflict in conflict_result.conflicts:
            print(f"  • {conflict.conflict_type}: {conflict.description}")
            print(f"    Resolution: {conflict.resolution}")

    # Demonstrate auto-sync
    print("\n⏰ Auto-sync demonstration...")
    print("Auto-sync is enabled for Backup Bot (5-minute interval)")
    print("Auto-sync is disabled for Analytics Bot")

    # Show auto-sync status
    for bot_name, stats in all_stats.items():
        auto_sync_status = "Enabled" if stats.get("auto_sync_enabled") else "Disabled"
        interval = stats.get("sync_interval_minutes", "N/A")
        print(f"  {bot_name}: {auto_sync_status} (Interval: {interval} min)")

    print("\n✅ Multi-bot sync demonstration completed!")
    print("\n📚 Key Features Demonstrated:")
    print("  • Multi-bot synchronization setup")
    print("  • Bidirectional and unidirectional sync")
    print("  • Auto-sync with configurable intervals")
    print("  • Conflict detection and resolution")
    print("  • Sync statistics and monitoring")
    print("  • Webhook integration for real-time updates")


async def demo_webhook_sync():
    """Demonstrate webhook-based synchronization"""

    print("\n🌐 Webhook Sync Demo")
    print("=" * 50)

    # This would typically involve setting up webhook endpoints
    # and handling real-time updates from other bots

    print("Webhook synchronization features:")
    print("  • Real-time payment stage updates")
    print("  • Automatic conflict resolution")
    print("  • Event-driven synchronization")
    print("  • Secure webhook verification")
    print("  • Retry mechanisms for failed syncs")

    # Simulate webhook events
    webhook_events = [
        {"event": "payment_stage_created", "bot": "Backup Bot", "stage_id": "premium"},
        {"event": "payment_stage_updated", "bot": "Analytics Bot", "stage_id": "theme"},
        {"event": "payment_completed", "bot": "Main Bot", "amount": 100},
    ]

    print("\n📡 Simulated webhook events:")
    for event in webhook_events:
        print(f"  • {event['event']} from {event['bot']}")
        if "stage_id" in event:
            print(f"    Stage: {event['stage_id']}")
        if "amount" in event:
            print(f"    Amount: {event['amount']} stars")


async def main():
    """Main demo function"""
    print("🎯 NEONPAY Sync Demo")
    print("=" * 60)
    print("This demo shows multi-bot synchronization capabilities")
    print("of the NEONPAY library.")
    print("=" * 60)

    try:
        # Run multi-bot sync demo
        await demo_multi_bot_sync()

        # Run webhook sync demo
        await demo_webhook_sync()

        print("\n🎉 All demos completed successfully!")

    except Exception as e:
        logger.error(f"Demo error: {e}")
        print(f"❌ Demo error: {e}")


if __name__ == "__main__":
    asyncio.run(main())

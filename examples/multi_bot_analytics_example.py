"""
NEONPAY Multi-Bot Analytics Example
Demonstrates automatic event tracking across multiple synchronized bots
"""

import asyncio
import logging
import random
import time

from neonpay import (
    BotSyncConfig,
    EventCollectorConfig,
    MultiBotAnalyticsManager,
    MultiBotEventCollector,
    MultiBotSyncManager,
    PaymentStage,
    SyncDirection,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class MultiBotAnalyticsDemo:
    """Demonstration of multi-bot analytics system"""

    def __init__(self):
        self.neonpay = None
        self.multi_sync = None
        self.multi_analytics = None
        self.event_collector = None

    async def setup_demo(self):
        """Setup the demonstration"""
        logger.info("🚀 Setting up Multi-Bot Analytics Demo...")

        # Initialize NEONPAY (mock for demo)
        self.neonpay = self.create_mock_neonpay()

        # Initialize multi-bot sync manager
        self.multi_sync = MultiBotSyncManager(self.neonpay)

        # Initialize multi-bot analytics
        self.multi_analytics = MultiBotAnalyticsManager(enable_analytics=True)

        # Initialize event collector
        collector_config = EventCollectorConfig(
            central_analytics_url="http://localhost:8081",
            collection_interval_seconds=10,  # Short interval for demo
            enable_real_time=True,
            enable_batch_collection=True,
        )
        self.event_collector = MultiBotEventCollector(collector_config)

        # Setup bots
        await self.setup_bots()

        # Setup initial data
        await self.setup_initial_data()

        logger.info("✅ Demo setup completed!")

    def create_mock_neonpay(self):
        """Create a mock NEONPAY instance for demo"""

        class MockNeonPay:
            def __init__(self):
                self._payment_stages = {}
                self._promo_codes = []

            def create_payment_stage(self, stage_id: str, stage: PaymentStage):
                self._payment_stages[stage_id] = stage
                logger.info(f"Created payment stage: {stage_id} - {stage.title}")

            def list_payment_stages(self):
                return self._payment_stages.copy()

            def send_payment(self, user_id: int, stage_id: str):
                logger.info(f"Sent payment to user {user_id} for stage {stage_id}")
                return True

        return MockNeonPay()

    async def setup_bots(self):
        """Setup synchronization with demo bots"""

        # Bot 1: Main Store Bot
        store_config = BotSyncConfig(
            target_bot_token="STORE_BOT_TOKEN",
            target_bot_name="Main Store Bot",
            sync_payment_stages=True,
            sync_promo_codes=True,
            direction=SyncDirection.BIDIRECTIONAL,
            auto_sync=True,
            sync_interval_minutes=5,
            webhook_url="https://store-bot.example.com/sync",
        )

        # Bot 2: Support Bot
        support_config = BotSyncConfig(
            target_bot_token="SUPPORT_BOT_TOKEN",
            target_bot_name="Support Bot",
            sync_payment_stages=False,
            sync_promo_codes=True,
            direction=SyncDirection.PUSH,
            auto_sync=False,
            webhook_url="https://support-bot.example.com/sync",
        )

        # Bot 3: Analytics Bot
        analytics_config = BotSyncConfig(
            target_bot_token="ANALYTICS_BOT_TOKEN",
            target_bot_name="Analytics Bot",
            sync_payment_stages=True,
            sync_promo_codes=False,
            direction=SyncDirection.PULL,
            auto_sync=True,
            sync_interval_minutes=10,
            webhook_url="https://analytics-bot.example.com/sync",
        )

        # Add bots to sync manager
        self.multi_sync.add_bot(store_config)
        self.multi_sync.add_bot(support_config)
        self.multi_sync.add_bot(analytics_config)

        # Register bots in analytics
        self.multi_analytics.register_bot("store_bot", "Main Store Bot")
        self.multi_analytics.register_bot("support_bot", "Support Bot")
        self.multi_analytics.register_bot("analytics_bot", "Analytics Bot")

        # Add bots to event collector
        self.event_collector.add_bot(
            "store_bot", "Main Store Bot", "https://store-bot.example.com"
        )
        self.event_collector.add_bot(
            "support_bot", "Support Bot", "https://support-bot.example.com"
        )
        self.event_collector.add_bot(
            "analytics_bot", "Analytics Bot", "https://analytics-bot.example.com"
        )

        logger.info(f"📡 Configured {len(self.multi_sync.list_configured_bots())} bots")

    async def setup_initial_data(self):
        """Setup initial payment stages"""

        # Create payment stages
        stages = [
            PaymentStage(
                title="Premium Access",
                description="Unlock all premium features for 30 days",
                price=25,
                payload={"type": "subscription", "duration": 30},
            ),
            PaymentStage(
                title="Custom Theme",
                description="Personalized bot theme and colors",
                price=15,
                payload={"type": "customization"},
            ),
            PaymentStage(
                title="Priority Support",
                description="24/7 priority customer support",
                price=30,
                payload={"type": "support"},
            ),
            PaymentStage(
                title="Advanced Analytics",
                description="Detailed analytics and reporting",
                price=20,
                payload={"type": "analytics"},
            ),
        ]

        for i, stage in enumerate(stages):
            self.neonpay.create_payment_stage(f"product_{i+1}", stage)

        logger.info("📦 Initial data created: 4 payment stages")

    async def simulate_events(self):
        """Simulate events across multiple bots"""
        logger.info("🎭 Starting event simulation...")

        # Simulate events for different bots
        bots = ["store_bot", "support_bot", "analytics_bot"]
        products = ["product_1", "product_2", "product_3", "product_4"]
        users = list(range(1001, 1101))  # 100 users

        # Simulate 100 events across all bots
        for i in range(100):
            bot_id = random.choice(bots)
            user_id = random.choice(users)
            product_id = random.choice(products)

            # Random event type
            event_types = [
                "user_started",
                "product_view",
                "product_click",
                "payment_started",
                "payment_completed",
                "payment_failed",
            ]
            event_type = random.choice(event_types)

            # Random amount for payment events
            amount = (
                random.randint(10, 50) if event_type == "payment_completed" else None
            )

            # Track event
            self.multi_analytics.track_event(
                event_type=event_type,
                bot_id=bot_id,
                user_id=user_id,
                amount=amount,
                product_id=product_id,
                metadata={
                    "simulation": True,
                    "event_number": i + 1,
                    "timestamp": time.time(),
                },
            )

            # Small delay to simulate real events
            await asyncio.sleep(0.1)

        logger.info("✅ Event simulation completed: 100 events tracked")

    async def demonstrate_analytics(self):
        """Demonstrate analytics features"""
        logger.info("📊 Demonstrating analytics features...")

        # Get network analytics
        network_analytics = self.multi_analytics.get_network_analytics(days=1)
        if network_analytics:
            logger.info("🌐 **Network Analytics:**")
            logger.info(f"  Total Bots: {network_analytics.total_bots}")
            logger.info(f"  Total Events: {network_analytics.total_events}")
            logger.info(f"  Total Users: {network_analytics.total_users}")
            logger.info(f"  Total Revenue: {network_analytics.total_revenue} stars")
            logger.info(f"  Total Transactions: {network_analytics.total_transactions}")
            logger.info(
                f"  Network Conversion Rate: {network_analytics.network_conversion_rate:.1f}%"
            )

            logger.info("\n🏆 **Top Performing Bots:**")
            for i, bot in enumerate(network_analytics.top_performing_bots[:3], 1):
                logger.info(
                    f"  {i}. {bot['bot_name']}: {bot['revenue']} stars ({bot['transactions']} transactions)"
                )

            logger.info("\n📈 **Top Products:**")
            for i, product in enumerate(network_analytics.top_products[:3], 1):
                logger.info(
                    f"  {i}. {product['product_id']}: {product['revenue']} stars"
                )

        # Get individual bot analytics
        for bot_id in ["store_bot", "support_bot", "analytics_bot"]:
            bot_analytics = self.multi_analytics.get_bot_analytics(bot_id, days=1)
            if bot_analytics:
                logger.info(f"\n🤖 **{bot_analytics.bot_name} Analytics:**")
                logger.info(f"  Total Events: {bot_analytics.total_events}")
                logger.info(f"  Total Users: {bot_analytics.total_users}")
                logger.info(f"  Total Revenue: {bot_analytics.total_revenue} stars")
                logger.info(f"  Conversion Rate: {bot_analytics.conversion_rate:.1f}%")

                logger.info("  Events by Type:")
                for event_type, count in list(bot_analytics.events_by_type.items())[:5]:
                    logger.info(f"    • {event_type}: {count}")

    async def demonstrate_export(self):
        """Demonstrate data export"""
        logger.info("📤 Demonstrating data export...")

        # Export to JSON
        json_data = self.multi_analytics.export_network_analytics(
            format_type="json", days=1
        )
        if json_data:
            logger.info("✅ JSON export successful")
            logger.info(f"  Data size: {len(json_data)} characters")

        # Export to CSV
        csv_data = self.multi_analytics.export_network_analytics(
            format_type="csv", days=1
        )
        if csv_data:
            logger.info("✅ CSV export successful")
            logger.info(f"  Data size: {len(csv_data)} characters")

    async def demonstrate_event_collection(self):
        """Demonstrate event collection"""
        logger.info("🔄 Demonstrating event collection...")

        # Start event collection
        await self.event_collector.start()

        # Simulate some events
        await self.simulate_events()

        # Wait for collection
        await asyncio.sleep(5)

        # Get collection stats
        stats = self.event_collector.get_stats()
        logger.info("📊 **Event Collection Stats:**")
        logger.info(f"  Registered Bots: {stats['collector_stats']['registered_bots']}")
        logger.info(
            f"  Collection Interval: {stats['collector_stats']['collection_interval']} seconds"
        )
        logger.info(
            f"  Real-time Enabled: {stats['collector_stats']['realtime_collection']['enabled']}"
        )

        # Stop collection
        await self.event_collector.stop()

    async def demonstrate_real_time_monitoring(self):
        """Demonstrate real-time monitoring"""
        logger.info("⚡ Demonstrating real-time monitoring...")

        # Start real-time collection
        await self.event_collector.start()

        # Simulate real-time events
        for i in range(10):
            event = {
                "event_type": "real_time_test",
                "bot_id": "store_bot",
                "user_id": 2000 + i,
                "timestamp": time.time(),
                "metadata": {"test": True, "event_number": i + 1},
            }

            await self.event_collector.receive_realtime_event(event)
            await asyncio.sleep(0.5)

        # Wait for processing
        await asyncio.sleep(2)

        logger.info("✅ Real-time monitoring demonstration completed")

        # Stop collection
        await self.event_collector.stop()

    async def run_demo(self):
        """Run the complete demonstration"""
        try:
            # Setup
            await self.setup_demo()

            # Demonstrate features
            await self.demonstrate_analytics()
            await asyncio.sleep(2)

            await self.demonstrate_export()
            await asyncio.sleep(2)

            await self.demonstrate_event_collection()
            await asyncio.sleep(2)

            await self.demonstrate_real_time_monitoring()

            # Show final statistics
            logger.info("\n📊 **Final Statistics:**")
            stats = self.multi_analytics.get_stats()
            logger.info(f"  Registered Bots: {stats['registered_bots']}")
            logger.info(f"  Total Events: {stats['total_events']}")
            logger.info(f"  Total Users: {stats['total_users']}")

            logger.info("🎉 Multi-Bot Analytics Demo completed successfully!")

        except Exception as e:
            logger.error(f"Demo failed: {e}")
            raise


async def main():
    """Main function"""
    demo = MultiBotAnalyticsDemo()
    await demo.run_demo()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("👋 Demo stopped by user")
    except Exception as e:
        logger.error(f"Critical error: {e}")

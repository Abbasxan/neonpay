"""
NEONPAY Multi-Bot Synchronization Example
Demonstrates how to synchronize data between multiple Telegram bots
"""

import asyncio
import logging
from datetime import datetime

from aiogram import Bot, Dispatcher, F, Router
from aiogram.filters import Command
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)

from neonpay import (
    BotSyncConfig,
    ConflictResolution,
    MultiBotSyncManager,
    PaymentStage,
    PaymentStatus,
    SyncDirection,
    SyncStatus,
    create_neonpay,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Bot configuration
BOT_TOKEN = "YOUR_BOT_TOKEN"
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
router = Router()

# Initialize NEONPAY
neonpay = create_neonpay(bot_instance=bot, dispatcher=dp)

# Initialize multi-bot sync manager
multi_sync = MultiBotSyncManager(neonpay)


async def setup_sync_bots():
    """Setup synchronization with other bots"""

    # Bot 1: Main Store Bot
    store_bot_config = BotSyncConfig(
        target_bot_token="STORE_BOT_TOKEN",
        target_bot_name="Main Store Bot",
        sync_payment_stages=True,
        sync_promo_codes=True,
        sync_templates=True,
        sync_settings=True,
        direction=SyncDirection.BIDIRECTIONAL,
        conflict_resolution=ConflictResolution.SOURCE_WINS,
        auto_sync=True,
        sync_interval_minutes=30,
        webhook_url="https://store-bot.example.com/sync",
    )

    # Bot 2: Support Bot
    support_bot_config = BotSyncConfig(
        target_bot_token="SUPPORT_BOT_TOKEN",
        target_bot_name="Support Bot",
        sync_payment_stages=False,  # Only sync promo codes and templates
        sync_promo_codes=True,
        sync_templates=True,
        sync_settings=False,
        direction=SyncDirection.PUSH,  # Only push data to support bot
        conflict_resolution=ConflictResolution.SOURCE_WINS,
        auto_sync=False,  # Manual sync only
        webhook_url="https://support-bot.example.com/sync",
    )

    # Bot 3: Analytics Bot
    analytics_bot_config = BotSyncConfig(
        target_bot_token="ANALYTICS_BOT_TOKEN",
        target_bot_name="Analytics Bot",
        sync_payment_stages=True,
        sync_promo_codes=False,
        sync_templates=False,
        sync_settings=False,
        direction=SyncDirection.PULL,  # Only pull analytics data
        conflict_resolution=ConflictResolution.TARGET_WINS,
        auto_sync=True,
        sync_interval_minutes=60,
        webhook_url="https://analytics-bot.example.com/sync",
    )

    # Add bots to sync manager
    multi_sync.add_bot(store_bot_config)
    multi_sync.add_bot(support_bot_config)
    multi_sync.add_bot(analytics_bot_config)

    logger.info("Multi-bot synchronization configured")


async def setup_payment_stages():
    """Setup initial payment stages"""

    # Create some payment stages
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
    ]

    for i, stage in enumerate(stages):
        neonpay.create_payment_stage(f"product_{i+1}", stage)

    logger.info("Payment stages created")


@neonpay.on_payment
async def handle_payment(result):
    """Enhanced payment handler with sync notifications"""
    if result.status == PaymentStatus.COMPLETED:
        user_id = result.user_id
        amount = result.amount
        product_id = result.metadata.get("product_id", "unknown")

        # Send confirmation to user
        await bot.send_message(
            user_id,
            f"🎉 Thank you for your purchase!\n\n"
            f"Product: {result.stage.title if result.stage else product_id}\n"
            f"Amount: {amount} stars\n\n"
            f"Your purchase has been processed successfully!",
        )

        # Trigger sync with all bots (if auto-sync is enabled)
        await multi_sync.sync_all_bots()

        logger.info(f"Payment processed and synced: user={user_id}, amount={amount}")


@router.message(Command("start"))
async def start_command(message: Message):
    """Welcome message with sync status"""
    # user_id = message.from_user.id  # Not used in this function

    welcome_text = (
        "🤖 Welcome to NEONPAY Multi-Bot Sync Demo!\n\n"
        "This bot demonstrates synchronization between multiple bots:\n"
        "• 🔄 Real-time data sync\n"
        "• 🛡️ Conflict resolution\n"
        "• 📊 Multi-bot analytics\n"
        "• ⚙️ Automated synchronization\n\n"
        "Use /sync to manage synchronization."
    )

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton("🔄 Sync Status", callback_data="sync_status")],
            [InlineKeyboardButton("🛒 Browse Store", callback_data="show_store")],
            [InlineKeyboardButton("⚙️ Sync Settings", callback_data="sync_settings")],
            [InlineKeyboardButton("📊 Sync Analytics", callback_data="sync_analytics")],
        ]
    )

    await message.answer(welcome_text, reply_markup=keyboard)


@router.message(Command("sync"))
async def sync_command(message: Message):
    """Show sync management interface"""
    # user_id = message.from_user.id  # Not used in this function

    # Get sync stats
    all_stats = multi_sync.get_all_sync_stats()
    configured_bots = multi_sync.list_configured_bots()

    sync_text = "🔄 **Multi-Bot Synchronization**\n\n"
    sync_text += f"**Configured Bots:** {len(configured_bots)}\n\n"

    for bot_name in configured_bots:
        stats = all_stats.get(bot_name, {})
        sync_text += f"🤖 **{bot_name}**\n"
        sync_text += f"  Total syncs: {stats.get('total_syncs', 0)}\n"
        sync_text += f"  Success rate: {stats.get('success_rate', 0):.1f}%\n"
        sync_text += f"  Items synced: {stats.get('total_items_synced', 0)}\n"
        sync_text += f"  Conflicts: {stats.get('total_conflicts', 0)}\n\n"

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton("🔄 Sync All Bots", callback_data="sync_all")],
            [InlineKeyboardButton("📊 Detailed Stats", callback_data="sync_stats")],
            [InlineKeyboardButton("⚙️ Configure Bots", callback_data="sync_config")],
        ]
    )

    await message.answer(sync_text, reply_markup=keyboard, parse_mode="Markdown")


@router.message(Command("store"))
async def store_command(message: Message):
    """Show store with synced products"""
    # user_id = message.from_user.id  # Not used in this function

    stages = neonpay.list_payment_stages()

    if not stages:
        await message.answer(
            "🛒 Store is empty. Products will appear after synchronization."
        )
        return

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    f"{stage.title} - {stage.price}⭐", callback_data=f"buy:{stage_id}"
                )
            ]
            for stage_id, stage in stages.items()
        ]
    )

    await message.answer(
        "🛒 **Synchronized Store**\n\n"
        "All products are automatically synchronized across bots!",
        reply_markup=keyboard,
        parse_mode="Markdown",
    )


@router.callback_query(F.data == "sync_status")
async def sync_status_callback(callback: CallbackQuery):
    """Show detailed sync status"""
    all_stats = multi_sync.get_all_sync_stats()
    configured_bots = multi_sync.list_configured_bots()

    status_text = "📊 **Sync Status Details**\n\n"

    for bot_name in configured_bots:
        stats = all_stats.get(bot_name, {})
        status_text += f"🤖 **{bot_name}**\n"
        status_text += f"  ✅ Successful: {stats.get('successful_syncs', 0)}\n"
        status_text += f"  ❌ Failed: {stats.get('failed_syncs', 0)}\n"
        status_text += f"  📈 Success Rate: {stats.get('success_rate', 0):.1f}%\n"
        status_text += f"  📦 Items Synced: {stats.get('total_items_synced', 0)}\n"
        status_text += f"  ⚠️ Conflicts: {stats.get('total_conflicts', 0)}\n"

        if stats.get("last_sync"):
            last_sync = datetime.fromtimestamp(stats["last_sync"])
            status_text += f"  🕐 Last Sync: {last_sync.strftime('%Y-%m-%d %H:%M')}\n"

        status_text += f"  🔄 Auto Sync: {'Enabled' if stats.get('auto_sync_enabled') else 'Disabled'}\n\n"

    await callback.message.edit_text(status_text, parse_mode="Markdown")
    await callback.answer()


@router.callback_query(F.data == "sync_all")
async def sync_all_callback(callback: CallbackQuery):
    """Trigger sync with all bots"""
    await callback.answer("🔄 Starting synchronization...")

    try:
        results = await multi_sync.sync_all_bots()

        sync_text = "✅ **Synchronization Results**\n\n"

        for bot_name, result in results.items():
            status_emoji = "✅" if result.status == SyncStatus.COMPLETED else "❌"
            sync_text += f"{status_emoji} **{bot_name}**\n"
            sync_text += f"  Status: {result.status.value}\n"

            if result.items_synced:
                sync_text += "  Items synced:\n"
                for item_type, count in result.items_synced.items():
                    sync_text += f"    • {item_type}: {count}\n"

            if result.conflicts:
                sync_text += f"  Conflicts: {len(result.conflicts)}\n"

            if result.errors:
                sync_text += f"  Errors: {len(result.errors)}\n"

            sync_text += "\n"

        await callback.message.edit_text(sync_text, parse_mode="Markdown")

    except Exception as e:
        await callback.message.edit_text(f"❌ Sync failed: {str(e)}")
        logger.error(f"Sync failed: {e}")


@router.callback_query(F.data == "sync_stats")
async def sync_stats_callback(callback: CallbackQuery):
    """Show detailed sync statistics"""
    all_stats = multi_sync.get_all_sync_stats()

    stats_text = "📈 **Sync Statistics**\n\n"

    total_syncs = sum(stats.get("total_syncs", 0) for stats in all_stats.values())
    total_successful = sum(
        stats.get("successful_syncs", 0) for stats in all_stats.values()
    )
    total_items = sum(
        stats.get("total_items_synced", 0) for stats in all_stats.values()
    )
    total_conflicts = sum(
        stats.get("total_conflicts", 0) for stats in all_stats.values()
    )

    stats_text += "📊 **Overall Statistics**\n"
    stats_text += f"  Total Syncs: {total_syncs}\n"
    stats_text += f"  Successful: {total_successful}\n"
    stats_text += f"  Success Rate: {(total_successful/total_syncs*100) if total_syncs > 0 else 0:.1f}%\n"
    stats_text += f"  Items Synced: {total_items}\n"
    stats_text += f"  Conflicts: {total_conflicts}\n\n"

    stats_text += "🤖 **Per-Bot Statistics**\n"
    for bot_name, stats in all_stats.items():
        stats_text += f"  {bot_name}:\n"
        stats_text += f"    Syncs: {stats.get('total_syncs', 0)}\n"
        stats_text += f"    Items: {stats.get('total_items_synced', 0)}\n"
        stats_text += f"    Conflicts: {stats.get('total_conflicts', 0)}\n"

    await callback.message.edit_text(stats_text, parse_mode="Markdown")
    await callback.answer()


@router.callback_query(F.data == "sync_config")
async def sync_config_callback(callback: CallbackQuery):
    """Show sync configuration"""
    configured_bots = multi_sync.list_configured_bots()

    config_text = "⚙️ **Sync Configuration**\n\n"

    for bot_name in configured_bots:
        config_text += f"🤖 **{bot_name}**\n"
        config_text += "  Direction: Bidirectional\n"
        config_text += "  Auto Sync: Enabled\n"
        config_text += "  Interval: 30 minutes\n"
        config_text += "  Conflict Resolution: Source Wins\n\n"

    config_text += "💡 **Configuration Options**\n"
    config_text += "• Push: Send data to target bot\n"
    config_text += "• Pull: Get data from target bot\n"
    config_text += "• Bidirectional: Sync both ways\n"
    config_text += "• Auto Sync: Automatic synchronization\n"
    config_text += "• Conflict Resolution: How to handle conflicts\n"

    await callback.message.edit_text(config_text, parse_mode="Markdown")
    await callback.answer()


@router.callback_query(F.data == "show_store")
async def show_store_callback(callback: CallbackQuery):
    """Show store with products"""
    stages = neonpay.list_payment_stages()

    if not stages:
        await callback.message.edit_text(
            "🛒 Store is empty. Products will appear after synchronization."
        )
        await callback.answer()
        return

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    f"{stage.title} - {stage.price}⭐", callback_data=f"buy:{stage_id}"
                )
            ]
            for stage_id, stage in stages.items()
        ]
    )

    await callback.message.edit_text(
        "🛒 **Synchronized Store**\n\n"
        "All products are automatically synchronized across bots!",
        reply_markup=keyboard,
        parse_mode="Markdown",
    )
    await callback.answer()


@router.callback_query(F.data.startswith("buy:"))
async def buy_product_callback(callback: CallbackQuery):
    """Handle product purchase"""
    user_id = callback.from_user.id
    product_id = callback.data.split(":")[1]

    # Send payment
    success = await neonpay.send_payment(user_id, product_id)

    if success:
        await callback.answer("✅ Payment message sent")
    else:
        await callback.answer("❌ Failed to send payment", show_alert=True)


async def main():
    """Main function"""
    logger.info("🚀 Starting NEONPAY Multi-Bot Sync Demo...")

    try:
        # Setup synchronization
        await setup_sync_bots()

        # Setup initial data
        await setup_payment_stages()

        # Start auto-sync for all bots
        await multi_sync.start_auto_sync_all()

        # Include router
        dp.include_router(router)

        logger.info("✅ Multi-bot sync system initialized!")
        logger.info(f"📡 Configured bots: {len(multi_sync.list_configured_bots())}")
        logger.info("🔄 Auto-sync enabled for all bots")
        logger.info("🔄 Starting polling...")

        # Start polling
        await dp.start_polling(bot)

    except Exception as e:
        logger.error(f"Failed to start bot: {e}")
        raise


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("👋 Bot stopped by user")
    except Exception as e:
        logger.error(f"Critical error: {e}")

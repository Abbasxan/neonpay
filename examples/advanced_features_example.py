"""
NEONPAY Advanced Features Example
Demonstrates analytics, notifications, templates, and backup systems
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
    AnalyticsManager,
    AnalyticsPeriod,
    BackupConfig,
    BackupManager,
    BackupType,
    NotificationConfig,
    NotificationManager,
    NotificationMessage,
    NotificationPriority,
    NotificationType,
    PaymentStatus,
    TemplateManager,
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

# Initialize NEONPAY with advanced features
neonpay = create_neonpay(bot_instance=bot, dispatcher=dp)

# Initialize analytics
analytics = AnalyticsManager(enable_analytics=True)

# Initialize notifications
notification_config = NotificationConfig(
    smtp_host="smtp.gmail.com",
    smtp_port=587,
    smtp_username="your_email@gmail.com",
    smtp_password="your_password",
    telegram_bot_token=BOT_TOKEN,
    telegram_admin_chat_id="YOUR_ADMIN_CHAT_ID",
    webhook_url="https://your-webhook-url.com/notifications",
)
notifications = NotificationManager(notification_config, enable_notifications=True)

# Initialize templates
templates = TemplateManager()

# Initialize backup
backup_config = BackupConfig(
    backup_directory="./backups",
    max_backups=5,
    auto_backup=True,
    backup_interval_hours=24,
)
backup = BackupManager(neonpay, backup_config)


async def setup_advanced_features():
    """Setup advanced features"""

    # Create payment stages using template
    digital_store_template = templates.get_template("digital_store")
    if digital_store_template:
        stages = templates.convert_to_payment_stages(digital_store_template)
        for stage_id, stage in stages.items():
            neonpay.create_payment_stage(stage_id, stage)

    # Track analytics events
    analytics.track_event(
        "bot_started", user_id=0, metadata={"timestamp": datetime.now().isoformat()}
    )

    # Send startup notification
    await notifications.send_template_notification(
        "system_startup",
        recipient="admin@example.com",
        variables={"timestamp": datetime.now().isoformat()},
        notification_type=NotificationType.EMAIL,
    )

    # Create initial backup
    await backup.create_backup(
        backup_type=BackupType.FULL, description="Initial setup backup"
    )

    logger.info("Advanced features initialized successfully")


@neonpay.on_payment
async def handle_payment(result):
    """Enhanced payment handler with analytics and notifications"""
    if result.status == PaymentStatus.COMPLETED:
        user_id = result.user_id
        amount = result.amount
        product_id = result.metadata.get("product_id", "unknown")

        # Track analytics events
        analytics.track_event(
            "payment_completed", user_id, amount=amount, stage_id=product_id
        )
        analytics.track_event(
            "product_purchased",
            user_id,
            stage_id=product_id,
            metadata={"amount": amount},
        )

        # Send notifications
        await notifications.send_template_notification(
            "payment_completed",
            recipient="admin@example.com",
            variables={
                "user_id": user_id,
                "amount": amount,
                "product_name": result.stage.title if result.stage else product_id,
            },
            notification_type=NotificationType.TELEGRAM,
        )

        # Send user confirmation
        await bot.send_message(
            user_id,
            f"🎉 Thank you for your purchase!\n\n"
            f"Product: {result.stage.title if result.stage else product_id}\n"
            f"Amount: {amount} stars\n\n"
            f"Your purchase has been processed successfully!",
        )

        logger.info(
            f"Payment processed: user={user_id}, amount={amount}, product={product_id}"
        )


@router.message(Command("start"))
async def start_command(message: Message):
    """Welcome message with analytics tracking"""
    user_id = message.from_user.id

    # Track user interaction
    analytics.track_event("user_started", user_id)

    welcome_text = (
        "🚀 Welcome to NEONPAY Advanced Features Demo!\n\n"
        "This bot demonstrates:\n"
        "• 📊 Advanced Analytics\n"
        "• 🔔 Smart Notifications\n"
        "• 🎨 Template System\n"
        "• 💾 Backup & Sync\n\n"
        "Use /help to see all available commands."
    )

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton("🛒 Browse Store", callback_data="show_store")],
            [InlineKeyboardButton("📊 View Analytics", callback_data="show_analytics")],
            [
                InlineKeyboardButton(
                    "🔔 Test Notifications", callback_data="test_notifications"
                )
            ],
            [InlineKeyboardButton("💾 Create Backup", callback_data="create_backup")],
        ]
    )

    await message.answer(welcome_text, reply_markup=keyboard)


@router.message(Command("analytics"))
async def analytics_command(message: Message):
    """Show analytics dashboard"""
    user_id = message.from_user.id

    # Track analytics request
    analytics.track_event("analytics_viewed", user_id)

    # Get analytics data
    revenue_data = analytics.get_revenue_analytics(AnalyticsPeriod.DAY, days=30)
    conversion_data = analytics.get_conversion_analytics(AnalyticsPeriod.DAY, days=30)
    product_data = analytics.get_product_analytics(AnalyticsPeriod.DAY, days=30)

    analytics_text = "📊 **Analytics Dashboard**\n\n"

    if revenue_data:
        analytics_text += "💰 **Revenue (30 days)**\n"
        analytics_text += f"Total: {revenue_data.total_revenue} stars\n"
        analytics_text += f"Transactions: {revenue_data.total_transactions}\n"
        analytics_text += f"Average: {revenue_data.average_transaction:.1f} stars\n\n"

    if conversion_data:
        analytics_text += "📈 **Conversion**\n"
        analytics_text += f"Rate: {conversion_data.conversion_rate:.1f}%\n"
        analytics_text += f"Visitors: {conversion_data.total_visitors}\n"
        analytics_text += f"Purchases: {conversion_data.total_purchases}\n\n"

    if product_data:
        analytics_text += "🏆 **Top Products**\n"
        for i, product in enumerate(product_data[:3], 1):
            analytics_text += (
                f"{i}. {product.product_name}: {product.total_revenue} stars\n"
            )

    await message.answer(analytics_text, parse_mode="Markdown")


@router.message(Command("templates"))
async def templates_command(message: Message):
    """Show available templates"""
    user_id = message.from_user.id

    # Track template view
    analytics.track_event("templates_viewed", user_id)

    template_list = templates.list_templates()

    templates_text = "🎨 **Available Templates**\n\n"
    for template in template_list:
        templates_text += f"• **{template.name}**\n"
        templates_text += f"  {template.description}\n"
        templates_text += (
            f"  Products: {sum(len(cat.products) for cat in template.categories)}\n\n"
        )

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    f"Use {template.name}",
                    callback_data=f"use_template:{template.name.lower().replace(' ', '_')}",
                )
            ]
            for template in template_list
        ]
    )

    await message.answer(templates_text, reply_markup=keyboard, parse_mode="Markdown")


@router.message(Command("backup"))
async def backup_command(message: Message):
    """Show backup information"""
    user_id = message.from_user.id

    # Track backup view
    analytics.track_event("backup_viewed", user_id)

    backups = backup.list_backups()

    backup_text = "💾 **Backup System**\n\n"
    backup_text += f"Total backups: {len(backups)}\n"
    backup_text += (
        f"Auto backup: {'Enabled' if backup.config.auto_backup else 'Disabled'}\n"
    )
    backup_text += f"Max backups: {backup.config.max_backups}\n\n"

    if backups:
        backup_text += "**Recent Backups:**\n"
        for backup_info in backups[:3]:
            status_emoji = "✅" if backup_info.status.value == "completed" else "⏳"
            backup_text += f"{status_emoji} {backup_info.backup_id}: {backup_info.created_at.strftime('%Y-%m-%d %H:%M')}\n"

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton("🔄 Create Backup", callback_data="create_backup")],
            [InlineKeyboardButton("📋 List Backups", callback_data="list_backups")],
        ]
    )

    await message.answer(backup_text, reply_markup=keyboard, parse_mode="Markdown")


@router.callback_query(F.data == "show_store")
async def show_store_callback(callback: CallbackQuery):
    """Show store with products"""
    user_id = callback.from_user.id

    # Track store view
    analytics.track_event("store_viewed", user_id)

    stages = neonpay.list_payment_stages()

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
        "🛒 **Digital Store**\n\nChoose a product to purchase:",
        reply_markup=keyboard,
        parse_mode="Markdown",
    )
    await callback.answer()


@router.callback_query(F.data.startswith("buy:"))
async def buy_product_callback(callback: CallbackQuery):
    """Handle product purchase"""
    user_id = callback.from_user.id
    product_id = callback.data.split(":")[1]

    # Track purchase attempt
    analytics.track_event("purchase_attempted", user_id, stage_id=product_id)

    # Send payment
    success = await neonpay.send_payment(user_id, product_id)

    if success:
        await callback.answer("✅ Payment message sent")
    else:
        await callback.answer("❌ Failed to send payment", show_alert=True)


@router.callback_query(F.data == "show_analytics")
async def show_analytics_callback(callback: CallbackQuery):
    """Show analytics dashboard"""
    await analytics_command(callback.message)
    await callback.answer()


@router.callback_query(F.data == "test_notifications")
async def test_notifications_callback(callback: CallbackQuery):
    """Test notification system"""
    user_id = callback.from_user.id

    # Send test notification
    await notifications.send_notification(
        NotificationMessage(
            notification_type=NotificationType.TELEGRAM,
            recipient=callback.from_user.username or str(user_id),
            subject="🧪 Test Notification",
            body=f"Hello {callback.from_user.first_name}! This is a test notification from NEONPAY.",
            priority=NotificationPriority.NORMAL,
        )
    )

    await callback.answer("✅ Test notification sent")


@router.callback_query(F.data == "create_backup")
async def create_backup_callback(callback: CallbackQuery):
    """Create backup"""
    user_id = callback.from_user.id

    # Track backup creation
    analytics.track_event("backup_created", user_id)

    try:
        backup_info = await backup.create_backup(
            backup_type=BackupType.FULL, description=f"Manual backup by user {user_id}"
        )

        await callback.answer(f"✅ Backup created: {backup_info.backup_id}")

        # Send notification about backup
        await notifications.send_template_notification(
            "backup_created",
            recipient="admin@example.com",
            variables={
                "backup_id": backup_info.backup_id,
                "user_id": user_id,
                "size": f"{backup_info.size_bytes / 1024:.1f} KB",
            },
        )

    except Exception as e:
        await callback.answer(f"❌ Backup failed: {str(e)}", show_alert=True)


@router.callback_query(F.data.startswith("use_template:"))
async def use_template_callback(callback: CallbackQuery):
    """Use a template"""
    user_id = callback.from_user.id
    template_name = callback.data.split(":", 1)[1]

    # Track template usage
    analytics.track_event(
        "template_used", user_id, metadata={"template": template_name}
    )

    template = templates.get_template(template_name)
    if template:
        # Generate bot code
        bot_code = templates.generate_bot_code(template, "aiogram")

        await callback.message.edit_text(
            f"🎨 **Template: {template.name}**\n\n"
            f"Description: {template.description}\n"
            f"Products: {sum(len(cat.products) for cat in template.categories)}\n\n"
            f"Bot code generated! Check logs for full code.",
            parse_mode="Markdown",
        )

        # Log the generated code
        logger.info(f"Generated bot code for template {template.name}:\n{bot_code}")

    await callback.answer()


async def main():
    """Main function"""
    logger.info("🚀 Starting NEONPAY Advanced Features Demo...")

    try:
        # Setup advanced features
        await setup_advanced_features()

        # Include router
        dp.include_router(router)

        logger.info("✅ Bot initialized successfully!")
        logger.info("📊 Analytics system ready!")
        logger.info("🔔 Notifications system ready!")
        logger.info("🎨 Templates system ready!")
        logger.info("💾 Backup system ready!")
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

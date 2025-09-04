"""
NEONPAY pyTelegramBotAPI (telebot) Example
Complete example showing how to use NEONPAY with pyTelegramBotAPI v4.0+
"""

import logging
import time
from telebot import TeleBot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

from neonpay import create_neonpay, PaymentStage, PaymentResult

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Bot token
BOT_TOKEN = "YOUR_BOT_TOKEN"  # Replace with your bot token

# Initialize bot
bot = TeleBot(BOT_TOKEN)

# Initialize NEONPAY
neonpay = create_neonpay(bot, "Thank you for your subscription! 🎉")

# Subscription plans
PLANS = {
    "basic": {
        "name": "📱 Basic Plan",
        "description": "Essential features for personal use",
        "price": 99,
        "features": ["5 Projects", "Basic Support", "1GB Storage"],
        "duration": 30
    },
    "pro": {
        "name": "💼 Pro Plan",
        "description": "Advanced features for professionals",
        "price": 299,
        "features": ["Unlimited Projects", "Priority Support", "10GB Storage", "Advanced Analytics"],
        "duration": 30
    },
    "enterprise": {
        "name": "🏢 Enterprise Plan",
        "description": "Full-featured plan for teams",
        "price": 599,
        "features": ["Everything in Pro", "Team Collaboration", "100GB Storage", "Custom Integrations", "Dedicated Manager"],
        "duration": 30
    }
}

# User database (in production, use a real database)
user_subscriptions = {}

def setup_payment_stages():
    """Initialize subscription payment stages"""
    for plan_id, plan in PLANS.items():
        stage = PaymentStage(
            title=plan["name"],
            description=f"{plan['description']} - {plan['duration']} days",
            price=plan["price"],
            label=f"Subscribe for {plan['price']} ⭐",
            photo_url=f"https://via.placeholder.com/400x300/4CAF50/white?text={plan_id.upper()}",
            payload={
                "plan_id": plan_id,
                "plan_name": plan["name"],
                "duration": plan["duration"],
                "features": plan["features"]
            }
        )
        neonpay.create_payment_stage(plan_id, stage)
    
    logger.info("✅ Subscription plans initialized")

# Payment completion handler
@neonpay.on_payment
async def handle_subscription_payment(result: PaymentResult):
    """Process successful subscription payments"""
    user_id = result.user_id
    amount = result.amount
    plan_id = result.metadata.get("plan_id")
    plan_name = result.metadata.get("plan_name", "Unknown Plan")
    duration = result.metadata.get("duration", 30)
    features = result.metadata.get("features", [])

    logger.info(f"💳 Subscription: {plan_name} by user {user_id} for {amount} ⭐")

    # Activate subscription
    expiry_date = time.time() + (duration * 24 * 60 * 60)
    user_subscriptions[user_id] = {
        "plan_id": plan_id,
        "plan_name": plan_name,
        "features": features,
        "expiry_date": expiry_date,
        "active": True
    }

    # Send confirmation
    confirmation_text = (
        "🎉 **Subscription Activated!**\n\n"
        f"📋 Plan: {plan_name}\n"
        f"💰 Amount: {amount} ⭐\n"
        f"⏰ Duration: {duration} days\n"
        f"📅 Expires: {time.strftime('%Y-%m-%d', time.localtime(expiry_date))}\n\n"
        "✨ **Your Features:**\n"
    )
    for feature in features:
        confirmation_text += f"• {feature}\n"
    confirmation_text += "\n🚀 Your subscription is now active! Enjoy all the features."

    # Create management keyboard
    keyboard = InlineKeyboardMarkup()
    keyboard.row(
        InlineKeyboardButton("📊 Dashboard", callback_data="dashboard"),
        InlineKeyboardButton("⚙️ Settings", callback_data="settings")
    )
    keyboard.row(
        InlineKeyboardButton("📞 Support", callback_data="support")
    )

    try:
        bot.send_message(user_id, confirmation_text, reply_markup=keyboard, parse_mode='Markdown')
        send_welcome_guide(user_id, plan_id)
    except Exception as e:
        logger.error(f"Failed to send confirmation to user {user_id}: {e}")

def send_welcome_guide(user_id: int, plan_id: str):
    """Send welcome guide for new subscribers"""
    guide_text = (
        f"📚 **Welcome Guide - {PLANS[plan_id]['name']}**\n\n"
        "Here's how to get started:\n\n"
        "1️⃣ **Access Dashboard**: Use /dashboard to view your account\n"
        "2️⃣ **Create Project**: Start your first project with /new_project\n"
        "3️⃣ **Get Support**: Need help? Use /support anytime\n"
        "4️⃣ **Manage Settings**: Customize your experience with /settings\n\n"
        "💡 **Pro Tips:**\n"
        "• Check /status to see your subscription details\n"
        "• Use /help to see all available commands\n"
        "• Join our community: @neonpay_community\n\n"
        "🎯 Ready to get started? Try /dashboard now!"
    )

    try:
        bot.send_message(user_id, guide_text, parse_mode='Markdown')
    except Exception as e:
        logger.error(f"Failed to send welcome guide to user {user_id}: {e}")

def is_subscribed(user_id: int) -> bool:
    """Check if user has active subscription"""
    subscription = user_subscriptions.get(user_id)
    if not subscription:
        return False
    
    if subscription["expiry_date"] < time.time():
        subscription["active"] = False
        return False
    
    return subscription["active"]

def get_user_plan(user_id: int) -> dict:
    """Get user's current subscription plan"""
    return user_subscriptions.get(user_id, {})

# Command handlers
@bot.message_handler(commands=['start'])
def start_command(message):
    """Welcome message"""
    welcome_text = (
        f"🌟 **Welcome to NEONPAY Subscription Bot!**\n\n"
        f"Hi {message.from_user.first_name}! 👋\n\n"
        "We offer premium subscription plans with amazing features:\n"
        "• Project Management Tools\n"
        "• Cloud Storage\n"
        "• Priority Support\n"
        "• Advanced Analytics\n\n"
        "💫 All subscriptions are powered by Telegram Stars!\n\n"
        "Ready to get started?"
    )

    keyboard = InlineKeyboardMarkup()
    keyboard.row(
        InlineKeyboardButton("🛍️ View Plans", callback_data="show_plans"),
        InlineKeyboardButton("ℹ️ Learn More", callback_data="learn_more")
    )

    if is_subscribed(message.from_user.id):
        keyboard.row(InlineKeyboardButton("📊 My Dashboard", callback_data="dashboard"))

    bot.reply_to(message, welcome_text, reply_markup=keyboard, parse_mode='Markdown')

@bot.message_handler(commands=['plans'])
def plans_command(message):
    """Show subscription plans"""
    show_subscription_plans(message.from_user.id)


@bot.message_handler(commands=['status'])
def status_command(message):
    """Show subscription status"""
    user_id = message.from_user.id

    if not is_subscribed(user_id):
        status_text = (
            "❌ **No Active Subscription**\n\n"
            "You don't have an active subscription.\n"
            "Use /plans to see available options!"
        )
    else:
        plan = get_user_plan(user_id)
        expiry_date = time.strftime('%Y-%m-%d %H:%M', time.localtime(plan["expiry_date"]))
        days_left = int((plan["expiry_date"] - time.time()) / (24 * 60 * 60))
        status_text = (
            f"✅ **Active Subscription**\n\n"
            f"📋 Plan: {plan['plan_name']}\n"
            f"📅 Expires: {expiry_date}\n"
            f"⏰ Days Left: {days_left}\n\n"
            "✨ **Your Features:**\n"
        )
        for feature in plan["features"]:
            status_text += f"• {feature}\n"

    keyboard = InlineKeyboardMarkup()
    if is_subscribed(user_id):
        keyboard.row(
            InlineKeyboardButton("📊 Dashboard", callback_data="dashboard"),
            InlineKeyboardButton("🔄 Renew", callback_data="show_plans")
        )
    else:
        keyboard.row(InlineKeyboardButton("🛍️ Subscribe Now", callback_data="show_plans"))

    bot.reply_to(message, status_text, reply_markup=keyboard, parse_mode='Markdown')

@bot.message_handler(commands=['dashboard'])
def dashboard_command(message):
    """Show user dashboard"""
    user_id = message.from_user.id

    if not is_subscribed(user_id):
        bot.reply_to(
            message,
            "❌ You need an active subscription to access the dashboard. Use /plans to subscribe!"
        )
        return

    plan = get_user_plan(user_id)
    dashboard_text = (
        f"📊 **Your Dashboard**\n\n"
        f"👤 User: {message.from_user.first_name}\n"
        f"📋 Plan: {plan['plan_name']}\n"
        f"📅 Expires: {time.strftime('%Y-%m-%d', time.localtime(plan['expiry_date']))}\n\n"
        "📈 **Quick Stats:**\n"
        "• Projects: 5 active\n"
        "• Storage Used: 2.3GB\n"
        "• API Calls: 1,247 this month\n"
        "• Support Tickets: 0 open\n\n"
        "🚀 Everything looks great!"
    )

    keyboard = InlineKeyboardMarkup()
    keyboard.row(
        InlineKeyboardButton("📁 Projects", callback_data="projects"),
        InlineKeyboardButton("📊 Analytics", callback_data="analytics")
    )
    keyboard.row(
        InlineKeyboardButton("⚙️ Settings", callback_data="settings"),
        InlineKeyboardButton("📞 Support", callback_data="support")
    )

    bot.reply_to(message, dashboard_text, reply_markup=keyboard, parse_mode='Markdown')

@bot.message_handler(commands=['help'])
def help_command(message):
    """Show help information"""
    help_text = (
        "🆘 **Help & Commands**\n\n"
        "**Main Commands:**\n"
        "• /start - Welcome message\n"
        "• /plans - View subscription plans\n"
        "• /status - Check subscription status\n"
        "• /dashboard - Access your dashboard\n"
        "• /help - This help message\n\n"
        "**Subscription Features:**\n"
        "• Project management tools\n"
        "• Cloud storage & sync\n"
        "• Advanced analytics\n"
        "• Priority support\n"
        "• Team collaboration\n\n"
        "**Payment Info:**\n"
        "• We accept Telegram Stars (⭐)\n"
        "• Instant activation\n"
        "• Secure payments\n"
        "• Auto-renewal available\n\n"
        "Need help? Contact @support"
    )
    
    bot.reply_to(message, help_text, parse_mode='Markdown')

def show_subscription_plans(user_id: int):
    """Display subscription plans"""
    plans_text = "🛍️ **Subscription Plans**\n\nChoose the perfect plan for your needs:"

    keyboard = InlineKeyboardMarkup()

    for plan_id, plan in PLANS.items():
        button_text = "{} - {} ⭐".format(plan['name'], plan['price'])
        keyboard.row(InlineKeyboardButton(button_text, callback_data="plan_" + plan_id))

    keyboard.row(InlineKeyboardButton("❓ Compare Plans", callback_data="compare_plans"))

    try:
        bot.send_message(user_id, plans_text, reply_markup=keyboard, parse_mode='Markdown')
    except Exception as e:
        logger.error("Failed to send plans to user {}: {}".format(user_id, e))

# Callback query handlers
@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    """Handle inline button presses"""
    user_id = call.from_user.id
    data = call.data

    try:
        if data == "show_plans":
            show_subscription_plans(user_id)
        elif data.startswith("plan_"):
            plan_id = data.split("_")[1]
            show_plan_details(call, plan_id)
        elif data.startswith("subscribe_"):
            plan_id = data.split("_")[1]
            process_subscription(call, plan_id)
        elif data == "dashboard":
            show_dashboard_callback(call)
        elif data == "compare_plans":
            show_plan_comparison(call)
        elif data == "learn_more":
            show_learn_more(call)
        elif data == "support":
            show_support_info(call)

        bot.answer_callback_query(call.id)

    except Exception as e:
        logger.error(f"Callback error: {e}")
        bot.answer_callback_query(call.id, "❌ An error occurred", show_alert=True)

def show_plan_details(call, plan_id: str):
    """Show detailed plan information"""
    plan = PLANS.get(plan_id)
    if not plan:
        bot.edit_message_text("❌ Plan not found", call.from_user.id, call.message.message_id)
        return

    details_text = (
        f"{plan['name']}\n\n"
        f"📝 **Description:**\n{plan['description']}\n\n"
        f"💰 **Price:** {plan['price']} ⭐ per month\n"
        f"⏰ **Duration:** {plan['duration']} days\n\n"
        "✨ **Features Included:**\n"
    )
    for feature in plan["features"]:
        details_text += f"• {feature}\n"
    details_text += "\n🎯 Perfect for your needs!"

    keyboard = InlineKeyboardMarkup()
    keyboard.row(InlineKeyboardButton(f"💳 Subscribe ({plan['price']} ⭐)", callback_data=f"subscribe_{plan_id}"))
    keyboard.row(InlineKeyboardButton("🔙 Back to Plans", callback_data="show_plans"))

    bot.edit_message_text(details_text, call.from_user.id, call.message.message_id, reply_markup=keyboard, parse_mode='Markdown')

def process_subscription(call, plan_id: str):
    """Process subscription purchase"""
    user_id = call.from_user.id

    try:
        import asyncio
        success = asyncio.run(neonpay.send_payment(user_id, plan_id))

        if success:
            bot.edit_message_text(
                "💫 **Payment Invoice Sent!**\n\n"
                "Please check your messages and complete the payment.\n"
                "Your subscription will be activated immediately after payment confirmation.\n\n"
                "🎉 Welcome to the premium experience!",
                call.from_user.id,
                call.message.message_id,
                parse_mode='Markdown'
            )
        else:
            bot.edit_message_text(
                "❌ Failed to create payment. Please try again.",
                call.from_user.id,
                call.message.message_id
            )

    except Exception as e:
        logger.error(f"Subscription error for user {user_id}: {e}")
        bot.edit_message_text(f"❌ Error: {e}", call.from_user.id, call.message.message_id)

def show_plan_comparison(call):
    """Show plan comparison table"""
    comparison_text = (
        "📊 **Plan Comparison**\n\n"
        "**📱 Basic Plan (99 ⭐)**\n"
        "• 5 Projects\n"
        "• Basic Support\n"
        "• 1GB Storage\n\n"
        "**💼 Pro Plan (299 ⭐)**\n"
        "• Unlimited Projects\n"
        "• Priority Support\n"
        "• 10GB Storage\n"
        "• Advanced Analytics\n\n"
        "**🏢 Enterprise Plan (599 ⭐)**\n"
        "• Everything in Pro\n"
        "• Team Collaboration\n"
        "• 100GB Storage\n"
        "• Custom Integrations\n"
        "• Dedicated Manager\n\n"
        "💡 Most popular: Pro Plan"
    )

    keyboard = InlineKeyboardMarkup()
    keyboard.row(InlineKeyboardButton("🛍️ Choose Plan", callback_data="show_plans"))

    bot.edit_message_text(comparison_text, call.from_user.id, call.message.message_id, reply_markup=keyboard, parse_mode='Markdown')

def show_learn_more(call):
    """Show detailed information about the service"""
    info_text = (
        "ℹ️ **About Our Service**\n\n"
        "🚀 **What We Offer:**\n"
        "• Professional project management tools\n"
        "• Secure cloud storage and sync\n"
        "• Real-time collaboration features\n"
        "• Advanced analytics and reporting\n"
        "• 24/7 priority support\n\n"
        "🏆 **Why Choose Us:**\n"
        "• 99.9% uptime guarantee\n"
        "• Enterprise-grade security\n"
        "• Regular feature updates\n"
        "• Dedicated customer success team\n"
        "• 30-day money-back guarantee\n\n"
        "💫 **Powered by Telegram Stars:**\n"
        "• Instant payments\n"
        "• No credit cards needed\n"
        "• Secure and private\n"
        "• Global accessibility"
    )

    keyboard = InlineKeyboardMarkup()
    keyboard.row(InlineKeyboardButton("🛍️ View Plans", callback_data="show_plans"))

    bot.edit_message_text(info_text, call.from_user.id, call.message.message_id, reply_markup=keyboard, parse_mode='Markdown')

def show_support_info(call):
    """Show support contact information"""
    support_text = (
        "📞 **Support & Contact**\n\n"
        "**Customer Support:**\n"
        "💬 Telegram: @neonpay_support\n"
        "📧 Email: support@neonpay.com\n"
        "📞 Phone: +1 (555) 123-4567\n\n"
        "**Business Hours:**\n"
        "🕘 Monday-Friday: 9 AM - 6 PM UTC\n"
        "🕘 Saturday: 10 AM - 4 PM UTC\n"
        "🕘 Sunday: Closed\n\n"
        "**Response Times:**\n"
        "• Basic Plan: 24 hours\n"
        "• Pro Plan: 4 hours\n"
        "• Enterprise: 1 hour\n\n"
        "**Self-Help Resources:**\n"
        "📚 Knowledge Base: help.neonpay.com\n"
        "🎥 Video Tutorials: youtube.com/neonpay\n"
        "💬 Community: t.me/neonpay_community"
    )

    bot.edit_message_text(support_text, call.from_user.id, call.message.message_id, parse_mode='Markdown')

def show_dashboard_callback(call):
    """Show dashboard via callback"""
    user_id = call.from_user.id

    if not is_subscribed(user_id):
        bot.edit_message_text(
            "❌ You need an active subscription to access the dashboard. Use /plans to subscribe!",
            call.from_user.id,
            call.message.message_id
        )
        return

    plan = get_user_plan(user_id)
    dashboard_text = (
        f"📊 **Your Dashboard**\n\n"
        f"👤 User: {call.from_user.first_name}\n"
        f"📋 Plan: {plan['plan_name']}\n"
        f"📅 Expires: {time.strftime('%Y-%m-%d', time.localtime(plan['expiry_date']))}\n\n"
        "📈 **Quick Stats:**\n"
        "• Projects: 5 active\n"
        "• Storage Used: 2.3GB\n"
        "• API Calls: 1,247 this month\n"
        "• Support Tickets: 0 open\n\n"
        "🚀 Everything looks great!"
    )

    keyboard = InlineKeyboardMarkup()
    keyboard.row(
        InlineKeyboardButton("📁 Projects", callback_data="projects"),
        InlineKeyboardButton("📊 Analytics", callback_data="analytics")
    )
    keyboard.row(
        InlineKeyboardButton("⚙️ Settings", callback_data="settings"),
        InlineKeyboardButton("🔄 Renew", callback_data="show_plans")
    )

    bot.edit_message_text(dashboard_text, call.from_user.id, call.message.message_id, reply_markup=keyboard, parse_mode='Markdown')
    

# Initialize and run
if __name__ == '__main__':
    logger.info("🚀 Starting NEONPAY pyTelegramBotAPI Demo...")
    
    # Setup payment stages
    setup_payment_stages()
    
    logger.info("✅ Bot started successfully!")
    logger.info("💫 NEONPAY is ready to process payments!")
    
    # Start polling
    bot.infinity_polling()


                



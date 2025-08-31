"""
NEONPAY python-telegram-bot Example
Complete example showing how to use NEONPAY with python-telegram-bot v20.0+
"""

import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler, 
    ContextTypes, MessageHandler, filters
)

from neonpay import create_neonpay, PaymentStage, PaymentResult, PaymentStatus

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Bot token
BOT_TOKEN = "YOUR_BOT_TOKEN"  # Replace with your bot token

# Service catalog
SERVICES = {
    "web_design": {
        "name": "🎨 Web Design",
        "description": "Professional website design service",
        "price": 1000,
        "delivery_time": "5-7 days"
    },
    "logo_design": {
        "name": "🎯 Logo Design", 
        "description": "Custom logo design with revisions",
        "price": 300,
        "delivery_time": "2-3 days"
    },
    "seo_audit": {
        "name": "📈 SEO Audit",
        "description": "Complete SEO analysis and recommendations",
        "price": 150,
        "delivery_time": "1-2 days"
    },
    "content_writing": {
        "name": "✍️ Content Writing",
        "description": "Professional content writing service",
        "price": 200,
        "delivery_time": "3-4 days"
    }
}

async def setup_neonpay(application: Application) -> None:
    """Initialize NEONPAY with payment stages"""
    global neonpay
    
    # Create NEONPAY instance
    neonpay = create_neonpay(application, "Thank you for choosing our services! 🚀")
    
    # Create payment stages for all services
    for service_id, service in SERVICES.items():
        stage = PaymentStage(
            title=service["name"],
            description=f"{service['description']} (Delivery: {service['delivery_time']})",
            price=service["price"],
            label=f"Order for {service['price']} ⭐",
            photo_url=f"https://via.placeholder.com/400x300/FF5722/white?text={service['name'].split()[1]}",
            payload={
                "service_id": service_id,
                "service_name": service["name"],
                "delivery_time": service["delivery_time"],
                "category": "professional_service"
            }
        )
        neonpay.create_payment_stage(service_id, stage)
    
    logger.info("✅ NEONPAY initialized with payment stages")

# Payment completion handler
async def handle_payment(result: PaymentResult) -> None:
    """Process successful service orders"""
    user_id = result.user_id
    amount = result.amount
    service_id = result.metadata.get("service_id")
    service_name = result.metadata.get("service_name", "Unknown Service")
    delivery_time = result.metadata.get("delivery_time", "Unknown")
    
    logger.info(f"💼 Service ordered: {service_name} by user {user_id} for {amount} ⭐")
    
    # Send order confirmation
    confirmation_text = (
        f"✅ **Order Confirmed!**\n\n"
        f"🛍️ Service: {service_name}\n"
        f"💰 Amount: {amount} ⭐\n"
        f"⏰ Delivery: {delivery_time}\n"
        f"📋 Order ID: #{result.transaction_id or 'NEON' + str(user_id)[-4:]}\n\n"
        f"📞 We'll contact you within 24 hours to discuss project details.\n"
        f"📧 Check your messages for further instructions!"
    )
    
    # Create action buttons
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("📋 Project Brief", callback_data=f"brief_{service_id}")],
        [InlineKeyboardButton("💬 Contact Manager", callback_data="contact_manager")],
        [InlineKeyboardButton("📊 Order Status", callback_data=f"status_{service_id}")]
    ])
    
    try:
        # Get application instance to send message
        app = neonpay.adapter.application
        await app.bot.send_message(
            user_id, 
            confirmation_text, 
            reply_markup=keyboard,
            parse_mode='Markdown'
        )
        
        # Start project workflow
        await initiate_project(user_id, service_id, result.transaction_id)
        
    except Exception as e:
        logger.error(f"Failed to send confirmation to user {user_id}: {e}")

async def initiate_project(user_id: int, service_id: str, transaction_id: str) -> None:
    """Start project workflow after payment"""
    # In a real application, you would:
    # 1. Create project in database
    # 2. Assign project manager
    # 3. Send project brief form
    # 4. Schedule initial consultation
    
    logger.info(f"🚀 Project initiated for user {user_id}, service {service_id}")

# Command handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send welcome message"""
    welcome_text = (
        "🏢 **Welcome to Professional Services Bot!**\n\n"
        "We offer high-quality digital services:\n"
        "• Web Design & Development\n"
        "• Logo & Brand Design\n"
        "• SEO & Marketing\n"
        "• Content Creation\n\n"
        "💫 All payments processed securely with Telegram Stars!\n\n"
        "Use /services to browse our offerings."
    )
    
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🛍️ View Services", callback_data="show_services")],
        [InlineKeyboardButton("📞 Contact Us", callback_data="contact_info")]
    ])
    
    await update.message.reply_text(
        welcome_text, 
        reply_markup=keyboard,
        parse_mode='Markdown'
    )

async def services(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show available services"""
    await show_services_catalog(update.effective_user.id, context)

async def portfolio(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show portfolio examples"""
    portfolio_text = (
        "🎨 **Our Portfolio**\n\n"
        "Recent projects:\n"
        "• E-commerce website for TechStore\n"
        "• Brand identity for StartupCo\n"
        "• SEO campaign for LocalBiz\n"
        "• Content strategy for BlogSite\n\n"
        "🏆 100+ satisfied clients\n"
        "⭐ 4.9/5 average rating\n"
        "🚀 2-week average delivery"
    )
    
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🛍️ Order Service", callback_data="show_services")],
        [InlineKeyboardButton("💬 Get Quote", callback_data="get_quote")]
    ])
    
    await update.message.reply_text(
        portfolio_text,
        reply_markup=keyboard,
        parse_mode='Markdown'
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show help information"""
    help_text = (
        "🆘 **Help & Support**\n\n"
        "**Available Commands:**\n"
        "• /start - Welcome message\n"
        "• /services - Browse services\n"
        "• /portfolio - View our work\n"
        "• /contact - Contact information\n"
        "• /help - This help message\n\n"
        "**How to Order:**\n"
        "1. Browse services with /services\n"
        "2. Select a service you need\n"
        "3. Pay with Telegram Stars\n"
        "4. Fill out project brief\n"
        "5. Get your project delivered!\n\n"
        "**Payment Info:**\n"
        "• We accept Telegram Stars (⭐)\n"
        "• Payments are instant and secure\n"
        "• Refunds available within 24h\n\n"
        "Need help? Contact @support"
    )
    
    await update.message.reply_text(help_text, parse_mode='Markdown')

async def show_services_catalog(user_id: int, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Display services catalog"""
    catalog_text = "🛍️ **Professional Services**\n\nChoose a service to order:"
    
    # Create service buttons
    keyboard_buttons = []
    for service_id, service in SERVICES.items():
        button_text = f"{service['name']} - {service['price']} ⭐"
        keyboard_buttons.append([
            InlineKeyboardButton(
                text=button_text,
                callback_data=f"service_{service_id}"
            )
        ])
    
    keyboard_buttons.append([
        InlineKeyboardButton("💬 Custom Quote", callback_data="custom_quote")
    ])
    
    keyboard = InlineKeyboardMarkup(keyboard_buttons)
    
    try:
        await context.bot.send_message(
            user_id, 
            catalog_text, 
            reply_markup=keyboard,
            parse_mode='Markdown'
        )
    except Exception as e:
        logger.error(f"Failed to send catalog to user {user_id}: {e}")

# Callback query handlers
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle inline button presses"""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    user_id = query.from_user.id
    
    if data == "show_services":
        await show_services_catalog(user_id, context)
        
    elif data.startswith("service_"):
        service_id = data.split("_")[1]
        await show_service_details(query, service_id, context)
        
    elif data.startswith("order_"):
        service_id = data.split("_")[1]
        await process_order(query, service_id, context)
        
    elif data.startswith("brief_"):
        service_id = data.split("_")[1]
        await send_project_brief(query, service_id, context)
        
    elif data == "contact_manager":
        await show_contact_info(query, context)
        
    elif data == "contact_info":
        await show_contact_info(query, context)
        
    elif data == "custom_quote":
        await request_custom_quote(query, context)

async def show_service_details(query, service_id: str, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show detailed service information"""
    service = SERVICES.get(service_id)
    if not service:
        await query.edit_message_text("❌ Service not found")
        return
    
    details_text = (
        f"{service['name']}\n\n"
        f"📝 **Description:**\n{service['description']}\n\n"
        f"💰 **Price:** {service['price']} ⭐\n"
        f"⏰ **Delivery:** {service['delivery_time']}\n\n"
        f"**What's Included:**\n"
        f"• Professional consultation\n"
        f"• Custom design/development\n"
        f"• Unlimited revisions\n"
        f"• Final files delivery\n"
        f"• 30-day support\n\n"
        f"Ready to order?"
    )
    
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton(f"💳 Order Now ({service['price']} ⭐)", callback_data=f"order_{service_id}")],
        [InlineKeyboardButton("🔙 Back to Services", callback_data="show_services")]
    ])
    
    await query.edit_message_text(details_text, reply_markup=keyboard, parse_mode='Markdown')

async def process_order(query, service_id: str, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Process service order"""
    user_id = query.from_user.id
    
    try:
        success = await neonpay.send_payment(user_id, service_id)
        if success:
            await query.edit_message_text(
                "💫 **Payment Invoice Sent!**\n\n"
                "Please check your messages and complete the payment.\n"
                "We'll start working on your project immediately after payment confirmation."
            )
        else:
            await query.edit_message_text("❌ Failed to create payment. Please try again.")
    except Exception as e:
        logger.error(f"Order error for user {user_id}: {e}")
        await query.edit_message_text(f"❌ Error: {e}")

async def send_project_brief(query, service_id: str, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send project brief form"""
    service = SERVICES.get(service_id)
    brief_text = (
        f"📋 **Project Brief - {service['name']}**\n\n"
        f"Please provide the following information:\n\n"
        f"1. **Project Goals:** What do you want to achieve?\n"
        f"2. **Target Audience:** Who is your audience?\n"
        f"3. **Style Preferences:** Any specific style/design preferences?\n"
        f"4. **Timeline:** Any specific deadlines?\n"
        f"5. **Additional Notes:** Anything else we should know?\n\n"
        f"📧 Send your brief to: projects@example.com\n"
        f"💬 Or reply to this message with your details."
    )
    
    await query.edit_message_text(brief_text, parse_mode='Markdown')

async def show_contact_info(query, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show contact information"""
    contact_text = (
        "📞 **Contact Information**\n\n"
        "**Project Manager:**\n"
        "👤 Sarah Johnson\n"
        "📧 sarah@example.com\n"
        "💬 @sarah_pm\n\n"
        "**Support Team:**\n"
        "📧 support@example.com\n"
        "💬 @support_bot\n"
        "📞 +1 (555) 123-4567\n\n"
        "**Business Hours:**\n"
        "🕘 Monday-Friday: 9 AM - 6 PM UTC\n"
        "🕘 Saturday: 10 AM - 4 PM UTC\n"
        "🕘 Sunday: Closed\n\n"
        "⚡ Average response time: 2 hours"
    )
    
    await query.edit_message_text(contact_text, parse_mode='Markdown')

async def request_custom_quote(query, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle custom quote request"""
    quote_text = (
        "💼 **Custom Quote Request**\n\n"
        "Need something specific? We'd love to help!\n\n"
        "Please describe your project:\n"
        "• What service do you need?\n"
        "• What's your budget range?\n"
        "• What's your timeline?\n"
        "• Any special requirements?\n\n"
        "📧 Send details to: quotes@example.com\n"
        "💬 Or contact our sales team: @sales_team\n\n"
        "We'll get back to you within 24 hours with a custom quote!"
    )
    
    await query.edit_message_text(quote_text, parse_mode='Markdown')

def main() -> None:
    """Run the bot"""
    # Create application
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Setup NEONPAY
    import asyncio
    asyncio.create_task(setup_neonpay(application))
    
    # Register payment handler
    neonpay.on_payment(handle_payment)
    
    # Add command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("services", services))
    application.add_handler(CommandHandler("portfolio", portfolio))
    application.add_handler(CommandHandler("help", help_command))
    
    # Add callback handler
    application.add_handler(CallbackQueryHandler(button_handler))
    
    # Log startup
    logger.info("🚀 Starting NEONPAY python-telegram-bot Demo...")
    logger.info("💫 NEONPAY is ready to process payments!")
    
    # Run the bot
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()

"""
NEONPAY Templates - Pre-built templates and UI builder system
Provides ready-to-use templates for common bot scenarios
"""

import json
import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional

from .core import PaymentStage

logger = logging.getLogger(__name__)


class TemplateType(Enum):
    """Types of templates"""

    DIGITAL_STORE = "digital_store"
    SUBSCRIPTION_SERVICE = "subscription_service"
    DONATION_BOT = "donation_bot"
    COURSE_PLATFORM = "course_platform"
    PREMIUM_FEATURES = "premium_features"
    CUSTOM = "custom"


class ThemeColor(Enum):
    """Predefined theme colors"""

    BLUE = "#007bff"
    GREEN = "#28a745"
    RED = "#dc3545"
    YELLOW = "#ffc107"
    PURPLE = "#6f42c1"
    ORANGE = "#fd7e14"
    TEAL = "#20c997"
    PINK = "#e83e8c"


@dataclass
class ThemeConfig:
    """Theme configuration"""

    primary_color: str = ThemeColor.BLUE.value
    secondary_color: str = "#6c757d"
    accent_color: str = "#17a2b8"
    background_color: str = "#ffffff"
    text_color: str = "#212529"
    success_color: str = "#28a745"
    warning_color: str = "#ffc107"
    danger_color: str = "#dc3545"
    font_family: str = "Arial, sans-serif"
    border_radius: int = 8
    shadow: bool = True


@dataclass
class TemplateProduct:
    """Template product definition"""

    id: str
    name: str
    description: str
    price: int
    category: str = "general"
    image_url: Optional[str] = None
    features: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)


@dataclass
class TemplateCategory:
    """Template category definition"""

    id: str
    name: str
    description: str
    icon: str = "📦"
    products: List[TemplateProduct] = field(default_factory=list)


@dataclass
class TemplateConfig:
    """Template configuration"""

    name: str
    description: str
    template_type: TemplateType
    theme: ThemeConfig = field(default_factory=ThemeConfig)
    categories: List[TemplateCategory] = field(default_factory=list)
    welcome_message: str = ""
    help_message: str = ""
    admin_commands: List[str] = field(default_factory=list)
    custom_styles: Dict[str, str] = field(default_factory=dict)


class DigitalStoreTemplate:
    """Digital store template with products and categories"""

    @staticmethod
    def create_template() -> TemplateConfig:
        """Create digital store template"""
        products = [
            TemplateProduct(
                id="premium_access",
                name="Premium Access",
                description="Unlock all premium features for 30 days",
                price=25,
                category="subscriptions",
                features=["Unlimited access", "Priority support", "Advanced features"],
                tags=["premium", "subscription"],
            ),
            TemplateProduct(
                id="custom_theme",
                name="Custom Theme",
                description="Personalized bot theme and colors",
                price=15,
                category="customization",
                features=["Custom colors", "Personal logo", "Unique design"],
                tags=["theme", "customization"],
            ),
            TemplateProduct(
                id="priority_support",
                name="Priority Support",
                description="24/7 priority customer support",
                price=30,
                category="support",
                features=["Fast response", "Expert help", "24/7 availability"],
                tags=["support", "priority"],
            ),
            TemplateProduct(
                id="advanced_analytics",
                name="Advanced Analytics",
                description="Detailed analytics and reporting",
                price=20,
                category="analytics",
                features=["Revenue tracking", "User insights", "Custom reports"],
                tags=["analytics", "reporting"],
            ),
        ]

        categories = [
            TemplateCategory(
                id="subscriptions",
                name="Subscriptions",
                description="Premium subscription plans",
                icon="👑",
                products=[p for p in products if p.category == "subscriptions"],
            ),
            TemplateCategory(
                id="customization",
                name="Customization",
                description="Custom themes and designs",
                icon="🎨",
                products=[p for p in products if p.category == "customization"],
            ),
            TemplateCategory(
                id="support",
                name="Support",
                description="Customer support services",
                icon="⚡",
                products=[p for p in products if p.category == "support"],
            ),
            TemplateCategory(
                id="analytics",
                name="Analytics",
                description="Analytics and reporting tools",
                icon="📊",
                products=[p for p in products if p.category == "analytics"],
            ),
        ]

        return TemplateConfig(
            name="Digital Store",
            description="Complete digital store with products and categories",
            template_type=TemplateType.DIGITAL_STORE,
            theme=ThemeConfig(
                primary_color=ThemeColor.BLUE.value,
                secondary_color="#6c757d",
                accent_color="#17a2b8",
            ),
            categories=categories,
            welcome_message=(
                "🛒 Welcome to our Digital Store!\n\n"
                "Browse our premium products and unlock new features.\n"
                "All purchases are instant and secure!"
            ),
            help_message=(
                "📋 **Store Help**\n\n"
                "• /store - Browse products\n"
                "• /categories - View categories\n"
                "• /help - Get help\n"
                "• /contact - Contact support"
            ),
            admin_commands=["/admin", "/stats", "/products", "/orders"],
        )


class SubscriptionServiceTemplate:
    """Subscription service template"""

    @staticmethod
    def create_template() -> TemplateConfig:
        """Create subscription service template"""
        products = [
            TemplateProduct(
                id="basic_plan",
                name="Basic Plan",
                description="Essential features for beginners",
                price=10,
                category="plans",
                features=["Basic features", "Email support", "5GB storage"],
                tags=["basic", "starter"],
            ),
            TemplateProduct(
                id="pro_plan",
                name="Pro Plan",
                description="Advanced features for professionals",
                price=25,
                category="plans",
                features=[
                    "All basic features",
                    "Priority support",
                    "50GB storage",
                    "Advanced analytics",
                ],
                tags=["pro", "professional"],
            ),
            TemplateProduct(
                id="enterprise_plan",
                name="Enterprise Plan",
                description="Full-featured solution for businesses",
                price=50,
                category="plans",
                features=[
                    "All pro features",
                    "24/7 support",
                    "Unlimited storage",
                    "Custom integrations",
                ],
                tags=["enterprise", "business"],
            ),
        ]

        categories = [
            TemplateCategory(
                id="plans",
                name="Subscription Plans",
                description="Choose your perfect plan",
                icon="📋",
                products=products,
            )
        ]

        return TemplateConfig(
            name="Subscription Service",
            description="Subscription-based service with multiple plans",
            template_type=TemplateType.SUBSCRIPTION_SERVICE,
            theme=ThemeConfig(
                primary_color=ThemeColor.GREEN.value,
                secondary_color="#6c757d",
                accent_color="#28a745",
            ),
            categories=categories,
            welcome_message=(
                "🎯 Welcome to our Subscription Service!\n\n"
                "Choose the perfect plan for your needs.\n"
                "Upgrade or downgrade anytime!"
            ),
            help_message=(
                "📋 **Subscription Help**\n\n"
                "• /plans - View subscription plans\n"
                "• /subscribe - Subscribe to a plan\n"
                "• /my_subscription - View current subscription\n"
                "• /cancel - Cancel subscription"
            ),
            admin_commands=["/admin", "/subscribers", "/revenue", "/plans"],
        )


class DonationBotTemplate:
    """Donation bot template"""

    @staticmethod
    def create_template() -> TemplateConfig:
        """Create donation bot template"""
        products = [
            TemplateProduct(
                id="donate_1",
                name="Small Support",
                description="1⭐ support: Will be used for bot server costs",
                price=1,
                category="donations",
                features=["Server maintenance", "Basic features"],
                tags=["small", "support"],
            ),
            TemplateProduct(
                id="donate_10",
                name="Medium Support",
                description="10⭐ support: Will be spent on developing new features",
                price=10,
                category="donations",
                features=["Feature development", "Bug fixes", "Improvements"],
                tags=["medium", "development"],
            ),
            TemplateProduct(
                id="donate_50",
                name="Big Support",
                description="50⭐ big support: Will be used for bot development and promotion",
                price=50,
                category="donations",
                features=["Major development", "Marketing", "Premium features"],
                tags=["big", "premium"],
            ),
        ]

        categories = [
            TemplateCategory(
                id="donations",
                name="Support Options",
                description="Choose how to support the bot",
                icon="❤️",
                products=products,
            )
        ]

        return TemplateConfig(
            name="Donation Bot",
            description="Bot for accepting donations and support",
            template_type=TemplateType.DONATION_BOT,
            theme=ThemeConfig(
                primary_color=ThemeColor.PINK.value,
                secondary_color="#6c757d",
                accent_color="#e83e8c",
            ),
            categories=categories,
            welcome_message=(
                "❤️ Thank you for using our bot!\n\n"
                "If you find it helpful, consider supporting development.\n"
                "Every contribution helps keep the bot running!"
            ),
            help_message=(
                "📋 **Support Help**\n\n"
                "• /donate - Support the bot\n"
                "• /support - Contact support\n"
                "• /about - Learn more about the bot"
            ),
            admin_commands=["/admin", "/donations", "/stats", "/supporters"],
        )


class CoursePlatformTemplate:
    """Course platform template"""

    @staticmethod
    def create_template() -> TemplateConfig:
        """Create course platform template"""
        products = [
            TemplateProduct(
                id="beginner_course",
                name="Beginner Course",
                description="Learn the basics with our comprehensive beginner course",
                price=30,
                category="courses",
                features=[
                    "10 video lessons",
                    "PDF materials",
                    "Certificate",
                    "Community access",
                ],
                tags=["beginner", "course"],
            ),
            TemplateProduct(
                id="advanced_course",
                name="Advanced Course",
                description="Master advanced techniques and strategies",
                price=60,
                category="courses",
                features=[
                    "20 video lessons",
                    "Live sessions",
                    "Personal mentor",
                    "Advanced materials",
                ],
                tags=["advanced", "mentor"],
            ),
            TemplateProduct(
                id="premium_bundle",
                name="Premium Bundle",
                description="All courses + exclusive bonuses",
                price=100,
                category="courses",
                features=[
                    "All courses",
                    "Exclusive bonuses",
                    "Lifetime access",
                    "VIP support",
                ],
                tags=["bundle", "premium", "lifetime"],
            ),
        ]

        categories = [
            TemplateCategory(
                id="courses",
                name="Online Courses",
                description="Learn with our expert courses",
                icon="🎓",
                products=products,
            )
        ]

        return TemplateConfig(
            name="Course Platform",
            description="Online learning platform with courses",
            template_type=TemplateType.COURSE_PLATFORM,
            theme=ThemeConfig(
                primary_color=ThemeColor.PURPLE.value,
                secondary_color="#6c757d",
                accent_color="#6f42c1",
            ),
            categories=categories,
            welcome_message=(
                "🎓 Welcome to our Learning Platform!\n\n"
                "Discover our courses and start your learning journey.\n"
                "Expert instructors, quality content, lifetime access!"
            ),
            help_message=(
                "📋 **Learning Help**\n\n"
                "• /courses - Browse available courses\n"
                "• /my_courses - View purchased courses\n"
                "• /progress - Check learning progress\n"
                "• /certificates - Download certificates"
            ),
            admin_commands=["/admin", "/courses", "/students", "/revenue"],
        )


class TemplateManager:
    """Manages templates and template creation"""

    def __init__(self) -> None:
        self._templates: Dict[str, TemplateConfig] = {}
        self._load_default_templates()

    def _load_default_templates(self) -> None:
        """Load default templates"""
        templates = [
            DigitalStoreTemplate.create_template(),
            SubscriptionServiceTemplate.create_template(),
            DonationBotTemplate.create_template(),
            CoursePlatformTemplate.create_template(),
        ]

        for template in templates:
            self._templates[template.name.lower().replace(" ", "_")] = template

    def get_template(self, name: str) -> Optional[TemplateConfig]:
        """Get template by name"""
        return self._templates.get(name.lower().replace(" ", "_"))

    def list_templates(self) -> List[TemplateConfig]:
        """List all available templates"""
        return list(self._templates.values())

    def create_custom_template(
        self,
        name: str,
        description: str,
        products: List[TemplateProduct],
        theme: Optional[ThemeConfig] = None,
        categories: Optional[List[TemplateCategory]] = None,
    ) -> TemplateConfig:
        """Create custom template"""
        if not categories:
            categories = [
                TemplateCategory(
                    id="custom",
                    name="Products",
                    description="Custom products",
                    icon="📦",
                    products=products,
                )
            ]

        template = TemplateConfig(
            name=name,
            description=description,
            template_type=TemplateType.CUSTOM,
            theme=theme or ThemeConfig(),
            categories=categories or [],
            welcome_message=f"Welcome to {name}!",
            help_message=f"Help for {name}",
        )

        self._templates[name.lower().replace(" ", "_")] = template
        return template

    def convert_to_payment_stages(
        self, template: TemplateConfig
    ) -> Dict[str, PaymentStage]:
        """Convert template to payment stages"""
        stages = {}

        for category in template.categories:
            for product in category.products:
                stage = PaymentStage(
                    title=product.name,
                    description=product.description,
                    price=product.price,
                    photo_url=product.image_url,
                    payload={
                        "product_id": product.id,
                        "category": product.category,
                        "features": product.features,
                        "tags": product.tags,
                    },
                )
                stages[product.id] = stage

        return stages

    def generate_bot_code(
        self, template: TemplateConfig, bot_library: str = "aiogram"
    ) -> str:
        """Generate bot code from template"""
        if bot_library.lower() == "aiogram":
            return self._generate_aiogram_code(template)
        elif bot_library.lower() == "pyrogram":
            return self._generate_pyrogram_code(template)
        else:
            raise ValueError(f"Unsupported bot library: {bot_library}")

    def _generate_aiogram_code(self, template: TemplateConfig) -> str:
        """Generate Aiogram bot code"""
        stages = self.convert_to_payment_stages(template)

        code = f'''"""
Generated bot code for {template.name}
Template: {template.description}
"""

from aiogram import Bot, Dispatcher, Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup

from neonpay import create_neonpay, PaymentStage, PaymentStatus

# Bot configuration
BOT_TOKEN = "YOUR_BOT_TOKEN"
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
router = Router()

# Initialize NEONPAY
neonpay = create_neonpay(bot_instance=bot, dispatcher=dp)

# Create payment stages
'''

        for stage_id, stage in stages.items():
            code += f"""neonpay.create_payment_stage("{stage_id}", PaymentStage(
    title="{stage.title}",
    description="{stage.description}",
    price={stage.price},
    photo_url="{stage.photo_url or ''}",
    payload={stage.payload}
))

"""

        code += f'''
# Payment handler
@neonpay.on_payment
async def handle_payment(result):
    if result.status == PaymentStatus.COMPLETED:
        await bot.send_message(
            result.user_id,
            f"🎉 Thank you for your purchase!\\n\\n"
            f"Product: {{result.metadata.get('product_id', 'Unknown')}}\\n"
            f"Amount: {{result.amount}} stars\\n\\n"
            f"Your purchase has been processed successfully!"
        )

# Commands
@router.message(Command("start"))
async def start_command(message: Message):
    """Welcome message"""
    await message.answer("{template.welcome_message}")

@router.message(Command("help"))
async def help_command(message: Message):
    """Help message"""
    await message.answer("{template.help_message}")

@router.message(Command("store"))
async def store_command(message: Message):
    """Show store/products"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="{{product.name}} - {{product.price}}⭐", callback_data="buy:{{product.id}}")]
        for category in template.categories for product in category.products
    ])
    
    await message.answer("🛒 Choose a product:", reply_markup=keyboard)

@router.callback_query(F.data.startswith("buy:"))
async def buy_product(callback: CallbackQuery):
    """Handle product purchase"""
    product_id = callback.data.split(":")[1]
    await neonpay.send_payment(callback.from_user.id, product_id)
    await callback.answer("✅ Payment message sent")

# Include router and start
dp.include_router(router)

if __name__ == "__main__":
    import asyncio
    asyncio.run(dp.start_polling(bot))
'''

        return code

    def _generate_pyrogram_code(self, template: TemplateConfig) -> str:
        """Generate Pyrogram bot code"""
        stages = self.convert_to_payment_stages(template)

        code = f'''"""
Generated bot code for {template.name}
Template: {template.description}
"""

from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from neonpay import create_neonpay, PaymentStage, PaymentStatus

# Initialize Pyrogram client
app = Client("my_bot", bot_token="YOUR_BOT_TOKEN")

# Initialize NEONPAY
neonpay = create_neonpay(bot_instance=app)

# Create payment stages
'''

        for stage_id, stage in stages.items():
            code += f"""neonpay.create_payment_stage("{stage_id}", PaymentStage(
    title="{stage.title}",
    description="{stage.description}",
    price={stage.price},
    photo_url="{stage.photo_url or ''}",
    payload={stage.payload}
))

"""

        code += f'''
# Payment handler
@neonpay.on_payment
async def handle_payment(result):
    if result.status == PaymentStatus.COMPLETED:
        await app.send_message(
            result.user_id,
            f"🎉 Thank you for your purchase!\\n\\n"
            f"Product: {{result.metadata.get('product_id', 'Unknown')}}\\n"
            f"Amount: {{result.amount}} stars\\n\\n"
            f"Your purchase has been processed successfully!"
        )

# Commands
@app.on_message(filters.command("start"))
async def start_command(client, message):
    """Welcome message"""
    await message.reply("{template.welcome_message}")

@app.on_message(filters.command("help"))
async def help_command(client, message):
    """Help message"""
    await message.reply("{template.help_message}")

@app.on_message(filters.command("store"))
async def store_command(client, message):
    """Show store/products"""
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("{{product.name}} - {{product.price}}⭐", callback_data="buy:{{product.id}}")]
        for category in template.categories for product in category.products
    ])
    
    await message.reply("🛒 Choose a product:", reply_markup=keyboard)

@app.on_callback_query()
async def handle_callback(client, callback_query):
    """Handle callback queries"""
    if callback_query.data.startswith("buy:"):
        product_id = callback_query.data.split(":")[1]
        await neonpay.send_payment(callback_query.from_user.id, product_id)
        await callback_query.answer("✅ Payment message sent")

# Start the bot
if __name__ == "__main__":
    app.run()
'''

        return code

    def export_template(
        self, template: TemplateConfig, format_type: str = "json"
    ) -> str:
        """Export template to different formats"""
        if format_type.lower() == "json":
            return json.dumps(
                {
                    "name": template.name,
                    "description": template.description,
                    "template_type": template.template_type.value,
                    "theme": {
                        "primary_color": template.theme.primary_color,
                        "secondary_color": template.theme.secondary_color,
                        "accent_color": template.theme.accent_color,
                    },
                    "categories": [
                        {
                            "id": cat.id,
                            "name": cat.name,
                            "description": cat.description,
                            "icon": cat.icon,
                            "products": [
                                {
                                    "id": prod.id,
                                    "name": prod.name,
                                    "description": prod.description,
                                    "price": prod.price,
                                    "category": prod.category,
                                    "features": prod.features,
                                    "tags": prod.tags,
                                }
                                for prod in cat.products
                            ],
                        }
                        for cat in template.categories
                    ],
                    "welcome_message": template.welcome_message,
                    "help_message": template.help_message,
                },
                indent=2,
                ensure_ascii=False,
            )
        else:
            raise ValueError(f"Unsupported export format: {format_type}")

    def get_stats(self) -> Dict[str, Any]:
        """Get template system statistics"""
        total_products = sum(
            len(cat.products)
            for template in self._templates.values()
            for cat in template.categories
        )

        return {
            "total_templates": len(self._templates),
            "total_products": total_products,
            "template_types": list(
                set(t.template_type.value for t in self._templates.values())
            ),
            "available_templates": list(self._templates.keys()),
        }

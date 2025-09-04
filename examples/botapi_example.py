"""
Example usage of BotAPIAdapter with python-telegram-bot
Run with: python examples/botapi_example.py
"""

import asyncio
from telegram import Bot, Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    PreCheckoutQueryHandler,
    filters,
)
from neonpay import NeonPayCore, PaymentStage, BotAPIAdapter, PaymentResult

TOKEN = "YOUR_BOT_TOKEN"

bot = Bot(TOKEN)
adapter = BotAPIAdapter(bot)
neon = NeonPayCore(adapter)


async def start(update: Update, context):
    """Send a payment invoice to the user"""
    stage = PaymentStage(
        title="Подписка",
        description="1 месяц подписки",
        price=100,  # Цена в Telegram Stars
        label="Подписка",
        payload={"plan": "monthly"},
    )
    neon.create_payment_stage("subscription", stage)
    await neon.send_payment(update.effective_user.id, "subscription")


async def precheckout(update: Update, context):
    """Handle pre-checkout query"""
    await adapter.handle_pre_checkout_query(update.pre_checkout_query)


async def successful_payment(update: Update, context):
    """Handle successful payment"""
    await adapter.handle_successful_payment(update.message)


async def payment_callback(result: PaymentResult):
    """This function will be called when payment is successful"""
    print(f"✅ Пользователь {result.user_id} оплатил {result.amount} {result.currency}")


async def main():
    """Main entry point"""
    await adapter.setup_handlers(payment_callback)

    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(PreCheckoutQueryHandler(precheckout))
    app.add_handler(MessageHandler(filters.SUCCESSFUL_PAYMENT, successful_payment))

    await app.run_polling()


if __name__ == "__main__":
    asyncio.run(main())
  

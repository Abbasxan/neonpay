from pyrogram import Client, filters
from neon_stars_payments import send_invoice, StarsPaymentError

app = Client("stars_bot", api_id=12345, api_hash="your_api_hash", bot_token="YOUR_BOT_TOKEN")


@app.on_message(filters.command("donate") & filters.private)
async def donate_handler(client, message):
    try:
        await send_invoice(
            client=client,
            user_id=message.from_user.id,
            amount=50,
            label="🥐 50 ⭐",
            title="Поддержка проекта",
            description="Спасибо за твою поддержку! 🥐 50 звёздочек",
        )
    except StarsPaymentError as e:
        await message.reply(f"Ошибка: {e}")


app.run()

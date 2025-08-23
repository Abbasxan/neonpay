from pyrogram import Client, filters
from neon_stars_payments import NeonStars, StarsPaymentError

app = Client("stars_bot", api_id=12345, api_hash="your_api_hash", bot_token="YOUR_BOT_TOKEN")

# Инициализация библиотеки
stars = NeonStars(app, thank_you="Спасибо за поддержку!")

# Обработка успешной оплаты
@stars.on_payment
async def handle_payment(user_id: int, amount: int):
    print(f"🎉 Пользователь {user_id} оплатил {amount} ⭐")
    # Здесь можно сохранять в БД или выдавать плюшки


@app.on_message(filters.command("donate") & filters.private)
async def donate(client, message):
    try:
        await stars.send_donate(
            user_id=message.from_user.id,
            amount=50,
            label="🥐 50 ⭐",
            title="Поддержка проекта",
            description="Спасибо за твою поддержку!",
        )
    except StarsPaymentError as e:
        await message.reply(f"Ошибка: {e}")


app.run()

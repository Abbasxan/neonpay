# neon-stars-payments ⭐

Библиотека для Telegram-ботов (Pyrogram), позволяющая легко принимать оплату **звёздами (XTR)**.

## Установка
```bash
pip install neon-stars-payments

Пример использования

from pyrogram import Client, filters
from neon_stars_payments import send_invoice

app = Client("stars_bot", api_id=12345, api_hash="your_api_hash", bot_token="YOUR_BOT_TOKEN")

@app.on_message(filters.command("donate") & filters.private)
async def donate_handler(client, message):
    await send_invoice(
        client=client,
        user_id=message.from_user.id,
        amount=50,
        label="🥐 50 ⭐",
        title="Поддержка проекта",
        description="Спасибо за твою поддержку!"
    )

app.run()

Лицензия

MIT

---

### **`LICENSE`**

MIT License

---

### **`.gitignore`**

pycache/ *.pyc *.pyo *.pyd *.log .env .venv/ dist/ build/ *.egg-info/

---

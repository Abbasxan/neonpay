```markdown
# ![Neon Stars Payments](.github/neonpay-logo.jpg) neon-stars-payments ⭐

Библиотека для Telegram-ботов (Pyrogram), которая позволяет легко принимать оплату **звёздами (XTR)**.

---

## 📦 Установка

```bash
pip install neon-stars-payments
```

---

## 🚀 Пример использования

```python
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
```

---

## 💡 Особенности

- Лёгкая интеграция с Pyrogram  
- Поддержка оплаты **звёздами (XTR)**  
- Простое создание инвойсов для пользователей  
- Подходит для любых Telegram-ботов  

---

## 📝 Лицензия

MIT License

---

## ⚙ `.gitignore`

```
__pycache__/
*.pyc
*.pyo
*.pyd
*.log
.env
.venv/
dist/
build/
*.egg-info/
```

---

> Добавьте файл логотипа `.github/neonpay-logo.png` в проект, чтобы он отображался корректно в README.
```

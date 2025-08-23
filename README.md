```
markdown

<h2 align="center">
    ──「 NEON STARS PAYMENTS 」──
</h2>

<p align="center">
  <img src=".github/neonpay-logo.jpg" width="150"/>
</p>

Библиотека для Telegram-ботов (Pyrogram), которая позволяет легко принимать оплату **звёздами (XTR)**.

---

<p align="center">
<a href="https://github.com/Abbasxan/neonpay/stargazers"><img src="https://img.shields.io/github/stars/Abbasxan/neonpay?color=black&logo=github&logoColor=black&style=for-the-badge" alt="Stars" /></a>
<a href="https://github.com/Abbasxan/neonpay/network/members"> <img src="https://img.shields.io/github/forks/Abbasxan/neonpay?color=black&logo=github&logoColor=black&style=for-the-badge" /></a>
<a href="https://github.com/Abbasxan/neonpay/blob/master/LICENSE"> <img src="https://img.shields.io/badge/License-MIT-blueviolet?style=for-the-badge" alt="License" /> </a>
<a href="https://www.python.org/"> <img src="https://img.shields.io/badge/Written%20in-Python-skyblue?style=for-the-badge&logo=python" alt="Python" /> </a>
<a href="https://pypi.org/project/neon-stars-payments/"> <img src="https://img.shields.io/pypi/v/neon-stars-payments?color=white&label=PyPI&logo=python&logoColor=blue&style=for-the-badge" /></a>
<a href="https://github.com/Abbasxan/neonpay"> <img src="https://img.shields.io/github/repo-size/Abbasxan/neonpay?color=skyblue&logo=github&logoColor=blue&style=for-the-badge" /></a>
<a href="https://github.com/Abbasxan/neonpay/commits/main"> <img src="https://img.shields.io/github/last-commit/Abbasxan/neonpay?color=black&logo=github&logoColor=black&style=for-the-badge" /></a>
</p>

---

## 📦 Установка

```
bash pip install neonpay
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

import random
from pyrogram import filters
from config import app

qeddar_quotes = [
    "Qorxaqlar həmişə sussa, ədəbsizlər danışar.",
    "Həqiqət acıdır, amma ən güclü dərmandır.",
    "Yalnız güclü olanlar ədalətli ola bilər.",
    "Sözlər bıçaq kimidir, diqqətli istifadə et.",
    "Əsl qəddar ürək yox, zəifliyi gizlədəndir.",
    "Qorxmadan addım atan, dünyanı dəyişdirər.",
]

@app.on_message(filters.command("qeddarsoz") & filters.group, group=-1)
async def send_qeddar_quote(client, message):
    quote = random.choice(qeddar_quotes)
    await message.reply_text(f"🧠 <b>Qəddar Söz:</b>\n\n<i>{quote}</i>")

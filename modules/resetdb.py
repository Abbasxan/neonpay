import logging
from config import db, LOG_ID, OWNER_ID, app
from pyrogram import Client, filters
from pyrogram.types import Message
from language import get_language_for_message, load_language

# Логирование
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s",
)

# Функция сброса базы данных
async def reset_database(lang_code="az"):
    try:
        txt = load_language(lang_code)
        
        # Очищаем коллекции
        await db.users.delete_many({})
        await db.groups.delete_many({})
        logging.info(txt.get('resetdb_log_success', '✅ Database has been successfully reset.'))

        # Логируем сброс в группе
        if LOG_ID:
            log_message = txt.get('resetdb_log_message', '⚠️ Database has been reset!')
            await app.send_message(LOG_ID, log_message)
        return True
    except Exception as e:
        txt = load_language(lang_code)
        logging.error(txt.get('resetdb_log_success', '✅ Database has been successfully reset.').replace('✅', '❌') + f": {e}")
        return False

# Команда сброса базы данных
@app.on_message(filters.command("resetdb") & filters.user(OWNER_ID))
async def reset_db_handler(client: Client, message: Message):
    """Команда для сброса базы данных"""
    try:
        lang_code = await get_language_for_message(message)
        txt = load_language(lang_code)
        
        success = await reset_database(lang_code)
        if success:
            await message.reply(txt.get('resetdb_success', '✅ Database reset successfully!'))
        else:
            await message.reply(txt.get('resetdb_fail', '❌ Error occurred while resetting database. Please try again.'))
    except Exception as e:
        # Fallback на английский язык при ошибке
        txt = load_language("en")
        await message.reply(txt.get('resetdb_fail', '❌ Error occurred while resetting database. Please try again.'))

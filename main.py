import asyncio
import logging
from config import app, LOG_ID, scheduler, userbot
from pyrogram import idle
from pyrogram.errors import FloodWait
from modules.commands import set_bot_commands
from helpers.utils import create_ttl_index  # импортируем функцию

# Конфигурация логгирования
logging.basicConfig(
    level=logging.INFO,  # Можно DEBUG для подробного лога
    format='%(asctime)s | %(levelname)s | %(name)s | %(message)s'
)
logger = logging.getLogger(__name__)

async def send_log_message(message: str):
    try:
        await app.send_message(LOG_ID, message)
        logger.info(f"Log message sent: {message}")
    except Exception as e:
        logger.error(f"❌ Mesaj log kanalına göndərilə bilmədi: {e}")

async def start_bot():
    logger.info("Bot işə düşür...")

    try:
        await app.start()
        logger.info("Bot started successfully")
        
        # Инициализация базы данных
        from config import db
        logger.info("✅ База данных инициализирована")
        
        import modules
        import helpers
        import oyunlar
        import modules.economy
        import modules.botversion
        
        # Инициализация экономической системы
        from modules.economy.economy import EconomyManager
        from modules.economy.database import EconomyDB
        
        # Инициализация базы данных экономической системы
        await EconomyDB.initialize_database()
        
        economy_manager = EconomyManager()
        app.economy_manager = economy_manager
        logger.info("✅ Экономическая система инициализирована")
        
        if userbot:
            try:
                await userbot.start()
                logger.info("✅ Userbot started successfully")
            except Exception as e:
                logger.error(f"❌ Userbot start error: {e}")
        
    except FloodWait as e:
        logger.warning(f"⚠️ FloodWait xətası: {e.value} saniyə gözlənilir...")
        await asyncio.sleep(e.value)
        await app.start()
        logger.info("Bot restarted after FloodWait")

    try:
        scheduler.start()
        logger.info("✅ Планировщик задач запущен")
    except Exception as e:
        logger.error(f"❌ Ошибка запуска планировщика: {e}")

    await create_ttl_index()
    logger.info("TTL индекс создан")

    bot = await app.get_me()
    app.bot_info = bot  # əlavə et
    app.bot_username = bot.username

    await send_log_message("🚀 Bot başladı!")
    await set_bot_commands()
    logger.info("✅ Bot aktivdir.")
    await send_log_message("✅ Bot aktivdir.")

    await idle()
    

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(start_bot())
    

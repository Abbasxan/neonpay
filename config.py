import os
import logging
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient
from pyrogram import Client
from pyrogram.enums import ParseMode
from apscheduler.schedulers.asyncio import AsyncIOScheduler

load_dotenv()

# Основные переменные
BOT_TOKEN = "7616785434:AAGqGVrd_jOf02unEBFSXNEkGrPjNAoz81w"
BOT_ID = 8147521656
API_ID = os.getenv("API_ID")
API_HASH = os.getenv("API_HASH")
MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME")
OWNER_ID = int(os.getenv("OWNER_ID", "0"))
ADMINS = [int(x) for x in os.getenv("ADMINS", str(OWNER_ID)).split(",")]

USERBOT_SESSION = os.getenv("USERBOT_SESSION")  # String session для userbot
USERBOT_API_ID = os.getenv("USERBOT_API_ID", API_ID)  # Можно использовать те же API_ID/HASH
USERBOT_API_HASH = os.getenv("USERBOT_API_HASH", API_HASH)

# Ссылки
BOT_CHANEL = os.getenv("BOT_CHANEL")
SUPPORT_CHAT = os.getenv("SUPPORT_CHAT")
SUPPORT_CHANNEL = os.getenv("SUPPORT_CHANNEL")

# 🔧 Автор идеи и разработчик
DEV_ID = os.getenv("DEV_ID", "gaddar_dev")       # Без @
IDEA_ID = os.getenv("IDEA_ID", "idea_master")  # Без @


# Локализация
LANGUAGE_PATH = os.getenv("LANGUAGE_PATH", default="langs")
DEFAULT_LANGUAGE = os.getenv("DEFAULT_LANGUAGE", default="az")

# ID лог-группы
LOG_ID = int(os.getenv("LOG_ID", "0"))

REQUIRED_VARS = {
    "BOT_TOKEN": BOT_TOKEN,
    "API_ID": API_ID,
    "API_HASH": API_HASH,
    "MONGO_URI": MONGO_URI,
    "DB_NAME": DB_NAME,
    "OWNER_ID": OWNER_ID,
    "BOT_CHANEL": BOT_CHANEL,
    "SUPPORT_CHAT": SUPPORT_CHAT,
    "SUPPORT_CHANNEL": SUPPORT_CHANNEL,
    "DEV_ID": DEV_ID,
    "IDEA_ID": IDEA_ID,
    "USERBOT_SESSION": USERBOT_SESSION,
    "USERBOT_API_ID": USERBOT_API_ID,
    "USERBOT_API_HASH": USERBOT_API_HASH
}

for var, value in REQUIRED_VARS.items():
    if not value:
        raise ValueError(f"\u274c {var} не установлен!")

# Логирование
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s",
)

# Настройка DEBUG только для модулей экономики
economy_logger = logging.getLogger('modules.economy')
economy_logger.setLevel(logging.DEBUG)

# MongoDB
try:
    client = AsyncIOMotorClient(MONGO_URI)
    db = client[DB_NAME]
    users_collection = db["users"]
    groups_collection = db["groups"]
    warnings_collection = db["warnings"]
    clones_collection = db["clones"]
    
    # Коллекции для экономической системы
    currencies_collection = db["currencies"]
    balances_collection = db["balances"]
    transactions_collection = db["transactions"]
    achievements_collection = db["achievements"]
    
    # Коллекции для системы отчетов
    activity_collection = db["activity"]
    reports_collection = db["reports"]
    
    logging.info("✅ Подключение к MongoDB прошло успешно.")
except Exception as e:
    logging.error(f"❌ Не удалось подключиться к MongoDB: {e}")
    raise


# Pyrogram Client
app = Client(
    name="nowear",
    api_id=int(API_ID),
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    parse_mode=ParseMode.HTML
)

userbot = None
if USERBOT_SESSION:
    try:
        userbot = Client(
            name="antireklam_userbot",
            api_id=int(USERBOT_API_ID),
            api_hash=USERBOT_API_HASH,
            session_string=USERBOT_SESSION,
            parse_mode=ParseMode.HTML
        )
        logging.info("✅ Userbot клиент создан успешно.")
    except Exception as e:
        logging.error(f"❌ Ошибка создания userbot клиента: {e}")
        userbot = None
else:
    logging.warning("⚠️ USERBOT_SESSION не установлен. Userbot не будет работать.")

# Планировщик заданий
scheduler = AsyncIOScheduler()
# Планировщик будет запущен в main.py




OTHER_BOTS = {
    "metabase": {
        "username": "metabaserobot",  # Имя пользователя бота
        "name": "Meta Base",  # Красивая форма имени
        "description": "İstifadəçi adın dəyişərsə bunu sənə bildirəcək və ad dəyişiklik tarixçəsini görə biləcəksən."
    },
    "neonmusic": {
        "username": "neonmuzik_bot",  # Имя пользователя бота
        "name": "Neon Music",  # Красивая форма имени
        "description": "Musiqi botudur, musiqi dinləmək üçün istifadə edilə bilər. İşləməsi üçün admin olraq qrupa əlavə et və bu yetkiləri verməyin kifayətdir:Link ilə dəvət etmək,Səsli söhbət açmaq, ban yetkisin verin asistanı dəvət etməkdən çətinlik çəkməsin sonra bu yetkini ləğv edə bilərsiz."
    },
    "neonstringbot": {
        "username": "neonstringbot",  # Имя пользователя бота
        "name": "String Session",  # Красивая форма имени
        "description": "Musiqi  botları üçün aktiv strinq sessiyası yarada bilən botdur. Pyrogram v2.0.106 və Telethon v1. Qeyd bu bot qrup daxilində istifadə üçün deyil gizli olduğu üçün bota start ver və məlumatlarını kənar şəxslərlə paylaşma: @neonstringbot "
    }
    }

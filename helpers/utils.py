from pyrogram.types import User
from pyrogram.errors import PeerIdInvalid
from config import app, db

async def get_user_info(app, user_id: int) -> dict:
    try:
        user: User = await app.get_users(user_id)
        return {
            "id": user.id,
            "username": user.username,  # без @ и без HTML
            "first_name": user.first_name
        }
    except PeerIdInvalid:
        return {
            "id": user_id,
            "username": None,
            "first_name": f"ID {user_id}"
        }



async def create_ttl_index():
    try:
        await db.love_attempts.create_index("createdAt", expireAfterSeconds=86400)
        print("✅ TTL индекс для love_attempts создан")
    except Exception as e:
        print(f"❌ Ошибка создания TTL индекса: {e}")

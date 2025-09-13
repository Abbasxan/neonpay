# helpers/activity.py
import datetime
import logging
from pyrogram import Client, filters
from pyrogram.types import Message
from config import app, users_collection, groups_collection, activity_collection

logging.basicConfig(level=logging.INFO)

# Обновление активности в группах (кроме команд)
@app.on_message(filters.group, group=999)
async def update_group_activity(client: Client, message: Message):
    if message.text and message.text.startswith("/"):
        return  # Игнорируем команды
    
    # Проверяем, что есть пользователь
    if not message.from_user:
        return

    try:
        await groups_collection.update_one(
            {"_id": message.chat.id},
            {
                "$set": {
                    "group_id": message.chat.id,
                    "group_title": message.chat.title,
                    "last_activity": datetime.datetime.utcnow()
                },
                "$inc": {"message_count": 1}
            },
            upsert=True
        )
        
        # Отслеживаем для отчетов
        message_type = "text"
        if message.photo:
            message_type = "photo"
        elif message.video:
            message_type = "video"
        elif message.document:
            message_type = "document"
        elif message.voice:
            message_type = "voice"
        elif message.sticker:
            message_type = "sticker"
        elif message.animation:
            message_type = "gif"
            
        await track_message_for_reports(message.from_user.id, message.chat.id, message_type)
    except Exception as e:
        logging.error(f"Error updating group activity in chat {message.chat.id}: {e}")


# Обновление активности пользователей (кроме команд)
@app.on_message(filters.private, group=999)
async def update_user_activity(client: Client, message: Message):
    if message.text and message.text.startswith("/"):
        return  # Игнорируем команды
    
    # Проверяем, что есть пользователь
    if not message.from_user:
        return

    try:
        user_id = message.from_user.id
        now = datetime.datetime.utcnow()
        await users_collection.update_one(
            {"_id": user_id},
            {
                "$set": {"last_activity": now},
                "$setOnInsert": {"join_date": now}
            },
            upsert=True
        )
    except Exception as e:
        logging.error(f"Error updating user activity for user {user_id}: {e}")


# Отслеживание новых участников
@app.on_message(filters.new_chat_members)
async def track_new_members(client: Client, message: Message):
    """Отслеживание новых участников"""
    try:
        for member in message.new_chat_members:
            await track_member_activity(member.id, message.chat.id, "joined")
    except Exception as e:
        logging.error(f"Error tracking new members: {e}")


@app.on_message(filters.left_chat_member)
async def track_left_members(client: Client, message: Message):
    """Отслеживание ушедших участников"""
    try:
        if message.left_chat_member:
            await track_member_activity(message.left_chat_member.id, message.chat.id, "left")
    except Exception as e:
        logging.error(f"Error tracking left members: {e}")


# Функции для системы отчетов
async def track_message_for_reports(user_id: int, chat_id: int, message_type: str = "text"):
    """Отслеживание сообщений для отчетов"""
    try:
        now = datetime.datetime.utcnow()
        activity_data = {
            "user_id": user_id,
            "chat_id": chat_id,
            "timestamp": now,
            "message_type": message_type,
            "date": now.date().isoformat(),  # Преобразуем в строку
            "hour": now.hour,
            "weekday": now.weekday()  # 0 = Monday, 6 = Sunday
        }
        await activity_collection.insert_one(activity_data)
    except Exception as e:
        logging.error(f"Error tracking message activity: {e}")


async def track_member_activity(user_id: int, chat_id: int, action: str):
    """Отслеживание активности участников"""
    try:
        now = datetime.datetime.utcnow()
        member_data = {
            "user_id": user_id,
            "chat_id": chat_id,
            "timestamp": now,
            "type": "member",
            "action": action,  # "joined" или "left"
            "date": now.date().isoformat()  # Преобразуем в строку
        }
        await activity_collection.insert_one(member_data)
    except Exception as e:
        logging.error(f"Error tracking member activity: {e}")


async def get_activity_data(chat_id: int, start_date: datetime.datetime, end_date: datetime.datetime):
    """Получение данных активности за период"""
    try:
        messages = await activity_collection.find({
            "chat_id": chat_id,
            "timestamp": {"$gte": start_date, "$lte": end_date},
            "type": {"$ne": "member"}
        }).to_list(length=None)
        
        new_members = await activity_collection.find({
            "chat_id": chat_id,
            "timestamp": {"$gte": start_date, "$lte": end_date},
            "type": "member",
            "action": "joined"
        }).to_list(length=None)
        
        left_members = await activity_collection.find({
            "chat_id": chat_id,
            "timestamp": {"$gte": start_date, "$lte": end_date},
            "type": "member",
            "action": "left"
        }).to_list(length=None)
        
        return {
            "total_messages": len(messages),
            "unique_users": len(set(msg["user_id"] for msg in messages)),
            "new_members": len(new_members),
            "left_members": len(left_members),
            "messages": messages
        }
    except Exception as e:
        logging.error(f"Error getting activity data: {e}")
        return {"total_messages": 0, "unique_users": 0, "new_members": 0, "left_members": 0, "messages": []}


async def get_top_active_users(chat_id: int, start_date: datetime.datetime, end_date: datetime.datetime, limit: int = 10):
    """Получение топ активных пользователей"""
    try:
        pipeline = [
            {
                "$match": {
                    "chat_id": chat_id,
                    "timestamp": {"$gte": start_date, "$lte": end_date},
                    "type": {"$ne": "member"}
                }
            },
            {
                "$group": {
                    "_id": "$user_id",
                    "messages_count": {"$sum": 1}
                }
            },
            {
                "$sort": {"messages_count": -1}
            },
            {
                "$limit": limit
            }
        ]
        
        users = await activity_collection.aggregate(pipeline).to_list(length=None)
        
        # Получаем общее количество сообщений для расчета процентов
        total_messages = await activity_collection.count_documents({
            "chat_id": chat_id,
            "timestamp": {"$gte": start_date, "$lte": end_date},
            "type": {"$ne": "member"}
        })
        
        result = []
        for user in users:
            user_id = user["_id"]
            messages_count = user["messages_count"]
            percentage = (messages_count / total_messages * 100) if total_messages > 0 else 0
            
            result.append({
                "user_id": user_id,
                "messages_count": messages_count,
                "percentage": percentage
            })
        
        return result
    except Exception as e:
        logging.error(f"Error getting top active users: {e}")
        return []


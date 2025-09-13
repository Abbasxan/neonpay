import asyncio
import logging
from datetime import datetime, timedelta
from collections import defaultdict
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.enums import ChatMemberStatus
from config import app, db
from language import get_group_language, load_language
from modules.mute_utils import mute_user

logger = logging.getLogger(__name__)

# Хранилище для отслеживания сообщений пользователей
user_messages = defaultdict(list)

async def log_deleted_message(chat_id, user_id, message_type="flood", reason="Flood mesajları"):
    """Записывает удаленное сообщение в базу данных для статистики"""
    try:
        await db.deleted_messages.insert_one({
            "chat_id": chat_id,
            "user_id": user_id,
            "type": message_type,
            "reason": reason,
            "timestamp": datetime.now()
        })
    except Exception as e:
        logger.error(f"[ANTIFLOOD] Failed to log deleted message: {e}")

async def add_warning(chat_id, user_id, reason="Flood mesajları"):
    """Добавляет предупреждение пользователю"""
    try:
        await db.warnings.insert_one({
            "chat_id": chat_id,
            "user_id": user_id,
            "reason": reason,
            "timestamp": datetime.now()
        })
    except Exception as e:
        logger.error(f"[ANTIFLOOD] Failed to add warning: {e}")

@app.on_message(filters.group & ~filters.command(["antiflood"]), group=3)
async def antiflood_handler(client: Client, message: Message):
    """Обработчик антифлуда"""
    if not message.from_user:
        return
    
    chat_id = message.chat.id
    user_id = message.from_user.id
    
    # Получаем настройки антифлуда для группы
    group_data = await db.groups.find_one({"_id": chat_id}) or {}
    if not group_data.get("antiflood_enabled", False):
        return
    
    # Настройки по умолчанию
    max_messages = group_data.get("antiflood_limit", 5)  # максимум сообщений
    time_window = group_data.get("antiflood_time", 10)   # за время в секундах
    action = group_data.get("antiflood_action", "delete") # действие: delete, warn, mute
    
    # Проверяем, является ли пользователь администратором
    try:
        member = await app.get_chat_member(chat_id, user_id)
        is_admin = member.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]
        if is_admin:
            return  # Не применяем антифлуд к администраторам
    except Exception:
        pass
    
    # Добавляем сообщение в список пользователя
    now = datetime.now()
    user_key = f"{chat_id}_{user_id}"
    user_messages[user_key].append(now)
    
    # Удаляем старые сообщения (вне временного окна)
    cutoff_time = now - timedelta(seconds=time_window)
    user_messages[user_key] = [msg_time for msg_time in user_messages[user_key] if msg_time > cutoff_time]
    
    # Проверяем превышение лимита
    if len(user_messages[user_key]) > max_messages:
        username = message.from_user.username or str(message.from_user.id)
        logger.info(f"[ANTIFLOOD] User {username} exceeded limit in {chat_id}: {len(user_messages[user_key])}/{max_messages}")
        
        # Выполняем действие
        if action == "delete":
            try:
                await message.delete()
                await log_deleted_message(chat_id, user_id, "flood", f"Flood: {len(user_messages[user_key])}/{max_messages}")
                logger.info(f"[ANTIFLOOD] Deleted flood message from {username} in {chat_id}")
            except Exception as e:
                logger.error(f"[ANTIFLOOD] Failed to delete message: {e}")
        
        elif action == "warn":
            try:
                await add_warning(chat_id, user_id, f"Flood mesajları: {len(user_messages[user_key])}/{max_messages}")
                
                lang_code = await get_group_language(chat_id)
                lang = load_language(lang_code)
                
                notice = await client.send_message(
                    chat_id,
                    f"<blockquote>⚠️ {lang.get('flood_warning', 'Flood xəbərdarlığı')} @{username}</blockquote>"
                )
                logger.info(f"[ANTIFLOOD] Warned user {username} for flood in {chat_id}")
            except Exception as e:
                logger.error(f"[ANTIFLOOD] Failed to warn user: {e}")
        
        elif action == "mute":
            try:
                lang_code = await get_group_language(chat_id)
                mute_duration = 5  # 5 минут
                
                success = await mute_user(chat_id, user_id, mute_duration, lang_code)
                
                if success:
                    await add_warning(chat_id, user_id, f"Flood üçün susturuldu: {len(user_messages[user_key])}/{max_messages}")
                    
                    lang = load_language(lang_code)
                    
                    notice = await client.send_message(
                        chat_id,
                        f"<blockquote>🔇 {lang.get('flood_muted', 'Flood üçün susturuldu')} @{username} ({mute_duration} dəqiqə)</blockquote>"
                    )
                    logger.info(f"[ANTIFLOOD] Muted user {username} for flood in {chat_id} for {mute_duration} minutes")
                else:
                    logger.error(f"[ANTIFLOOD] Failed to mute user {username} using mute_utils")
            except Exception as e:
                logger.error(f"[ANTIFLOOD] Failed to mute user: {e}")
        
        # Очищаем счетчик после действия
        user_messages[user_key] = []

@app.on_message(filters.command("antiflood") & filters.group, group=-1)
async def antiflood_command(client: Client, message: Message):
    """Команда для настройки антифлуда"""
    if not message.from_user:
        return
    
    chat_id = message.chat.id
    user_id = message.from_user.id
    
    # Проверяем права администратора
    try:
        member = await app.get_chat_member(chat_id, user_id)
        is_admin = member.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]
    except Exception:
        lang_code = await get_group_language(chat_id)
        lang = load_language(lang_code)
        return await message.reply(f"<blockquote>{lang.get('antiflood_admin_check_failed')}</blockquote>")
    
    if not is_admin:
        lang_code = await get_group_language(chat_id)
        lang = load_language(lang_code)
        return await message.reply(f"<blockquote>{lang.get('antiflood_admin_only')}</blockquote>")
    
    lang_code = await get_group_language(chat_id)
    lang = load_language(lang_code)
    
    args = message.text.split()[1:]
    
    if not args:
        # Показываем текущие настройки
        group_data = await db.groups.find_one({"_id": chat_id}) or {}
        is_enabled = group_data.get("antiflood_enabled", False)
        limit = group_data.get("antiflood_limit", 5)
        time_window = group_data.get("antiflood_time", 10)
        action = group_data.get("antiflood_action", "delete")
        
        status_text = lang.get('antiflood_status_active') if is_enabled else lang.get('antiflood_status_inactive')
        action_text = {
            "delete": lang.get('antiflood_action_names'),
            "warn": lang.get('antiflood_action_warn'),
            "mute": lang.get('antiflood_action_mute')
        }.get(action, action)
        
        status_msg = lang.get('antiflood_status', '🌊 AntiFlood Statusu: {status}\n📊 Limit: {limit} mesaj / {time_window} saniyə\n⚡ Hərəkət: {action}').format(status=status_text, limit=limit, time_window=time_window, action=action_text)
        usage_msg = lang.get('antiflood_usage', 'İstifadə:\n/antiflood on|off - Aktiv/deaktiv et\n/antiflood limit 5 10 - 5 mesaj / 10 saniyə\n/antiflood action delete|warn|mute - Hərəkət növü')
        
        return await message.reply(
            f"<blockquote>{status_msg}\n\n{usage_msg}</blockquote>"
        )
    
    if args[0].lower() in ["on", "off"]:
        enabled = args[0].lower() == "on"
        await db.groups.update_one(
            {"_id": chat_id}, 
            {"$set": {"antiflood_enabled": enabled}}, 
            upsert=True
        )
        
        status_text = lang.get('antiflood_enabled') if enabled else lang.get('antiflood_disabled')
        return await message.reply(f"<blockquote>✅ {status_text}</blockquote>")
    
    elif args[0].lower() == "limit" and len(args) >= 3:
        try:
            limit = int(args[1])
            time_window = int(args[2])
            
            if limit < 1 or limit > 50:
                return await message.reply(f"<blockquote>{lang.get('antiflood_limit_range')}</blockquote>")
            
            if time_window < 1 or time_window > 300:
                return await message.reply(f"<blockquote>{lang.get('antiflood_time_range')}</blockquote>")
            
            await db.groups.update_one(
                {"_id": chat_id}, 
                {"$set": {
                    "antiflood_limit": limit,
                    "antiflood_time": time_window
                }}, 
                upsert=True
            )
            
            return await message.reply(
                f"<blockquote>{lang.get('antiflood_set_success', '✅ AntiFlood limiti yeniləndi: {limit} mesaj / {time_window} saniyə').format(limit=limit, time=time_window, action='')}</blockquote>"
            )
        except ValueError:
            return await message.reply(f"<blockquote>{lang.get('antiflood_invalid_numbers')}</blockquote>")
    
    elif args[0].lower() == "action" and len(args) >= 2:
        action = args[1].lower()
        if action not in ["delete", "warn", "mute"]:
            return await message.reply(f"<blockquote>{lang.get('antiflood_invalid_action')}</blockquote>")
        
        await db.groups.update_one(
            {"_id": chat_id}, 
            {"$set": {"antiflood_action": action}}, 
            upsert=True
        )
        
        action_text = {
            "delete": lang.get('antiflood_action_names'),
            "warn": lang.get('antiflood_action_warn'),
            "mute": lang.get('antiflood_action_mute')
        }.get(action)
        return await message.reply(f"<blockquote>✅ AntiFlood hərəkəti yeniləndi: {action_text}</blockquote>")
    
    else:
        return await message.reply(
            f"<blockquote>{lang.get('antiflood_set_fail')}</blockquote>"
        )
          

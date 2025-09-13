# modules/qrup_qeydiyyati.py

import logging
from pyrogram import Client
from pyrogram.enums import ChatMemberStatus
from pyrogram.types import ChatMemberUpdated
from config import app, db, LOG_ID
from language import get_group_language, load_language
import time

# Настройка логгера
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# Подписчики на обновление участников чата
chat_member_update_subscribers = []

def register_chat_member_update_subscriber(func):
    chat_member_update_subscribers.append(func)
    return func  # Позволяет использовать как декоратор

# Функция для конвертации enum в строку
def enum_to_str(enum_value):
    if enum_value is None:
        return None
    return str(enum_value).split('.')[-1]

@app.on_chat_member_updated()
async def handle_bot_status_change(client: Client, event: ChatMemberUpdated):
    chat = event.chat
    if event.new_chat_member and event.new_chat_member.user.is_self:
        new_status = event.new_chat_member.status
        old_status = event.old_chat_member.status if event.old_chat_member else None
        logger.info("🌀 Обработчик on_chat_member_updated сработал.")
        logger.info("🤖 Изменения касаются самого бота.")
        logger.info(f"🔁 Статус изменён: {old_status} → {new_status}")
        logger.info(f"👥 Чат: {chat.id} — {chat.title}")
        
        existing_group = await db.groups_collection.find_one({"chat_id": chat.id})
        
        if old_status in (ChatMemberStatus.LEFT, ChatMemberStatus.BANNED, None) and new_status in (
            ChatMemberStatus.MEMBER, ChatMemberStatus.ADMINISTRATOR
        ):
            logger.info("✅ Бот добавлен в группу. Сохраняем информацию.")
            await db.groups_collection.update_one(
                {"chat_id": chat.id},
                {
                    "$set": {
                        "chat_id": chat.id,
                        "title": chat.title,
                        "username": chat.username,
                        "added": True,
                        "removed": False,
                        "added_date": time.time(),
                        "member_status": enum_to_str(new_status)
                    }
                },
                upsert=True
            )
            updated_group = await db.groups_collection.find_one({"chat_id": chat.id})
            logger.info(f"✅ Проверка обновления: added={updated_group.get('added')}, removed={updated_group.get('removed')}")
            
            # Get language for the group
            lang_code = await get_group_language(chat.id)
            lang = load_language(lang_code)
            
            text = lang.get("bot_added_greeting")
            await client.send_message(chat.id, text)
            
            log_text = lang.get("bot_added_log").format(
                chat_id=chat.id,
                chat_title=chat.title,
                chat_username=chat.username or 'yoxdur',
                member_status=enum_to_str(new_status),
                date=time.strftime('%Y-%m-%d %H:%M:%S'),
                added_by=f"{event.from_user.first_name} (<code>{event.from_user.id}</code>)" if event.from_user else "Naməlum"
            )
            await client.send_message(LOG_ID, f"<blockquote>\n{log_text}\n</blockquote>")
            
            if not existing_group:
                logger.info("🆕 Новая группа добавлена в базу данных")
                
        elif new_status == ChatMemberStatus.BANNED or new_status == ChatMemberStatus.LEFT:
            logger.info("❌ Бот был удалён из группы. Отмечаем как удаленную.")
            result = await db.groups_collection.update_one(
                {"chat_id": chat.id},
                {
                    "$set": {
                        "chat_id": chat.id,
                        "title": chat.title,
                        "username": chat.username,
                        "removed": True,
                        "added": False,
                        "removed_date": time.time(),
                        "member_status": enum_to_str(new_status)
                    }
                },
                upsert=True
            )
            logger.info(f"✅ Результат обновления: matched={result.matched_count}, modified={result.modified_count}")
            updated_group = await db.groups_collection.find_one({"chat_id": chat.id})
            if updated_group:
                logger.info(f"✅ Проверка обновления: added={updated_group.get('added')}, removed={updated_group.get('removed')}")
            else:
                logger.warning("⚠️ Группа не найдена в базе данных после обновления")
            
            # Get language for the group
            lang_code = await get_group_language(chat.id)
            lang = load_language(lang_code)
            
            status_text = lang.get("status_banned") if new_status == ChatMemberStatus.BANNED else lang.get("status_left")
            log_text = lang.get("bot_removed_log").format(
                status_text=status_text,
                chat_id=chat.id,
                chat_title=chat.title,
                date=time.strftime('%Y-%m-%d %H:%M:%S'),
                removed_by=f"{event.from_user.first_name} (<code>{event.from_user.id}</code>)" if event.from_user else "Naməlum"
            )
            await client.send_message(LOG_ID, f"<blockquote>\n{log_text}\n</blockquote>")
            
        elif old_status == ChatMemberStatus.ADMINISTRATOR and new_status == ChatMemberStatus.MEMBER:
            logger.warning("⚠️ Бота понизили до участника!")
            await db.groups_collection.update_one(
                {"chat_id": chat.id},
                {
                    "$set": {
                        "member_status": enum_to_str(new_status),
                        "status_changed_date": time.time()
                    }
                },
                upsert=True
            )
            # Get language for the group
            lang_code = await get_group_language(chat.id)
            lang = load_language(lang_code)
            
            await client.send_message(chat.id, lang.get("bot_admin_removed"))
            log_text = lang.get("bot_admin_removed_log").format(
                chat_id=chat.id,
                chat_title=chat.title,
                chat_username=chat.username or 'yoxdur',
                date=time.strftime('%Y-%m-%d %H:%M:%S'),
                changed_by=f"{event.from_user.first_name} (<code>{event.from_user.id}</code>)" if event.from_user else "Naməlum"
            )
            await client.send_message(LOG_ID, f"<blockquote>\n{log_text}\n</blockquote>")
            
        elif old_status == ChatMemberStatus.ADMINISTRATOR and new_status == ChatMemberStatus.ADMINISTRATOR:
            old_rights = event.old_chat_member.privileges if event.old_chat_member else None
            new_rights = event.new_chat_member.privileges
            await db.groups_collection.update_one(
                {"chat_id": chat.id},
                {
                    "$set": {
                        "member_status": enum_to_str(new_status),
                        "can_delete_messages": new_rights.can_delete_messages,
                        "can_invite_users": new_rights.can_invite_users if new_rights else False,
                        "status_changed_date": time.time()
                    }
                },
                upsert=True
            )
            
            # Check if bot got invite_users permission and antireklam is enabled
            if (old_rights and not old_rights.can_invite_users and 
                new_rights and new_rights.can_invite_users):
                logger.info(f"[ANTIREKLAM] Bot got invite_users permission in chat {chat.id}, checking if userbot needs to be added")
                try:
                    # Check if antireklam is enabled for this group
                    group_data = await db.groups.find_one({"_id": chat.id}) or {}
                    if group_data.get("antireklam_enabled", True):
                        logger.info(f"[ANTIREKLAM] Antireklam is enabled, attempting to add userbot to {chat.id}")
                        # Import here to avoid circular imports
                        from modules.antireklam import invite_userbot_to_group
                        await invite_userbot_to_group(chat.id)
                except Exception as e:
                    logger.error(f"[ANTIREKLAM] Failed to auto-add userbot after getting permissions: {e}")
            if old_rights and old_rights.can_delete_messages and not new_rights.can_delete_messages:
                # Get language for the group
                lang_code = await get_group_language(chat.id)
                lang = load_language(lang_code)
                
                await client.send_message(chat.id, lang.get("bot_delete_rights_removed"))
                log_text = lang.get("bot_delete_rights_removed_log").format(
                    chat_id=chat.id,
                    chat_title=chat.title,
                    chat_username=chat.username or 'yoxdur',
                    date=time.strftime('%Y-%m-%d %H:%M:%S'),
                    changed_by=f"{event.from_user.first_name} (<code>{event.from_user.id}</code>)" if event.from_user else "Naməlum"
                )
                await client.send_message(LOG_ID, f"<blockquote>\n{log_text}\n</blockquote>")
            elif not old_rights or (not old_rights.can_delete_messages and new_rights.can_delete_messages):
                # Get language for the group
                lang_code = await get_group_language(chat.id)
                lang = load_language(lang_code)
                
                log_text = lang.get("bot_delete_rights_gained_log").format(
                    chat_id=chat.id,
                    chat_title=chat.title,
                    chat_username=chat.username or 'yoxdur',
                    date=time.strftime('%Y-%m-%d %H:%M:%S'),
                    changed_by=f"{event.from_user.first_name} (<code>{event.from_user.id}</code>)" if event.from_user else "Naməlum"
                )
                await client.send_message(LOG_ID, f"<blockquote>\n{log_text}\n</blockquote>")
                
        elif old_status == ChatMemberStatus.MEMBER and new_status == ChatMemberStatus.ADMINISTRATOR:
            new_rights = event.new_chat_member.privileges
            await db.groups_collection.update_one(
                {"chat_id": chat.id},
                {
                    "$set": {
                        "member_status": enum_to_str(new_status),
                        "can_delete_messages": new_rights.can_delete_messages,
                        "can_invite_users": new_rights.can_invite_users if new_rights else False,
                        "status_changed_date": time.time()
                    }
                },
                upsert=True
            )
            
            # Check if bot got admin with invite_users permission and antireklam is enabled
            if new_rights and new_rights.can_invite_users:
                logger.info(f"[ANTIREKLAM] Bot became admin with invite_users permission in chat {chat.id}, checking if userbot needs to be added")
                try:
                    # Check if antireklam is enabled for this group
                    group_data = await db.groups.find_one({"_id": chat.id}) or {}
                    if group_data.get("antireklam_enabled", True):
                        logger.info(f"[ANTIREKLAM] Antireklam is enabled, attempting to add userbot to {chat.id}")
                        # Import here to avoid circular imports
                        from modules.antireklam import invite_userbot_to_group
                        await invite_userbot_to_group(chat.id)
                except Exception as e:
                    logger.error(f"[ANTIREKLAM] Failed to auto-add userbot after becoming admin: {e}")
            # Get language for the group
            lang_code = await get_group_language(chat.id)
            lang = load_language(lang_code)
            
            log_text = lang.get("bot_admin_gained_log").format(
                chat_id=chat.id,
                chat_title=chat.title,
                chat_username=chat.username or 'yoxdur',
                delete_rights='✅' if new_rights.can_delete_messages else '❌',
                date=time.strftime('%Y-%m-%d %H:%M:%S'),
                changed_by=f"{event.from_user.first_name} (<code>{event.from_user.id}</code>)" if event.from_user else "Naməlum"
            )
            await client.send_message(LOG_ID, f"<blockquote>\n{log_text}\n</blockquote>")
            if not new_rights.can_delete_messages:
                await client.send_message(chat.id, lang.get("bot_admin_gained_no_delete"))
            else:
                await client.send_message(chat.id, lang.get("bot_admin_gained_with_delete"))
    else:
        logger.warning("⚠️ Нет данных о новом участнике или изменение не касается бота. Пропуск.")
    
    # Вызов всех подписанных функций
    for subscriber in chat_member_update_subscribers:
        try:
            await subscriber(client, event)
        except Exception as e:
            logger.error(f"[SUBSCRIBER ERROR] {subscriber.__name__}: {e}")

            

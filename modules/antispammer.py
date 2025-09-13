# modules/antispammer
import logging
import asyncio
import re
from pyrogram.enums import ChatMemberStatus
from pyrogram.types import ChatPermissions, ChatMemberUpdated, Message
from pyrogram import filters
from config import app, db
from language import get_language_for_message, get_text, get_group_language
from modules.qrup_qeydiyyati import register_chat_member_update_subscriber

logger = logging.getLogger(__name__)

# Получение слов из MongoDB blacklist_keywords
async def get_blacklisted_words():
    results = await db.blacklist_keywords.find().to_list(length=100)
    return {item["word"].lower() for item in results if "word" in item}

# === 1. Обработка входа пользователя с подозрительным именем ===
@register_chat_member_update_subscriber
async def handle_join_with_name(client, event: ChatMemberUpdated):
    try:
        user = getattr(event.new_chat_member, "user", None)
        if not user or user.is_bot:
            return

        old_status = getattr(event.old_chat_member, "status", None)
        new_status = event.new_chat_member.status
        if old_status not in [None, ChatMemberStatus.LEFT] or new_status != ChatMemberStatus.MEMBER:
            return

        chat_id = event.chat.id  # Это просто число, и его нужно использовать как есть

        # Проверка включена ли защита
        settings = await db.group_settings.find_one({"chat_id": chat_id}) or {}
        if not settings.get("antijoin_enabled", True):
            return

        blacklisted = await get_blacklisted_words()
        full_name = f"{user.first_name or ''} {user.last_name or ''}".strip().lower()

        if any(word in full_name for word in blacklisted):
            # Дать мут навсегда
            await client.restrict_chat_member(
                chat_id,
                user.id,
                permissions=ChatPermissions(can_send_messages=False)
            )
            logger.info(f"[Mute] User {user.id} restricted (muted) in chat {chat_id}")

            # Исправлено: правильная функция для получения языка группы
            lang_code = await get_group_language(chat_id)
            texts = await get_text(chat_id, is_private=False, lang_code=lang_code)

            mention = f"<a href='tg://user?id={user.id}'>{user.first_name}</a>"
            alert = texts.get("antijoin_alert", "{mention} NEON tərəfindən susduruldu.").format(mention=mention)

            await app.send_message(chat_id, alert)

    except Exception as e:
        logger.error(f"[handle_join_with_name] Error: {e}")
            


# === 2. Удаление сообщений от ботов с подозрительными словами ===
@app.on_message(filters.bot & filters.group, group=4)
async def delete_bot_spam_messages(client, message: Message):
    try:
        text = (message.text or message.caption or "").lower()
        
        has_links = bool(re.search(r"(https?://|t\.me/|www\.|@\w+|\.com|\.ru|\.org|\.net)", text, re.IGNORECASE))
        
        blacklisted = await get_blacklisted_words()
        has_blacklisted_words = any(word in text for word in blacklisted)
        
        # Удаляем если есть либо ссылки, либо запрещенные слова
        if has_links or has_blacklisted_words:
            await message.delete()
            
            reason = "links" if has_links else "blacklisted_words"
            lang_code = await get_group_language(message.chat.id)
            texts = await get_text(message.chat.id, is_private=False, lang_code=lang_code)
            notice = await message.reply(f"<blockquote>{texts.get('bot_spam_deleted', '🚫 Reklam tərkibli mesaj silindi ({reason}).').format(reason=reason)}</blockquote>")
            await asyncio.sleep(4)
            await notice.delete()
            logger.info(f"[AutoDelete] Deleted bot message from {message.from_user.id} in {message.chat.id} (reason: {reason})")
    except Exception as e:
        logger.error(f"[delete_bot_spam_messages] Error: {e}")


# === 3. Команда /antijoin on|off ===
@app.on_message(filters.command("antijoin") & filters.group, group=-1)
async def toggle_antijoin(client, message: Message):
    if not message.from_user or not message.from_user.id:
        return

    member = await client.get_chat_member(message.chat.id, message.from_user.id)
    if member.status not in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
        lang_code = await get_group_language(message.chat.id)
        texts = await get_text(message.chat.id, is_private=False, lang_code=lang_code)
        await message.reply(f"<blockquote>{texts.get('antijoin_admin_only')}</blockquote>")
        return

    args = message.text.split(maxsplit=1)
    if len(args) < 2 or args[1] not in ("on", "off"):
        lang_code = await get_group_language(message.chat.id)
        texts = await get_text(message.chat.id, is_private=False, lang_code=lang_code)
        await message.reply(f"<blockquote>{texts.get('antijoin_usage')}</blockquote>")
        return

    enabled = args[1] == "on"

    await db.group_settings.update_one(
        {"chat_id": message.chat.id},
        {"$set": {"antijoin_enabled": enabled}},
        upsert=True
    )

    lang_code = await get_group_language(message.chat.id)
    texts = await get_text(message.chat.id, is_private=False, lang_code=lang_code)
    status = texts.get('antijoin_enabled') if enabled else texts.get('antijoin_disabled')
    await message.reply(f"<blockquote>{texts.get('antijoin_status', '🛡️ Anti-Join müdafiəsi: {status}').format(status=status)}</blockquote>")
    

# === 4. /blacklist_add ===
@app.on_message(filters.command("blacklist_add") & filters.group, group=-1)
async def add_blacklist_word(client, message: Message):
    if not message.from_user or not message.from_user.id:
        return

    member = await client.get_chat_member(message.chat.id, message.from_user.id)
    if member.status not in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
        lang_code = await get_group_language(message.chat.id)
        texts = await get_text(message.chat.id, is_private=False, lang_code=lang_code)
        await message.reply(f"<blockquote>{texts.get('blacklist_add_admin_only')}</blockquote>")
        return

    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        lang_code = await get_group_language(message.chat.id)
        texts = await get_text(message.chat.id, is_private=False, lang_code=lang_code)
        await message.reply(f"<blockquote>{texts.get('blacklist_add_usage')}</blockquote>")
        return

    word = args[1].strip().lower()
    if not word:
        lang_code = await get_group_language(message.chat.id)
        texts = await get_text(message.chat.id, is_private=False, lang_code=lang_code)
        return await message.reply(f"<blockquote>{texts.get('blacklist_add_empty')}</blockquote>")

    existing = await db.blacklist_keywords.find_one({"word": word})
    if existing:
        lang_code = await get_group_language(message.chat.id)
        texts = await get_text(message.chat.id, is_private=False, lang_code=lang_code)
        return await message.reply(f"<blockquote>{texts.get('blacklist_add_exists')}</blockquote>")

    await db.blacklist_keywords.insert_one({"word": word})
    lang_code = await get_group_language(message.chat.id)
    texts = await get_text(message.chat.id, is_private=False, lang_code=lang_code)
    await message.reply(f"<blockquote>{texts.get('blacklist_add_success', '✅ <b>{word}</b> qara siyahıya əlavə olundu.').format(word=word)}</blockquote>")
    


# === 5. /blacklist_del ===
@app.on_message(filters.command("blacklist_del") & filters.group, group=-1)
async def delete_blacklist_word(client, message: Message):
    if not message.from_user or not message.from_user.id:
        return

    member = await client.get_chat_member(message.chat.id, message.from_user.id)
    if member.status not in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
        lang_code = await get_group_language(message.chat.id)
        texts = await get_text(message.chat.id, is_private=False, lang_code=lang_code)
        await message.reply(f"<blockquote>{texts.get('blacklist_del_admin_only')}</blockquote>")
        return

    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        lang_code = await get_group_language(message.chat.id)
        texts = await get_text(message.chat.id, is_private=False, lang_code=lang_code)
        await message.reply(f"<blockquote>{texts.get('blacklist_del_usage')}</blockquote>")
        return

    word = args[1].strip().lower()
    result = await db.blacklist_keywords.delete_one({"word": word})
    lang_code = await get_group_language(message.chat.id)
    texts = await get_text(message.chat.id, is_private=False, lang_code=lang_code)
    if result.deleted_count:
        await message.reply(f"<blockquote>{texts.get('blacklist_del_success', '🗑️ <b>{word}</b> qara siyahıdan silindi.').format(word=word)}</blockquote>")
    else:
        await message.reply(f"<blockquote>{texts.get('blacklist_del_not_found')}</blockquote>")
        

# === 6. spamera aid xoş gəldin mesajlarım siıir ===
@app.on_message(filters.group & filters.bot, group=10)
async def auto_delete_bot_welcome(client, message: Message):
    try:
        if not message.from_user or not message.from_user.is_bot:
            return

        text = (message.text or message.caption or "").lower()
        if not text:
            logger.info("[AutoDeleteBotGreeting] Empty message, skipping.")
            return

        blacklisted = await get_blacklisted_words()
        logger.info(f"[Debug] Text to check: {text}")
        
        if any(word in text for word in blacklisted):
            await asyncio.sleep(3.5)
            await message.delete()
            logger.info(f"[AutoDeleteBotGreeting] Deleted bot message from {message.from_user.id} in {message.chat.id}")
    except Exception as e:
        logger.error(f"[auto_delete_bot_welcome] Error: {e}")
                

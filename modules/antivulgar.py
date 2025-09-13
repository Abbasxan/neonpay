import logging
from pyrogram import filters
from pyrogram.types import Message
from config import app, db
from language import load_vulgar_words, get_language_for_message, get_text
from datetime import datetime
from modules.mute_utils import mute_user
from pyrogram.enums import ChatMemberStatus
import re

# Логгер для этого модуля
logger = logging.getLogger(__name__)

_vulgar_tries_cache = {}

def normalize_text(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^\w\s]", "", text)
    text = re.sub(r"(.)\1{2,}", r"\1\1", text)
    return text

def build_trie(bad_words: set) -> dict:
    trie = {}
    for word in bad_words:
        current = trie
        for char in word:
            current = current.setdefault(char, {})
        current["*"] = True
    return trie

def word_in_trie(word: str, trie: dict) -> bool:
    word = word.lower()
    current = trie
    for char in word:
        if char not in current:
            return False
        current = current[char]
    return "*" in current

def has_bad_word(text: str, trie: dict) -> bool:
    words = re.findall(r"\b\w+\b", normalize_text(text))
    for word in words:
        if word_in_trie(word, trie):
            return True
    return False

async def get_trie_cached(lang_code: str) -> dict:
    if lang_code in _vulgar_tries_cache:
        logger.debug(f"Trie cache hit for language '{lang_code}'")
        return _vulgar_tries_cache[lang_code]

    bad_words = load_vulgar_words(lang_code)
    trie = build_trie(bad_words)
    _vulgar_tries_cache[lang_code] = trie
    logger.info(f"Trie built and cached for language '{lang_code}' with {len(bad_words)} bad words")
    return trie

@app.on_message(filters.command("noarqo") & filters.group, group=0)
async def set_antivulgar_settings(client, message: Message):
    logger.info(f"Received /noarqo command from user {message.from_user.id} in chat {message.chat.id}")
    if not message.from_user:
        logger.warning("Message has no from_user, ignoring")
        return

    lang_code = await get_language_for_message(message)
    texts = await get_text(message.chat.id, is_private=False, lang_code=lang_code)

    member = await app.get_chat_member(message.chat.id, message.from_user.id)
    if member.status not in [ChatMemberStatus.OWNER, ChatMemberStatus.ADMINISTRATOR]:
        logger.warning(f"User {message.from_user.id} is not admin in chat {message.chat.id}")
        return await message.reply(f"<blockquote>{texts.get('admin_only', 'Bu əmri yalnız adminlər istifadə edə bilər.')}</blockquote>")

    args = message.text.split()[1:]
    group_data = await db.groups.find_one({"_id": message.chat.id}) or {}
    warn_limit = group_data.get("warn_limit_vulgar", 3)
    mute_duration = group_data.get("mute_duration_vulgar", 1440)
    is_enabled = group_data.get("antivulgar_enabled", True)
    mute_enabled = group_data.get("antivulgar_mute_enabled", True)

    if not args or args[0].lower() == "status":
        status_text = texts.get("antivulgar_status",
            "🛡 <b>QƏDDAR Rejimi</b>:\nStatus: <b>{status}</b>\nLimit: <b>{limit}</b>\nMute: <b>{mute}</b> dəq\nMute rejimi: <b>{mute_mode}</b>").format(
                status=texts.get("antivulgar_status_active") if is_enabled else texts.get("antivulgar_status_inactive"),
                limit=warn_limit,
                mute=mute_duration,
                mute_mode=texts.get("antivulgar_status_active") if mute_enabled else texts.get("antivulgar_status_inactive")
            )
        logger.info(f"Status requested in chat {message.chat.id}")
        return await message.reply(f"<blockquote>{status_text}</blockquote>")

    if args[0].lower() in ["on", "off"]:
        is_enabled = args[0].lower() == "on"
        await db.groups.update_one(
            {"_id": message.chat.id},
            {"$set": {"antivulgar_enabled": is_enabled}},
            upsert=True
        )
        msg = texts.get("antivulgar_enabled" if is_enabled else "antivulgar_disabled",
                        "Antivulqar filtri aktiv edildi." if is_enabled else "Antivulqar filtri deaktiv edildi.")
        logger.info(f"Antivulgar filter {'enabled' if is_enabled else 'disabled'} in chat {message.chat.id}")
        return await message.reply(f"<blockquote>✅ {msg}</blockquote>")

    if args[0].lower() in ["muteon", "muteoff"]:
        mute_enabled = args[0].lower() == "muteon"
        await db.groups.update_one(
            {"_id": message.chat.id},
            {"$set": {"antivulgar_mute_enabled": mute_enabled}},
            upsert=True
        )
        msg = texts.get("antivulgar_mute_enabled") if mute_enabled else texts.get("antivulgar_mute_disabled")
        logger.info(f"Antivulgar mute mode {'enabled' if mute_enabled else 'disabled'} in chat {message.chat.id}")
        return await message.reply(f"<blockquote>✅ {msg}</blockquote>")

    try:
        count, duration = map(int, args)
        await db.groups.update_one(
            {"_id": message.chat.id},
            {"$set": {
                "warn_limit_vulgar": count,
                "mute_duration_vulgar": duration
            }},
            upsert=True
        )
        msg = texts.get("antivulgar_set_success", "✅ Söhüş ayarları yeniləndi.\nLimit: {count}\nMute: {duration} dəq").format(
            count=count, duration=duration
        )
        logger.info(f"Antivulgar settings updated in chat {message.chat.id}: limit={count}, mute_duration={duration}")
        await message.reply(f"<blockquote>{msg}</blockquote>")
    except Exception as e:
        logger.error(f"Failed to update antivulgar settings in chat {message.chat.id}: {e}")
        await message.reply(f"<blockquote>{texts.get('antivulgar_set_fail', 'İstifadə: /noarqo [on|off|status|muteon|muteoff] və ya /noarqo [limit] [dəq]')}</blockquote>")


@app.on_message(
    filters.group 
    & filters.text 
    & ~filters.via_bot 
    & ~filters.regex(r"^/"),
    group=2
)
async def noarqo_filter(client, message: Message):
    logger.debug(f"noarqo_filter triggered for message {message.id} in chat {message.chat.id}")
    if not message.from_user or message.from_user.is_bot:
        logger.debug("Message ignored because from_user is None or a bot")
        return

    lang_code = await get_language_for_message(message)
    texts = await get_text(message.chat.id, is_private=False, lang_code=lang_code)

    group_data = await db.groups.find_one({"_id": message.chat.id}) or {}
    if not group_data.get("antivulgar_enabled", True):
        logger.debug(f"Antivulgar filter disabled in chat {message.chat.id}")
        return

    trie = await get_trie_cached(lang_code)

    if not has_bad_word(message.text, trie):
        logger.debug(f"No vulgar words detected in message {message.id}")
        return

    try:
        await message.delete()
        logger.info(f"Deleted vulgar message {message.id} from user {message.from_user.id} in chat {message.chat.id}")
    except Exception as e:
        logger.error(f"Failed to delete message {message.id} in chat {message.chat.id}: {e}")
        return await message.reply(
            f"<blockquote>{texts.get('no_delete_permission', 'Mesaj silmək üçün icazəm yoxdur.')}</blockquote>"
        )

    try:
        await db.deleted_messages.insert_one({
            "chat_id": message.chat.id,
            "user_id": message.from_user.id,
            "message_id": message.id,
            "type": "vulgar",
            "reason": "Vulgar language detected",
            "timestamp": datetime.utcnow(),
            "deleted_by": "bot"
        })
        logger.info(f"[ANTIVULGAR] Logged deleted vulgar message for user {message.from_user.id} in {message.chat.id}")
    except Exception as e:
        logger.error(f"[ANTIVULGAR] Failed to log deleted message: {e}")

    user = message.from_user
    user_id = user.id
    user_mention = user.mention
    now = datetime.utcnow()

    await db.bad_word_stats.update_one(
        {"chat_id": message.chat.id, "user_id": user_id},
        {
            "$inc": {"count": 1},
            "$set": {"last_used": now},
            "$push": {
                "history": {
                    "date": now,
                    "message_id": message.id,
                    "text": message.text[:100]
                }
            }
        },
        upsert=True
    )
    logger.info(f"Logged vulgar word usage for user {user_id} in chat {message.chat.id}")

    await db.vulgar_user_stats.update_one(
        {"_id": user_id},
        {"$inc": {"total": 1}},
        upsert=True
    )

    await db.vulgar_group_stats.update_one(
        {"_id": message.chat.id},
        {"$inc": {"total": 1}},
        upsert=True
    )

    try:
        member = await client.get_chat_member(message.chat.id, user_id)
        is_admin = member.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]
    except Exception as e:
        logger.error(f"Failed to get chat member status for user {user_id} in chat {message.chat.id}: {e}")
        is_admin = False

    try:
        await client.send_message(user_id, f"<blockquote>{texts.get('vulqar_warn_private')}</blockquote>")
        logger.info(f"Sent warning private message to user {user_id}")
    except Exception as e:
        # Check if it's a PEER_ID_INVALID error (user hasn't started conversation with bot)
        if "PEER_ID_INVALID" in str(e):
            logger.debug(f"Cannot send private warning to user {user_id}: user hasn't started conversation with bot")
        else:
            logger.warning(f"Failed to send private warning to user {user_id}: {e}")

    mute_enabled = group_data.get("antivulgar_mute_enabled", True)

    if not mute_enabled:
        logger.info(f"Mute mode disabled in chat {message.chat.id}, only deleting message")
        return await message.reply(
            f"<blockquote>{texts.get('warn_group_no_mute', 'Mesaj silindi, amma mute rejimi deaktivdir.')}</blockquote>"
        )

    if is_admin:
        logger.info(f"User {user_id} is admin, skipping mute")
        return await message.reply(
            f"<blockquote>{texts.get('admin_warning', 'Admin xəbərdarlığı')}</blockquote>"
        )

    warnings = await db.warnings.find_one({"chat_id": message.chat.id, "user_id": user_id})
    warn_count = warnings["count"] + 1 if warnings else 1

    await db.warnings.update_one(
        {"chat_id": message.chat.id, "user_id": user_id},
        {"$set": {"count": warn_count, "last": now}},
        upsert=True
    )

    warn_limit = group_data.get("warn_limit_vulgar", 3)
    mute_duration = group_data.get("mute_duration_vulgar", 1440)

    if warn_count >= warn_limit:
        muted = await mute_user(message.chat.id, user_id, duration_minutes=mute_duration)
        if muted:
            logger.info(f"User {user_id} muted in chat {message.chat.id} for {mute_duration} minutes")
            await message.reply(
                f"<blockquote>{texts.get('mute_message', '{user} istifadəçi mutelendi.').format(user=user_mention)}</blockquote>"
            )
        else:
            logger.warning(f"Failed to mute user {user_id} in chat {message.chat.id}")
            await message.reply(
                f"<blockquote>{texts.get('mute_fail', '{user} mute alınmadı. QƏDDAR xəbərdarlıq etdi.').format(user=user_mention)}</blockquote>"
            )
    else:
        logger.info(f"User {user_id} warned ({warn_count}/{warn_limit}) in chat {message.chat.id}")
        
        try:
            await db.warnings.insert_one({
                "chat_id": message.chat.id,
                "user_id": user_id,
                "reason": "Vulgar language usage",
                "timestamp": now,
                "warned_by": "antivulgar_module"
            })
            logger.info(f"[ANTIVULGAR] Logged warning for user {user_id} in {message.chat.id}")
        except Exception as e:
            logger.error(f"[ANTIVULGAR] Failed to log warning: {e}")
        
        await message.reply(
            f"<blockquote>{texts.get('warn_group_with_user', '{user}, qadağan edilmiş söz istifadə etdiniz.').format(user=user_mention)}</blockquote>"
        )

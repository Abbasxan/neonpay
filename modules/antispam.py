import re
import logging
from datetime import datetime
from collections import defaultdict
from pyrogram import Client, filters
from pyrogram.enums import ChatMemberStatus
from pyrogram.types import Message
from config import app, db
from language import load_language, get_group_language
from modules.mute_utils import mute_user
from modules.qrup_qeydiyyati import register_chat_member_update_subscriber

logger = logging.getLogger(__name__)
user_links_count = defaultdict(lambda: defaultdict(int))


def format_duration(duration_minutes: int, lang: dict) -> str:
    if duration_minutes >= 1440:
        days = duration_minutes // 1440
        return f"{days} {lang.get('day', 'günlük')}"
    elif duration_minutes >= 60:
        hours = duration_minutes // 60
        return f"{hours} {lang.get('hour', 'saatlıq')}"
    return f"{duration_minutes} {lang.get('minute', 'dəqiqəlik')}"


@app.on_message(filters.group & filters.text & ~filters.via_bot, group=1)
async def delete_links(client: Client, message: Message):
    user = message.from_user
    if not user or user.is_bot:
        return

    chat_id = message.chat.id
    user_id = user.id
    text = message.text or ""

    if not re.search(r"(https?://|t\.me/|www\.)", text):
        return

    lang_code = await get_group_language(chat_id)
    lang = load_language(lang_code)

    group_data = await db.groups.find_one({"_id": chat_id}) or {}
    if not group_data.get("antispam_enabled", True):
        return

    try:
        member = await client.get_chat_member(chat_id, user_id)
        if member.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
            return
    except Exception as e:
        logger.error(f"[ANTISPAM] Error checking admin status: {e}")
        return

    try:
        await message.delete()
    except Exception as e:
        logger.error(f"[ANTISPAM] Cannot delete message: {e}")
        return await message.reply(f"<blockquote>{lang.get('no_delete_permission', 'Mesajı silə bilmədim.')}</blockquote>")

    try:
        await db.deleted_messages.insert_one({
            "chat_id": chat_id,
            "user_id": user_id,
            "message_id": message.id,
            "type": "spam",
            "reason": "Unauthorized link sharing",
            "timestamp": datetime.utcnow(),
            "deleted_by": "bot"
        })
        logger.info(f"[ANTISPAM] Logged deleted spam for user {user_id} in {chat_id}")
    except Exception as e:
        logger.error(f"[ANTISPAM] Failed to log deleted message: {e}")

    await db.global_link_stats.update_one(
        {"_id": user_id},
        {"$inc": {"count": 1}, "$set": {"last_seen": datetime.utcnow()}},
        upsert=True
    )

    try:
        await client.send_message(user_id, f"<blockquote>{lang.get('spam_warn_private', 'İcazəsiz link paylaşdığınız üçün xəbərdarlıq aldınız.')}</blockquote>")
    except Exception as e:
        # Check if it's a PEER_ID_INVALID error (user hasn't started conversation with bot)
        if "PEER_ID_INVALID" in str(e):
            logger.debug(f"[ANTISPAM] Cannot send PM to {user_id}: user hasn't started conversation with bot")
        else:
            logger.warning(f"[ANTISPAM] Cannot send PM to {user_id}: {e}")

    warnings = await db.warnings.find_one({"chat_id": chat_id, "user_id": user_id})
    warn_count = (warnings["count"] + 1) if warnings else 1

    await db.warnings.update_one(
        {"chat_id": chat_id, "user_id": user_id},
        {"$set": {"count": warn_count, "last": datetime.utcnow()}},
        upsert=True
    )

    try:
        await db.warnings.insert_one({
            "chat_id": chat_id,
            "user_id": user_id,
            "reason": "Spam - unauthorized link sharing",
            "timestamp": datetime.utcnow(),
            "warned_by": "antispam_module"
        })
        logger.info(f"[ANTISPAM] Logged warning for user {user_id} in {chat_id}")
    except Exception as e:
        logger.error(f"[ANTISPAM] Failed to log warning: {e}")

    warn_limit = group_data.get("warn_limit_spam", 3)
    mute_duration = group_data.get("mute_duration_spam", 10)
    user_mention = user.mention

    if warn_count >= warn_limit:
        await mute_user(chat_id, user_id, duration_minutes=mute_duration, lang_code=lang_code)
        duration_str = format_duration(mute_duration, lang)
        text = lang.get(
            'spam_mute_message',
            '{user}, icazəsiz link paylaşdığınız üçün {duration} susduruldunuz. QƏDDAR qaydaları pozanları bağışlamır.'
        )
        await message.reply(f"<blockquote>{text.format(user=user_mention, duration=duration_str)}</blockquote>")
    else:
        text = lang.get(
            'spam_warn_group_with_user',
            '{user}, icazəsiz link paylaşdınız. Bu QƏDDAR tərəfindən qeydə alındı.'
        )
        await message.reply(f"<blockquote>{text.format(user=user_mention)}</blockquote>")


@app.on_message(filters.command("antispam") & filters.group, group=-1)
async def antispam_command(client: Client, message: Message):
    user = message.from_user
    if not user:
        return

    chat_id = message.chat.id
    lang_code = await get_group_language(chat_id)
    lang = load_language(lang_code)
    args = message.text.split()[1:]

    try:
        member = await app.get_chat_member(chat_id, user.id)
        is_admin = member.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]
    except Exception as e:
        logger.error(f"[ANTISPAM CMD] Admin check failed: {e}")
        return await message.reply(f"<blockquote>{lang.get('error_checking_admin', 'Admin statusunu yoxlaya bilmədim.')}</blockquote>")

    group_data = await db.groups.find_one({"_id": chat_id}) or {}
    warn_limit = group_data.get("warn_limit_spam", 3)
    mute_duration = group_data.get("mute_duration_spam", 10)
    is_enabled = group_data.get("antispam_enabled", True)

    if not args:
        text = lang.get(
            'antispam_status',
            '🛡 AntiSpam Ayarları:\nStatus: {status}\nLimit: {limit} xəbərdarlıq\nMute: {mute} dəqiqə'
        )
        return await message.reply(f"<blockquote>{text.format(status='Aktiv' if is_enabled else 'Deaktiv', limit=warn_limit, mute=mute_duration)}</blockquote>")

    if not is_admin:
        return await message.reply(f"<blockquote>{lang.get('admin_only', 'Bu əmri yalnız adminlər istifadə edə bilər.')}</blockquote>")

    if args[0].lower() in ["on", "off"]:
        enabled = args[0].lower() == "on"
        await db.groups.update_one({"_id": chat_id}, {"$set": {"antispam_enabled": enabled}}, upsert=True)
        msg = lang.get("antispam_enabled" if enabled else "antispam_disabled", "AntiSpam aktiv edildi." if enabled else "AntiSpam deaktiv edildi.")
        return await message.reply(f"<blockquote>✅ {msg}</blockquote>")

    if len(args) == 2 and all(arg.isdigit() for arg in args):
        count, duration = map(int, args)
        await db.groups.update_one({"_id": chat_id}, {"$set": {"warn_limit_spam": count, "mute_duration_spam": duration}}, upsert=True)
        text = lang.get('antispam_set_success', '✅ Spam ayarları yeniləndi.\nLimit: {count}\nMute: {duration} dəq')
        return await message.reply(f"<blockquote>{text.format(count=count, duration=duration)}</blockquote>")

    fallback = lang.get('antispam_set_fail', 'İstifadə:\n/antispam on|off\n/antispam [limit] [dəq]')
    return await message.reply(f"<blockquote>{fallback}</blockquote>")
        

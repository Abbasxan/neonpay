from pyrogram import Client, filters
from pyrogram.types import Message, ChatPermissions
from pyrogram.enums import ChatMemberStatus
from pyrogram.errors import RPCError, UserNotParticipant, PeerIdInvalid
from config import app, scheduler, db
from language import get_group_language, load_language, is_user_admin, is_bot_admin
from modules.mute_utils import mute_user, auto_unmute
from datetime import datetime, timedelta
import re
import logging

# Vaxtı pars etmək üçün müntəzəm ifadələr
TIME_REGEX = re.compile(r'(\d+)([smhd]?)', re.IGNORECASE)
TIME_UNITS = {
    's': 1/60,      # saniyə → dəqiqə
    'm': 1,         # dəqiqə
    'h': 60,        # saat → dəqiqə
    'd': 1440       # gün → dəqiqə
}

def parse_time_duration(time_str: str) -> int:
    """Verilən vaxt sətirini pars edir və dəqiqə sayını qaytarır."""
    if not time_str:
        return 60  # Susmaya görə 1 saat

    # Əgər sadəcə rəqəmdir – dəqiqə sayılır
    if time_str.isdigit():
        return int(time_str)

    total_minutes = 0
    matches = TIME_REGEX.findall(time_str.lower())

    for value, unit in matches:
        value = int(value)
        unit = unit or 'm'  # Susmaya görə dəqiqə
        multiplier = TIME_UNITS.get(unit, 1)
        total_minutes += value * multiplier

    return max(1, int(total_minutes))  # Minimum 1 dəqiqə

async def get_target_user(client: Client, message: Message, args: list):
    """Komanda arqumentlərindən hədəf istifadəçini müəyyən edir."""
    if not args:
        if message.reply_to_message and message.reply_to_message.from_user:
            return message.reply_to_message.from_user
        return None

    target = args[0]

    # ID verilibsə
    if target.isdigit():
        try:
            return await client.get_users(int(target))
        except (PeerIdInvalid, RPCError):
            return None

    # @username verilibsə
    if target.startswith('@'):
        try:
            return await client.get_users(target[1:])
        except (PeerIdInvalid, RPCError):
            return None

    # @ olmadan username
    try:
        return await client.get_users(target)
    except (PeerIdInvalid, RPCError):
        return None

async def check_admin_permissions(client: Client, message: Message, target_user_id: int = None) -> tuple[bool, str]:
    """Komandanı icra etmək üçün lazım olan admin icazələrini yoxlayır."""
    chat_id = message.chat.id
    user_id = message.from_user.id

    # Botun admin olub-olmamasını yoxla
    if not await is_bot_admin(client, chat_id):
        return False, "bot_not_admin"

    # İstifadəçinin admin olub-olmamasını yoxla
    if not await is_user_admin(client, chat_id, user_id):
        return False, "user_not_admin"

    # Hədəf istifadəçi göstərilibsə, onun statusunu yoxla
    if target_user_id:
        try:
            target_member = await client.get_chat_member(chat_id, target_user_id)
            if target_member.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
                return False, "target_is_admin"
        except (RPCError, UserNotParticipant):
            return False, "user_not_found"

    return True, "success"

@app.on_message(filters.command("mute") & filters.group, group=0)
async def mute_command(client: Client, message: Message):
    """İstifadəçini susdurmaq üçün komanda."""
    try:
        args = message.text.split()[1:]
        target_user = await get_target_user(client, message, args)

        if not target_user:
            lang_code = await get_group_language(message.chat.id)
            lang = load_language(lang_code)
            await message.reply(lang.get("mute_no_target"))
            return

        # İcazələri yoxla
        can_execute, error_key = await check_admin_permissions(client, message, target_user.id)
        if not can_execute:
            lang_code = await get_group_language(message.chat.id)
            lang = load_language(lang_code)
            error_messages = {
                "bot_not_admin": lang.get("bot_not_admin"),
                "user_not_admin": lang.get("user_not_admin"),
                "target_is_admin": lang.get("target_is_admin"),
                "user_not_found": lang.get("user_not_found")
            }
            await message.reply(error_messages.get(error_key, lang.get("command_error")))
            return

        # Vaxtı pars et
        duration_minutes = 60  # Susmaya görə 1 saat
        if len(args) > 1:
            duration_minutes = parse_time_duration(args[1])
        elif len(args) == 1 and not args[0].startswith('@') and not args[0].isdigit():
            # Əgər ilk arqument vaxtdırsa və istifadəçi reply-dəndirsə
            duration_minutes = parse_time_duration(args[0])

        # Maksimum 30 gün
        duration_minutes = min(duration_minutes, 43200)  # 30 gün

        # Mute tətbiq et
        lang_code = await get_group_language(message.chat.id)
        success = await mute_user(message.chat.id, target_user.id, duration_minutes, lang_code)

        lang = load_language(lang_code)
        if success:
            # Vaxtın görünüşünü formatlaşdır
            time_str = format_duration(duration_minutes, lang)
            mention = f"<a href='tg://user?id={target_user.id}'>{target_user.first_name}</a>"

            await message.reply(
                lang.get("mute_success").format(
                    mention=mention,
                    duration=time_str
                )
            )

            logging.info(f"[MUTE] İstifadəçi {target_user.id}, {message.from_user.id} tərəfindən {duration_minutes} dəqiqəlik susduruldu (çat: {message.chat.id})")
        else:
            await message.reply(lang.get("mute_failed"))

    except Exception as e:
        logging.error(f"[MUTE COMMAND ERROR] {e}")
        try:
            lang_code = await get_group_language(message.chat.id)
            lang = load_language(lang_code)
            await message.reply(lang.get("command_error"))
        except:
            await message.reply("❌ Komandanın icrası zamanı xəta baş verdi.")

@app.on_message(filters.command("unmute") & filters.group, group=0)
async def unmute_command(client: Client, message: Message):
    """İstifadəçini susdurmadan çıxarmaq üçün komanda."""
    try:
        args = message.text.split()[1:]
        target_user = await get_target_user(client, message, args)

        if not target_user:
            lang_code = await get_group_language(message.chat.id)
            lang = load_language(lang_code)
            await message.reply(lang.get("unmute_no_target"))
            return

        # İcazələri yoxla
        can_execute, error_key = await check_admin_permissions(client, message)
        if not can_execute:
            lang_code = await get_group_language(message.chat.id)
            lang = load_language(lang_code)
            error_messages = {
                "bot_not_admin": lang.get("bot_not_admin"),
                "user_not_admin": lang.get("user_not_admin")
            }
            await message.reply(error_messages.get(error_key, lang.get("command_error")))
            return

        # Susdurmanı götür
        try:
            await client.restrict_chat_member(
                message.chat.id,
                target_user.id,
                permissions=ChatPermissions(
                    can_send_messages=True,
                    can_send_media_messages=True,
                    can_send_other_messages=True,
                    can_add_web_page_previews=True
                )
            )

            # Avto unmute üçün planlaşdırılmış işi ləğv et
            job_id = f"unmute_{message.chat.id}_{target_user.id}"
            for job in scheduler.get_jobs():
                if job.id == job_id:
                    job.remove()
                    break

            # Bazada statusu yenilə
            await db.mutes.update_one(
                {"chat_id": message.chat.id, "user_id": target_user.id},
                {"$set": {"unmuted_at": datetime.utcnow(), "active": False}}
            )

            lang_code = await get_group_language(message.chat.id)
            lang = load_language(lang_code)
            mention = f"<a href='tg://user?id={target_user.id}'>{target_user.first_name}</a>"

            await message.reply(
                lang.get("unmute_success").format(mention=mention)
            )

            logging.info(f"[UNMUTE] İstifadəçi {target_user.id}, {message.from_user.id} tərəfindən susdurmadan çıxarıldı (çat: {message.chat.id})")

        except Exception as e:
            logging.error(f"[UNMUTE ERROR] {e}")
            lang_code = await get_group_language(message.chat.id)
            lang = load_language(lang_code)
            await message.reply(lang.get("unmute_failed"))

    except Exception as e:
        logging.error(f"[UNMUTE COMMAND ERROR] {e}")
        try:
            lang_code = await get_group_language(message.chat.id)
            lang = load_language(lang_code)
            await message.reply(lang.get("command_error"))
        except:
            await message.reply("❌ Komandanın icrası zamanı xəta baş verdi.")

@app.on_message(filters.command("ban") & filters.group, group=0)
async def ban_command(client: Client, message: Message):
    """İstifadəçini ban etmək üçün komanda."""
    try:
        args = message.text.split()[1:]
        target_user = await get_target_user(client, message, args)

        if not target_user:
            lang_code = await get_group_language(message.chat.id)
            lang = load_language(lang_code)
            await message.reply(lang.get("ban_no_target"))
            return

        # İcazələri yoxla
        can_execute, error_key = await check_admin_permissions(client, message, target_user.id)
        if not can_execute:
            lang_code = await get_group_language(message.chat.id)
            lang = load_language(lang_code)
            error_messages = {
                "bot_not_admin": lang.get("bot_not_admin"),
                "user_not_admin": lang.get("user_not_admin"),
                "target_is_admin": lang.get("target_is_admin"),
                "user_not_found": lang.get("user_not_found")
            }
            await message.reply(error_messages.get(error_key, lang.get("command_error")))
            return

        # Ban et
        try:
            await client.ban_chat_member(message.chat.id, target_user.id)

            lang_code = await get_group_language(message.chat.id)
            lang = load_language(lang_code)
            mention = f"<a href='tg://user?id={target_user.id}'>{target_user.first_name}</a>"

            await message.reply(
                lang.get("ban_success").format(mention=mention)
            )

            logging.info(f"[BAN] İstifadəçi {target_user.id}, {message.from_user.id} tərəfindən ban olundu (çat: {message.chat.id})")

        except Exception as e:
            logging.error(f"[BAN ERROR] {e}")
            lang_code = await get_group_language(message.chat.id)
            lang = load_language(lang_code)
            await message.reply(lang.get("ban_failed"))

    except Exception as e:
        logging.error(f"[BAN COMMAND ERROR] {e}")
        try:
            lang_code = await get_group_language(message.chat.id)
            lang = load_language(lang_code)
            await message.reply(lang.get("command_error"))
        except:
            await message.reply("❌ Komandanın icrası zamanı xəta baş verdi.")

@app.on_message(filters.command("unban") & filters.group, group=0)
async def unban_command(client: Client, message: Message):
    """İstifadəçinin banını götürmək üçün komanda."""
    try:
        args = message.text.split()[1:]
        target_user = await get_target_user(client, message, args)

        if not target_user:
            lang_code = await get_group_language(message.chat.id)
            lang = load_language(lang_code)
            await message.reply(lang.get("unban_no_target"))
            return

        # İcazələri yoxla
        can_execute, error_key = await check_admin_permissions(client, message)
        if not can_execute:
            lang_code = await get_group_language(message.chat.id)
            lang = load_language(lang_code)
            error_messages = {
                "bot_not_admin": lang.get("bot_not_admin"),
                "user_not_admin": lang.get("user_not_admin")
            }
            await message.reply(error_messages.get(error_key, lang.get("command_error")))
            return

        # Banı götür
        try:
            await client.unban_chat_member(message.chat.id, target_user.id)

            lang_code = await get_group_language(message.chat.id)
            lang = load_language(lang_code)
            mention = f"<a href='tg://user?id={target_user.id}'>{target_user.first_name}</a>"

            await message.reply(
                lang.get("unban_success").format(mention=mention)
            )

            logging.info(f"[UNBAN] İstifadəçi {target_user.id}, {message.from_user.id} tərəfindən ban-dan çıxarıldı (çat: {message.chat.id})")

        except Exception as e:
            logging.error(f"[UNBAN ERROR] {e}")
            lang_code = await get_group_language(message.chat.id)
            lang = load_language(lang_code)
            await message.reply(lang.get("unban_failed"))

    except Exception as e:
        logging.error(f"[UNBAN COMMAND ERROR] {e}")
        try:
            lang_code = await get_group_language(message.chat.id)
            lang = load_language(lang_code)
            await message.reply(lang.get("command_error"))
        except:
            await message.reply("❌ Komandanın icrası zamanı xəta baş verdi.")

@app.on_message(filters.command("kick") & filters.group, group=0)
async def kick_command(client: Client, message: Message):
    """İstifadəçini qrupdan çıxarmaq üçün komanda."""
    try:
        args = message.text.split()[1:]
        target_user = await get_target_user(client, message, args)

        if not target_user:
            lang_code = await get_group_language(message.chat.id)
            lang = load_language(lang_code)
            await message.reply(lang.get("kick_no_target"))
            return

        # İcazələri yoxla
        can_execute, error_key = await check_admin_permissions(client, message, target_user.id)
        if not can_execute:
            lang_code = await get_group_language(message.chat.id)
            lang = load_language(lang_code)
            error_messages = {
                "bot_not_admin": lang.get("bot_not_admin"),
                "user_not_admin": lang.get("user_not_admin"),
                "target_is_admin": lang.get("target_is_admin"),
                "user_not_found": lang.get("user_not_found")
            }
            await message.reply(error_messages.get(error_key, lang.get("command_error")))
            return

        # Kick = ban + unban
        try:
            await client.ban_chat_member(message.chat.id, target_user.id)
            await client.unban_chat_member(message.chat.id, target_user.id)

            lang_code = await get_group_language(message.chat.id)
            lang = load_language(lang_code)
            mention = f"<a href='tg://user?id={target_user.id}'>{target_user.first_name}</a>"

            await message.reply(
                lang.get("kick_success").format(mention=mention)
            )

            logging.info(f"[KICK] İstifadəçi {target_user.id}, {message.from_user.id} tərəfindən qrupdan çıxarıldı (çat: {message.chat.id})")

        except Exception as e:
            logging.error(f"[KICK ERROR] {e}")
            lang_code = await get_group_language(message.chat.id)
            lang = load_language(lang_code)
            await message.reply(lang.get("kick_failed"))

    except Exception as e:
        logging.error(f"[KICK COMMAND ERROR] {e}")
        try:
            lang_code = await get_group_language(message.chat.id)
            lang = load_language(lang_code)
            await message.reply(lang.get("command_error"))
        except:
            await message.reply("❌ Komandanın icrası zamanı xəta baş verdi.")

def format_duration(minutes: int, lang: dict = None) -> str:
    """Dəqiqə ilə verilmiş müddəti oxunaqlı mətnə çevirir."""
    if lang is None:
        # Fallback to Azerbaijani if no language provided
        if minutes < 60:
            return f"{minutes} dəqiqə"
        elif minutes < 1440:
            hours = minutes // 60
            remaining_minutes = minutes % 60
            if remaining_minutes == 0:
                return f"{hours} saat"
            else:
                return f"{hours} saat {remaining_minutes} dəqiqə"
        else:
            days = minutes // 1440
            remaining_hours = (minutes % 1440) // 60
            if remaining_hours == 0:
                return f"{days} gün"
            else:
                return f"{days} gün {remaining_hours} saat"
    
    # Use language keys
    if minutes < 60:
        return lang.get("duration_minutes").format(minutes=minutes)
    elif minutes < 1440:
        hours = minutes // 60
        remaining_minutes = minutes % 60
        if remaining_minutes == 0:
            return lang.get("duration_hours").format(hours=hours)
        else:
            return lang.get("duration_hours_minutes").format(hours=hours, minutes=remaining_minutes)
    else:
        days = minutes // 1440
        remaining_hours = (minutes % 1440) // 60
        if remaining_hours == 0:
            return lang.get("duration_days").format(days=days)
        else:
            return lang.get("duration_days_hours").format(days=days, hours=remaining_hours)

@app.on_message(filters.command("mutelist") & filters.group, group=0)
async def mutelist_command(client: Client, message: Message):
    """Aktiv susdurmaların siyahısını göstərir."""
    try:
        # Admin icazələrini yoxla
        can_execute, error_key = await check_admin_permissions(client, message)
        if not can_execute:
            lang_code = await get_group_language(message.chat.id)
            lang = load_language(lang_code)
            error_messages = {
                "bot_not_admin": lang.get("bot_not_admin"),
                "user_not_admin": lang.get("user_not_admin")
            }
            await message.reply(error_messages.get(error_key, lang.get("command_error")))
            return

        # Bu qrup üçün aktiv susdurmaları götür
        active_mutes = await db.mutes.find({
            "chat_id": message.chat.id,
            "muted_until": {"$gt": datetime.utcnow()},
            "active": {"$ne": False}
        }).to_list(length=50)

        lang_code = await get_group_language(message.chat.id)
        lang = load_language(lang_code)

        if not active_mutes:
            await message.reply(lang.get("no_active_mutes"))
            return

        text = lang.get("active_mutes_header")

        for mute in active_mutes:
            try:
                user = await client.get_users(mute["user_id"])
                mention = f"<a href='tg://user?id={mute['user_id']}'>{user.first_name}</a>"
            except Exception:
                mention = f"<a href='tg://user?id={mute['user_id']}'>ID {mute['user_id']}</a>"

            remaining_time = mute["muted_until"] - datetime.utcnow()
            remaining_minutes = int(remaining_time.total_seconds() / 60)
            time_str = format_duration(max(1, remaining_minutes), lang)

            text += f"• {mention} — {time_str}\n"

        await message.reply(text)

    except Exception as e:
        logging.error(f"[MUTELIST COMMAND ERROR] {e}")
        try:
            lang_code = await get_group_language(message.chat.id)
            lang = load_language(lang_code)
            await message.reply(lang.get("command_error"))
        except:
            await message.reply("❌ Komandanın icrası zamanı xəta baş verdi.")


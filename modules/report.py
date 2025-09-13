from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.enums import ChatMemberStatus
from config import app, db
from language import get_group_language, load_language
import html
from datetime import datetime, timedelta

@app.on_message(filters.command("rapor") & filters.group, group=0)
async def complain_handler(client: Client, message: Message):
    """Отправляет жалобу на пользователя всем администраторам"""
    group_id = message.chat.id
    reporter = message.from_user

    if not reporter:
        return

    if message.reply_to_message:
        mentioned_user = message.reply_to_message.from_user
        if not mentioned_user:
            lang_code = await get_group_language(message.chat.id)
            lang = load_language(lang_code)
            return await message.reply(lang.get("report_user_not_found"))
        reason = " ".join(message.command[1:]) if len(message.command) > 1 else lang.get("report_no_reason")
    else:
        lang_code = await get_group_language(message.chat.id)
        lang = load_language(lang_code)
        
        if len(message.command) < 3:
            return await message.reply(lang.get("report_usage"))

        mentioned = message.command[1]
        reason = " ".join(message.command[2:])
        if not mentioned.startswith("@"):
            return await message.reply(lang.get("report_mention_user"))
        
        # Попытка найти пользователя по username
        try:
            mentioned_user = await client.get_users(mentioned.replace("@", ""))
        except:
            mentioned_user = None

    try:
        admins = []
        async for member in client.get_chat_members(group_id):
            if member.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
                admins.append(member)
            if len(admins) >= 50:  # Ограничиваем количество для производительности
                break
    except Exception as e:
        print(f"[RAPOR ERROR] Failed to get admins: {e}")
        return await message.reply(lang.get("report_get_admins_error"))

    if not admins:
        return await message.reply(lang.get("report_no_admins"))

    # Формируем текст жалобы
    text = lang.get("report_header").format(
        reporter_id=reporter.id,
        reporter_name=html.escape(reporter.first_name)
    )
    
    if reporter.username:
        text += f" (@{reporter.username})"
    
    if mentioned_user:
        text += lang.get("report_reported_user").format(
            reported_id=mentioned_user.id,
            reported_name=html.escape(mentioned_user.first_name)
        )
        if mentioned_user.username:
            text += f" (@{mentioned_user.username})"
    else:
        text += lang.get("report_reported_username").format(reported_username=html.escape(mentioned))
    
    text += (
        lang.get("report_reason").format(reason=html.escape(reason)) +
        lang.get("report_group").format(group_title=html.escape(message.chat.title), group_id=group_id) +
        lang.get("report_date").format(date=datetime.now().strftime('%d.%m.%Y %H:%M'))
    )
    
    if message.reply_to_message:
        text += lang.get("report_message_link").format(message_link=message.reply_to_message.link)

    # Отправляем жалобу всем администраторам
    success = 0
    for admin in admins:
        user = admin.user
        if user.is_bot:
            continue
        try:
            await client.send_message(user.id, text)
            success += 1
        except Exception as e:
            # Check if it's a PEER_ID_INVALID error (admin hasn't started conversation with bot)
            if "PEER_ID_INVALID" in str(e):
                print(f"[RAPOR] Cannot send report to admin {user.id}: admin hasn't started conversation with bot")
            else:
                print(f"[RAPOR] Failed to send to admin {user.id}: {e}")
            continue

    if success > 0:
        await message.reply(lang.get("report_success").format(success_count=success))
        
        # Сохраняем жалобу в базу данных для статистики
        try:
            await db.reports.insert_one({
                "chat_id": group_id,
                "reporter_id": reporter.id,
                "reported_user_id": mentioned_user.id if mentioned_user else None,
                "reported_username": mentioned if not mentioned_user else None,
                "reason": reason,
                "timestamp": datetime.now(),
                "admins_notified": success
            })
        except Exception as e:
            print(f"[RAPOR] Failed to save report: {e}")
    else:
        await message.reply(lang.get("report_failed"))

@app.on_message(filters.command("reports") & filters.group, group=0)
async def reports_command(client: Client, message: Message):
    """Показывает статистику жалоб и нарушений в группе"""
    if not message.from_user:
        return
    
    chat_id = message.chat.id
    user_id = message.from_user.id
    
    # Проверяем права администратора
    try:
        member = await app.get_chat_member(chat_id, user_id)
        is_admin = member.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]
    except Exception:
        lang_code = await get_group_language(message.chat.id)
        lang = load_language(lang_code)
        return await message.reply(lang.get("report_admin_check_error"))
    
    if not is_admin:
        lang_code = await get_group_language(message.chat.id)
        lang = load_language(lang_code)
        return await message.reply(lang.get("report_admin_only"))
    
    lang_code = await get_group_language(chat_id)
    lang = load_language(lang_code)
    
    try:
        # Получаем статистику нарушений за последние 30 дней
        thirty_days_ago = datetime.now() - timedelta(days=30)
        
        # Статистика предупреждений
        warnings_stats = await db.warnings.aggregate([
            {"$match": {"chat_id": chat_id, "timestamp": {"$gte": thirty_days_ago}}},
            {"$group": {
                "_id": "$user_id",
                "count": {"$sum": 1},
                "reasons": {"$push": "$reason"},
                "last_warning": {"$max": "$timestamp"}
            }},
            {"$sort": {"count": -1}},
            {"$limit": 10}
        ]).to_list(length=10)
        
        # Статистика удаленных сообщений (антиспам, антивульгар, антиреклама)
        deleted_stats = await db.deleted_messages.aggregate([
            {"$match": {"chat_id": chat_id, "timestamp": {"$gte": thirty_days_ago}}},
            {"$group": {
                "_id": {"user_id": "$user_id", "type": "$type"},
                "count": {"$sum": 1}
            }},
            {"$group": {
                "_id": "$_id.user_id",
                "total": {"$sum": "$count"},
                "types": {"$push": {"type": "$_id.type", "count": "$count"}}
            }},
            {"$sort": {"total": -1}},
            {"$limit": 10}
        ]).to_list(length=10)
        
        report_text = lang.get("report_group_header").format(group_title=html.escape(message.chat.title))
        
        # Топ нарушители по предупреждениям
        if warnings_stats:
            report_text += lang.get("report_top_warnings")
            for i, stat in enumerate(warnings_stats[:5], 1):
                try:
                    user = await client.get_users(stat["_id"])
                    name = html.escape(user.first_name)
                    username = f"@{user.username}" if user.username else ""
                except:
                    name = lang.get("report_unknown_user")
                    username = ""
                
                report_text += lang.get("report_warning_user").format(
                    index=i,
                    user_id=stat["_id"],
                    user_name=name,
                    username=username,
                    count=stat["count"]
                )
            report_text += "\n"
        
        # Топ нарушители по удаленным сообщениям
        if deleted_stats:
            report_text += lang.get("report_top_deleted")
            for i, stat in enumerate(deleted_stats[:5], 1):
                try:
                    user = await client.get_users(stat["_id"])
                    name = html.escape(user.first_name)
                    username = f"@{user.username}" if user.username else ""
                except:
                    name = lang.get("report_unknown_user")
                    username = ""
                
                types_text = ", ".join([f"{t['type']}: {t['count']}" for t in stat['types']])
                report_text += lang.get("report_deleted_user").format(
                    index=i,
                    user_id=stat["_id"],
                    user_name=name,
                    username=username,
                    total=stat["total"],
                    types_text=types_text
                )
            report_text += "\n"
        
        # Общая статистика
        total_warnings = sum(stat["count"] for stat in warnings_stats)
        total_deleted = sum(stat["total"] for stat in deleted_stats)
        
        report_text += lang.get("report_stats_header")
        report_text += lang.get("report_total_warnings").format(total_warnings=total_warnings)
        report_text += lang.get("report_total_deleted").format(total_deleted=total_deleted)
        report_text += lang.get("report_active_users").format(active_users=len(warnings_stats) + len(deleted_stats))
        
        if not warnings_stats and not deleted_stats:
            report_text += lang.get("report_no_violations_30")
        
        await message.reply(report_text)
        
    except Exception as e:
        await message.reply(lang.get("report_error_general"))
        print(f"[REPORTS ERROR] {e}")

@app.on_message(filters.command("report") & filters.group, group=0)
async def user_report_command(client: Client, message: Message):
    """Показывает детальный репорт о конкретном пользователе"""
    if not message.from_user:
        return
    
    chat_id = message.chat.id
    user_id = message.from_user.id
    
    # Проверяем права администратора
    try:
        member = await app.get_chat_member(chat_id, user_id)
        is_admin = member.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]
    except Exception:
        lang_code = await get_group_language(message.chat.id)
        lang = load_language(lang_code)
        return await message.reply(lang.get("report_admin_check_error"))
    
    if not is_admin:
        lang_code = await get_group_language(message.chat.id)
        lang = load_language(lang_code)
        return await message.reply(lang.get("report_admin_only"))
    
    # Получаем пользователя для репорта
    target_user = None
    if message.reply_to_message and message.reply_to_message.from_user:
        target_user = message.reply_to_message.from_user
    elif len(message.command) > 1:
        try:
            username_or_id = message.command[1].replace("@", "")
            target_user = await client.get_users(username_or_id)
        except:
            lang_code = await get_group_language(message.chat.id)
            lang = load_language(lang_code)
            return await message.reply(lang.get("report_user_not_found_cmd"))
    else:
        lang_code = await get_group_language(message.chat.id)
        lang = load_language(lang_code)
        return await message.reply(lang.get("report_user_usage"))
    
    try:
        # Получаем статистику пользователя за все время
        warnings = await db.warnings.find({"chat_id": chat_id, "user_id": target_user.id}).to_list(length=None)
        deleted_messages = await db.deleted_messages.find({"chat_id": chat_id, "user_id": target_user.id}).to_list(length=None)
        
        lang_code = await get_group_language(message.chat.id)
        lang = load_language(lang_code)
        
        report_text = lang.get("report_user_header").format(
            group_title=html.escape(message.chat.title),
            user_id=target_user.id,
            user_name=html.escape(target_user.first_name)
        )
        if target_user.username:
            report_text += f" (@{target_user.username})"
        report_text += lang.get("report_user_id").format(user_id=target_user.id)
        
        # Предупреждения
        if warnings:
            report_text += lang.get("report_warnings_header").format(warning_count=len(warnings))
            for warning in warnings[-5:]:  # Последние 5 предупреждений
                date = warning.get('timestamp', datetime.now()).strftime('%d.%m.%Y %H:%M')
                reason = warning.get('reason', lang.get("report_no_reason"))
                report_text += lang.get("report_warning_item").format(date=date, reason=html.escape(reason))
            if len(warnings) > 5:
                report_text += lang.get("report_more_warnings").format(more_count=len(warnings) - 5)
            report_text += "\n"
        
        # Удаленные сообщения по типам
        if deleted_messages:
            types_count = {}
            for msg in deleted_messages:
                msg_type = msg.get('type', 'unknown')
                types_count[msg_type] = types_count.get(msg_type, 0) + 1
            
            report_text += lang.get("report_deleted_header").format(deleted_count=len(deleted_messages))
            for msg_type, count in types_count.items():
                type_names = {
                    'spam': lang.get("report_type_spam"),
                    'vulgar': lang.get("report_type_vulgar"),
                    'ad': lang.get("report_type_ad"),
                    'flood': lang.get("report_type_flood")
                }
                type_name = type_names.get(msg_type, msg_type.title())
                report_text += lang.get("report_deleted_item").format(type_name=type_name, count=count)
            report_text += "\n"
        
        if not warnings and not deleted_messages:
            report_text += lang.get("report_no_violations")
        
        await message.reply(report_text)
        
    except Exception as e:
        await message.reply(lang.get("report_error"))
        print(f"[USER REPORT ERROR] {e}")
            

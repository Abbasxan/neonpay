from pyrogram import filters, Client
from pyrogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from config import app, users_collection, groups_collection, OWNER_ID, LOG_ID
from language import load_language, get_user_language
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

async def get_chat_info(client: Client, chat_id: int):
    """Получает актуальную информацию о чате"""
    try:
        chat = await client.get_chat(chat_id)
        member_count = 0
        
        # Пытаемся получить количество участников разными способами
        try:
            member_count = await client.get_chat_members_count(chat_id)
        except Exception:
            try:
                # Альтернативный способ через get_chat
                if hasattr(chat, 'members_count') and chat.members_count:
                    member_count = chat.members_count
            except Exception:
                member_count = 0
        
        return {
            "title": chat.title or "Unknown Group",
            "username": chat.username,
            "type": str(chat.type),
            "member_count": member_count
        }
    except Exception as e:
        logger.error(f"Error getting chat info for {chat_id}: {e}")
        return None

# Обработчик для отслеживания добавления бота в группы
@app.on_message(filters.new_chat_members, group=1)
async def track_group_join(client: Client, message: Message):
    """Отслеживает добавление бота в новые группы"""
    bot = await client.get_me()
    
    # Проверяем, добавлен ли наш бот
    for new_member in message.new_chat_members:
        if new_member.id == bot.id:
            chat = message.chat
            
            chat_info = await get_chat_info(client, chat.id)
            if not chat_info:
                chat_info = {
                    "title": chat.title or "Unknown Group",
                    "username": chat.username,
                    "type": str(chat.type),
                    "member_count": 0
                }
            
            # Сохраняем информацию о группе в базу данных
            try:
                result = await groups_collection.update_one(
                    {"_id": chat.id},
                    {
                        "$set": {
                            "title": chat_info["title"],
                            "type": chat_info["type"],
                            "username": chat_info["username"],
                            "member_count": chat_info["member_count"],
                            "last_activity": datetime.utcnow(),
                            "status": "active"  # Явно устанавливаем статус
                        },
                        "$setOnInsert": {
                            "join_date": datetime.utcnow()
                        }
                    },
                    upsert=True
                )
                
                # Если это новая группа, отправляем уведомление в лог
                if result.upserted_id and LOG_ID:
                    try:
                        # Get language for log message (default to Russian for logs)
                        lang = load_language("ru")
                        
                        await app.send_message(
                            chat_id=LOG_ID,
                            text=lang.get("new_group_log").format(
                                title=chat_info['title'],
                                chat_id=chat.id,
                                member_count=chat_info['member_count'],
                                username=chat_info['username'] or '—',
                                date=datetime.utcnow().strftime('%d.%m.%Y %H:%M')
                            )
                        )
                        logger.info(f"Bot added to new group: {chat_info['title']} ({chat.id}) with {chat_info['member_count']} members")
                    except Exception as e:
                        logger.error(f"Failed to send group join log: {e}")
                        
            except Exception as e:
                logger.error(f"Failed to save group info: {e}")
            break

# Обработчик для отслеживания удаления бота из групп
@app.on_message(filters.left_chat_member, group=1)
async def track_group_leave(client: Client, message: Message):
    """Отслеживает удаление бота из групп"""
    bot = await client.get_me()
    
    if message.left_chat_member.id == bot.id:
        chat = message.chat
        
        # Обновляем информацию о группе
        try:
            await groups_collection.update_one(
                {"_id": chat.id},
                {
                    "$set": {
                        "left_date": datetime.utcnow(),
                        "status": "left"
                    }
                }
            )
            
            # Отправляем уведомление в лог
            if LOG_ID:
                try:
                    # Get language for log message (default to Russian for logs)
                    lang = load_language("ru")
                    
                    await app.send_message(
                        chat_id=LOG_ID,
                        text=lang.get("left_group_log").format(
                            title=chat.title,
                            chat_id=chat.id,
                            date=datetime.utcnow().strftime('%d.%m.%Y %H:%M')
                        )
                    )
                    logger.info(f"Bot removed from group: {chat.title} ({chat.id})")
                except Exception as e:
                    logger.error(f"Failed to send group leave log: {e}")
                    
        except Exception as e:
            logger.error(f"Failed to update group leave info: {e}")

# Команда для просмотра статистики (только для владельца)
@app.on_message(filters.command("stats") & filters.user(OWNER_ID), group=0)
async def stats_command(client: Client, message: Message):
    """Показывает статистику бота"""
    try:
        # Get language for owner (default to Russian)
        lang = load_language("ru")
        
        # Подсчитываем пользователей
        total_users = await users_collection.count_documents({})
        
        # Подсчитываем активные группы (где бот еще находится)
        active_groups = await groups_collection.count_documents({"status": {"$ne": "left"}})
        total_groups = await groups_collection.count_documents({})
        left_groups = total_groups - active_groups
        
        # Получаем статистику за последние 24 часа
        from datetime import timedelta
        yesterday = datetime.utcnow() - timedelta(days=1)
        
        new_users_today = await users_collection.count_documents({
            "join_date": {"$gte": yesterday}
        })
        
        new_groups_today = await groups_collection.count_documents({
            "join_date": {"$gte": yesterday}
        })
        
        stats_text = (
            f"{lang.get('stats_title')}\n\n"
            f"{lang.get('stats_users')}\n"
            f"{lang.get('stats_users_total').format(total=total_users)}\n"
            f"{lang.get('stats_users_new_24h').format(new=new_users_today)}\n\n"
            f"{lang.get('stats_groups')}\n"
            f"{lang.get('stats_groups_active').format(active=active_groups)}\n"
            f"{lang.get('stats_groups_left').format(left=left_groups)}\n"
            f"{lang.get('stats_groups_total').format(total=total_groups)}\n"
            f"{lang.get('stats_groups_new_24h').format(new=new_groups_today)}\n\n"
            f"{lang.get('stats_updated').format(date=datetime.utcnow().strftime('%d.%m.%Y %H:%M'))}"
        )
        
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton(lang.get("stats_top_groups"), callback_data="stats_top_groups"),
                InlineKeyboardButton(lang.get("stats_details"), callback_data="stats_details")
            ],
            [InlineKeyboardButton(lang.get("stats_refresh"), callback_data="stats_refresh")]
        ])
        
        await message.reply(stats_text, reply_markup=keyboard)
        
    except Exception as e:
        logger.error(f"Error in stats command: {e}")
        lang = load_language("ru")
        await message.reply(lang.get("stats_error").format(error=e))

# Callback для обновления статистики
@app.on_callback_query(filters.regex("^stats_refresh$"))
async def refresh_stats_callback(client: Client, callback_query: CallbackQuery):
    """Обновляет статистику"""
    if callback_query.from_user.id != OWNER_ID:
        lang = load_language("ru")
        await callback_query.answer(lang.get("stats_no_permission"), show_alert=True)
        return
    
    try:
        # Get language for owner (default to Russian)
        lang = load_language("ru")
        
        # Подсчитываем статистику заново
        total_users = await users_collection.count_documents({})
        active_groups = await groups_collection.count_documents({"status": {"$ne": "left"}})
        total_groups = await groups_collection.count_documents({})
        left_groups = total_groups - active_groups
        
        from datetime import timedelta
        yesterday = datetime.utcnow() - timedelta(days=1)
        
        new_users_today = await users_collection.count_documents({
            "join_date": {"$gte": yesterday}
        })
        
        new_groups_today = await groups_collection.count_documents({
            "join_date": {"$gte": yesterday}
        })
        
        stats_text = (
            f"{lang.get('stats_title')}\n\n"
            f"{lang.get('stats_users')}\n"
            f"{lang.get('stats_users_total').format(total=total_users)}\n"
            f"{lang.get('stats_users_new_24h').format(new=new_users_today)}\n\n"
            f"{lang.get('stats_groups')}\n"
            f"{lang.get('stats_groups_active').format(active=active_groups)}\n"
            f"{lang.get('stats_groups_left').format(left=left_groups)}\n"
            f"{lang.get('stats_groups_total').format(total=total_groups)}\n"
            f"{lang.get('stats_groups_new_24h').format(new=new_groups_today)}\n\n"
            f"{lang.get('stats_updated').format(date=datetime.utcnow().strftime('%d.%m.%Y %H:%M'))}"
        )
        
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton(lang.get("stats_top_groups"), callback_data="stats_top_groups"),
                InlineKeyboardButton(lang.get("stats_details"), callback_data="stats_details")
            ],
            [InlineKeyboardButton(lang.get("stats_refresh"), callback_data="stats_refresh")]
        ])
        
        await callback_query.edit_message_text(stats_text, reply_markup=keyboard)
        await callback_query.answer(lang.get("stats_refresh_success"))
        
    except Exception as e:
        logger.error(f"Error refreshing stats: {e}")
        lang = load_language("ru")
        await callback_query.answer(lang.get("stats_refresh_error").format(error=e), show_alert=True)

# Callback для показа топ групп
@app.on_callback_query(filters.regex("^stats_top_groups$"))
async def top_groups_callback(client: Client, callback_query: CallbackQuery):
    """Показывает топ групп по количеству участников"""
    if callback_query.from_user.id != OWNER_ID:
        lang = load_language("ru")
        await callback_query.answer(lang.get("stats_no_permission"), show_alert=True)
        return
    
    try:
        # Get language for owner (default to Russian)
        lang = load_language("ru")
        
        # Получаем топ-10 групп по количеству участников
        top_groups = await groups_collection.find(
            {"status": {"$ne": "left"}},
            {"title": 1, "member_count": 1, "join_date": 1}
        ).sort("member_count", -1).limit(10).to_list(length=10)
        
        if not top_groups:
            await callback_query.answer(lang.get("stats_no_active_groups"), show_alert=True)
            return
        
        text = f"{lang.get('stats_top_groups_title')}\n\n"
        
        for i, group in enumerate(top_groups, 1):
            title = group.get("title", "Unknown Group")[:30]
            member_count = group.get("member_count", 0)
            join_date = group.get("join_date", datetime.utcnow()).strftime("%d.%m.%Y")
            
            text += f"{i}. <b>{title}</b>\n"
            text += f"   {lang.get('stats_group_members').format(count=member_count)}\n"
            text += f"   {lang.get('stats_group_joined').format(date=join_date)}\n\n"
        
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(lang.get("stats_back_to_stats"), callback_data="stats_refresh")]
        ])
        
        await callback_query.edit_message_text(text, reply_markup=keyboard)
        
    except Exception as e:
        logger.error(f"Error showing top groups: {e}")
        lang = load_language("ru")
        await callback_query.answer(lang.get("stats_top_groups_error").format(error=e), show_alert=True)

# Callback для детальной статистики
@app.on_callback_query(filters.regex("^stats_details$"))
async def stats_details_callback(client: Client, callback_query: CallbackQuery):
    """Показывает детальную статистику"""
    if callback_query.from_user.id != OWNER_ID:
        lang = load_language("ru")
        await callback_query.answer(lang.get("stats_no_permission"), show_alert=True)
        return
    
    try:
        # Get language for owner (default to Russian)
        lang = load_language("ru")
        
        from datetime import timedelta
        
        # Статистика за разные периоды
        now = datetime.utcnow()
        day_ago = now - timedelta(days=1)
        week_ago = now - timedelta(days=7)
        month_ago = now - timedelta(days=30)
        
        # Пользователи по периодам
        users_day = await users_collection.count_documents({"join_date": {"$gte": day_ago}})
        users_week = await users_collection.count_documents({"join_date": {"$gte": week_ago}})
        users_month = await users_collection.count_documents({"join_date": {"$gte": month_ago}})
        
        # Группы по периодам
        groups_day = await groups_collection.count_documents({"join_date": {"$gte": day_ago}})
        groups_week = await groups_collection.count_documents({"join_date": {"$gte": week_ago}})
        groups_month = await groups_collection.count_documents({"join_date": {"$gte": month_ago}})
        
        # Покинутые группы за периоды
        left_day = await groups_collection.count_documents({"left_date": {"$gte": day_ago}})
        left_week = await groups_collection.count_documents({"left_date": {"$gte": week_ago}})
        left_month = await groups_collection.count_documents({"left_date": {"$gte": month_ago}})
        
        text = (
            f"{lang.get('stats_detailed_title')}\n\n"
            f"{lang.get('stats_new_users')}\n"
            f"{lang.get('stats_period_day').format(count=users_day)}\n"
            f"{lang.get('stats_period_week').format(count=users_week)}\n"
            f"{lang.get('stats_period_month').format(count=users_month)}\n\n"
            f"{lang.get('stats_new_groups')}\n"
            f"{lang.get('stats_period_day').format(count=groups_day)}\n"
            f"{lang.get('stats_period_week').format(count=groups_week)}\n"
            f"{lang.get('stats_period_month').format(count=groups_month)}\n\n"
            f"{lang.get('stats_left_groups')}\n"
            f"{lang.get('stats_period_day').format(count=left_day)}\n"
            f"{lang.get('stats_period_week').format(count=left_week)}\n"
            f"{lang.get('stats_period_month').format(count=left_month)}\n\n"
            f"{lang.get('stats_updated').format(date=now.strftime('%d.%m.%Y %H:%M'))}"
        )
        
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(lang.get("stats_back_to_stats"), callback_data="stats_refresh")]
        ])
        
        await callback_query.edit_message_text(text, reply_markup=keyboard)
        
    except Exception as e:
        logger.error(f"Error showing stats details: {e}")
        lang = load_language("ru")
        await callback_query.answer(lang.get("stats_details_error").format(error=e), show_alert=True)

# Команда для обновления информации о группах
@app.on_message(filters.command("update_groups") & filters.user(OWNER_ID), group=0)
async def update_groups_info(client: Client, message: Message):
    """Обновляет информацию о всех активных группах"""
    try:
        # Get language for owner (default to Russian)
        lang = load_language("ru")
        
        # Получаем все активные группы
        active_groups = await groups_collection.find({"status": {"$ne": "left"}}).to_list(length=None)
        
        updated_count = 0
        failed_count = 0
        
        status_msg = await message.reply(lang.get("stats_update_groups_start"))
        
        for group in active_groups:
            try:
                chat_info = await get_chat_info(client, group["_id"])
                if chat_info:
                    await groups_collection.update_one(
                        {"_id": group["_id"]},
                        {
                            "$set": {
                                "title": chat_info["title"],
                                "member_count": chat_info["member_count"],
                                "username": chat_info["username"],
                                "last_activity": datetime.utcnow()
                            }
                        }
                    )
                    updated_count += 1
                else:
                    failed_count += 1
                    
            except Exception as e:
                logger.error(f"Failed to update group {group['_id']}: {e}")
                failed_count += 1
        
        await status_msg.edit_text(
            f"{lang.get('stats_update_complete')}\n\n"
            f"{lang.get('stats_updated_groups').format(updated=updated_count)}\n"
            f"{lang.get('stats_update_errors').format(errors=failed_count)}\n"
            f"{lang.get('stats_update_time').format(date=datetime.utcnow().strftime('%d.%m.%Y %H:%M'))}"
        )
        
    except Exception as e:
        logger.error(f"Error updating groups info: {e}")
        lang = load_language("ru")
        await message.reply(lang.get("stats_update_error").format(error=e))

logger.info("✅ Statistics module loaded successfully")
                                     

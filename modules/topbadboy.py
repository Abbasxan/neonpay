from pyrogram import filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from pyrogram.errors import MessageNotModified
from config import app, db
from datetime import datetime, timedelta
from language import get_group_language, load_language

PERIODS = {
    "today": timedelta(days=1),
    "week": timedelta(days=7),
    "month": timedelta(days=30),
    "all": None,
}

def get_period_filter(period: str):
    if PERIODS[period]:
        since = datetime.utcnow() - PERIODS[period]
        return {"last": {"$gte": since}}
    return {}

def build_keyboard(view: str, period: str, stat_type: str = "warnings", lang: dict = None):
    if lang is None:
        # Fallback to default language if not provided
        lang = {
            "topbad_today": "📅 Bu gün",
            "topbad_week": "🗓 Bu həftə", 
            "topbad_month": "📆 Bu ay",
            "topbad_all": "🕰 Bütün zamanlar",
            "topbad_groups": "🌐 Qruplar",
            "topbad_users": "👥 İstifadəçilər",
            "topbad_warnings": "⚠️ Xəbərdarlıqlar",
            "topbad_vulgar": "🤬 Vulqar sözlər",
            "topbad_close": "❌ Bağla"
        }
    
    if view == "users":
        buttons = [
            [InlineKeyboardButton(lang.get("topbad_today"), callback_data=f"topbad_users_today_{stat_type}"),
             InlineKeyboardButton(lang.get("topbad_week"), callback_data=f"topbad_users_week_{stat_type}"),
             InlineKeyboardButton(lang.get("topbad_month"), callback_data=f"topbad_users_month_{stat_type}")],
            [InlineKeyboardButton(lang.get("topbad_all"), callback_data=f"topbad_users_all_{stat_type}"),
             InlineKeyboardButton(lang.get("topbad_groups"), callback_data=f"topbad_groups_today_{stat_type}")],
            [InlineKeyboardButton(lang.get("topbad_warnings") if stat_type == "vulgar" else lang.get("topbad_vulgar"), 
                                callback_data=f"topbad_users_{period}_{'warnings' if stat_type == 'vulgar' else 'vulgar'}"),
             InlineKeyboardButton(lang.get("topbad_close"), callback_data="topbad_close")]
        ]
    else:  # groups
        buttons = [
            [InlineKeyboardButton(lang.get("topbad_today"), callback_data=f"topbad_groups_today_{stat_type}"),
             InlineKeyboardButton(lang.get("topbad_week"), callback_data=f"topbad_groups_week_{stat_type}"),
             InlineKeyboardButton(lang.get("topbad_month"), callback_data=f"topbad_groups_month_{stat_type}")],
            [InlineKeyboardButton(lang.get("topbad_all"), callback_data=f"topbad_groups_all_{stat_type}"),
             InlineKeyboardButton(lang.get("topbad_users"), callback_data=f"topbad_users_today_{stat_type}")],
            [InlineKeyboardButton(lang.get("topbad_warnings") if stat_type == "vulgar" else lang.get("topbad_vulgar"), 
                                callback_data=f"topbad_groups_{period}_{'warnings' if stat_type == 'vulgar' else 'vulgar'}"),
             InlineKeyboardButton(lang.get("topbad_close"), callback_data="topbad_close")]
        ]
    return InlineKeyboardMarkup(buttons)

@app.on_message(filters.command("topbadder") & filters.group, group=0)
async def show_top_bad_users(client, message: Message):
    await send_top_list(message, view="users", period="today", stat_type="warnings")

@app.on_callback_query(filters.regex(r"topbad_(users|groups)_(today|week|month|all)_(warnings|vulgar)"))
async def on_callback_change_view_period(client, callback_query: CallbackQuery):
    parts = callback_query.data.split("_")
    view, period, stat_type = parts[1], parts[2], parts[3]
    await send_top_list(callback_query.message, view=view, period=period, stat_type=stat_type, cb=callback_query)

@app.on_callback_query(filters.regex(r"topbad_close"))
async def on_close_callback(client, callback_query: CallbackQuery):
    await callback_query.message.delete()

async def get_user_name(user_id: int) -> str:
    try:
        user = await app.get_users(user_id)
        if user.first_name:
            return user.first_name
        elif user.username:
            return f"@{user.username}"
        else:
            return None
    except Exception:
        return None

async def get_chat_name(chat_id: int) -> str:
    try:
        chat = await app.get_chat(chat_id)
        return chat.title or "Unknown Group"
    except Exception:
        return f"ID: {chat_id}"

def extract_entity_id(result: dict, stat_type: str, is_group: bool) -> int:
    """Безопасно извлекает ID сущности из результата запроса"""
    try:
        if stat_type == "warnings":
            # Дл�� агрегации warnings всегда используется _id
            return result["_id"]
        else:
            # Для vulgar статистики
            if is_group:
                return result.get("chat_id", result.get("_id", 0))
            else:
                return result.get("user_id", result.get("_id", 0))
    except (KeyError, TypeError):
        return 0

async def send_top_list(message: Message, view="users", period="today", stat_type="warnings", cb: CallbackQuery = None):
    is_group = view == "groups"
    current_chat_id = message.chat.id

    # Get group language
    lang_code = await get_group_language(current_chat_id)
    lang = load_language(lang_code)

    try:
        if stat_type == "warnings":
            # Статистика предупреждений
            if period == "all":
                if is_group:
                    pipeline = [
                        {"$group": {
                            "_id": "$chat_id",
                            "total_warnings": {"$sum": "$count"}
                        }},
                        {"$sort": {"total_warnings": -1}},
                        {"$limit": 10}
                    ]
                    results = await db.warnings.aggregate(pipeline).to_list(length=10)
                else:
                    pipeline = [
                        {"$match": {"chat_id": current_chat_id}},
                        {"$group": {
                            "_id": "$user_id", 
                            "total_warnings": {"$sum": "$count"}
                        }},
                        {"$sort": {"total_warnings": -1}},
                        {"$limit": 10}
                    ]
                    results = await db.warnings.aggregate(pipeline).to_list(length=10)
            else:
                filter_query = get_period_filter(period)
                if is_group:
                    pipeline = [
                        {"$match": filter_query},
                        {"$group": {
                            "_id": "$chat_id",
                            "total_warnings": {"$sum": "$count"}
                        }},
                        {"$sort": {"total_warnings": -1}},
                        {"$limit": 10}
                    ]
                    results = await db.warnings.aggregate(pipeline).to_list(length=10)
                else:
                    filter_query["chat_id"] = current_chat_id
                    pipeline = [
                        {"$match": filter_query},
                        {"$group": {
                            "_id": "$user_id",
                            "total_warnings": {"$sum": "$count"}
                        }},
                        {"$sort": {"total_warnings": -1}},
                        {"$limit": 10}
                    ]
                    results = await db.warnings.aggregate(pipeline).to_list(length=10)

            title = lang.get("topbad_warnings_title")
            unit = lang.get("topbad_warning_unit")
            key = "total_warnings"
        
        else:  # vulgar words statistics
            collection = db.bad_word_stats
            
            if period == "all":
                if is_group:
                    pipeline = [
                        {"$group": {
                            "_id": "$chat_id",
                            "total_vulgar": {"$sum": "$count"}
                        }},
                        {"$sort": {"total_vulgar": -1}},
                        {"$limit": 10}
                    ]
                    results = await collection.aggregate(pipeline).to_list(length=10)
                else:
                    pipeline = [
                        {"$match": {"chat_id": current_chat_id}},
                        {"$group": {
                            "_id": "$user_id",
                            "total_vulgar": {"$sum": "$count"}
                        }},
                        {"$sort": {"total_vulgar": -1}},
                        {"$limit": 10}
                    ]
                    results = await collection.aggregate(pipeline).to_list(length=10)
            else:
                period_filter = {}
                if PERIODS[period]:
                    since = datetime.utcnow() - PERIODS[period]
                    period_filter = {"last_used": {"$gte": since}}
                
                if is_group:
                    pipeline = [
                        {"$match": period_filter},
                        {"$group": {
                            "_id": "$chat_id",
                            "total_vulgar": {"$sum": "$count"}
                        }},
                        {"$sort": {"total_vulgar": -1}},
                        {"$limit": 10}
                    ]
                    results = await collection.aggregate(pipeline).to_list(length=10)
                else:
                    period_filter["chat_id"] = current_chat_id
                    pipeline = [
                        {"$match": period_filter},
                        {"$group": {
                            "_id": "$user_id",
                            "total_vulgar": {"$sum": "$count"}
                        }},
                        {"$sort": {"total_vulgar": -1}},
                        {"$limit": 10}
                    ]
                    results = await collection.aggregate(pipeline).to_list(length=10)

            title = lang.get("topbad_vulgar_title")
            unit = lang.get("topbad_vulgar_unit")
            key = "total_vulgar"

        period_text = {
            "today": lang.get("topbad_period_today"),
            "week": lang.get("topbad_period_week"), 
            "month": lang.get("topbad_period_month"),
            "all": lang.get("topbad_period_all")
        }[period]

        text = f"{title} ({period_text})\n\n"

        display_count = 0
        for i, res in enumerate(results, start=1):
            entity_id = extract_entity_id(res, stat_type, is_group)
            
            if entity_id == 0:
                continue  # Пропускаем записи с некорректным ID
                
            if is_group:
                name = await get_chat_name(entity_id)
            else:
                name = await get_user_name(entity_id)
                if name is None:
                    continue

            display_count += 1
            count = res.get(key, 0)
            text += f"{display_count}. {name} — <code>{count} {unit}</code>\n"

        if not results or display_count == 0:
            text += lang.get("topbad_empty")

        if cb:
            try:
                await cb.message.edit_text(text, reply_markup=build_keyboard(view, period, stat_type, lang))
            except MessageNotModified:
                pass  # Игнорируем ошибку если контент не изменился
            except Exception as e:
                print(f"[DEBUG] Error editing message: {e}")
            await cb.answer()
        else:
            await message.reply(text, reply_markup=build_keyboard(view, period, stat_type, lang))
            
    except Exception as e:
        error_text = lang.get("topbad_error")
        print(f"[DEBUG] Error in send_top_list: {e}")
        
        if cb:
            try:
                await cb.message.edit_text(error_text, reply_markup=build_keyboard(view, period, stat_type, lang))
            except:
                pass
            await cb.answer(lang.get("topbad_error_callback"))
        else:
            await message.reply(error_text, reply_markup=build_keyboard(view, period, stat_type, lang))

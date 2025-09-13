from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from config import app, groups_collection, scheduler
from datetime import datetime, timedelta
import asyncio
from language import get_language_for_message, load_language
from helpers.activity import get_activity_data, get_top_active_users, track_message_for_reports, track_member_activity
from language import is_user_admin


# Настройки отчетов
REPORT_SETTINGS = {
    "daily_time": "09:00",
    "weekly_time": "18:00", 
    "monthly_time": "12:00",
    "yearly_time": "00:00",
    "enabled_groups": set()
}


@app.on_message(filters.command("news"))
async def news_command(client: Client, message: Message):
    """Команда для управления автоматическими отчетами"""
    lang_code = await get_language_for_message(message)
    lang = load_language(lang_code)
    
    # Проверяем, что это группа
    if message.chat.type == "private":
        await message.reply("Bu əmr yalnız qruplarda işləyir.")
        return
    
    # Проверяем права администратора
    if not await is_user_admin(client, message.chat.id, message.from_user.id):
        await message.reply(lang.get("report_admin_only", "This command can only be used by administrators"))
        return
    
    # Обрабатываем параметры команды
    parts = message.text.split()
    if len(parts) == 1:
        # Показать текущий статус
        is_enabled = message.chat.id in REPORT_SETTINGS["enabled_groups"]
        status_text = lang.get("news_enabled", "enabled") if is_enabled else lang.get("news_disabled", "disabled")
        
        text = f"📊 <b>{lang.get('news_title', 'Activity Report')}</b>\n\n"
        text += f"<b>{lang.get('news_status', 'Status')}:</b> {status_text}\n\n"
        text += "<b>İstifadə:</b>\n"
        text += "• `/news on` - aktiv et\n"
        text += "• `/news off` - deaktiv et\n"
        text += "• `/news` - statusu göstər"
        
        await message.reply(text)
        
    elif len(parts) == 2:
        action = parts[1].lower()
        
        if action == "on":
            REPORT_SETTINGS["enabled_groups"].add(message.chat.id)
            await message.reply(f"✅ {lang.get('report_enabled_success', 'Automatic reports enabled')}")
            
        elif action == "off":
            REPORT_SETTINGS["enabled_groups"].discard(message.chat.id)
            await message.reply(f"✅ {lang.get('report_disabled_success', 'Automatic reports disabled')}")
            
        else:
            await message.reply("Yanlış parametr. İstifadə: `/news on` və ya `/news off`")


@app.on_callback_query(filters.regex("^report_top_active$"))
async def show_top_active_users(client: Client, callback_query: CallbackQuery):
    """Показать топ активных пользователей"""
    lang_code = await get_language_for_message(callback_query.message)
    lang = load_language(lang_code)
    
    # Получаем данные активности
    chat_id = callback_query.message.chat.id
    end_date = datetime.now()
    start_date = end_date - timedelta(days=7)  # За неделю
    
    top_users = await get_top_active_users(chat_id, start_date, end_date, limit=10)
    
    if not top_users:
        text = f"👑 <b>{lang.get('report_top_active_title', 'Top-10 Most Active Users')}</b>\n\n"
        text += lang.get("report_no_data", "No data available")
    else:
        text = f"👑 <b>{lang.get('report_top_active_title', 'Top-10 Most Active Users')}</b>\n\n"
        
        for i, user in enumerate(top_users, 1):
            username = user.get("username", "Unknown")
            messages_count = user.get("messages_count", 0)
            percentage = user.get("percentage", 0)
            
            text += f"{i}. @{username} - {messages_count} {lang.get('report_messages_count', 'messages')} ({percentage:.1f}%)\n"
    
    keyboard = [[InlineKeyboardButton(
        lang.get("report_back", "Back to Report"), 
        callback_data="report_main"
    )]]
    
    await callback_query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))


@app.on_callback_query(filters.regex("^report_time_analysis$"))
async def show_time_analysis(client: Client, callback_query: CallbackQuery):
    """Показать анализ времени активности"""
    lang_code = await get_language_for_message(callback_query.message)
    lang = load_language(lang_code)
    
    chat_id = callback_query.message.chat.id
    end_date = datetime.now()
    start_date = end_date - timedelta(days=7)
    
    # Получаем данные по времени (симуляция)
    peak_hour = "20:00-21:00"
    most_active_day = "Friday"
    
    # Данные по дням недели (симуляция)
    days_data = {
        "Monday": 80,
        "Tuesday": 100,
        "Wednesday": 70,
        "Thursday": 85,
        "Friday": 120,
        "Saturday": 60,
        "Sunday": 90
    }
    
    text = f"⏰ <b>{lang.get('report_time_analysis', 'Time Analysis')}</b>\n\n"
    
    text += f"<b>{lang.get('report_by_days', 'By Days')}:</b>\n"
    for day, activity in days_data.items():
        bar_length = int(activity / 10)
        bar = "█" * bar_length + "░" * (12 - bar_length)
        day_name = lang.get(f"day_{day.lower()}", day)
        text += f"{day_name}: {bar} {activity}%\n"
    
    text += f"\n<b>{lang.get('report_peak_hour', 'Peak Hour')}:</b> {peak_hour}\n"
    text += f"<b>{lang.get('report_most_active_day_name', 'Most Active Day')}:</b> {most_active_day}"
    
    keyboard = [[InlineKeyboardButton(
        lang.get("report_back", "Back to Report"), 
        callback_data="report_main"
    )]]
    
    await callback_query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))


@app.on_callback_query(filters.regex("^report_achievements$"))
async def show_achievements(client: Client, callback_query: CallbackQuery):
    """Показать все достижения"""
    lang_code = await get_language_for_message(callback_query.message)
    lang = load_language(lang_code)
    
    chat_id = callback_query.message.chat.id
    end_date = datetime.now()
    start_date = end_date - timedelta(days=7)
    
    # Получаем достижения (симуляция)
    achievements = {
        "most_helpful": {"user": "@helper_user", "value": "23 ответа на вопросы"},
        "most_funny": {"user": "@funny_user", "value": "156 реакций 😂"},
        "best_newcomer": {"user": "@new_user", "value": "67 сообщений за неделю"},
        "chatterbox": {"user": "@talkative_user", "value": "234 сообщения"}
    }
    
    text = f"🏆 <b>{lang.get('report_achievements_title', 'Weekly Achievements')}</b>\n\n"
    
    text += f"🎯 <b>{lang.get('report_most_helpful', 'Most Helpful')}:</b> {achievements['most_helpful']['user']}\n"
    text += f"   • {achievements['most_helpful']['value']}\n\n"
    
    text += f"😄 <b>{lang.get('report_most_funny', 'Most Funny')}:</b> {achievements['most_funny']['user']}\n"
    text += f"   • {achievements['most_funny']['value']}\n\n"
    
    text += f"👤 <b>{lang.get('report_best_newcomer', 'Best Newcomer')}:</b> {achievements['best_newcomer']['user']}\n"
    text += f"   • {achievements['best_newcomer']['value']}\n\n"
    
    text += f"💬 <b>{lang.get('report_chatterbox', 'Chatterbox')}:</b> {achievements['chatterbox']['user']}\n"
    text += f"   • {achievements['chatterbox']['value']}"
    
    keyboard = [[InlineKeyboardButton(
        lang.get("report_back", "Back to Report"), 
        callback_data="report_main"
    )]]
    
    await callback_query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))


@app.on_callback_query(filters.regex("^report_main$"))
async def show_main_report(client: Client, callback_query: CallbackQuery):
    """Показать основной отчет"""
    await generate_weekly_report(client, callback_query.message)


async def generate_weekly_report(client: Client, message: Message):
    """Генерация еженедельного отчета"""
    lang_code = await get_language_for_message(message)
    lang = load_language(lang_code)
    
    chat_id = message.chat.id
    end_date = datetime.now()
    start_date = end_date - timedelta(days=7)
    
    # Получаем данные активности (симуляция)
    total_messages = 1247
    active_participants = 89
    total_members = 156
    new_members = 5
    left_members = 2
    change_percent = 15
    
    # Форматируем даты
    start_str = start_date.strftime("%d.%m")
    end_str = end_date.strftime("%d.%m")
    
    # Основной текст отчета
    text = f"📊 **{lang.get('report_title', 'REPORT')} {lang.get('report_period_weekly', 'weekly').upper()}**\n"
    text += f"**{lang.get('report_from_to', '{start_date} - {end_date}').format(start_date=start_str, end_date=end_str)}**\n\n"
    
    text += f"📈 **{lang.get('report_activity', 'Activity')}:**\n"
    text += f"• {lang.get('report_messages', 'Messages')}: {total_messages:,} ({change_percent:+d}% {lang.get('report_change_percent', '{percent}% {direction}').format(percent=abs(change_percent), direction=lang.get('report_increase' if change_percent > 0 else 'report_decrease', 'change'))})\n"
    text += f"• {lang.get('report_participants', 'Participants')}: {active_participants} активных из {total_members}\n"
    text += f"• {lang.get('report_new_members', 'New Members')}: {new_members} | {lang.get('report_left_members', 'Left Members')}: {left_members}\n\n"
    
    text += f"⏰ **{lang.get('report_peak_time', 'Peak Time')}:**\n"
    text += f"Самый активный час: 20:00-21:00\n"
    text += f"{lang.get('report_most_active_day', 'Most Active Day')}: Пятница\n\n"
    
    text += f"🏆 **{lang.get('report_achievements', 'Achievements')} {lang.get('report_period_weekly', 'weekly')}:**\n"
    text += f"🎯 {lang.get('report_most_helpful', 'Most Helpful')}: @helper_user\n"
    text += f"😄 {lang.get('report_most_funny', 'Most Funny')}: @funny_user\n"
    text += f"👤 {lang.get('report_best_newcomer', 'Best Newcomer')}: @new_user"
    
    # Создаем клавиатуру
    keyboard = [
        [
            InlineKeyboardButton(
                f"👑 {lang.get('report_top_active', 'Top Active Users')}", 
                callback_data="report_top_active"
            ),
            InlineKeyboardButton(
                f"⏰ {lang.get('report_time_analysis', 'Time Analysis')}", 
                callback_data="report_time_analysis"
            )
        ],
        [
            InlineKeyboardButton(
                f"🏆 {lang.get('report_achievements_title', 'Weekly Achievements')}", 
                callback_data="report_achievements"
            )
        ]
    ]
    
    if isinstance(message, CallbackQuery):
        await message.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
    else:
        await message.reply(text, reply_markup=InlineKeyboardMarkup(keyboard))


# Автоматическая отправка отчетов
async def send_weekly_report(chat_id: int):
    """Отправка еженедельного отчета"""
    if chat_id not in REPORT_SETTINGS["enabled_groups"]:
        return
    
    try:
        # Получаем информацию о чате
        chat = await app.get_chat(chat_id)
        
        # Создаем сообщение для отчета
        class ReportMessage:
            def __init__(self, chat):
                self.chat = chat
        
        report_msg = ReportMessage(chat)
        
        # Генерируем отчет
        await generate_weekly_report(app, report_msg)
        
    except Exception as e:
        print(f"Ошибка отправки еженедельного отчета в чат {chat_id}: {e}")


# Планировщик отчетов
def setup_report_scheduler():
    """Настройка планировщика для автоматических отчетов"""
    # Еженедельные отчеты - каждое воскресенье в 18:00
    scheduler.add_job(
        send_all_weekly_reports,
        'cron',
        day_of_week=6,  # Воскресенье
        hour=18,
        minute=0,
        id='weekly_reports'
    )


async def send_all_weekly_reports():
    """Отправка еженедельных отчетов во все активные группы"""
    for chat_id in REPORT_SETTINGS["enabled_groups"]:
        await send_weekly_report(chat_id)

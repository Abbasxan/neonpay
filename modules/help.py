from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from language import get_user_language, get_group_language, get_language_for_message, load_language
from config import app, SUPPORT_CHAT, SUPPORT_CHANNEL, OWNER_ID

def get_help_main_menu(txt):
    """Создает главное меню помощи с кнопками модулей"""
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(txt.get('help_general_button', '🔰 Bütün əmrlər'), callback_data="help_general"),
            InlineKeyboardButton(txt.get('help_antivulgar_button', '🤬 AntiVulgar'), callback_data="help_antivulgar")
        ],
        [
            InlineKeyboardButton(txt.get('help_antispam_button', '🚫 AntiSpam'), callback_data="help_antispam"),
            InlineKeyboardButton(txt.get('help_antireklam_button', '🛡 AntiReklam'), callback_data="help_antireklam")
        ],
        [
            InlineKeyboardButton(txt.get('help_antiflood_button', '🌊 AntiFlood'), callback_data="help_antiflood"),
            InlineKeyboardButton(txt.get('help_warnings_title', '⚠️ Xəbərdarlıqlar'), callback_data="help_warnings")
        ],
        [
            InlineKeyboardButton(txt.get('help_captcha_title', '🤖 Captcha'), callback_data="help_captcha"),
            InlineKeyboardButton(txt.get('help_admin_button', '🔇 Mute/Admin'), callback_data="help_admin")
        ],
        [
            InlineKeyboardButton(txt.get('help_report_button', '📊 Hesabat'), callback_data="help_reports"),
            InlineKeyboardButton(txt.get('support_button', '🧑‍💻 Dəstək'), url=SUPPORT_CHAT)
        ],
        [
            InlineKeyboardButton(txt.get('other_bots_button', '📢 Kanal'), url=SUPPORT_CHANNEL),
            InlineKeyboardButton(txt.get('developer_button', '👨‍💻 Sahib'), url=f"tg://user?id={OWNER_ID}")
        ]
    ])

def get_back_button(txt):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(txt.get('help_back_button', '🔙 Geriyə'), callback_data="help_main")]
    ])

@app.on_message(filters.command("help") & (filters.private | filters.group), group=0)
async def help_command(client: Client, message: Message):
    if not message.from_user:
        return

    try:
        # Определяем язык в зависимости от типа чата
        if message.chat.type == "private":
            # Для приватных чатов используем язык пользователя
            lang_code = await get_user_language(message.from_user.id)
        else:
            # Для групп используем язык группы
            lang_code = await get_group_language(message.chat.id)
        
        print(f"[HELP COMMAND DEBUG] User ID: {message.from_user.id}, Chat ID: {message.chat.id}, Chat Type: {message.chat.type}, Language Code: {lang_code}")
        txt = load_language(lang_code)
        print(f"[HELP COMMAND DEBUG] Loaded language data keys: {list(txt.keys())[:10]}...")  # Показываем первые 10 ключей

        help_text = f"""
<b>🤖 {txt.get('bot_help_title')}</b>

<blockquote>{txt.get('help_main_description')}</blockquote>

<i>{txt.get('help_select_modules')}</i>
"""

        await message.reply(help_text.strip(), reply_markup=get_help_main_menu(txt))

    except Exception as e:
        print(f"[HELP COMMAND ERROR] {e}")
        # Fallback на случай ошибки - определяем язык по типу чата
        try:
            if message.chat.type == "private":
                fallback_lang_code = await get_user_language(message.from_user.id)
            else:
                fallback_lang_code = await get_group_language(message.chat.id)
            fallback_txt = load_language(fallback_lang_code)
            help_text = f"""
<b>🤖 {fallback_txt.get('bot_help_title')}</b>

<blockquote>{fallback_txt.get('help_main_description')}</blockquote>

<i>{fallback_txt.get('help_select_modules')}</i>
"""
            await message.reply(help_text.strip(), reply_markup=get_help_main_menu(fallback_txt))
        except Exception as fallback_error:
            print(f"[HELP COMMAND FALLBACK ERROR] {fallback_error}")
            # Если и fallback не работает, отправляем базовое сообщение
            await message.reply("❌ Xəta baş verdi. Zəhmət olmasa yenidən cəhd edin.")

@app.on_callback_query(filters.regex(r"^help_"))
async def help_callback_handler(client: Client, callback_query: CallbackQuery):
    try:
        # Определяем язык в зависимости от типа чата
        chat = callback_query.message.chat
        if chat.type == "private":
            # Для приватных чатов используем язык пользователя
            lang_code = await get_user_language(callback_query.from_user.id)
        else:
            # Для групп используем язык группы
            lang_code = await get_group_language(chat.id)
        
        print(f"[HELP CALLBACK DEBUG] User ID: {callback_query.from_user.id}, Chat ID: {chat.id}, Chat Type: {chat.type}, Language Code: {lang_code}")
        txt = load_language(lang_code)
        print(f"[HELP CALLBACK DEBUG] Loaded language data keys: {list(txt.keys())[:10]}...")  # Показываем первые 10 ключей
        
        data = callback_query.data
        
        if data == "help_main":
            help_text = f"""
<b>🤖 {txt.get('bot_help_title')}</b>

<blockquote>{txt.get('help_main_description')}</blockquote>

<i>{txt.get('help_select_modules')}</i>
"""
            await callback_query.edit_message_text(help_text, reply_markup=get_help_main_menu(txt))
            
        elif data == "help_general":
            text = f"""
<b>🔰 {txt.get('help_general_commands')}</b>

<blockquote>
/start – {txt.get('help_general_start_desc')}
/help – {txt.get('help_general_help_desc')}
/lang – {txt.get('help_general_lang_desc')}
/id – {txt.get('help_general_id_desc')}
/info @user – {txt.get('help_general_info_desc')}
</blockquote>

<i>{txt.get('help_general_note')}</i>
"""
            await callback_query.edit_message_text(text, reply_markup=get_back_button(txt))
            
        elif data == "help_antivulgar":
            text = f"""
<b>🤬 {txt.get('help_antivulgar_title')}</b>

<blockquote>
/noarqo on|off – {txt.get('help_antivulgar_toggle')}
/noarqo 3 60 – {txt.get('help_antivulgar_limit')}
/noarqo status – {txt.get('help_antivulgar_status')}
</blockquote>

<b>{txt.get('help_antivulgar_features')}</b>
• {txt.get('help_antivulgar_feature1')}
• {txt.get('help_antivulgar_feature2')}
• {txt.get('help_antivulgar_feature3')}
• {txt.get('help_antivulgar_feature4')}

<i>{txt.get('help_antivulgar_note')}</i>
"""
            await callback_query.edit_message_text(text, reply_markup=get_back_button(txt))
            
        elif data == "help_antispam":
            text = f"""
<b>🚫 {txt.get('help_antispam_title')}</b>

<blockquote>
/antispam on|off – {txt.get('help_antispam_toggle')}
/antispam 3 60 – {txt.get('help_antispam_limit')}
/antispam – {txt.get('help_antispam_status')}
</blockquote>

<b>{txt.get('help_antispam_features')}</b>
• {txt.get('help_antispam_feature1')}
• {txt.get('help_antispam_feature2')}
• {txt.get('help_antispam_feature3')}
• {txt.get('help_antispam_feature4')}

<i>{txt.get('help_antispam_note')}</i>
"""
            await callback_query.edit_message_text(text, reply_markup=get_back_button(txt))
            
        elif data == "help_antireklam":
            text = f"""
<b>🛡 {txt.get('help_antireklam_title')}</b>

<blockquote>
/antireklam on|off – {txt.get('help_antireklam_toggle')}
/antireklam – {txt.get('help_antireklam_status')}
</blockquote>

<b>{txt.get('help_antireklam_features')}</b>
• {txt.get('help_antireklam_feature1')}
• {txt.get('help_antireklam_feature2')}
• {txt.get('help_antireklam_feature3')}
• {txt.get('help_antireklam_feature4')}
• {txt.get('help_antireklam_feature5')}

<i>{txt.get('help_antireklam_note')}</i>
"""
            await callback_query.edit_message_text(text, reply_markup=get_back_button(txt))
            
        elif data == "help_antiflood":
            text = f"""
<b>🌊 {txt.get('help_antiflood_title')}</b>

<blockquote>
/antiflood on|off – {txt.get('help_antiflood_toggle')}
/antiflood 5 10 – {txt.get('help_antiflood_settings')}
/antiflood action delete|warn|mute – {txt.get('help_antiflood_action_type')}
/antiflood – {txt.get('help_antiflood_status')}
</blockquote>

<b>{txt.get('help_antiflood_actions')}</b>
• {txt.get('help_antiflood_action1')}
• {txt.get('help_antiflood_action2')}
• {txt.get('help_antiflood_action3')}

<i>{txt.get('help_antiflood_note')}</i>
"""
            await callback_query.edit_message_text(text, reply_markup=get_back_button(txt))
            
        elif data == "help_warnings":
            text = f"""
<b>⚠️ {txt.get('help_warnings_title')}</b>

<blockquote>
/rapor @user səbəb – {txt.get('help_warning_complain')}
/resetwarn – {txt.get('help_warning_resetwarn')}
/resetall – {txt.get('help_warning_resetall')}
</blockquote>

<b>{txt.get('help_warnings_features')}</b>
• {txt.get('help_warnings_feature1')}
• {txt.get('help_warnings_feature2')}
• {txt.get('help_warnings_feature3')}
• {txt.get('help_warnings_feature4')}

<i>{txt.get('help_warnings_note')}</i>
"""
            await callback_query.edit_message_text(text, reply_markup=get_back_button(txt))
            
        elif data == "help_reports":
            text = f"""
<b>📊 {txt.get('help_reports_title')}</b>

<blockquote>
/reports – {txt.get('help_reports_group_stats')}
/userreport @user – {txt.get('help_reports_user_report')}
</blockquote>

<b>{txt.get('help_reports_stats')}</b>
• {txt.get('help_reports_stat1')}
• {txt.get('help_reports_stat2')}
• {txt.get('help_reports_stat3')}
• {txt.get('help_reports_stat4')}
• {txt.get('help_reports_stat5')}

<i>{txt.get('help_reports_note')}</i>
"""
            await callback_query.edit_message_text(text, reply_markup=get_back_button(txt))
            
        elif data == "help_admin":
            text = f"""
<b>🔇 {txt.get('help_admin_title')}</b>

<blockquote>
{txt.get('help_mute_note')}
</blockquote>

<b>{txt.get('help_admin_commands')}</b>
• {txt.get('help_admin_command1')}
• {txt.get('help_admin_command2')}
• {txt.get('help_admin_command3')}
• {txt.get('help_admin_command4')}
• {txt.get('help_admin_command5')}

<i>{txt.get('help_admin_note2')}</i>
"""
            await callback_query.edit_message_text(text, reply_markup=get_back_button(txt))
            
        elif data == "help_captcha":
            text = f"""
<b>🤖 {txt.get('help_captcha_title')}</b>

<blockquote>
/captcha on|off – {txt.get('help_captcha_toggle')}
/captcha timeout 300 – {txt.get('help_captcha_timeout')}
/captcha – {txt.get('help_captcha_status')}
</blockquote>

<b>{txt.get('help_captcha_features')}</b>
• {txt.get('help_captcha_feature1')}
• {txt.get('help_captcha_feature2')}
• {txt.get('help_captcha_feature3')}
• {txt.get('help_captcha_feature4')}
• {txt.get('help_captcha_feature5')}
• {txt.get('help_captcha_feature6')}

<b>{txt.get('help_captcha_types')}</b>
• {txt.get('help_captcha_type1')}
• {txt.get('help_captcha_type2')}
• {txt.get('help_captcha_type3')}

<i>{txt.get('help_captcha_note')}</i>
"""
            await callback_query.edit_message_text(text, reply_markup=get_back_button(txt))
            
        await callback_query.answer()
        
    except Exception as e:
        print(f"[HELP CALLBACK ERROR] {e}")
        try:
            # Определяем язык в зависимости от типа чата для fallback
            chat = callback_query.message.chat
            if chat.type == "private":
                lang_code = await get_user_language(callback_query.from_user.id)
            else:
                lang_code = await get_group_language(chat.id)
            txt = load_language(lang_code)
            await callback_query.answer(txt.get('help_error'), show_alert=True)
        except:
            await callback_query.answer("Xəta baş verdi!", show_alert=True)
    

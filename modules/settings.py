import logging
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from pyrogram.enums import ChatMemberStatus
from config import app, db
from language import load_language, get_group_language, get_user_language

logger = logging.getLogger(__name__)

def create_main_settings_keyboard(lang):
    """Создает главную клавиатуру настроек"""
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(f"🛡 {lang.get('antispam_title', 'AntiSpam')}", callback_data="settings_antispam"),
            InlineKeyboardButton(f"🚫 {lang.get('antireklam_title', 'AntiReklam')}", callback_data="settings_antireklam")
        ],
        [
            InlineKeyboardButton(f"🤬 {lang.get('antivulgar_title', 'AntiVulgar')}", callback_data="settings_antivulgar"),
            InlineKeyboardButton(f"🌊 {lang.get('antiflood_title', 'AntiFlood')}", callback_data="settings_antiflood")
        ],
        [
            InlineKeyboardButton(f"🤖 {lang.get('antispammer_title', 'AntiSpammer')}", callback_data="settings_antispammer"),
            InlineKeyboardButton(f"🔐 {lang.get('captcha_title', 'Captcha')}", callback_data="settings_captcha")
        ],
        [
            InlineKeyboardButton(f"📊 {lang.get('view_all_status', 'Bütün statuslar')}", callback_data="settings_status_all")
        ]
    ])

def create_module_keyboard(module_name, is_enabled, lang):
    """Создает клавиатуру для конкретного модуля"""
    status_text = lang.get('enabled', 'Aktiv') if is_enabled else lang.get('disabled', 'Deaktiv')
    toggle_text = lang.get('disable', 'Deaktiv et') if is_enabled else lang.get('enable', 'Aktiv et')
    
    keyboard = [
        [InlineKeyboardButton(f"📊 Status: {status_text}", callback_data=f"settings_{module_name}_status")],
        [InlineKeyboardButton(f"🔄 {toggle_text}", callback_data=f"settings_{module_name}_toggle")],
        [InlineKeyboardButton(f"⚙️ {lang.get('configure', 'Tənzimlə')}", callback_data=f"settings_{module_name}_config")],
        [InlineKeyboardButton(f"◀️ {lang.get('back', 'Geri')}", callback_data="settings_main")]
    ]
    
    return InlineKeyboardMarkup(keyboard)

def create_config_keyboard(module_name, lang):
    """Создает клавиатуру для настройки конкретного модуля"""
    keyboards = {
        "antispam": [
            [InlineKeyboardButton("📊 Limit: 5 mesaj", callback_data=f"config_{module_name}_limit")],
            [InlineKeyboardButton("⏱ Vaxt: 60 saniyə", callback_data=f"config_{module_name}_time")],
            [InlineKeyboardButton("◀️ Geri", callback_data=f"settings_{module_name}")]
        ],
        "antiflood": [
            [InlineKeyboardButton("📊 Limit: 10 mesaj", callback_data=f"config_{module_name}_limit")],
            [InlineKeyboardButton("⏱ Vaxt: 10 saniyə", callback_data=f"config_{module_name}_time")],
            [InlineKeyboardButton("⚡ Hərəkət: Sil", callback_data=f"config_{module_name}_action")],
            [InlineKeyboardButton("◀️ Geri", callback_data=f"settings_{module_name}")]
        ],
        "antivulgar": [
            [InlineKeyboardButton("📊 Limit: 3 xəbərdarlıq", callback_data=f"config_{module_name}_limit")],
            [InlineKeyboardButton("⏱ Vaxt: 60 saniyə", callback_data=f"config_{module_name}_time")],
            [InlineKeyboardButton("🔇 Mute rejimi: OFF", callback_data=f"config_{module_name}_mute")],
            [InlineKeyboardButton("◀️ Geri", callback_data=f"settings_{module_name}")]
        ],
        "antireklam": [
            [InlineKeyboardButton("🤖 Userbot: Aktiv", callback_data=f"config_{module_name}_userbot")],
            [InlineKeyboardButton("◀️ Geri", callback_data=f"settings_{module_name}")]
        ],
        "captcha": [
            [InlineKeyboardButton("⏰ Vaxt limiti: 300 saniyə", callback_data=f"config_{module_name}_timeout")],
            [InlineKeyboardButton("◀️ Geri", callback_data=f"settings_{module_name}")]
        ]
    }
    
    return InlineKeyboardMarkup(keyboards.get(module_name, [[InlineKeyboardButton("◀️ Geri", callback_data=f"settings_{module_name}")]]))

async def get_module_status(chat_id, module_name):
    """Получает статус модуля из базы данных"""
    group_data = await db.groups.find_one({"_id": chat_id}) or {}
    
    status_map = {
        "antispam": group_data.get("antispam_enabled", True),
        "antireklam": group_data.get("antireklam_enabled", True),
        "antivulgar": group_data.get("antivulgar_enabled", True),
        "antiflood": group_data.get("antiflood_enabled", False),
        "antispammer": True,  # antispammer всегда активен
        "captcha": group_data.get("captcha_enabled", False)
    }
    
    return status_map.get(module_name, False)

async def toggle_module_status(chat_id, module_name):
    """Переключает статус модуля"""
    current_status = await get_module_status(chat_id, module_name)
    new_status = not current_status
    
    field_map = {
        "antispam": "antispam_enabled",
        "antireklam": "antireklam_enabled", 
        "antivulgar": "antivulgar_enabled",
        "antiflood": "antiflood_enabled",
        "captcha": "captcha_enabled"
    }
    
    if module_name in field_map:
        await db.groups.update_one(
            {"_id": chat_id},
            {"$set": {field_map[module_name]: new_status}},
            upsert=True
        )
        
        # Специальная логика для antireklam
        if module_name == "antireklam" and new_status:
            from modules.antireklam import invite_userbot_to_group
            from config import userbot
            if userbot and userbot.is_connected:
                await invite_userbot_to_group(chat_id)
    
    return new_status

async def get_module_config(chat_id, module_name):
    """Получает конфигурацию модуля"""
    group_data = await db.groups.find_one({"_id": chat_id}) or {}
    
    configs = {
        "antispam": {
            "limit": group_data.get("antispam_limit", 5),
            "time": group_data.get("antispam_time", 60)
        },
        "antiflood": {
            "limit": group_data.get("antiflood_limit", 10),
            "time": group_data.get("antiflood_time", 10),
            "action": group_data.get("antiflood_action", "delete")
        },
        "antivulgar": {
            "limit": group_data.get("antivulgar_limit", 3),
            "time": group_data.get("antivulgar_time", 60),
            "mute": group_data.get("antivulgar_mute", False)
        },
        "antireklam": {
            "userbot": group_data.get("antireklam_userbot", True)
        },
        "captcha": {
            "timeout": group_data.get("captcha_timeout", 300)
        }
    }
    
    return configs.get(module_name, {})

async def update_module_config(chat_id, module_name, config_key, new_value):
    """Обновляет конфигурацию модуля"""
    field_name = f"{module_name}_{config_key}"
    await db.groups.update_one(
        {"_id": chat_id},
        {"$set": {field_name: new_value}},
        upsert=True
    )

@app.on_message(filters.command("settings") & filters.group, group=-1)
async def settings_command(client: Client, message: Message):
    """Главная команда настроек"""
    if not message.from_user:
        return
    
    chat_id = message.chat.id
    user_id = message.from_user.id
    
    # Проверяем права администратора
    try:
        member = await app.get_chat_member(chat_id, user_id)
        is_admin = member.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]
    except Exception:
        return await message.reply("Admin statusunu yoxlaya bilmədim.")
    
    if not is_admin:
        return await message.reply("Bu əmri yalnız adminlər istifadə edə bilər.")
    
    lang_code = await get_group_language(chat_id)
    lang = load_language(lang_code)
    
    text = f"<blockquote>⚙️ <b>{lang.get('settings_title', 'Qrup Tənzimləmələri')}</b>\n\n" \
           f"{lang.get('settings_description', 'Aşağıdakı düymələrdən istifadə edərək modulları idarə edin:')}</blockquote>"
    
    keyboard = create_main_settings_keyboard(lang)
    
    await message.reply(text, reply_markup=keyboard)

@app.on_callback_query(filters.regex(r"^settings_"))
async def settings_callback(client: Client, callback_query: CallbackQuery):
    """Обработчик callback запросов для настроек"""
    if not callback_query.from_user:
        return
    
    chat_id = callback_query.message.chat.id
    user_id = callback_query.from_user.id
    data = callback_query.data
    
    # Проверяем права администратора
    try:
        member = await app.get_chat_member(chat_id, user_id)
        is_admin = member.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]
    except Exception:
        return await callback_query.answer("Admin statusunu yoxlaya bilmədim.", show_alert=True)
    
    if not is_admin:
        return await callback_query.answer("Bu funksiya yalnız adminlər üçündür.", show_alert=True)
    
    lang_code = await get_group_language(chat_id)
    lang = load_language(lang_code)
    
    try:
        if data == "settings_main":
            # Возврат к главному меню
            text = f"<blockquote>⚙️ <b>{lang.get('settings_title', 'Qrup Tənzimləmələri')}</b>\n\n" \
                   f"{lang.get('settings_description', 'Aşağıdakı düymələrdən istifadə edərək modulları idarə edin:')}</blockquote>"
            keyboard = create_main_settings_keyboard(lang)
            
            await callback_query.edit_message_text(text, reply_markup=keyboard)
        
        elif data == "settings_status_all":
            # Показать статус всех модулей
            group_data = await db.groups.find_one({"_id": chat_id}) or {}
            
            antispam_status = "✅" if group_data.get("antispam_enabled", True) else "❌"
            antireklam_status = "✅" if group_data.get("antireklam_enabled", True) else "❌"
            antivulgar_status = "✅" if group_data.get("antivulgar_enabled", True) else "❌"
            antiflood_status = "✅" if group_data.get("antiflood_enabled", False) else "❌"
            captcha_status = "✅" if group_data.get("captcha_enabled", False) else "❌"
            
            text = f"<blockquote>📊 <b>{lang.get('all_modules_status', 'Bütün Modulların Statusu')}</b>\n\n" \
                   f"🛡 AntiSpam: {antispam_status}\n" \
                   f"🚫 AntiReklam: {antireklam_status}\n" \
                   f"🤬 AntiVulgar: {antivulgar_status}\n" \
                   f"🌊 AntiFlood: {antiflood_status}\n" \
                   f"🔐 Captcha: {captcha_status}\n" \
                   f"🤖 AntiSpammer: ✅ ({lang.get('antispammer_always_active', 'həmişə aktiv')})</blockquote>"
            
            keyboard = InlineKeyboardMarkup([[
                InlineKeyboardButton(f"◀️ {lang.get('back', 'Geri')}", callback_data="settings_main")
            ]])
            
            await callback_query.edit_message_text(text, reply_markup=keyboard)
        
        elif data.startswith("settings_") and not data.endswith(("_toggle", "_status", "_config")):
            # Показать настройки конкретного модуля
            module_name = data.replace("settings_", "")
            is_enabled = await get_module_status(chat_id, module_name)
            
            module_titles = {
                "antispam": "🛡 AntiSpam",
                "antireklam": "🚫 AntiReklam", 
                "antivulgar": "🤬 AntiVulgar",
                "antiflood": "🌊 AntiFlood",
                "antispammer": "🤖 AntiSpammer",
                "captcha": "🔐 Captcha"
            }
            
            title = module_titles.get(module_name, module_name.title())
            status_text = lang.get('enabled', 'Aktiv') if is_enabled else lang.get('disabled', 'Deaktiv')
            
            text = f"<blockquote>⚙️ <b>{title} {lang.get('module_settings_title', 'Tənzimləmələri')}</b>\n\n" \
                   f"📊 Status: {status_text}\n\n" \
                   f"{lang.get('module_description_' + module_name, 'Bu modul qrupunuzu qoruyur.')}</blockquote>"
            
            keyboard = create_module_keyboard(module_name, is_enabled, lang)
            
            await callback_query.edit_message_text(text, reply_markup=keyboard)
        
        elif data.endswith("_toggle"):
            # Переключить статус модуля
            module_name = data.replace("settings_", "").replace("_toggle", "")
            
            if module_name == "antispammer":
                await callback_query.answer("AntiSpammer həmişə aktivdir və deaktiv edilə bilməz.", show_alert=True)
                return
            
            new_status = await toggle_module_status(chat_id, module_name)
            status_text = lang.get('enabled', 'Aktiv') if new_status else lang.get('disabled', 'Deaktiv')
            
            await callback_query.answer(f"✅ {module_name.title()} {status_text.lower()} edildi!")
            
            # Обновляем сообщение
            module_titles = {
                "antispam": "🛡 AntiSpam",
                "antireklam": "🚫 AntiReklam",
                "antivulgar": "🤬 AntiVulgar", 
                "antiflood": "🌊 AntiFlood",
                "captcha": "🔐 Captcha"
            }
            
            title = module_titles.get(module_name, module_name.title())
            
            text = f"<blockquote>⚙️ <b>{title} {lang.get('module_settings_title', 'Tənzimləmələri')}</b>\n\n" \
                   f"📊 Status: {status_text}\n\n" \
                   f"{lang.get('module_description_' + module_name, 'Bu modul qrupunuzu qoruyur.')}</blockquote>"
            
            keyboard = create_module_keyboard(module_name, new_status, lang)
            
            await callback_query.edit_message_text(text, reply_markup=keyboard)
        
        elif data.endswith("_config"):
            module_name = data.replace("settings_", "").replace("_config", "")
            
            if module_name == "antispammer":
                text = f"<blockquote>⚙️ <b>AntiSpammer {lang.get('module_settings_title', 'Tənzimləmələri')}</b>\n\n" \
                       f"🤖 {lang.get('antispammer_auto_works', 'AntiSpammer avtomatik işləyir və əlavə tənzimləmə tələb etmir.')}\n" \
                       f"{lang.get('antispammer_detects', 'Bu modul spam botları və şübhəli hesabları avtomatik aşkar edir.')}</blockquote>"
                
                keyboard = InlineKeyboardMarkup([[
                    InlineKeyboardButton(f"◀️ Geri", callback_data=f"settings_{module_name}")
                ]])
            else:
                config = await get_module_config(chat_id, module_name)
                
                config_texts = {
                    "antispam": f"📊 {lang.get('config_limit', 'Limit')}: {config.get('limit', 5)} {lang.get('config_messages', 'mesaj')}\n⏱ {lang.get('config_time', 'Vaxt')}: {config.get('time', 60)} {lang.get('config_seconds', 'saniyə')}",
                    "antiflood": f"📊 {lang.get('config_limit', 'Limit')}: {config.get('limit', 10)} {lang.get('config_messages', 'mesaj')}\n⏱ {lang.get('config_time', 'Vaxt')}: {config.get('time', 10)} {lang.get('config_seconds', 'saniyə')}\n⚡ {lang.get('config_action', 'Hərəkət')}: {config.get('action', 'delete').title()}",
                    "antivulgar": f"📊 {lang.get('config_limit', 'Limit')}: {config.get('limit', 3)} {lang.get('config_warnings', 'xəbərdarlıq')}\n⏱ {lang.get('config_time', 'Vaxt')}: {config.get('time', 60)} {lang.get('config_seconds', 'saniyə')}\n🔇 {lang.get('config_mute', 'Mute')}: {lang.get('enabled', 'Aktiv') if config.get('mute', False) else lang.get('disabled', 'Deaktiv')}",
                    "antireklam": f"🤖 {lang.get('config_works_with_userbot', 'Userbot ilə işləyir')}\n🔗 {lang.get('config_auto_deletes_ads', 'Reklam linklərini avtomatik silir')}",
                    "captcha": f"⏰ {lang.get('config_timeout', 'Vaxt limiti')}: {config.get('timeout', 300)} {lang.get('config_seconds', 'saniyə')}\n🔐 {lang.get('config_math_problem', 'Yeni üzvlər üçün riyazi məsələ')}"
                }

                text = f"<blockquote>⚙️ <b>{module_name.title()} {lang.get('module_settings_title', 'Tənzimləmələri')}</b>\n\n" \
                       f"{config_texts.get(module_name, lang.get('config_not_available', 'Tənzimləmə mövcud deyil'))}\n\n" \
                       f"{lang.get('configure_with_buttons', 'Aşağıdakı düymələrlə tənzimləyin:')}</blockquote>"
                
                keyboard = create_config_keyboard(module_name, lang)
            
            await callback_query.edit_message_text(text, reply_markup=keyboard)
        
        await callback_query.answer()
        
    except Exception as e:
        logger.error(f"Settings callback error: {e}")
        await callback_query.answer("Xəta baş verdi!", show_alert=True)

@app.on_callback_query(filters.regex(r"^config_"))
async def config_callback(client: Client, callback_query: CallbackQuery):
    """Обработчик настройки параметров модулей"""
    if not callback_query.from_user:
        return
    
    chat_id = callback_query.message.chat.id
    user_id = callback_query.from_user.id
    data = callback_query.data
    
    # Проверяем права администратора
    try:
        member = await app.get_chat_member(chat_id, user_id)
        is_admin = member.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]
    except Exception:
        return await callback_query.answer("Admin statusunu yoxlaya bilmədim.", show_alert=True)
    
    if not is_admin:
        return await callback_query.answer("Bu funksiya yalnız adminlər üçündür.", show_alert=True)
    
    # Определяем язык в зависимости от типа чата
    chat = callback_query.message.chat
    if chat.type == "private":
        # Для приватных чатов используем язык пользователя
        lang_code = await get_user_language(callback_query.from_user.id)
    else:
        # Для групп используем язык группы
        lang_code = await get_group_language(chat.id)
    lang = load_language(lang_code)
    
    try:
        parts = data.split("_")
        module_name = parts[1]
        config_type = parts[2]
        
        config = await get_module_config(chat_id, module_name)
        
        if config_type == "limit":
            # Циклическое изменение лимита
            current_limit = config.get('limit', 5)
            limits = [3, 5, 10, 15, 20] if module_name != "antiflood" else [5, 10, 15, 20, 25]
            
            try:
                current_index = limits.index(current_limit)
                new_limit = limits[(current_index + 1) % len(limits)]
            except ValueError:
                new_limit = limits[0]
            
            await update_module_config(chat_id, module_name, "limit", new_limit)
            await callback_query.answer(f"✅ Limit {new_limit} olaraq təyin edildi!")
            
        elif config_type == "time":
            # Циклическое изменение времени
            current_time = config.get('time', 60)
            times = [10, 30, 60, 120, 300]
            
            try:
                current_index = times.index(current_time)
                new_time = times[(current_index + 1) % len(times)]
            except ValueError:
                new_time = times[0]
            
            await update_module_config(chat_id, module_name, "time", new_time)
            await callback_query.answer(f"✅ Vaxt {new_time} saniyə olaraq təyin edildi!")
            
        elif config_type == "action" and module_name == "antiflood":
            # Циклическое изменение действия для antiflood
            current_action = config.get('action', 'delete')
            actions = ['delete', 'warn', 'mute']
            
            try:
                current_index = actions.index(current_action)
                new_action = actions[(current_index + 1) % len(actions)]
            except ValueError:
                new_action = actions[0]
            
            await update_module_config(chat_id, module_name, "action", new_action)
            await callback_query.answer(f"✅ Hərəkət {new_action} olaraq təyin edildi!")
            
        elif config_type == "mute" and module_name == "antivulgar":
            # Переключение режима мута
            current_mute = config.get('mute', False)
            new_mute = not current_mute
            
            await update_module_config(chat_id, module_name, "mute", new_mute)
            status = "aktiv" if new_mute else "deaktiv"
            await callback_query.answer(f"✅ Mute rejimi {status} edildi!")
        
        elif config_type == "timeout" and module_name == "captcha":
            # Циклическое изменение времени ожидания для captcha
            current_timeout = config.get('timeout', 300)
            timeouts = [60, 120, 300, 600]  # 1, 2, 5, 10 минут
            
            try:
                current_index = timeouts.index(current_timeout)
                new_timeout = timeouts[(current_index + 1) % len(timeouts)]
            except ValueError:
                new_timeout = timeouts[0]
            
            await update_module_config(chat_id, module_name, "timeout", new_timeout)
            await callback_query.answer(f"✅ Vaxt limiti {new_timeout} saniyə olaraq təyin edildi!")

        config = await get_module_config(chat_id, module_name)
        
        config_texts = {
            "antispam": f"📊 {lang.get('config_limit', 'Limit')}: {config.get('limit', 5)} {lang.get('config_messages', 'mesaj')}\n⏱ {lang.get('config_time', 'Vaxt')}: {config.get('time', 60)} {lang.get('config_seconds', 'saniyə')}",
            "antiflood": f"📊 {lang.get('config_limit', 'Limit')}: {config.get('limit', 10)} {lang.get('config_messages', 'mesaj')}\n⏱ {lang.get('config_time', 'Vaxt')}: {config.get('time', 10)} {lang.get('config_seconds', 'saniyə')}\n⚡ {lang.get('config_action', 'Hərəkət')}: {config.get('action', 'delete').title()}",
            "antivulgar": f"📊 {lang.get('config_limit', 'Limit')}: {config.get('limit', 3)} {lang.get('config_warnings', 'xəbərdarlıq')}\n⏱ {lang.get('config_time', 'Vaxt')}: {config.get('time', 60)} {lang.get('config_seconds', 'saniyə')}\n🔇 {lang.get('config_mute', 'Mute')}: {lang.get('enabled', 'Aktiv') if config.get('mute', False) else lang.get('disabled', 'Deaktiv')}",
            "captcha": f"⏰ {lang.get('config_timeout', 'Vaxt limiti')}: {config.get('timeout', 300)} {lang.get('config_seconds', 'saniyə')}\n🔐 {lang.get('config_math_problem', 'Yeni üzvlər üçün riyazi məsələ')}"
        }

        text = f"<blockquote>⚙️ <b>{module_name.title()} {lang.get('module_settings_title', 'Tənzimləmələri')}</b>\n\n" \
               f"{config_texts.get(module_name, lang.get('config_not_available', 'Tənzimləmə mövcud deyil'))}\n\n" \
               f"{lang.get('configure_with_buttons', 'Aşağıdakı düymələrlə tənzimləyin:')}</blockquote>"
        
        keyboard = create_config_keyboard(module_name, {})
        
        await callback_query.edit_message_text(text, reply_markup=keyboard)
        
    except Exception as e:
        logger.error(f"Config callback error: {e}")
        await callback_query.answer("Xəta baş verdi!", show_alert=True)

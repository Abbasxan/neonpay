from pyrogram import Client, filters
from pyrogram.types import Message
from config import app, userbot, OWNER_ID
from language import get_language_for_message, load_language
import logging

@app.on_message(filters.command("reload") & filters.user(OWNER_ID))
async def reload_command(client: Client, message: Message):
    """Команда для перезагрузки фильтров и проверки прав"""
    lang_code = await get_language_for_message(message)
    lang = load_language(lang_code)
    
    try:
        # Проверяем, что это группа
        if message.chat.type == "private":
            await message.reply(lang.get("reload_group_only", "Bu əmr yalnız qruplarda işləyir."))
            return
        
        chat_id = message.chat.id
        
        # 1. Проверяем права бота
        bot_member = await client.get_chat_member(chat_id, "me")
        bot_permissions = []
        
        if not bot_member.privileges:
            await message.reply(lang.get("reload_bot_not_admin", "❌ Bot admin deyil! Admin hüquqları verin."))
            return
        
        # Проверяем основные права
        if bot_member.privileges.can_delete_messages:
            bot_permissions.append("✅ Mesajları silmək")
        else:
            bot_permissions.append("❌ Mesajları silmək")
            
        if bot_member.privileges.can_restrict_members:
            bot_permissions.append("✅ İstifadəçiləri məhdudlaşdırmaq")
        else:
            bot_permissions.append("❌ İstifadəçiləri məhdudlaşdırmaq")
            
        if bot_member.privileges.can_invite_users:
            bot_permissions.append("✅ İstifadəçiləri dəvət etmək")
        else:
            bot_permissions.append("❌ İstifadəçiləri dəvət etmək")
        
        # 2. Проверяем права userbot (если активен)
        userbot_status = ""
        if userbot:
            try:
                userbot_member = await userbot.get_chat_member(chat_id, "me")
                if userbot_member.status in ["administrator", "creator"]:
                    # Проверяем только право на удаление сообщений для userbot
                    if userbot_member.privileges and userbot_member.privileges.can_delete_messages:
                        userbot_status = "✅ Userbot: Mesajları silmək hüququ var"
                    else:
                        userbot_status = "❌ Userbot: Mesajları silmək hüququ yoxdur"
                else:
                    userbot_status = "❌ Userbot admin deyil"
            except Exception as e:
                userbot_status = f"❌ Userbot xətası: {str(e)[:50]}"
        else:
            userbot_status = "⚠️ Userbot aktiv deyil"
        
        # 3. Перезагружаем вульгарные слова
        vulgar_words_reload = ""
        try:
            # Импортируем и перезагружаем модуль вульгарных слов
            import importlib
            import modules.antivulgar
            importlib.reload(modules.antivulgar)
            vulgar_words_reload = "✅ Vulqar sözlər yeniləndi"
        except Exception as e:
            vulgar_words_reload = f"❌ Vulqar sözlər xətası: {str(e)[:50]}"
        
        # 4. Перезагружаем другие фильтры
        filters_reload = ""
        try:
            import importlib
            import modules.antispam
            import modules.antiflood
            importlib.reload(modules.antispam)
            importlib.reload(modules.antiflood)
            filters_reload = "✅ Filtrlər yeniləndi"
        except Exception as e:
            filters_reload = f"❌ Filtrlər xətası: {str(e)[:50]}"
        
        # Формируем отчет
        report_text = f"🔄 <b>{lang.get('reload_title', 'Filter Reload Report')}</b>\n\n"
        
        report_text += f"🤖 <b>{lang.get('reload_bot_permissions', 'Bot Permissions')}:</b>\n"
        for perm in bot_permissions:
            report_text += f"• {perm}\n"
        
        report_text += f"\n👤 <b>{lang.get('reload_userbot_status', 'Userbot Status')}:</b>\n"
        report_text += f"• {userbot_status}\n"
        
        report_text += f"\n🛡 <b>{lang.get('reload_filters_status', 'Filters Status')}:</b>\n"
        report_text += f"• {vulgar_words_reload}\n"
        report_text += f"• {filters_reload}\n"
        
        report_text += f"\n⏰ <b>{lang.get('reload_time', 'Reload Time')}:</b> {message.date.strftime('%H:%M:%S')}"
        
        await message.reply(report_text)
        
    except Exception as e:
        logging.error(f"Reload command error: {e}")
        await message.reply(lang.get("reload_error", f"❌ Reload xətası: {str(e)[:100]}"))

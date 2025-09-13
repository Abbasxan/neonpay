"""
Currency Management Module
Модуль управления валютами
"""

import logging
import re
from datetime import datetime
from pyrogram import Client, filters
from pyrogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, Message
from pyrogram.enums import ChatMemberStatus
from config import app
from language import load_language, get_group_language
from .database import EconomyDB

logger = logging.getLogger(__name__)

class CurrencyManager:
    """Менеджер валют"""
    
    async def show_create_currency(self, client: Client, callback_query: CallbackQuery):
        """Показать создание валюты"""
        chat_id = callback_query.message.chat.id
        user_id = callback_query.from_user.id
        lang_code = await get_group_language(chat_id)
        lang = load_language(lang_code)
        
        # Проверяем права администратора
        try:
            member = await client.get_chat_member(chat_id, user_id)
            if member.status not in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
                return await callback_query.answer(
                    lang.get('economy_admin_only')
                )
        except Exception as e:
            logger.error(f"Error checking admin status: {e}")
            return
        
        # Получаем текущие настройки валюты (если есть)
        group_currency = await EconomyDB.get_group_currency(chat_id)
        
        if group_currency:
            # Показываем существующую валюту с возможностью редактирования
            currency_name = group_currency["currency_name"]
            currency_symbol = group_currency["currency_symbol"]
            exchange_rate = group_currency["exchange_rate_to_nc"]
            activity_score = group_currency.get("daily_activity_score", 0)
            
            keyboard = InlineKeyboardMarkup([
                [
                    InlineKeyboardButton(
                        f"✏️ {lang.get('economy_edit_currency')}",
                        callback_data=f"economy_edit_currency_{chat_id}"
                    )
                ],
                [
                    InlineKeyboardButton(
                        f"🗑️ {lang.get('economy_delete_currency')}",
                        callback_data=f"economy_delete_currency_{chat_id}"
                    )
                ],
                [
                    InlineKeyboardButton(
                        f"🔙 {lang.get('economy_back')}",
                        callback_data=f"economy_back_{chat_id}"
                    )
                ]
            ])
            
            text = f"""
🏦 <b>{lang.get('economy_currency_settings')}</b>

📊 <b>{lang.get('economy_current_settings')}:</b>
• {lang.get('economy_currency_name')}: <b>{currency_name}</b>
• {lang.get('economy_currency_symbol')}: <b>{currency_symbol}</b>
• {lang.get('economy_exchange_rate_short')}: <b>{exchange_rate:.2f}</b>
• {lang.get('economy_activity_score')}: <b>{activity_score}</b>

🔄 <b>{lang.get('economy_auto_rate_update')}:</b>
{lang.get('economy_rate_updates_daily')}
            """
        else:
            # Показываем форму создания валюты
            keyboard = InlineKeyboardMarkup([
                [
                    InlineKeyboardButton(
                        f"📝 {lang.get('economy_create_new_currency')}",
                        callback_data=f"economy_create_new_currency_{chat_id}"
                    )
                ],
                [
                    InlineKeyboardButton(
                        f"🔙 {lang.get('economy_back')}",
                        callback_data=f"economy_back_{chat_id}"
                    )
                ]
            ])
            
            text = f"""
🏦 <b>{lang.get('economy_create_currency_title')}</b>

📋 <b>{lang.get('economy_requirements')}:</b>
• {lang.get('economy_currency_name_requirements')}
• {lang.get('economy_currency_symbol_requirements')}
• {lang.get('economy_admin_only_create')}

💡 <b>{lang.get('economy_examples')}:</b>
• {lang.get('economy_currency_name')}: "Neon Coins", {lang.get('economy_currency_symbol')}: "NC"
• {lang.get('economy_currency_name')}: "Group Gold", {lang.get('economy_currency_symbol')}: "GG"
• {lang.get('economy_currency_name')}: "Chat Cash", {lang.get('economy_currency_symbol')}: "CC"

⚠️ <b>{lang.get('economy_important')}:</b> {lang.get('economy_currency_one_time')}

{lang.get('economy_click_button_create')}
            """
        
        await callback_query.edit_message_text(text, reply_markup=keyboard)
    
    async def create_currency(self, chat_id: int, user_id: int, currency_name: str, currency_symbol: str) -> tuple[bool, str]:
        """Создать валюту для группы"""
        # Получаем язык группы
        lang_code = await get_group_language(chat_id)
        lang = load_language(lang_code)
        
        # Проверяем, что валюта еще не создана
        existing_currency = await EconomyDB.get_group_currency(chat_id)
        if existing_currency:
            return False, lang.get('economy_currency_already_exists')
        
        # Валидация названия валюты
        if not currency_name or len(currency_name) > 10:
            return False, lang.get('economy_currency_name_validation')
        
        # Валидация символа валюты
        if not currency_symbol or len(currency_symbol) > 4:
            return False, lang.get('economy_currency_symbol_validation')
        
        # Проверяем, что символ содержит только буквы и цифры
        if not re.match(r'^[A-Za-z0-9]+$', currency_symbol):
            return False, lang.get('economy_currency_symbol_format')
        
        # Создаем валюту
        try:
            await EconomyDB.create_group_currency(chat_id, currency_name, currency_symbol, user_id)
            return True, lang.get('economy_currency_created', 'Валюта \'{name}\' ({symbol}) успешно создана!').format(name=currency_name, symbol=currency_symbol)
        except Exception as e:
            logger.error(f"Error creating currency: {e}")
            return False, lang.get('economy_currency_creation_error')
    
    async def update_exchange_rate(self, chat_id: int, user_id: int) -> tuple[bool, str]:
        """Обновить курс обмена"""
        # Получаем язык группы
        lang_code = await get_group_language(chat_id)
        lang = load_language(lang_code)
        
        # Проверяем права администратора
        try:
            from config import app
            member = await app.get_chat_member(chat_id, user_id)
            if member.status not in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
                return False, lang.get('economy_admin_only')
        except Exception as e:
            logger.error(f"Error checking admin status: {e}")
            return False, lang.get('economy_rate_update_error')
        
        # Получаем данные о валюте
        group_currency = await EconomyDB.get_group_currency(chat_id)
        if not group_currency:
            return False, lang.get('economy_currency_not_created')
        
        # Используем продвинутый алгоритм ценообразования
        from .advanced_pricing import advanced_pricing
        new_rate = await advanced_pricing.calculate_dynamic_rate(chat_id)
        
        # Обновляем курс
        await EconomyDB.update_exchange_rate(chat_id, new_rate)
        
        return True, lang.get('economy_rate_updated').format(symbol=group_currency['currency_symbol'], rate=new_rate)
    
    async def get_exchange_info(self, chat_id: int) -> dict:
        """Получить информацию о курсе обмена"""
        group_currency = await EconomyDB.get_group_currency(chat_id)
        if not group_currency:
            return None
        
        return {
            "currency_name": group_currency["currency_name"],
            "currency_symbol": group_currency["currency_symbol"],
            "exchange_rate": group_currency["exchange_rate_to_nc"],
            "activity_score": group_currency.get("daily_activity_score", 0),
            "last_update": group_currency["last_rate_update"]
        }
    
    async def show_create_new_currency_form(self, client: Client, callback_query: CallbackQuery):
        """Показать форму создания новой валюты"""
        chat_id = callback_query.message.chat.id
        user_id = callback_query.from_user.id
        lang_code = await get_group_language(chat_id)
        lang = load_language(lang_code)
        
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton(
                    f"🔙 {lang.get('economy_back')}",
                    callback_data=f"economy_create_currency_{chat_id}"
                )
            ]
        ])
        
        text = f"""
📝 <b>{lang.get('economy_create_new_currency_form')}</b>

{lang.get('economy_currency_creation_format')}
<code>/create_currency &lt;название&gt; &lt;символ&gt;</code>

📋 <b>{lang.get('economy_examples')}:</b>
• <code>/create_currency Neon Coins NC</code>
• <code>/create_currency Group Gold GG</code>
• <code>/create_currency Chat Cash CC</code>

⚠️ <b>{lang.get('economy_requirements')}:</b>
• {lang.get('economy_currency_name_requirements')}
• {lang.get('economy_currency_symbol_requirements')}
• {lang.get('economy_currency_one_time')}
        """
        
        await callback_query.edit_message_text(text, reply_markup=keyboard)
    
    async def delete_currency(self, chat_id: int, user_id: int) -> tuple[bool, str]:
        """Удалить валюту группы"""
        # Получаем язык группы
        lang_code = await get_group_language(chat_id)
        lang = load_language(lang_code)
        
        # Проверяем права администратора
        try:
            from config import app
            member = await app.get_chat_member(chat_id, user_id)
            if member.status not in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
                return False, lang.get('economy_admin_only')
        except Exception as e:
            logger.error(f"Error checking admin status: {e}")
            return False, lang.get('economy_rate_update_error')
        
        # Удаляем валюту
        try:
            from config import db
            await db.group_currencies.delete_one({"_id": chat_id})
            return True, lang.get('economy_currency_deleted')
        except Exception as e:
            logger.error(f"Error deleting currency: {e}")
            return False, lang.get('economy_currency_deletion_error')

# Команда для создания валюты
@app.on_message(filters.command("create_currency") & filters.group, group=20)
async def create_currency_command(client: Client, message: Message):
    """Команда для создания валюты"""
    chat_id = message.chat.id
    user_id = message.from_user.id
    lang_code = await get_group_language(chat_id)
    lang = load_language(lang_code)
    
    # Проверяем права администратора
    try:
        member = await client.get_chat_member(chat_id, user_id)
        if member.status not in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
            admin_only_text = lang.get('economy_admin_only', 'Только администраторы могут создавать валюту')
            return await message.reply(f"❌ {admin_only_text}")
    except Exception as e:
        logger.error(f"Error checking admin status: {e}")
        return
    
    # Парсим аргументы
    args = message.text.split()[1:]
    if len(args) < 2:
        usage_text = lang.get('economy_create_currency_usage', 'Использование: /create_currency <название> <символ>')
        return await message.reply(f"❌ {usage_text}")
    
    currency_name = " ".join(args[:-1])  # Все аргументы кроме последнего
    currency_symbol = args[-1].upper()   # Последний аргумент - символ
    
    # Создаем валюту
    currency_manager = CurrencyManager()
    success, result_message = await currency_manager.create_currency(chat_id, user_id, currency_name, currency_symbol)
    
    if success:
        # Удаляем сообщение с командой
        try:
            await message.delete()
        except Exception as e:
            logger.warning(f"Could not delete message: {e}")
        
        # Примечание: Удаление формы создания валюты происходит автоматически
        # при показе нового меню экономики через edit_message_text
        
        # Показываем меню экономики
        from .economy import economy_manager
        await economy_manager.show_main_menu(client, message)
    else:
        await message.reply(f"❌ {result_message}")

# Курс обновляется автоматически по алгоритму

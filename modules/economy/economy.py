"""
Main Economy Module
Основной модуль экономической системы
"""

import logging
from datetime import datetime, timedelta
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from pyrogram.enums import ChatMemberStatus
from config import app, db
from language import load_language, get_group_language, get_text
from .database import EconomyDB
from .currency import CurrencyManager
from .profile import ProfileManager
from .achievements import AchievementManager
from .daily_bonus import DailyBonusManager

logger = logging.getLogger(__name__)

class EconomyManager:
    """Менеджер экономической системы"""
    
    def __init__(self):
        self.currency_manager = CurrencyManager()
        self.profile_manager = ProfileManager()
        self.achievement_manager = AchievementManager()
        self.daily_bonus_manager = DailyBonusManager()
    
    async def show_main_menu(self, client: Client, message: Message):
        """Показать главное меню экономики"""
        chat_id = message.chat.id
        user_id = message.from_user.id
        lang_code = await get_group_language(chat_id)
        lang = load_language(lang_code)
        
        # Проверяем, есть ли валюта в группе
        group_currency = await EconomyDB.get_group_currency(chat_id)
        if not group_currency:
            return await self.show_setup_menu(client, message)
        
        # Получаем баланс пользователя и статистику группы
        balance = await EconomyDB.get_user_balance(chat_id, user_id)
        group_stats = await EconomyDB.get_group_statistics(chat_id)
        
        # Создаем клавиатуру
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton(
                    f"🔄 {lang.get('economy_convert')}",
                    callback_data=f"economy_convert_{chat_id}"
                ),
                InlineKeyboardButton(
                    f"🏆 {lang.get('economy_achievements')}",
                    callback_data=f"economy_achievements_{chat_id}"
                )
            ],
            [
                InlineKeyboardButton(
                    f"🎁 {lang.get('economy_daily_bonus')}",
                    callback_data=f"economy_daily_{chat_id}"
                ),
                InlineKeyboardButton(
                    f"📊 {lang.get('economy_leaderboard')}",
                    callback_data=f"economy_leaderboard_{chat_id}"
                )
            ],
            [
                InlineKeyboardButton(
                    f"👤 {lang.get('economy_profile')}",
                    callback_data=f"economy_profile_{chat_id}"
                ),
                InlineKeyboardButton(
                    f"📈 {lang.get('economy_charts')}",
                    callback_data=f"economy_charts_{chat_id}"
                )
            ],
            [
                InlineKeyboardButton(
                    f"⚙️ {lang.get('economy_settings')}",
                    callback_data=f"economy_settings_{chat_id}"
                )
            ]
        ])
        
        # Формируем сообщение
        currency_name = group_currency["currency_name"]
        currency_symbol = group_currency["currency_symbol"]
        
        text = f"""
💰 <b>{lang.get('economy_title')}</b>

🏦 <b>{currency_name} ({currency_symbol})</b>
💎 <b>{lang.get('economy_neon_coins')}</b>

👤 <b>{lang.get('economy_your_balance')}:</b>
• {currency_symbol}: <code>{balance['group_currency']:.2f}</code>
• NC: <code>{balance['neon_coins']:.2f}</code>
• {lang.get('economy_total_earned_short')}: <code>{balance['total_earned']:.2f}</code>

🏢 <b>{lang.get('economy_group_statistics')}:</b>
• {lang.get('economy_total_users')}: <code>{group_stats['total_users']}</code>
• {lang.get('economy_group_total')} {currency_symbol}: <code>{group_stats['total_group_currency']:.2f}</code>
• {lang.get('economy_group_total')} NC: <code>{group_stats['total_neon_coins']:.2f}</code>

🔄 <b>{lang.get('economy_exchange_rate')}:</b> 1 {currency_symbol} = {group_currency['exchange_rate_to_nc']:.2f} NC
        """
        
        await message.reply(text, reply_markup=keyboard)
    
    async def show_main_menu_callback(self, client: Client, callback_query: CallbackQuery):
        """Показать главное меню экономики через callback (редактирование сообщения)"""
        chat_id = callback_query.message.chat.id
        user_id = callback_query.from_user.id
        lang_code = await get_group_language(chat_id)
        lang = load_language(lang_code)
        
        # Проверяем, есть ли валюта в группе
        group_currency = await EconomyDB.get_group_currency(chat_id)
        if not group_currency:
            return await self.show_setup_menu_callback(client, callback_query)
        
        # Получаем баланс пользователя и статистику группы
        balance = await EconomyDB.get_user_balance(chat_id, user_id)
        group_stats = await EconomyDB.get_group_statistics(chat_id)
        
        # Создаем клавиатуру
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton(
                    f"🔄 {lang.get('economy_convert')}",
                    callback_data=f"economy_convert_{chat_id}"
                ),
                InlineKeyboardButton(
                    f"🏆 {lang.get('economy_achievements')}",
                    callback_data=f"economy_achievements_{chat_id}"
                )
            ],
            [
                InlineKeyboardButton(
                    f"🎁 {lang.get('economy_daily_bonus')}",
                    callback_data=f"economy_daily_{chat_id}"
                ),
                InlineKeyboardButton(
                    f"📊 {lang.get('economy_leaderboard')}",
                    callback_data=f"economy_leaderboard_{chat_id}"
                )
            ],
            [
                InlineKeyboardButton(
                    f"👤 {lang.get('economy_profile')}",
                    callback_data=f"economy_profile_{chat_id}"
                ),
                InlineKeyboardButton(
                    f"📈 {lang.get('economy_charts')}",
                    callback_data=f"economy_charts_{chat_id}"
                )
            ],
            [
                InlineKeyboardButton(
                    f"⚙️ {lang.get('economy_settings')}",
                    callback_data=f"economy_settings_{chat_id}"
                )
            ]
        ])
        
        # Формируем сообщение
        currency_name = group_currency["currency_name"]
        currency_symbol = group_currency["currency_symbol"]
        
        text = f"""
💰 <b>{lang.get('economy_title')}</b>

🏦 <b>{currency_name} ({currency_symbol})</b>
💎 <b>{lang.get('economy_neon_coins')}</b>

👤 <b>{lang.get('economy_your_balance')}:</b>
• {currency_symbol}: <code>{balance['group_currency']:.2f}</code>
• NC: <code>{balance['neon_coins']:.2f}</code>
• {lang.get('economy_total_earned_short')}: <code>{balance['total_earned']:.2f}</code>

🏢 <b>{lang.get('economy_group_statistics')}:</b>
• {lang.get('economy_total_users')}: <code>{group_stats['total_users']}</code>
• {lang.get('economy_group_total')} {currency_symbol}: <code>{group_stats['total_group_currency']:.2f}</code>
• {lang.get('economy_group_total')} NC: <code>{group_stats['total_neon_coins']:.2f}</code>

🔄 <b>{lang.get('economy_exchange_rate')}:</b> 1 {currency_symbol} = {group_currency['exchange_rate_to_nc']:.2f} NC
        """
        
        await callback_query.edit_message_text(text, reply_markup=keyboard)
    
    async def show_setup_menu_callback(self, client: Client, callback_query: CallbackQuery):
        """Показать меню настройки валюты через callback"""
        chat_id = callback_query.message.chat.id
        user_id = callback_query.from_user.id
        lang_code = await get_group_language(chat_id)
        lang = load_language(lang_code)
        
        # Проверяем права администратора
        try:
            member = await client.get_chat_member(chat_id, user_id)
            if member.status not in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
                return await callback_query.edit_message_text(
                    f"<blockquote>{lang.get('economy_admin_only')}</blockquote>"
                )
        except Exception as e:
            logger.error(f"Error checking admin status: {e}")
            return
        
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton(
                    f"🏦 {lang.get('economy_create_currency')}",
                    callback_data=f"economy_create_currency_{chat_id}"
                )
            ],
            [
                InlineKeyboardButton(
                    f"ℹ️ {lang.get('economy_info')}",
                    callback_data=f"economy_info_{chat_id}"
                )
            ]
        ])
        
        text = f"""
💰 <b>{lang.get('economy_setup_title')}</b>

{lang.get('economy_setup_description')}

📋 <b>{lang.get('economy_features')}:</b>
• {lang.get('economy_create_group_currency')}
• {lang.get('economy_daily_bonuses')}
• {lang.get('economy_achievements_system')}
• {lang.get('economy_currency_conversion')}
• {lang.get('economy_leaderboard', 'Рейтинг пользователей')}
        """
        
        await callback_query.edit_message_text(text, reply_markup=keyboard)
    
    async def show_setup_menu(self, client: Client, message: Message):
        """Показать меню настройки валюты"""
        chat_id = message.chat.id
        user_id = message.from_user.id
        lang_code = await get_group_language(chat_id)
        lang = load_language(lang_code)
        
        # Проверяем права администратора
        try:
            member = await client.get_chat_member(chat_id, user_id)
            if member.status not in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
                return await message.reply(
                    f"<blockquote>{lang.get('economy_admin_only')}</blockquote>"
                )
        except Exception as e:
            logger.error(f"Error checking admin status: {e}")
            return
        
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton(
                    f"🏦 {lang.get('economy_create_currency')}",
                    callback_data=f"economy_create_currency_{chat_id}"
                )
            ],
            [
                InlineKeyboardButton(
                    f"ℹ️ {lang.get('economy_info')}",
                    callback_data=f"economy_info_{chat_id}"
                )
            ]
        ])
        
        text = f"""
💰 <b>{lang.get('economy_setup_title')}</b>

{lang.get('economy_setup_description')}

📋 <b>{lang.get('economy_features')}:</b>
• {lang.get('economy_create_group_currency')}
• {lang.get('economy_daily_bonuses')}
• {lang.get('economy_achievements_system')}
• {lang.get('economy_currency_conversion')}
• {lang.get('economy_leaderboard', 'Рейтинг пользователей')}
        """
        
        await message.reply(text, reply_markup=keyboard)
    
    async def handle_callback(self, client: Client, callback_query: CallbackQuery):
        """Обработчик callback запросов"""
        data = callback_query.data
        chat_id = callback_query.message.chat.id
        user_id = callback_query.from_user.id
        logger.info(f"Economy callback received: {data} from user {user_id} in chat {chat_id}")
        
        # Load language for error messages
        lang_code = await get_group_language(chat_id)
        lang = load_language(lang_code)
        
        if data.startswith("economy_convert_to_nc_"):
            logger.debug(f"DEBUG: Processing economy_convert_to_nc_ callback")
            try:
                await self.show_convert_to_nc(client, callback_query)
            except Exception as e:
                logger.error(f"Error in show_convert_to_nc: {e}")
                import traceback
                logger.error(f"Full traceback: {traceback.format_exc()}")
                await callback_query.answer(f"❌ {lang.get('economy_conversion_error', 'Ошибка при показе меню конвертации')}!", show_alert=True)
        elif data.startswith("economy_convert_to_group_"):
            try:
                await self.show_convert_to_group(client, callback_query)
            except Exception as e:
                logger.error(f"Error in show_convert_to_group: {e}")
                await callback_query.answer(f"❌ {lang.get('economy_conversion_error', 'Ошибка при показе меню конвертации')}!", show_alert=True)
        elif data.startswith("economy_convert_nc_amount_"):
            logger.debug(f"DEBUG: Processing economy_convert_nc_amount_ callback")
            await self.handle_convert_nc_amount(client, callback_query)
        elif data.startswith("economy_convert_group_amount_"):
            logger.debug(f"DEBUG: Processing economy_convert_group_amount_ callback")
            await self.handle_convert_group_amount(client, callback_query)
        elif data.startswith("economy_convert_"):
            await self.show_conversion(client, callback_query)
        elif data.startswith("economy_achievements_"):
            await self.show_achievements(client, callback_query)
        elif data.startswith("economy_daily_"):
            await self.show_daily_bonus(client, callback_query)
        elif data.startswith("economy_leaderboard_"):
            await self.show_leaderboard(client, callback_query)
        elif data.startswith("economy_profile_"):
            await self.show_profile(client, callback_query)
        elif data.startswith("economy_settings_"):
            await self.show_settings(client, callback_query)
        elif data.startswith("economy_charts_"):
            await self.show_chart_menu(client, callback_query)
        elif data.startswith("economy_create_currency_"):
            await self.show_create_currency(client, callback_query)
        elif data.startswith("economy_create_new_currency_"):
            await self.currency_manager.show_create_new_currency_form(client, callback_query)
        elif data.startswith("economy_edit_currency_"):
            await self.show_edit_currency(client, callback_query)
        elif data.startswith("economy_delete_currency_"):
            await self.show_delete_currency(client, callback_query)
        elif data.startswith("economy_confirm_delete_"):
            await self.confirm_delete_currency(client, callback_query)
        elif data.startswith("economy_info_"):
            await self.show_info(client, callback_query)
        elif data.startswith("economy_no_group_currency_"):
            await self.show_no_currency_message(client, callback_query, "group")
        elif data.startswith("economy_no_nc_"):
            await self.show_no_currency_message(client, callback_query, "nc")
        elif data.startswith("economy_market_analysis_"):
            await self.show_market_analysis(client, callback_query)
        elif data.startswith("economy_chart_"):
            await self.show_chart_menu(client, callback_query)
        elif data.startswith("economy_generate_chart_"):
            await self.generate_chart(client, callback_query)
        elif data.startswith("economy_back_"):
            await self.show_main_menu_callback(client, callback_query)
    
    async def show_conversion(self, client: Client, callback_query: CallbackQuery):
        """Показать меню конвертации"""
        chat_id = callback_query.message.chat.id
        user_id = callback_query.from_user.id
        lang_code = await get_group_language(chat_id)
        lang = load_language(lang_code)
        
        balance = await EconomyDB.get_user_balance(chat_id, user_id)
        group_currency = await EconomyDB.get_group_currency(chat_id)
        
        currency_symbol = group_currency["currency_symbol"]
        exchange_rate = group_currency["exchange_rate_to_nc"]
        
        # Проверяем баланс для определения активных кнопок
        has_group_currency = balance['group_currency'] > 0
        has_neon_coins = balance['neon_coins'] > 0
        
        # Создаем кнопки в зависимости от наличия валют
        buttons = []
        
        # Кнопка конвертации групповой валюты в NC
        if has_group_currency:
            buttons.append([
                InlineKeyboardButton(
                    f"{currency_symbol} → NC",
                    callback_data=f"economy_convert_to_nc_{chat_id}"
                )
            ])
        else:
            buttons.append([
                InlineKeyboardButton(
                    f"❌ {currency_symbol} → NC",
                    callback_data=f"economy_no_group_currency_{chat_id}"
                )
            ])
        
        # Кнопка конвертации NC в групповую валюту
        if has_neon_coins:
            buttons.append([
                InlineKeyboardButton(
                    f"NC → {currency_symbol}",
                    callback_data=f"economy_convert_to_group_{chat_id}"
                )
            ])
        else:
            buttons.append([
                InlineKeyboardButton(
                    f"❌ NC → {currency_symbol}",
                    callback_data=f"economy_no_nc_{chat_id}"
                )
            ])
        
        # Кнопка "Назад"
        buttons.append([
            InlineKeyboardButton(
                f"🔙 {lang.get('economy_back')}",
                callback_data=f"economy_back_{chat_id}"
            )
        ])
        
        keyboard = InlineKeyboardMarkup(buttons)
        
        text = f"""
🔄 <b>{lang.get('economy_conversion')}</b>

💰 <b>{lang.get('economy_your_balance')}:</b>
• {currency_symbol}: <code>{balance['group_currency']:.2f}</code>
• NC: <code>{balance['neon_coins']:.2f}</code>

📈 <b>{lang.get('economy_current_rate')}:</b>
• 1 {currency_symbol} = {exchange_rate:.2f} NC
• 1 NC = {1/exchange_rate:.2f} {currency_symbol}

{lang.get('economy_choose_conversion')}:
        """
        
        await callback_query.edit_message_text(text, reply_markup=keyboard)
    
    async def show_no_currency_message(self, client: Client, callback_query: CallbackQuery, currency_type: str):
        """Показать сообщение о недостатке валюты"""
        chat_id = callback_query.message.chat.id
        user_id = callback_query.from_user.id
        lang_code = await get_group_language(chat_id)
        lang = load_language(lang_code)
        
        group_currency = await EconomyDB.get_group_currency(chat_id)
        currency_symbol = group_currency["currency_symbol"]
        
        if currency_type == "group":
            message = f"❌ {lang.get('economy_no_group_currency', 'У вас нет групповой валюты')} {currency_symbol}!"
            button_text = f"❌ {currency_symbol} → NC"
        else:  # nc
            message = f"❌ {lang.get('economy_no_nc', 'У вас нет NC')}!"
            button_text = f"❌ NC → {currency_symbol}"
        
        await callback_query.answer(message, show_alert=True)
    
    async def show_market_analysis(self, client: Client, callback_query: CallbackQuery):
        """Показать анализ рынка"""
        chat_id = callback_query.message.chat.id
        user_id = callback_query.from_user.id
        lang_code = await get_group_language(chat_id)
        lang = load_language(lang_code)
        
        try:
            from .advanced_pricing import advanced_pricing
            analysis = await advanced_pricing.get_market_analysis(chat_id)
            
            if "error" in analysis:
                await callback_query.answer(f"❌ {analysis['error']}", show_alert=True)
                return
            
            # Создаем текст анализа
            text = f"""
📊 <b>Анализ рынка валюты</b>

💰 <b>Текущий курс:</b> {analysis['current_rate']:.4f} NC
📈 <b>Статус:</b> {analysis['status']}
💡 <b>Рекомендация:</b> {analysis['recommendation']}

📋 <b>Факторы влияния:</b>
• 🎯 Активность: {analysis['factors']['activity']}
• 📦 Предложение: {analysis['factors']['supply']}
• ⏰ Возраст: {analysis['factors']['age']}
• 🔥 Спрос: {analysis['factors']['demand']}
• 📊 Тренд: {analysis['factors']['trend']}

🏆 <b>Общий рейтинг:</b> {analysis['total_score']}/1.0
            """
            
            keyboard = InlineKeyboardMarkup([
                [
                    InlineKeyboardButton(
                        f"🔙 {lang.get('economy_back')}",
                        callback_data=f"economy_back_{chat_id}"
                    )
                ]
            ])
            
            await callback_query.edit_message_text(text, reply_markup=keyboard)
            
        except Exception as e:
            logger.error(f"Ошибка при показе анализа рынка: {e}")
            await callback_query.answer("❌ Ошибка при анализе рынка", show_alert=True)
    
    async def show_chart_menu(self, client: Client, callback_query: CallbackQuery):
        """Показать меню графиков"""
        chat_id = callback_query.message.chat.id
        user_id = callback_query.from_user.id
        lang_code = await get_group_language(chat_id)
        lang = load_language(lang_code)
        
        text = """
📊 <b>Генератор графиков</b>

Выберите тип графика для анализа экономической системы:
        """
        
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton(
                    "📈 Анализ рынка",
                    callback_data=f"economy_generate_chart_market_{chat_id}"
                )
            ],
            [
                InlineKeyboardButton(
                    "💼 Мой портфель",
                    callback_data=f"economy_generate_chart_portfolio_{chat_id}"
                )
            ],
            [
                InlineKeyboardButton(
                    "🏦 Сравнение валют",
                    callback_data=f"economy_generate_chart_comparison_{chat_id}"
                )
            ],
            [
                InlineKeyboardButton(
                    f"🔙 {lang.get('economy_back')}",
                    callback_data=f"economy_back_{chat_id}"
                )
            ]
        ])
        
        await callback_query.edit_message_text(text, reply_markup=keyboard)
    
    async def generate_chart(self, client: Client, callback_query: CallbackQuery):
        """Генерировать график"""
        chat_id = callback_query.message.chat.id
        user_id = callback_query.from_user.id
        lang_code = await get_group_language(chat_id)
        lang = load_language(lang_code)
        
        try:
            # Показываем сообщение о генерации
            await callback_query.edit_message_text("🎨 Генерирую график...")
            
            from .chart_generator import chart_generator
            
            # Определяем тип графика
            if "market" in callback_query.data:
                chart_buffer = await chart_generator.generate_market_analysis_chart(chat_id)
                caption = "📊 Анализ рынка валюты"
            elif "portfolio" in callback_query.data:
                chart_buffer = await chart_generator.generate_user_portfolio_chart(chat_id, user_id)
                caption = "💼 Ваш портфель"
            elif "comparison" in callback_query.data:
                # Получаем список всех групп с валютами
                from .database import EconomyDB
                cursor = db.group_currencies.find({"is_active": True}).limit(5)
                groups = await cursor.to_list(length=5)
                chat_ids = [group["_id"] for group in groups]
                
                if not chat_ids:
                    await callback_query.edit_message_text("❌ Нет данных для сравнения")
                    return
                
                chart_buffer = await chart_generator.generate_currency_comparison_chart(chat_ids)
                caption = "🏦 Сравнение валют групп"
            else:
                await callback_query.edit_message_text("❌ Неизвестный тип графика")
                return
            
            # Отправляем график
            await client.send_photo(
                chat_id=chat_id,
                photo=chart_buffer,
                caption=caption,
                reply_to_message_id=callback_query.message.reply_to_message_id if callback_query.message.reply_to_message_id else None
            )
            
            # Возвращаемся к меню графиков
            await self.show_chart_menu(client, callback_query)
            
        except Exception as e:
            logger.error(f"Ошибка при генерации графика: {e}")
            await callback_query.edit_message_text("❌ Ошибка при генерации графика")
    
    async def show_convert_to_nc(self, client: Client, callback_query: CallbackQuery):
        """Показать форму конвертации в NC"""
        chat_id = callback_query.message.chat.id
        user_id = callback_query.from_user.id
        logger.info(f"show_convert_to_nc: Starting for user {user_id} in chat {chat_id}")
        
        try:
            lang_code = await get_group_language(chat_id)
            lang = load_language(lang_code)
            logger.info(f"show_convert_to_nc: Language loaded: {lang_code}")
            
            balance = await EconomyDB.get_user_balance(chat_id, user_id)
            logger.info(f"show_convert_to_nc: Balance loaded: {balance}")
            
            # Проверяем, есть ли у пользователя групповая валюта
            if balance['group_currency'] <= 0:
                await callback_query.answer(f"❌ {lang.get('economy_no_group_currency', 'У вас нет групповой валюты')}!", show_alert=True)
                return
            
            group_currency = await EconomyDB.get_group_currency(chat_id)
            logger.info(f"show_convert_to_nc: Group currency loaded: {group_currency}")
            
            currency_symbol = group_currency["currency_symbol"]
            exchange_rate = group_currency["exchange_rate_to_nc"]
            logger.info(f"show_convert_to_nc: Currency symbol: {currency_symbol}, Exchange rate: {exchange_rate}")
            
            # Создаем кнопки с предустановленными суммами
            keyboard = InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("10", callback_data=f"economy_convert_nc_amount_{chat_id}_10"),
                    InlineKeyboardButton("50", callback_data=f"economy_convert_nc_amount_{chat_id}_50"),
                    InlineKeyboardButton("100", callback_data=f"economy_convert_nc_amount_{chat_id}_100")
                ],
                [
                    InlineKeyboardButton("500", callback_data=f"economy_convert_nc_amount_{chat_id}_500"),
                    InlineKeyboardButton("1000", callback_data=f"economy_convert_nc_amount_{chat_id}_1000"),
                    InlineKeyboardButton(lang.get('economy_all', 'Все'), callback_data=f"economy_convert_nc_amount_{chat_id}_all")
                ],
                [
                    InlineKeyboardButton(
                        f"🔙 {lang.get('economy_back')}",
                        callback_data=f"economy_convert_{chat_id}"
                    )
                ]
            ])
            logger.info(f"show_convert_to_nc: Keyboard created")
            
            text = f"""
🔄 <b>{lang.get('economy_convert_to_nc', 'Конвертация')} {currency_symbol} → NC</b>

💰 <b>{lang.get('economy_your_balance')}:</b>
• {currency_symbol}: <code>{balance['group_currency']:.2f}</code>
• NC: <code>{balance['neon_coins']:.2f}</code>

📈 <b>{lang.get('economy_exchange_rate_short')}:</b> 1 {currency_symbol} = {exchange_rate:.2f} NC

💡 <b>{lang.get('economy_select_amount', 'Выберите сумму для конвертации')}:</b>
            """
            logger.info(f"show_convert_to_nc: Text created")
            
            logger.info(f"Showing convert to NC menu for user {user_id} in chat {chat_id}")
            try:
                await callback_query.edit_message_text(text, reply_markup=keyboard)
                logger.info(f"show_convert_to_nc: Message sent successfully")
            except Exception as edit_error:
                if "MESSAGE_NOT_MODIFIED" in str(edit_error):
                    logger.debug(f"show_convert_to_nc: Message not modified (same content), ignoring")
                    await callback_query.answer()
                else:
                    raise edit_error
            
        except Exception as e:
            logger.error(f"show_convert_to_nc: Error: {e}")
            await callback_query.answer("❌ Ошибка при показе меню конвертации!", show_alert=True)
    
    async def show_convert_to_group(self, client: Client, callback_query: CallbackQuery):
        """Показать форму конвертации в групповую валюту"""
        chat_id = callback_query.message.chat.id
        user_id = callback_query.from_user.id
        lang_code = await get_group_language(chat_id)
        lang = load_language(lang_code)
        
        balance = await EconomyDB.get_user_balance(chat_id, user_id)
        
        # Проверяем, есть ли у пользователя NC
        if balance['neon_coins'] <= 0:
            await callback_query.answer(f"❌ {lang.get('economy_no_nc', 'У вас нет NC')}!", show_alert=True)
            return
        
        group_currency = await EconomyDB.get_group_currency(chat_id)
        
        currency_symbol = group_currency["currency_symbol"]
        exchange_rate = group_currency["exchange_rate_to_nc"]
        
        # Создаем кнопки с предустановленными суммами
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("10", callback_data=f"economy_convert_group_amount_{chat_id}_10"),
                InlineKeyboardButton("50", callback_data=f"economy_convert_group_amount_{chat_id}_50"),
                InlineKeyboardButton("100", callback_data=f"economy_convert_group_amount_{chat_id}_100")
            ],
            [
                InlineKeyboardButton("500", callback_data=f"economy_convert_group_amount_{chat_id}_500"),
                InlineKeyboardButton("1000", callback_data=f"economy_convert_group_amount_{chat_id}_1000"),
                InlineKeyboardButton(lang.get('economy_all', 'Все'), callback_data=f"economy_convert_group_amount_{chat_id}_all")
            ],
            [
                InlineKeyboardButton(
                    f"🔙 {lang.get('economy_back')}",
                    callback_data=f"economy_convert_{chat_id}"
                )
            ]
        ])
        
        text = f"""
🔄 <b>{lang.get('economy_convert_to_group', 'Конвертация')} NC → {currency_symbol}</b>

💰 <b>{lang.get('economy_your_balance')}:</b>
• {currency_symbol}: <code>{balance['group_currency']:.2f}</code>
• NC: <code>{balance['neon_coins']:.2f}</code>

📈 <b>{lang.get('economy_exchange_rate_short')}:</b> 1 NC = {1/exchange_rate:.2f} {currency_symbol}

💡 <b>{lang.get('economy_select_amount', 'Выберите сумму для конвертации')}:</b>
        """
        
        logger.info(f"Showing convert to group menu for user {user_id} in chat {chat_id}")
        try:
            await callback_query.edit_message_text(text, reply_markup=keyboard)
        except Exception as edit_error:
            if "MESSAGE_NOT_MODIFIED" in str(edit_error):
                logger.debug(f"show_convert_to_group: Message not modified (same content), ignoring")
                await callback_query.answer()
            else:
                raise edit_error
    
    async def show_achievements(self, client: Client, callback_query: CallbackQuery):
        """Показать достижения"""
        await self.achievement_manager.show_achievements(client, callback_query)
    
    async def show_daily_bonus(self, client: Client, callback_query: CallbackQuery):
        """Показать ежедневный бонус"""
        await self.daily_bonus_manager.show_daily_bonus(client, callback_query)
    
    async def show_leaderboard(self, client: Client, callback_query: CallbackQuery):
        """Показать рейтинг (исключая всех ботов)"""
        chat_id = callback_query.message.chat.id
        user_id = callback_query.from_user.id
        lang_code = await get_group_language(chat_id)
        lang = load_language(lang_code)
        
        all_users = await EconomyDB.get_top_users(chat_id, 50)  # Получаем больше для фильтрации
        group_currency = await EconomyDB.get_group_currency(chat_id)
        
        currency_symbol = group_currency["currency_symbol"]
        
        text = f"""
🏆 <b>{lang.get('economy_leaderboard', 'Рейтинг пользователей')}</b>

💰 <b>{lang.get('economy_top_10_earners')}:</b>
        """
        
        real_users = []
        position = 1
        
        # Фильтруем всех ботов и получаем только реальных пользователей
        for user_data in all_users:
            if position > 10:  # Ограничиваем топ-10
                break
                
            try:
                user = await client.get_users(user_data["user_id"])
                
                # Исключаем всех ботов
                if user.is_bot:
                    continue
                
                # Проверяем, что у пользователя есть заработанные средства
                if user_data.get('total_earned', 0) <= 0:
                    continue
                
                username = user.username or user.first_name
                real_users.append({
                    'position': position,
                    'username': username,
                    'total_earned': user_data['total_earned']
                })
                position += 1
                
            except Exception as e:
                # Пропускаем пользователей, которых не можем получить
                continue
        
        # Формируем текст рейтинга
        if not real_users:
            text += f"\n\n📝 <i>{lang.get('economy_no_users')}</i>"
        else:
            for user_info in real_users:
                text += f"\n{user_info['position']}. <b>{user_info['username']}</b> - <code>{user_info['total_earned']:,}</code> {currency_symbol}"
        
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton(
                    f"🔙 {lang.get('economy_back')}",
                    callback_data=f"economy_back_{chat_id}"
                )
            ]
        ])
        
        await callback_query.edit_message_text(text, reply_markup=keyboard)
    
    async def show_profile(self, client: Client, callback_query: CallbackQuery):
        """Показать профиль"""
        await self.profile_manager.show_profile(client, callback_query)
    
    async def show_settings(self, client: Client, callback_query: CallbackQuery):
        """Показать настройки"""
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
        
        group_currency = await EconomyDB.get_group_currency(chat_id)
        
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton(
                    f"📊 {lang.get('economy_update_rate')}",
                    callback_data=f"economy_update_rate_{chat_id}"
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
⚙️ <b>{lang.get('economy_settings')}</b>

🏦 <b>{lang.get('economy_group_currency')}:</b> {group_currency['currency_name']} ({group_currency['currency_symbol']})
📈 <b>{lang.get('economy_rate_to_nc')}:</b> {group_currency['exchange_rate_to_nc']:.2f}
📊 <b>{lang.get('economy_group_activity')}:</b> {group_currency['daily_activity_score']}
🕐 <b>{lang.get('economy_last_update')}:</b> {group_currency['last_rate_update'].strftime('%d.%m.%Y %H:%M')}
        """
        
        await callback_query.edit_message_text(text, reply_markup=keyboard)
    
    async def show_create_currency(self, client: Client, callback_query: CallbackQuery):
        """Показать создание валюты"""
        await self.currency_manager.show_create_currency(client, callback_query)
    
    async def show_edit_currency(self, client: Client, callback_query: CallbackQuery):
        """Показать редактирование валюты"""
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
        
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton(
                    f"🔙 {lang.get('economy_back')}",
                    callback_data=f"economy_create_currency_{chat_id}"
                )
            ]
        ])
        
        text = f"""
✏️ <b>{lang.get('economy_edit_currency_title')}</b>

⚠️ <b>{lang.get('economy_important')}:</b> {lang.get('economy_currency_cannot_change')}

{lang.get('economy_to_change_currency')}:
1. {lang.get('economy_delete_current')}
2. {lang.get('economy_create_new')}

{lang.get('economy_will_delete_data')}
        """
        
        await callback_query.edit_message_text(text, reply_markup=keyboard)
    
    async def show_delete_currency(self, client: Client, callback_query: CallbackQuery):
        """Показать подтверждение удаления валюты"""
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
        
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton(
                    f"✅ {lang.get('economy_confirm_delete')}",
                    callback_data=f"economy_confirm_delete_{chat_id}"
                ),
                InlineKeyboardButton(
                    f"❌ {lang.get('economy_cancel_delete')}",
                    callback_data=f"economy_create_currency_{chat_id}"
                )
            ]
        ])
        
        text = f"""
🗑️ <b>{lang.get('economy_delete_currency_title')}</b>

⚠️ <b>{lang.get('economy_warning')}</b> {lang.get('economy_this_action')}:
• {lang.get('economy_delete_currency_forever')}
• {lang.get('economy_delete_user_balances')}
• {lang.get('economy_delete_transaction_history')}
• {lang.get('economy_delete_user_achievements')}

❌ <b>{lang.get('economy_action_irreversible')}</b>

{lang.get('economy_confirm_delete_question')}
        """
        
        await callback_query.edit_message_text(text, reply_markup=keyboard)
    
    async def confirm_delete_currency(self, client: Client, callback_query: CallbackQuery):
        """Подтвердить удаление валюты"""
        chat_id = int(callback_query.data.split("_")[-1])
        user_id = callback_query.from_user.id
        lang_code = await get_group_language(chat_id)
        lang = load_language(lang_code)
        
        # Удаляем валюту
        success, message = await self.currency_manager.delete_currency(chat_id, user_id)
        
        if success:
            await callback_query.answer(f"✅ {lang.get('economy_currency_deleted')}")
            # Возвращаемся к главному меню
            await self.show_main_menu(client, callback_query.message)
        else:
            await callback_query.answer(f"❌ {message}")
    
    async def show_info(self, client: Client, callback_query: CallbackQuery):
        """Показать информацию"""
        chat_id = callback_query.message.chat.id
        lang_code = await get_group_language(chat_id)
        lang = load_language(lang_code)
        
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton(
                    f"🔙 {lang.get('economy_back')}",
                    callback_data=f"economy_back_{chat_id}"
                )
            ]
        ])
        
        text = f"""
ℹ️ <b>{lang.get('economy_info_title')}</b>

💰 <b>{lang.get('economy_main_features')}:</b>
• {lang.get('economy_create_group_currency')} ({lang.get('economy_max_4_symbols')})
• {lang.get('economy_daily_bonuses')}
• {lang.get('economy_achievements_system')}
• {lang.get('economy_currency_conversion')}
• {lang.get('economy_leaderboard')}

🔄 <b>{lang.get('economy_exchange_rate')}:</b>
• {lang.get('economy_auto_calculated')}
• {lang.get('economy_cannot_be_expensive')}
• {lang.get('economy_updates_daily')}

🎯 <b>{lang.get('economy_how_to_earn')}:</b>
• {lang.get('economy_daily_bonuses')}
• {lang.get('economy_complete_achievements')}
• {lang.get('economy_participate_games')}
        """
        
        await callback_query.edit_message_text(text, reply_markup=keyboard)
    
    async def handle_convert_nc_amount(self, client: Client, callback_query: CallbackQuery):
        """Обработчик конвертации групповой валюты в NC"""
        try:
            data = callback_query.data
            chat_id = callback_query.message.chat.id
            user_id = callback_query.from_user.id
            logger.info(f"Processing convert NC amount: {data} for user {user_id} in chat {chat_id}")
            
            # Загружаем язык
            lang_code = await get_group_language(chat_id)
            lang = load_language(lang_code)
            
            # Извлекаем chat_id и сумму из callback_data
            parts = data.split("_")
            chat_id_from_callback = int(parts[-2])  # Предпоследняя часть - это chat_id
            amount_str = parts[-1]  # Последняя часть - это сумма
            logger.info(f"Parsed callback data: parts={parts}, chat_id={chat_id_from_callback}, amount_str={amount_str}")
            
            # Проверяем, что chat_id совпадает (защита от пересылки сообщений)
            if chat_id_from_callback != chat_id:
                await callback_query.answer(f"❌ {lang.get('economy_wrong_chat_error', 'Ошибка: сообщение из другого чата')}!", show_alert=True)
                return
            
            # Получаем данные о валюте и балансе
            group_currency = await EconomyDB.get_group_currency(chat_id)
            if not group_currency:
                await callback_query.answer(f"❌ {lang.get('economy_not_setup', 'Валютная система не настроена')}!", show_alert=True)
                return
            
            balance = await EconomyDB.get_user_balance(chat_id, user_id)
            currency_symbol = group_currency["currency_symbol"]
            exchange_rate = group_currency["exchange_rate_to_nc"]
            
            # Определяем сумму для конвертации
            if amount_str == "all":
                amount = balance["group_currency"]
            else:
                try:
                    amount = float(amount_str)
                except ValueError:
                    await callback_query.answer(f"❌ {lang.get('economy_invalid_amount', 'Неверная сумма')}!", show_alert=True)
                    return
            
            # Проверяем достаточность средств
            if amount <= 0:
                await callback_query.answer(f"❌ {lang.get('economy_amount_zero_error', 'Сумма должна быть больше 0')}!", show_alert=True)
                return
            
            if balance["group_currency"] < amount:
                await callback_query.answer(f"❌ {lang.get('economy_insufficient_funds', 'Недостаточно средств')}! {lang.get('economy_your_balance', 'У вас')}: {balance['group_currency']:.2f} {currency_symbol}", show_alert=True)
                return
            
            # Рассчитываем количество NC
            nc_amount = amount * exchange_rate
            
            # Выполняем конвертацию
            success = await EconomyDB.convert_currency(
                chat_id, user_id, amount, nc_amount, 
                currency_symbol, "NC", "group_to_nc"
            )
            
            if success:
                await callback_query.answer(f"✅ {lang.get('economy_converted', 'Конвертировано')}: {amount:.2f} {currency_symbol} → {nc_amount:.2f} NC")
                # Показываем главное меню конвертации (обновлённый баланс загрузится из БД)
                try:
                    await self.show_conversion(client, callback_query)
                except Exception as e:
                    logger.error(f"Error showing conversion menu after conversion: {e}")
                    # хотя конвертация прошла, уведомим пользователя, если меню не обновилось
                    await callback_query.answer(f"✅ {lang.get('economy_conversion_success_menu_error', 'Конвертация выполнена, но не удалось обновить меню')}.", show_alert=True)
            else:
                await callback_query.answer(f"❌ {lang.get('economy_conversion_failed', 'Ошибка при конвертации')}!", show_alert=True)
                
        except Exception as e:
            logger.error(f"Error in handle_convert_nc_amount: {e}")
            await callback_query.answer(f"❌ {lang.get('economy_general_error', 'Произошла ошибка')}!", show_alert=True)
    
    async def handle_convert_group_amount(self, client: Client, callback_query: CallbackQuery):
        """Обработчик конвертации NC в групповую валюту"""
        try:
            data = callback_query.data
            chat_id = callback_query.message.chat.id
            user_id = callback_query.from_user.id
            logger.info(f"Processing convert group amount: {data} for user {user_id} in chat {chat_id}")
            
            # Загружаем язык
            lang_code = await get_group_language(chat_id)
            lang = load_language(lang_code)
            
            # Извлекаем chat_id и сумму из callback_data
            parts = data.split("_")
            chat_id_from_callback = int(parts[-2])  # Предпоследняя часть - это chat_id
            amount_str = parts[-1]  # Последняя часть - это сумма
            logger.info(f"Parsed callback data: parts={parts}, chat_id={chat_id_from_callback}, amount_str={amount_str}")
            
            # Проверяем, что chat_id совпадает (защита от пересылки сообщений)
            if chat_id_from_callback != chat_id:
                await callback_query.answer(f"❌ {lang.get('economy_wrong_chat_error', 'Ошибка: сообщение из другого чата')}!", show_alert=True)
                return
            
            # Получаем данные о валюте и балансе
            group_currency = await EconomyDB.get_group_currency(chat_id)
            if not group_currency:
                await callback_query.answer(f"❌ {lang.get('economy_not_setup', 'Валютная система не настроена')}!", show_alert=True)
                return
            
            balance = await EconomyDB.get_user_balance(chat_id, user_id)
            currency_symbol = group_currency["currency_symbol"]
            exchange_rate = group_currency["exchange_rate_to_nc"]
            
            # Определяем сумму для конвертации
            if amount_str == "all":
                amount = balance["neon_coins"]
            else:
                try:
                    amount = float(amount_str)
                except ValueError:
                    await callback_query.answer(f"❌ {lang.get('economy_invalid_amount', 'Неверная сумма')}!", show_alert=True)
                    return
            
            # Проверяем достаточность средств
            if amount <= 0:
                await callback_query.answer(f"❌ {lang.get('economy_amount_zero_error', 'Сумма должна быть больше 0')}!", show_alert=True)
                return
            
            if balance["neon_coins"] < amount:
                await callback_query.answer(f"❌ {lang.get('economy_insufficient_nc', 'Недостаточно NC')}! {lang.get('economy_your_balance', 'У вас')}: {balance['neon_coins']:.2f} NC", show_alert=True)
                return
            
            # Рассчитываем количество групповой валюты
            group_amount = amount / exchange_rate
            
            # Выполняем конвертацию
            success = await EconomyDB.convert_currency(
                chat_id, user_id, amount, group_amount, 
                "NC", currency_symbol, "nc_to_group"
            )
            
            if success:
                await callback_query.answer(f"✅ {lang.get('economy_converted', 'Конвертировано')}: {amount:.2f} NC → {group_amount:.2f} {currency_symbol}")
                try:
                    await self.show_conversion(client, callback_query)
                except Exception as e:
                    logger.error(f"Error showing conversion menu after conversion: {e}")
                    await callback_query.answer(f"✅ {lang.get('economy_conversion_success_menu_error', 'Конвертация выполнена, но не удалось обновить меню')}.", show_alert=True)
            else:
                await callback_query.answer(f"❌ {lang.get('economy_conversion_failed', 'Ошибка при конвертации')}!", show_alert=True)
                
        except Exception as e:
            logger.error(f"Error in handle_convert_group_amount: {e}")
            await callback_query.answer(f"❌ {lang.get('economy_general_error', 'Произошла ошибка')}!", show_alert=True)

# Создаем экземпляр менеджера
economy_manager = EconomyManager()

# Команда для входа в экономику
@app.on_message(filters.command("economy") & filters.group, group=20)
async def economy_command(client: Client, message: Message):
    """Команда для входа в экономическую систему"""
    await economy_manager.show_main_menu(client, message)

# Команда для просмотра профиля
@app.on_message(filters.command("profile") & filters.group, group=20)
async def profile_command(client: Client, message: Message):
    """Команда для просмотра профиля"""
    chat_id = message.chat.id
    user_id = message.from_user.id
    lang_code = await get_group_language(chat_id)
    lang = load_language(lang_code)
    
    # Проверяем, настроена ли экономическая система
    group_currency = await EconomyDB.get_group_currency(chat_id)
    if not group_currency:
        return await message.reply(
            f"<blockquote>{lang.get('economy_not_setup')}</blockquote>"
        )
    
    # Показываем профиль через ProfileManager
    from .profile import ProfileManager
    profile_manager = ProfileManager()
    
    # Создаем фиктивный callback_query для использования существующего метода
    class FakeCallbackQuery:
        def __init__(self, message, chat_id):
            self.message = message
            self.data = f"economy_profile_{chat_id}"
    
    fake_callback = FakeCallbackQuery(message, chat_id)
    await profile_manager.show_profile(client, fake_callback)

# Обработчик callback запросов
@app.on_callback_query(filters.regex("^economy_"), group=20)
async def economy_callback_handler(client: Client, callback_query: CallbackQuery):
    """Обработчик callback запросов экономики"""
    try:
        await economy_manager.handle_callback(client, callback_query)
    except Exception as e:
        error_message = str(e)
        if "MESSAGE_NOT_MODIFIED" in error_message:
            # Игнорируем ошибку, если сообщение не изменилось
            logger.debug(f"Message not modified (ignored): {error_message}")
            await callback_query.answer()
        else:
            logger.error(f"Error in economy callback handler: {e}")
            try:
                await callback_query.answer("Произошла ошибка!", show_alert=True)
            except:
                pass

# Конвертация валют происходит только через инлайн-кнопки в интерфейсе
# Команды конвертации удалены по запросу пользователя

"""
Daily Bonus System Module
Модуль системы ежедневных бонусов
"""

import logging
import random
from datetime import datetime, timedelta
from pyrogram import Client, filters
from pyrogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from config import app
from language import load_language, get_group_language
from .database import EconomyDB

logger = logging.getLogger(__name__)

class DailyBonusManager:
    """Менеджер ежедневных бонусов"""
    
    async def show_daily_bonus(self, client: Client, callback_query: CallbackQuery):
        """Показать ежедневный бонус"""
        chat_id = callback_query.message.chat.id
        user_id = callback_query.from_user.id
        lang_code = await get_group_language(chat_id)
        lang = load_language(lang_code)
        
        # Проверяем, может ли пользователь получить бонус
        can_claim = await EconomyDB.can_claim_daily_bonus(chat_id, user_id)
        
        balance = await EconomyDB.get_user_balance(chat_id, user_id)
        group_currency = await EconomyDB.get_group_currency(chat_id)
        
        if not group_currency:
            return await callback_query.answer(
                lang.get('economy_not_setup')
            )
        
        currency_symbol = group_currency["currency_symbol"]
        
        if can_claim:
            # Показываем возможность получить бонус
            bonus_amount = await self.calculate_bonus_amount(chat_id, user_id)
            
            keyboard = InlineKeyboardMarkup([
                [
                    InlineKeyboardButton(
                        f"🎁 {lang.get('economy_claim_bonus')}",
                        callback_data=f"economy_claim_bonus_{chat_id}"
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
🎁 <b>{lang.get('economy_daily_bonus_title')}</b>

💰 <b>{lang.get('economy_today_bonus')}:</b> <code>{bonus_amount:,}</code> {currency_symbol}

🎯 <b>{lang.get('economy_how_to_increase')}:</b>
• {lang.get('economy_be_active')}
• {lang.get('economy_participate')}
• {lang.get('economy_complete_achievements')}

📊 <b>{lang.get('economy_current_balance')}:</b>
• {currency_symbol}: <code>{balance['group_currency']:.2f}</code>
• NC: <code>{balance['neon_coins']:.2f}</code>

{lang.get('economy_click_button_bonus')}
            """
        else:
            # Показываем время до следующего бонуса
            last_bonus = balance.get("last_daily_bonus")
            if last_bonus:
                next_bonus_time = last_bonus + timedelta(hours=24)
                time_left = next_bonus_time - datetime.utcnow()
                
                hours_left = int(time_left.total_seconds() // 3600)
                minutes_left = int((time_left.total_seconds() % 3600) // 60)
                
                keyboard = InlineKeyboardMarkup([
                    [
                        InlineKeyboardButton(
                            f"🔙 {lang.get('economy_back')}",
                            callback_data=f"economy_back_{chat_id}"
                        )
                    ]
                ])
                
                text = f"""
🎁 <b>{lang.get('economy_daily_bonus_title')}</b>

⏰ <b>{lang.get('economy_next_bonus_in')}:</b> {hours_left}{lang.get('economy_bonus_hours')} {minutes_left}{lang.get('economy_bonus_minutes')}

📊 <b>{lang.get('economy_current_balance')}:</b>
• {currency_symbol}: <code>{balance['group_currency']:.2f}</code>
• NC: <code>{balance['neon_coins']:.2f}</code>

🔄 <b>{lang.get('economy_last_bonus_short')}:</b> {last_bonus.strftime('%d.%m.%Y %H:%M')}

{lang.get('economy_come_back_tomorrow')}
                """
            else:
                # Первый бонус
                keyboard = InlineKeyboardMarkup([
                    [
                        InlineKeyboardButton(
                            f"🎁 {lang.get('economy_claim_bonus')}",
                            callback_data=f"economy_claim_bonus_{chat_id}"
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
🎁 <b>{lang.get('economy_daily_bonus_title')}</b>

🎉 <b>{lang.get('economy_welcome_economy')}</b>

💰 <b>{lang.get('economy_first_bonus')}:</b> <code>100</code> {currency_symbol}

📊 <b>{lang.get('economy_current_balance')}:</b>
• {currency_symbol}: <code>{balance['group_currency']:.2f}</code>
• NC: <code>{balance['neon_coins']:.2f}</code>

{lang.get('economy_get_first_bonus')}
                """
        
        await callback_query.edit_message_text(text, reply_markup=keyboard)
    
    async def claim_daily_bonus(self, chat_id: int, user_id: int) -> tuple[bool, str, int]:
        """Выдать ежедневный бонус"""
        # Получаем язык группы
        lang_code = await get_group_language(chat_id)
        lang = load_language(lang_code)
        
        # Проверяем, может ли пользователь получить бонус
        can_claim = await EconomyDB.can_claim_daily_bonus(chat_id, user_id)
        
        if not can_claim:
            return False, lang.get('economy_bonus_already_claimed'), 0
        
        # Рассчитываем размер бонуса
        bonus_amount = await self.calculate_bonus_amount(chat_id, user_id)
        
        # Выдаем бонус
        await EconomyDB.claim_daily_bonus(chat_id, user_id, bonus_amount)
        
        # Отслеживаем активность группы
        from .auto_updater import track_daily_bonus_activity
        await track_daily_bonus_activity(chat_id)
        
        # Проверяем достижения
        from .achievements import AchievementManager
        achievement_manager = AchievementManager()
        await achievement_manager.check_achievements(chat_id, user_id, "daily_bonus")
        
        return True, lang.get('economy_bonus_claimed').format(amount=bonus_amount), bonus_amount
    
    async def calculate_bonus_amount(self, chat_id: int, user_id: int) -> int:
        """Рассчитать размер бонуса"""
        # Базовый бонус
        base_bonus = 50
        
        # Бонус за активность группы
        group_currency = await EconomyDB.get_group_currency(chat_id)
        activity_score = group_currency.get("daily_activity_score", 0)
        activity_bonus = min(activity_score // 10, 50)  # Максимум +50 за активность
        
        # Бонус за достижения
        achievements = await EconomyDB.get_user_achievements(chat_id, user_id)
        achievement_bonus = len(achievements) * 5  # +5 за каждое достижение
        
        # Случайный бонус
        random_bonus = random.randint(0, 25)
        
        # Общий бонус
        total_bonus = base_bonus + activity_bonus + achievement_bonus + random_bonus
        
        return total_bonus
    
    async def update_group_activity(self, chat_id: int, activity_points: int):
        """Обновить активность группы"""
        await EconomyDB.update_activity_score(chat_id, activity_points)
    
    async def get_bonus_info(self, chat_id: int, user_id: int) -> dict:
        """Получить информацию о бонусе"""
        can_claim = await EconomyDB.can_claim_daily_bonus(chat_id, user_id)
        balance = await EconomyDB.get_user_balance(chat_id, user_id)
        
        info = {
            "can_claim": can_claim,
            "last_bonus": balance.get("last_daily_bonus"),
            "next_bonus_time": None
        }
        
        if not can_claim and balance.get("last_daily_bonus"):
            next_bonus_time = balance["last_daily_bonus"] + timedelta(hours=24)
            info["next_bonus_time"] = next_bonus_time
        
        return info

# Обработчик для получения бонуса
@app.on_callback_query(filters.regex("^economy_claim_bonus_"), group=20)
async def claim_bonus_callback(client: Client, callback_query: CallbackQuery):
    """Обработчик получения ежедневного бонуса"""
    try:
        chat_id = int(callback_query.data.split("_")[-1])
        user_id = callback_query.from_user.id
        
        daily_bonus_manager = DailyBonusManager()
        success, message, bonus_amount = await daily_bonus_manager.claim_daily_bonus(chat_id, user_id)
        
        if success:
            await callback_query.answer(f"✅ {message}")
            # Обновляем меню
            await daily_bonus_manager.show_daily_bonus(client, callback_query)
        else:
            await callback_query.answer(f"❌ {message}")
            
    except Exception as e:
        logger.error(f"Error in claim bonus callback: {e}")
        # Получаем язык группы для ошибки
        try:
            lang_code = await get_group_language(chat_id)
            lang = load_language(lang_code)
            await callback_query.answer(lang.get('economy_error_occurred'))
        except:
            await callback_query.answer('Произошла ошибка!')

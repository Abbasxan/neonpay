"""
Profile Management Module
Модуль управления профилями
"""

import logging
from datetime import datetime, timedelta
from pyrogram import Client
from pyrogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from config import app
from language import load_language, get_group_language
from .database import EconomyDB

logger = logging.getLogger(__name__)

class ProfileManager:
    """Менеджер профилей"""
    
    async def show_profile(self, client: Client, callback_query: CallbackQuery):
        """Показать профиль пользователя"""
        try:
            chat_id = callback_query.message.chat.id
            user_id = callback_query.from_user.id
            lang_code = await get_group_language(chat_id)
            lang = load_language(lang_code)
            
            # Получаем данные пользователя
            try:
                user = await client.get_users(user_id)
            except Exception as e:
                logger.error(f"Error getting user: {e}")
                await callback_query.answer(lang.get('economy_user_data_error', 'Ошибка получения данных пользователя'))
                return
            
            # Получаем баланс
            balance = await EconomyDB.get_user_balance(chat_id, user_id)
            group_currency = await EconomyDB.get_group_currency(chat_id)
            
            # Отладочная информация
            logger.info(f"Profile balance for user {user_id} in chat {chat_id}: GG={balance.get('group_currency', 0):.2f}, NC={balance.get('neon_coins', 0):.2f}, Total={balance.get('total_earned', 0):.2f}")
            
            if not group_currency:
                await callback_query.answer(lang.get('economy_not_setup', 'Экономическая система не настроена в этой группе'))
                return
            
            currency_symbol = group_currency["currency_symbol"]
            currency_name = group_currency["currency_name"]
            
            # Получаем достижения
            achievements = await EconomyDB.get_user_achievements(chat_id, user_id)
            
            # Рассчитываем статистику
            days_in_group = await self.calculate_days_in_group(chat_id, user_id)
            daily_earnings = balance.get('total_earned', 0) / max(days_in_group, 1)
            
            keyboard = InlineKeyboardMarkup([
                [
                    InlineKeyboardButton(
                        f"🏆 {lang.get('economy_achievements', 'Достижения')}",
                        callback_data=f"economy_achievements_{chat_id}"
                    )
                ],
                [
                    InlineKeyboardButton(
                        f"🔙 {lang.get('economy_back', 'Назад')}",
                        callback_data=f"economy_back_{chat_id}"
                    )
                ]
            ])
            
            # Формируем текст профиля с улучшенным форматированием
            text = f"""
👤 <b>{lang.get('economy_profile_title')}</b>

<b>{user.first_name}</b> {f'(@{user.username})' if user.username else ''}
🆔 ID: <code>{user_id}</code>

💰 <b>{lang.get('economy_finances')}:</b>
🏦 {currency_name} ({currency_symbol}): <code>{balance.get('group_currency', 0):.2f}</code>
💎 Neon Coins (NC): <code>{balance.get('neon_coins', 0):.2f}</code>
📈 {lang.get('economy_total_earned')}: <code>{balance.get('total_earned', 0):.2f}</code> {currency_symbol}

📊 <b>{lang.get('economy_activity_stats')}:</b>
📅 {lang.get('economy_days_in_group')}: <code>{days_in_group}</code>
💹 {lang.get('economy_daily_earnings')}: <code>{daily_earnings:.1f}</code> {currency_symbol}
🏆 {lang.get('economy_achievements_count')}: <code>{len(achievements)}</code>

🎯 <b>{lang.get('economy_recent_achievements')}:</b>
            """
            
            # Добавляем последние достижения
            recent_achievements = achievements[-3:] if achievements else []
            if recent_achievements:
                for achievement in recent_achievements:
                    achievement_id = achievement['achievement_id']
                    reward_amount = achievement['reward_amount']
                    reward_currency = achievement['reward_currency']
                    earned_date = achievement.get('earned_at', datetime.utcnow())
                    
                    # Форматируем дату
                    date_str = earned_date.strftime('%d.%m.%Y')
                    
                    text += f"\n🏅 {achievement_id} (+{reward_amount} {reward_currency}) - {date_str}"
            else:
                text += f"\n📝 <i>{lang.get('economy_no_achievements', 'Пока нет достижений')}</i>"
            
            # Отправляем профиль
            await callback_query.edit_message_text(text, reply_markup=keyboard)
            
        except Exception as e:
            logger.error(f"Error in show_profile: {e}")
            try:
                # Получаем язык для сообщения об ошибке
                lang_code = await get_group_language(chat_id)
                lang = load_language(lang_code)
                await callback_query.answer(lang.get('economy_profile_error', 'Произошла ошибка при загрузке профиля'), show_alert=True)
            except:
                # Если не удается получить язык, используем дефолтное сообщение
                try:
                    await callback_query.answer("Произошла ошибка при загрузке профиля", show_alert=True)
                except:
                    pass
    
    async def calculate_days_in_group(self, chat_id: int, user_id: int) -> int:
        """Рассчитать количество дней в группе"""
        try:
            # Получаем информацию о пользователе в группе
            from config import app
            member = await app.get_chat_member(chat_id, user_id)
            
            # Если пользователь в группе, считаем с момента присоединения
            if member.status in ["member", "administrator", "creator"]:
                # Примерная дата присоединения (можно улучшить, если есть доступ к истории)
                return 30  # По умолчанию 30 дней
            else:
                return 0
        except Exception as e:
            logger.error(f"Error calculating days in group: {e}")
            return 0
    
    async def get_user_stats(self, chat_id: int, user_id: int) -> dict:
        """Получить статистику пользователя"""
        balance = await EconomyDB.get_user_balance(chat_id, user_id)
        achievements = await EconomyDB.get_user_achievements(chat_id, user_id)
        
        # Получаем транзакции пользователя
        transactions = await self.get_user_transactions(chat_id, user_id, limit=10)
        
        return {
            "balance": balance,
            "achievements_count": len(achievements),
            "recent_transactions": transactions,
            "days_in_group": await self.calculate_days_in_group(chat_id, user_id)
        }
    
    async def get_user_transactions(self, chat_id: int, user_id: int, limit: int = 10) -> list:
        """Получить последние транзакции пользователя"""
        try:
            from config import db
            cursor = db.economy_transactions.find(
                {"chat_id": chat_id, "user_id": user_id}
            ).sort("timestamp", -1).limit(limit)
            
            transactions = await cursor.to_list(length=limit)
            return transactions
        except Exception as e:
            logger.error(f"Error getting user transactions: {e}")
            return []
    
    async def format_transaction(self, transaction: dict) -> str:
        """Форматировать транзакцию для отображения"""
        transaction_type = transaction.get("type", "unknown")
        amount = transaction.get("amount", 0)
        currency = transaction.get("currency", "")
        description = transaction.get("description", "")
        timestamp = transaction.get("timestamp", datetime.utcnow())
        
        # Форматируем время
        time_str = timestamp.strftime("%d.%m %H:%M")
        
        # Определяем эмодзи для типа транзакции
        type_emoji = {
            "daily_bonus": "🎁",
            "achievement": "🏆",
            "conversion": "🔄",
            "game_win": "🎮",
            "admin_gift": "🎁"
        }.get(transaction_type, "💰")
        
        return f"{type_emoji} {time_str}: {amount} {currency} - {description}"

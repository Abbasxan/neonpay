"""
Achievement System Module
Модуль системы достижений
"""

import logging
from datetime import datetime, timedelta
from pyrogram import Client
from pyrogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from config import app
from language import load_language, get_group_language
from .database import EconomyDB

logger = logging.getLogger(__name__)

class AchievementManager:
    """Менеджер достижений"""
    
    # Определяем достижения (названия и описания будут переведены динамически)
    ACHIEVEMENTS = {
        # === ОСНОВНЫЕ ДОСТИЖЕНИЯ ===
        "first_bonus": {
            "name_key": "achievement_first_bonus",
            "description_key": "achievement_first_bonus_desc",
            "reward_amount": 50,
            "reward_currency": "group",
            "emoji": "🎁"
        },
        "first_conversion": {
            "name_key": "achievement_first_conversion",
            "description_key": "achievement_first_conversion_desc",
            "reward_amount": 25,
            "reward_currency": "nc",
            "emoji": "🔄"
        },
        
        # === СЕРИИ ЕЖЕДНЕВНЫХ БОНУСОВ ===
        "week_streak": {
            "name_key": "achievement_week_streak",
            "description_key": "achievement_week_streak_desc",
            "reward_amount": 200,
            "reward_currency": "group",
            "emoji": "🔥"
        },
        "month_streak": {
            "name_key": "achievement_month_streak",
            "description_key": "achievement_month_streak_desc",
            "reward_amount": 1000,
            "reward_currency": "group",
            "emoji": "🏆"
        },
        "year_streak": {
            "name_key": "achievement_year_streak",
            "description_key": "achievement_year_streak_desc",
            "reward_amount": 5000,
            "reward_currency": "nc",
            "emoji": "💯"
        },
        
        # === БОГАТСТВО И НАКОПЛЕНИЯ ===
        "rich_user": {
            "name_key": "achievement_rich_user",
            "description_key": "achievement_rich_user_desc",
            "reward_amount": 100,
            "reward_currency": "nc",
            "emoji": "💰"
        },
        "millionaire": {
            "name_key": "achievement_millionaire",
            "description_key": "achievement_millionaire_desc",
            "reward_amount": 500,
            "reward_currency": "nc",
            "emoji": "💸"
        },
        "billionaire": {
            "name_key": "achievement_billionaire",
            "description_key": "achievement_billionaire_desc",
            "reward_amount": 1000,
            "reward_currency": "nc",
            "emoji": "🏦"
        },
        "neon_collector": {
            "name_key": "achievement_neon_collector",
            "description_key": "achievement_neon_collector_desc",
            "reward_amount": 200,
            "reward_currency": "nc",
            "emoji": "💎"
        },
        "neon_master": {
            "name_key": "achievement_neon_master",
            "description_key": "achievement_neon_master_desc",
            "reward_amount": 1000,
            "reward_currency": "nc",
            "emoji": "💠"
        },
        
        # === АКТИВНОСТЬ И ЗАРАБОТОК ===
        "active_member": {
            "name_key": "achievement_active_member",
            "description_key": "achievement_active_member_desc",
            "reward_amount": 300,
            "reward_currency": "group",
            "emoji": "⭐"
        },
        "super_earner": {
            "name_key": "achievement_super_earner",
            "description_key": "achievement_super_earner_desc",
            "reward_amount": 500,
            "reward_currency": "nc",
            "emoji": "💪"
        },
        "money_magnet": {
            "name_key": "achievement_money_magnet",
            "description_key": "achievement_money_magnet_desc",
            "reward_amount": 800,
            "reward_currency": "nc",
            "emoji": "🧲"
        },
        
        # === КОНВЕРТАЦИИ ===
        "conversion_master": {
            "name_key": "achievement_conversion_master",
            "description_key": "achievement_conversion_master_desc",
            "reward_amount": 150,
            "reward_currency": "nc",
            "emoji": "🔄"
        },
        "currency_trader": {
            "name_key": "achievement_currency_trader",
            "description_key": "achievement_currency_trader_desc",
            "reward_amount": 300,
            "reward_currency": "nc",
            "emoji": "📈"
        },
        
        # === РЕЙТИНГИ И СОРЕВНОВАНИЯ ===
        "top_earner": {
            "name_key": "achievement_top_earner",
            "description_key": "achievement_top_earner_desc",
            "reward_amount": 500,
            "reward_currency": "nc",
            "emoji": "👑"
        },
        "top_3": {
            "name_key": "achievement_top_3",
            "description_key": "achievement_top_3_desc",
            "reward_amount": 300,
            "reward_currency": "nc",
            "emoji": "🥉"
        },
        "top_10": {
            "name_key": "achievement_top_10",
            "description_key": "achievement_top_10_desc",
            "reward_amount": 150,
            "reward_currency": "nc",
            "emoji": "🔟"
        },
        "leaderboard_legend": {
            "name_key": "achievement_leaderboard_legend",
            "description_key": "achievement_leaderboard_legend_desc",
            "reward_amount": 1000,
            "reward_currency": "nc",
            "emoji": "🏅"
        },
        
        # === СПЕЦИАЛЬНЫЕ ДОСТИЖЕНИЯ ===
        "early_bird": {
            "name_key": "achievement_early_bird",
            "description_key": "achievement_early_bird_desc",
            "reward_amount": 100,
            "reward_currency": "nc",
            "emoji": "🐦"
        },
        "night_owl": {
            "name_key": "achievement_night_owl",
            "description_key": "achievement_night_owl_desc",
            "reward_amount": 100,
            "reward_currency": "nc",
            "emoji": "🦉"
        },
        "lucky_streak": {
            "name_key": "achievement_lucky_streak",
            "description_key": "achievement_lucky_streak_desc",
            "reward_amount": 200,
            "reward_currency": "nc",
            "emoji": "🍀"
        },
        "persistent": {
            "name_key": "achievement_persistent",
            "description_key": "achievement_persistent_desc",
            "reward_amount": 400,
            "reward_currency": "nc",
            "emoji": "💪"
        },
        
        # === МАСТЕРСТВО ===
        "achievement_hunter": {
            "name_key": "achievement_achievement_hunter",
            "description_key": "achievement_achievement_hunter_desc",
            "reward_amount": 500,
            "reward_currency": "nc",
            "emoji": "🎯"
        },
        "completionist": {
            "name_key": "achievement_completionist",
            "description_key": "achievement_completionist_desc",
            "reward_amount": 2000,
            "reward_currency": "nc",
            "emoji": "🏆"
        },
        "economy_master": {
            "name_key": "achievement_economy_master",
            "description_key": "achievement_economy_master_desc",
            "reward_amount": 1500,
            "reward_currency": "nc",
            "emoji": "🎖️"
        },
        
        # === ВРЕМЕННЫЕ ДОСТИЖЕНИЯ ===
        "daily_warrior": {
            "name_key": "achievement_daily_warrior",
            "description_key": "achievement_daily_warrior_desc",
            "reward_amount": 100,
            "reward_currency": "nc",
            "emoji": "⚔️"
        },
        "weekly_champion": {
            "name_key": "achievement_weekly_champion",
            "description_key": "achievement_weekly_champion_desc",
            "reward_amount": 300,
            "reward_currency": "nc",
            "emoji": "🏆"
        },
        "monthly_legend": {
            "name_key": "achievement_monthly_legend",
            "description_key": "achievement_monthly_legend_desc",
            "reward_amount": 800,
            "reward_currency": "nc",
            "emoji": "🌟"
        }
    }
    
    async def show_achievements(self, client: Client, callback_query: CallbackQuery):
        """Показать достижения пользователя"""
        chat_id = callback_query.message.chat.id
        user_id = callback_query.from_user.id
        lang_code = await get_group_language(chat_id)
        lang = load_language(lang_code)
        
        # Получаем достижения пользователя
        user_achievements = await EconomyDB.get_user_achievements(chat_id, user_id)
        earned_achievement_ids = {ach["achievement_id"] for ach in user_achievements}
        
        # Получаем баланс для проверки условий
        balance = await EconomyDB.get_user_balance(chat_id, user_id)
        group_currency = await EconomyDB.get_group_currency(chat_id)
        
        if not group_currency:
            return await callback_query.answer(
                lang.get('economy_not_setup')
            )
        
        currency_symbol = group_currency["currency_symbol"]
        
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton(
                    f"🔙 {lang.get('economy_back')}",
                    callback_data=f"economy_back_{chat_id}"
                )
            ]
        ])
        
        text = f"""
🏆 <b>{lang.get('economy_achievements_title')}</b>

📊 <b>{lang.get('achievement_progress')}:</b> {len(earned_achievement_ids)}/{len(self.ACHIEVEMENTS)}

<b>{lang.get('achievement_earned')}:</b>
        """
        
        # Показываем полученные достижения
        for achievement_id, achievement_data in self.ACHIEVEMENTS.items():
            if achievement_id in earned_achievement_ids:
                name = lang.get(achievement_data['name_key'], achievement_data['name_key'])
                description = lang.get(achievement_data['description_key'], achievement_data['description_key'])
                text += f"\n✅ {achievement_data['emoji']} <b>{name}</b>"
                text += f"\n   {description}"
                text += f"\n   {lang.get('achievement_reward')}: {achievement_data['reward_amount']} {achievement_data['reward_currency'].upper()}"
        
        text += f"\n\n<b>{lang.get('achievement_available')}:</b>"
        
        # Показываем недоступные достижения
        for achievement_id, achievement_data in self.ACHIEVEMENTS.items():
            if achievement_id not in earned_achievement_ids:
                name = lang.get(achievement_data['name_key'], achievement_data['name_key'])
                description = lang.get(achievement_data['description_key'], achievement_data['description_key'])
                text += f"\n❌ {achievement_data['emoji']} <b>{name}</b>"
                text += f"\n   {description}"
                text += f"\n   {lang.get('achievement_reward')}: {achievement_data['reward_amount']} {achievement_data['reward_currency'].upper()}"
        
        await callback_query.edit_message_text(text, reply_markup=keyboard)
    
    async def check_achievements(self, chat_id: int, user_id: int, action: str, **kwargs):
        """Проверить и выдать достижения"""
        user_achievements = await EconomyDB.get_user_achievements(chat_id, user_id)
        earned_achievement_ids = {ach["achievement_id"] for ach in user_achievements}
        
        balance = await EconomyDB.get_user_balance(chat_id, user_id)
        
        # Добавляем chat_id и user_id в kwargs для передачи в методы проверки
        kwargs.update({"chat_id": chat_id, "user_id": user_id})
        
        # Проверяем каждое достижение
        for achievement_id, achievement_data in self.ACHIEVEMENTS.items():
            if achievement_id in earned_achievement_ids:
                continue  # Уже получено
            
            if await self.check_achievement_condition(achievement_id, action, balance, **kwargs):
                await self.give_achievement(chat_id, user_id, achievement_id, achievement_data)
    
    async def check_achievement_condition(self, achievement_id: str, action: str, balance: dict, **kwargs) -> bool:
        """Проверить условие достижения"""
        chat_id = kwargs.get("chat_id")
        user_id = kwargs.get("user_id")
        
        # === ОСНОВНЫЕ ДОСТИЖЕНИЯ ===
        if achievement_id == "first_bonus" and action == "daily_bonus":
            return True
        elif achievement_id == "first_conversion" and action == "conversion":
            return True
        
        # === СЕРИИ ЕЖЕДНЕВНЫХ БОНУСОВ ===
        elif achievement_id == "week_streak":
            return await self.check_daily_bonus_streak(chat_id, user_id, 7)
        elif achievement_id == "month_streak":
            return await self.check_daily_bonus_streak(chat_id, user_id, 30)
        elif achievement_id == "year_streak":
            return await self.check_daily_bonus_streak(chat_id, user_id, 365)
        
        # === БОГАТСТВО И НАКОПЛЕНИЯ ===
        elif achievement_id == "rich_user" and balance.get("group_currency", 0) >= 1000:
            return True
        elif achievement_id == "millionaire" and balance.get("group_currency", 0) >= 1000000:
            return True
        elif achievement_id == "billionaire" and balance.get("group_currency", 0) >= 1000000000:
            return True
        elif achievement_id == "neon_collector" and balance.get("neon_coins", 0) >= 500:
            return True
        elif achievement_id == "neon_master" and balance.get("neon_coins", 0) >= 10000:
            return True
        
        # === АКТИВНОСТЬ И ЗАРАБОТОК ===
        elif achievement_id == "active_member" and balance.get("total_earned", 0) >= 5000:
            return True
        elif achievement_id == "super_earner" and balance.get("total_earned", 0) >= 50000:
            return True
        elif achievement_id == "money_magnet" and balance.get("total_earned", 0) >= 100000:
            return True
        
        # === КОНВЕРТАЦИИ ===
        elif achievement_id == "conversion_master" and action == "conversion":
            return await self.check_conversion_count(chat_id, user_id, 10)
        elif achievement_id == "currency_trader" and action == "conversion":
            return await self.check_conversion_count(chat_id, user_id, 50)
        
        # === РЕЙТИНГИ И СОРЕВНОВАНИЯ ===
        elif achievement_id == "top_earner":
            return await self.check_leaderboard_position(chat_id, user_id, 1)
        elif achievement_id == "top_3":
            return await self.check_leaderboard_position(chat_id, user_id, 3)
        elif achievement_id == "top_10":
            return await self.check_leaderboard_position(chat_id, user_id, 10)
        elif achievement_id == "leaderboard_legend":
            return await self.check_leaderboard_position(chat_id, user_id, 1) and balance.get("total_earned", 0) >= 1000000
        
        # === СПЕЦИАЛЬНЫЕ ДОСТИЖЕНИЯ ===
        elif achievement_id == "early_bird" and action == "daily_bonus":
            return await self.check_time_based_achievement("early_bird")
        elif achievement_id == "night_owl" and action == "daily_bonus":
            return await self.check_time_based_achievement("night_owl")
        elif achievement_id == "lucky_streak" and action == "daily_bonus":
            return await self.check_lucky_streak(chat_id, user_id)
        elif achievement_id == "persistent" and action == "daily_bonus":
            return await self.check_daily_bonus_streak(chat_id, user_id, 100)
        
        # === МАСТЕРСТВО ===
        elif achievement_id == "achievement_hunter":
            return await self.check_achievement_count(chat_id, user_id, 10)
        elif achievement_id == "completionist":
            return await self.check_achievement_count(chat_id, user_id, len(self.ACHIEVEMENTS))
        elif achievement_id == "economy_master":
            return await self.check_economy_master(chat_id, user_id, balance)
        
        # === ВРЕМЕННЫЕ ДОСТИЖЕНИЯ ===
        elif achievement_id == "daily_warrior" and action == "daily_bonus":
            return await self.check_daily_warrior(chat_id, user_id)
        elif achievement_id == "weekly_champion" and action == "daily_bonus":
            return await self.check_weekly_champion(chat_id, user_id)
        elif achievement_id == "monthly_legend" and action == "daily_bonus":
            return await self.check_monthly_legend(chat_id, user_id)
        
        return False
    
    async def check_daily_bonus_streak(self, chat_id: int, user_id: int, required_days: int) -> bool:
        """Проверить серию ежедневных бонусов"""
        try:
            from config import db
            # Получаем последние записи о ежедневных бонусах
            cursor = db.daily_bonuses.find(
                {"chat_id": chat_id, "user_id": user_id}
            ).sort("date", -1).limit(required_days)
            
            bonuses = await cursor.to_list(length=required_days)
            if len(bonuses) < required_days:
                return False
            
            # Проверяем, что все бонусы получены подряд
            from datetime import datetime, timedelta
            today = datetime.now().date()
            
            for i, bonus in enumerate(bonuses):
                expected_date = today - timedelta(days=i)
                bonus_date = bonus["date"].date() if isinstance(bonus["date"], datetime) else bonus["date"]
                if bonus_date != expected_date:
                    return False
            
            return True
        except Exception as e:
            logger.error(f"Error checking daily bonus streak: {e}")
            return False
    
    async def check_conversion_count(self, chat_id: int, user_id: int, required_count: int) -> bool:
        """Проверить количество конвертаций"""
        try:
            from config import db
            count = await db.economy_transactions.count_documents({
                "chat_id": chat_id,
                "user_id": user_id,
                "type": "conversion"
            })
            return count >= required_count
        except Exception as e:
            logger.error(f"Error checking conversion count: {e}")
            return False
    
    async def check_leaderboard_position(self, chat_id: int, user_id: int, max_position: int) -> bool:
        """Проверить позицию в рейтинге"""
        try:
            top_users = await EconomyDB.get_top_users(chat_id, max_position)
            for i, user in enumerate(top_users):
                if user["user_id"] == user_id:
                    return i + 1 <= max_position
            return False
        except Exception as e:
            logger.error(f"Error checking leaderboard position: {e}")
            return False
    
    async def check_time_based_achievement(self, achievement_type: str) -> bool:
        """Проверить временные достижения"""
        from datetime import datetime
        current_hour = datetime.now().hour
        
        if achievement_type == "early_bird":
            return 6 <= current_hour < 10  # Ранняя птичка: 6-10 утра
        elif achievement_type == "night_owl":
            return 22 <= current_hour or current_hour < 2  # Ночная сова: 22-02
        return False
    
    async def check_lucky_streak(self, chat_id: int, user_id: int) -> bool:
        """Проверить счастливую серию (случайное достижение)"""
        import random
        return random.random() < 0.1  # 10% шанс
    
    async def check_achievement_count(self, chat_id: int, user_id: int, required_count: int) -> bool:
        """Проверить количество полученных достижений"""
        try:
            user_achievements = await EconomyDB.get_user_achievements(chat_id, user_id)
            return len(user_achievements) >= required_count
        except Exception as e:
            logger.error(f"Error checking achievement count: {e}")
            return False
    
    async def check_economy_master(self, chat_id: int, user_id: int, balance: dict) -> bool:
        """Проверить достижение мастера экономики"""
        try:
            # Нужно выполнить несколько условий одновременно
            conditions = [
                balance.get("group_currency", 0) >= 100000,
                balance.get("neon_coins", 0) >= 1000,
                balance.get("total_earned", 0) >= 500000,
                await self.check_conversion_count(chat_id, user_id, 25),
                await self.check_daily_bonus_streak(chat_id, user_id, 14)
            ]
            return all(conditions)
        except Exception as e:
            logger.error(f"Error checking economy master: {e}")
            return False
    
    async def check_daily_warrior(self, chat_id: int, user_id: int) -> bool:
        """Проверить достижение ежедневного воина"""
        try:
            from datetime import datetime, timedelta
            from config import db
            
            # Проверяем активность за последние 7 дней
            week_ago = datetime.now() - timedelta(days=7)
            count = await db.daily_bonuses.count_documents({
                "chat_id": chat_id,
                "user_id": user_id,
                "date": {"$gte": week_ago}
            })
            return count >= 7
        except Exception as e:
            logger.error(f"Error checking daily warrior: {e}")
            return False
    
    async def check_weekly_champion(self, chat_id: int, user_id: int) -> bool:
        """Проверить достижение недельного чемпиона"""
        try:
            from datetime import datetime, timedelta
            from config import db
            
            # Проверяем, что пользователь был в топе за последнюю неделю
            week_ago = datetime.now() - timedelta(days=7)
            
            # Получаем всех пользователей и их заработок за неделю
            pipeline = [
                {"$match": {"chat_id": chat_id, "date": {"$gte": week_ago}}},
                {"$group": {"_id": "$user_id", "total_earned": {"$sum": "$amount"}}},
                {"$sort": {"total_earned": -1}},
                {"$limit": 1}
            ]
            
            result = await db.daily_bonuses.aggregate(pipeline).to_list(1)
            if result and result[0]["_id"] == user_id:
                return True
            return False
        except Exception as e:
            logger.error(f"Error checking weekly champion: {e}")
            return False
    
    async def check_monthly_legend(self, chat_id: int, user_id: int) -> bool:
        """Проверить достижение месячной легенды"""
        try:
            from datetime import datetime, timedelta
            from config import db
            
            # Проверяем, что пользователь был в топе за последний месяц
            month_ago = datetime.now() - timedelta(days=30)
            
            # Получаем всех пользователей и их заработок за месяц
            pipeline = [
                {"$match": {"chat_id": chat_id, "date": {"$gte": month_ago}}},
                {"$group": {"_id": "$user_id", "total_earned": {"$sum": "$amount"}}},
                {"$sort": {"total_earned": -1}},
                {"$limit": 1}
            ]
            
            result = await db.daily_bonuses.aggregate(pipeline).to_list(1)
            if result and result[0]["_id"] == user_id:
                return True
            return False
        except Exception as e:
            logger.error(f"Error checking monthly legend: {e}")
            return False
    
    async def give_achievement(self, chat_id: int, user_id: int, achievement_id: str, achievement_data: dict):
        """Выдать достижение"""
        try:
            await EconomyDB.add_achievement(
                chat_id, user_id, achievement_id,
                achievement_data["reward_amount"],
                achievement_data["reward_currency"]
            )
            
            # Отслеживаем активность группы
            from .auto_updater import track_achievement_activity
            await track_achievement_activity(chat_id)
            
            # Отправляем уведомление
            await self.send_achievement_notification(chat_id, user_id, achievement_data)
            
        except Exception as e:
            logger.error(f"Error giving achievement: {e}")
    
    async def send_achievement_notification(self, chat_id: int, user_id: int, achievement_data: dict):
        """Отправить уведомление о получении достижения"""
        try:
            # Получаем информацию о пользователе
            from config import app
            user = await app.get_users(user_id)
            username = user.username or user.first_name
            
            # Получаем язык группы
            lang_code = await get_group_language(chat_id)
            lang = load_language(lang_code)
            
            name = lang.get(achievement_data['name_key'], achievement_data['name_key'])
            description = lang.get(achievement_data['description_key'], achievement_data['description_key'])
            
            text = f"""
🏆 <b>{lang.get('achievement_new')}</b>

{achievement_data['emoji']} <b>{name}</b>
{description}

🎁 <b>{lang.get('achievement_reward')}:</b> {achievement_data['reward_amount']} {achievement_data['reward_currency'].upper()}

{lang.get('achievement_congratulations').format(username=username)}
            """
            
            await app.send_message(chat_id, text)
            
        except Exception as e:
            logger.error(f"Error sending achievement notification: {e}")
    
    async def get_achievement_progress(self, chat_id: int, user_id: int) -> dict:
        """Получить прогресс по достижениям"""
        user_achievements = await EconomyDB.get_user_achievements(chat_id, user_id)
        earned_achievement_ids = {ach["achievement_id"] for ach in user_achievements}
        
        balance = await EconomyDB.get_user_balance(chat_id, user_id)
        
        progress = {}
        for achievement_id, achievement_data in self.ACHIEVEMENTS.items():
            if achievement_id in earned_achievement_ids:
                progress[achievement_id] = {
                    "earned": True,
                    "progress": 100
                }
            else:
                # Рассчитываем прогресс для недоступных достижений
                progress_value = await self.calculate_achievement_progress(achievement_id, balance)
                progress[achievement_id] = {
                    "earned": False,
                    "progress": progress_value
                }
        
        return progress
    
    async def calculate_achievement_progress(self, achievement_id: str, balance: dict) -> int:
        """Рассчитать прогресс достижения"""
        if achievement_id == "rich_user":
            current = balance.get("group_currency", 0)
            target = 1000
            return min(int((current / target) * 100), 100)
        
        elif achievement_id == "millionaire":
            current = balance.get("group_currency", 0)
            target = 1000000
            return min(int((current / target) * 100), 100)
        
        elif achievement_id == "billionaire":
            current = balance.get("group_currency", 0)
            target = 1000000000
            return min(int((current / target) * 100), 100)
        
        elif achievement_id == "neon_collector":
            current = balance.get("neon_coins", 0)
            target = 500
            return min(int((current / target) * 100), 100)
        
        elif achievement_id == "neon_master":
            current = balance.get("neon_coins", 0)
            target = 10000
            return min(int((current / target) * 100), 100)
        
        elif achievement_id == "active_member":
            current = balance.get("total_earned", 0)
            target = 5000
            return min(int((current / target) * 100), 100)
        
        elif achievement_id == "super_earner":
            current = balance.get("total_earned", 0)
            target = 50000
            return min(int((current / target) * 100), 100)
        
        elif achievement_id == "money_magnet":
            current = balance.get("total_earned", 0)
            target = 100000
            return min(int((current / target) * 100), 100)
        
        return 0
    
    async def get_achievement_statistics(self, chat_id: int, user_id: int) -> dict:
        """Получить статистику достижений пользователя"""
        try:
            user_achievements = await EconomyDB.get_user_achievements(chat_id, user_id)
            earned_count = len(user_achievements)
            total_count = len(self.ACHIEVEMENTS)
            
            # Группируем достижения по категориям
            categories = {
                "basic": ["first_bonus", "first_conversion"],
                "streaks": ["week_streak", "month_streak", "year_streak"],
                "wealth": ["rich_user", "millionaire", "billionaire", "neon_collector", "neon_master"],
                "activity": ["active_member", "super_earner", "money_magnet"],
                "conversions": ["conversion_master", "currency_trader"],
                "rankings": ["top_earner", "top_3", "top_10", "leaderboard_legend"],
                "special": ["early_bird", "night_owl", "lucky_streak", "persistent"],
                "mastery": ["achievement_hunter", "completionist", "economy_master"],
                "temporal": ["daily_warrior", "weekly_champion", "monthly_legend"]
            }
            
            category_stats = {}
            for category, achievement_ids in categories.items():
                earned_in_category = sum(1 for ach in user_achievements if ach["achievement_id"] in achievement_ids)
                category_stats[category] = {
                    "earned": earned_in_category,
                    "total": len(achievement_ids),
                    "percentage": int((earned_in_category / len(achievement_ids)) * 100) if achievement_ids else 0
                }
            
            return {
                "total_earned": earned_count,
                "total_available": total_count,
                "completion_percentage": int((earned_count / total_count) * 100),
                "categories": category_stats,
                "recent_achievements": user_achievements[-5:] if user_achievements else []
            }
        except Exception as e:
            logger.error(f"Error getting achievement statistics: {e}")
            return {}

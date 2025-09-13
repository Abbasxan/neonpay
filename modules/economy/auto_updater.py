"""
Automatic Rate Updater Module
Модуль автоматического обновления курса
"""

import logging
import asyncio
from datetime import datetime, timedelta
from config import app, db
from .database import EconomyDB

logger = logging.getLogger(__name__)

class AutoRateUpdater:
    """Автоматический обновлятель курса"""
    
    def __init__(self):
        self.is_running = False
    
    async def start(self):
        """Запустить автоматическое обновление"""
        if self.is_running:
            return
        
        self.is_running = True
        logger.info("🚀 Автоматическое обновление курса запущено")
        
        # Запускаем в фоновом режиме
        asyncio.create_task(self._update_loop())
    
    async def stop(self):
        """Остановить автоматическое обновление"""
        self.is_running = False
        logger.info("⏹️ Автоматическое обновление курса остановлено")
    
    async def _update_loop(self):
        """Основной цикл обновления"""
        while self.is_running:
            try:
                await self._update_all_rates()
                # Обновляем каждые 24 часа
                await asyncio.sleep(86400)  # 24 часа в секундах
            except Exception as e:
                logger.error(f"Ошибка в цикле обновления курса: {e}")
                # При ошибке ждем час и пробуем снова
                await asyncio.sleep(3600)
    
    async def _update_all_rates(self):
        """Обновить курсы для всех групп"""
        try:
            # Получаем все группы с валютами
            cursor = db.group_currencies.find({"is_active": True})
            groups = await cursor.to_list(length=None)
            
            logger.info(f"🔄 Обновление курса для {len(groups)} групп")
            
            for group in groups:
                chat_id = group["_id"]
                await self._update_group_rate(chat_id)
            
            logger.info("✅ Обновление курса завершено")
            
        except Exception as e:
            logger.error(f"Ошибка при обновлении курсов: {e}")
    
    async def _update_group_rate(self, chat_id: int):
        """Обновить курс для конкретной группы"""
        try:
            group_currency = await EconomyDB.get_group_currency(chat_id)
            if not group_currency:
                return
            
            # Используем продвинутый алгоритм ценообразования
            from .advanced_pricing import advanced_pricing
            new_rate = await advanced_pricing.calculate_dynamic_rate(chat_id)
            
            # Обновляем курс
            await EconomyDB.update_exchange_rate(chat_id, new_rate)
            
            # Обновляем счетчик активности (сбрасываем на 0)
            await EconomyDB.update_activity_score(chat_id, 0)
            
            logger.info(f"📈 Курс обновлен для группы {chat_id}: {new_rate:.4f} NC (продвинутый алгоритм)")
            
        except Exception as e:
            logger.error(f"Ошибка при обновлении курса для группы {chat_id}: {e}")
    
    async def add_activity_point(self, chat_id: int, points: int = 1):
        """Добавить очки активности для группы"""
        try:
            group_currency = await EconomyDB.get_group_currency(chat_id)
            if not group_currency:
                return
            
            current_score = group_currency.get("daily_activity_score", 0)
            new_score = current_score + points
            
            await EconomyDB.update_activity_score(chat_id, new_score)
            
        except Exception as e:
            logger.error(f"Ошибка при добавлении очков активности: {e}")
    
    async def get_activity_score(self, chat_id: int) -> int:
        """Получить текущий счет активности группы"""
        try:
            group_currency = await EconomyDB.get_group_currency(chat_id)
            if not group_currency:
                return 0
            
            return group_currency.get("daily_activity_score", 0)
            
        except Exception as e:
            logger.error(f"Ошибка при получении счета активности: {e}")
            return 0

# Создаем глобальный экземпляр
auto_updater = AutoRateUpdater()

# Функция для добавления активности при сообщениях
async def track_message_activity(chat_id: int):
    """Отслеживать активность сообщений"""
    try:
        await auto_updater.add_activity_point(chat_id, 1)
    except Exception as e:
        logger.error(f"Ошибка при отслеживании активности: {e}")

# Функция для добавления активности при ежедневных бонусах
async def track_daily_bonus_activity(chat_id: int):
    """Отслеживать активность ежедневных бонусов"""
    try:
        await auto_updater.add_activity_point(chat_id, 5)  # Бонусы дают больше очков
    except Exception as e:
        logger.error(f"Ошибка при отслеживании активности бонусов: {e}")

# Функция для добавления активности при достижениях
async def track_achievement_activity(chat_id: int):
    """Отслеживать активность достижений"""
    try:
        await auto_updater.add_activity_point(chat_id, 3)  # Достижения дают средние очки
    except Exception as e:
        logger.error(f"Ошибка при отслеживании активности достижений: {e}")

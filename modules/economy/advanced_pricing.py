"""
Advanced Pricing Algorithm Module
Модуль продвинутого алгоритма ценообразования
"""

import logging
import math
import random
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from config import db
from .database import EconomyDB

logger = logging.getLogger(__name__)

class AdvancedPricingEngine:
    """Продвинутый движок ценообразования"""
    
    def __init__(self):
        self.market_volatility = 0.15  # Волатильность рынка (15%)
        self.base_demand_factor = 0.1  # Базовый фактор спроса
        self.supply_factor = 0.05  # Фактор предложения
        
    async def calculate_dynamic_rate(self, chat_id: int) -> float:
        """Рассчитать динамический курс валюты"""
        try:
            group_currency = await EconomyDB.get_group_currency(chat_id)
            if not group_currency:
                return 0.1  # Минимальный курс
            
            # Получаем данные для расчета
            activity_score = group_currency.get("daily_activity_score", 0)
            total_supply = group_currency.get("total_supply", 0)
            created_at = group_currency.get("created_at", datetime.utcnow())
            
            # Рассчитываем различные факторы
            activity_factor = self._calculate_activity_factor(activity_score)
            supply_factor = self._calculate_supply_factor(total_supply)
            age_factor = self._calculate_age_factor(created_at)
            demand_factor = self._calculate_demand_factor(chat_id)
            market_trend = self._calculate_market_trend(chat_id)
            
            # Базовый курс
            base_rate = 0.05  # Минимальный курс 0.05 NC
            
            # Рассчитываем итоговый курс
            calculated_rate = (
                base_rate + 
                (activity_factor * 0.3) +
                (supply_factor * 0.2) +
                (age_factor * 0.15) +
                (demand_factor * 0.2) +
                (market_trend * 0.15)
            )
            
            # Добавляем случайную волатильность
            volatility = random.uniform(-self.market_volatility, self.market_volatility)
            final_rate = calculated_rate * (1 + volatility)
            
            # Ограничиваем курс в разумных пределах
            final_rate = max(0.01, min(final_rate, 2.0))  # От 0.01 до 2.0 NC
            
            logger.info(f"📊 Курс для группы {chat_id}: {final_rate:.4f} NC "
                       f"(активность: {activity_factor:.2f}, предложение: {supply_factor:.2f}, "
                       f"возраст: {age_factor:.2f}, спрос: {demand_factor:.2f}, тренд: {market_trend:.2f})")
            
            return final_rate
            
        except Exception as e:
            logger.error(f"Ошибка при расчете курса для группы {chat_id}: {e}")
            return 0.1
    
    def _calculate_activity_factor(self, activity_score: int) -> float:
        """Рассчитать фактор активности"""
        # Логарифмическая шкала для активности
        if activity_score <= 0:
            return 0.0
        
        # Максимальная активность = 1000 очков
        normalized_activity = min(activity_score / 1000, 1.0)
        return math.log(1 + normalized_activity * 9) / math.log(10)  # От 0 до 1
    
    def _calculate_supply_factor(self, total_supply: float) -> float:
        """Рассчитать фактор предложения (дефицит увеличивает цену)"""
        if total_supply <= 0:
            return 0.5  # Нет предложения = высокая цена
        
        # Чем меньше предложение, тем выше цена
        # Оптимальное предложение = 10000 единиц
        optimal_supply = 10000
        supply_ratio = total_supply / optimal_supply
        
        if supply_ratio < 0.1:  # Критический дефицит
            return 0.8
        elif supply_ratio < 0.5:  # Дефицит
            return 0.6
        elif supply_ratio < 2.0:  # Нормальное предложение
            return 0.3
        else:  # Избыток
            return 0.1
    
    def _calculate_age_factor(self, created_at: datetime) -> float:
        """Рассчитать фактор возраста валюты"""
        age_days = (datetime.utcnow() - created_at).days
        
        if age_days < 1:  # Новые валюты
            return 0.1
        elif age_days < 7:  # Молодые валюты
            return 0.3
        elif age_days < 30:  # Стабильные валюты
            return 0.5
        elif age_days < 90:  # Зрелые валюты
            return 0.7
        else:  # Старые валюты
            return 0.9
    
    async def _calculate_demand_factor(self, chat_id: int) -> float:
        """Рассчитать фактор спроса на основе конвертаций"""
        try:
            # Подсчитываем количество конвертаций за последние 24 часа
            yesterday = datetime.utcnow() - timedelta(days=1)
            
            conversions = await db.economy_transactions.count_documents({
                "chat_id": chat_id,
                "transaction_type": {"$in": ["group_to_nc", "nc_to_group"]},
                "created_at": {"$gte": yesterday}
            })
            
            # Нормализуем спрос
            if conversions == 0:
                return 0.1  # Нет спроса
            elif conversions < 5:
                return 0.3  # Низкий спрос
            elif conversions < 20:
                return 0.5  # Средний спрос
            elif conversions < 50:
                return 0.7  # Высокий спрос
            else:
                return 0.9  # Очень высокий спрос
                
        except Exception as e:
            logger.error(f"Ошибка при расчете спроса для группы {chat_id}: {e}")
            return 0.3
    
    async def _calculate_market_trend(self, chat_id: int) -> float:
        """Рассчитать рыночный тренд"""
        try:
            # Получаем историю курсов за последние 7 дней
            week_ago = datetime.utcnow() - timedelta(days=7)
            
            # Получаем последние обновления курса
            group_currency = await EconomyDB.get_group_currency(chat_id)
            if not group_currency:
                return 0.0
            
            last_update = group_currency.get("last_rate_update", datetime.utcnow())
            current_rate = group_currency.get("exchange_rate_to_nc", 0.1)
            
            # Простой тренд на основе времени последнего обновления
            hours_since_update = (datetime.utcnow() - last_update).total_seconds() / 3600
            
            if hours_since_update < 1:  # Недавно обновлен
                return 0.1
            elif hours_since_update < 6:  # Несколько часов назад
                return 0.0
            elif hours_since_update < 24:  # Вчера
                return -0.1
            else:  # Давно не обновлялся
                return -0.2
                
        except Exception as e:
            logger.error(f"Ошибка при расчете тренда для группы {chat_id}: {e}")
            return 0.0
    
    async def get_market_analysis(self, chat_id: int) -> Dict:
        """Получить анализ рынка для группы"""
        try:
            group_currency = await EconomyDB.get_group_currency(chat_id)
            if not group_currency:
                return {"error": "Валюта не найдена"}
            
            current_rate = group_currency.get("exchange_rate_to_nc", 0.1)
            activity_score = group_currency.get("daily_activity_score", 0)
            total_supply = group_currency.get("total_supply", 0)
            
            # Рассчитываем факторы
            activity_factor = self._calculate_activity_factor(activity_score)
            supply_factor = self._calculate_supply_factor(total_supply)
            age_factor = self._calculate_age_factor(group_currency.get("created_at", datetime.utcnow()))
            demand_factor = await self._calculate_demand_factor(chat_id)
            market_trend = await self._calculate_market_trend(chat_id)
            
            # Определяем статус валюты
            total_score = (activity_factor + supply_factor + age_factor + demand_factor + market_trend) / 5
            
            if total_score >= 0.8:
                status = "🔥 Горячая валюта"
                recommendation = "Отличное время для инвестиций"
            elif total_score >= 0.6:
                status = "📈 Растущая валюта"
                recommendation = "Хорошие перспективы роста"
            elif total_score >= 0.4:
                status = "📊 Стабильная валюта"
                recommendation = "Надежная инвестиция"
            elif total_score >= 0.2:
                status = "📉 Слабая валюта"
                recommendation = "Осторожно с инвестициями"
            else:
                status = "❄️ Холодная валюта"
                recommendation = "Не рекомендуется для инвестиций"
            
            return {
                "current_rate": current_rate,
                "status": status,
                "recommendation": recommendation,
                "factors": {
                    "activity": f"{activity_factor:.2f}",
                    "supply": f"{supply_factor:.2f}",
                    "age": f"{age_factor:.2f}",
                    "demand": f"{demand_factor:.2f}",
                    "trend": f"{market_trend:.2f}"
                },
                "total_score": f"{total_score:.2f}"
            }
            
        except Exception as e:
            logger.error(f"Ошибка при анализе рынка для группы {chat_id}: {e}")
            return {"error": str(e)}

# Создаем глобальный экземпляр
advanced_pricing = AdvancedPricingEngine()

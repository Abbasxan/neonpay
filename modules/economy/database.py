"""
Database schema for Economy System
Схема базы данных для экономической системы
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from config import db

logger = logging.getLogger(__name__)

class EconomyDB:
    """Класс для работы с базой данных экономической системы"""
    
    @staticmethod
    async def initialize_database():
        """Инициализация базы данных и создание индексов"""
        try:
            # Создаем индексы для оптимизации запросов
            await db.group_currencies.create_index("_id")
            await db.user_balances.create_index([("chat_id", 1), ("user_id", 1)])
            await db.economy_transactions.create_index([("chat_id", 1), ("user_id", 1)])
            await db.user_achievements.create_index([("chat_id", 1), ("user_id", 1)])
            await db.daily_bonuses.create_index([("chat_id", 1), ("user_id", 1), ("date", 1)])
            
            logger.info("✅ Экономическая база данных инициализирована")
            return True
        except Exception as e:
            logger.error(f"❌ Ошибка инициализации экономической базы данных: {e}")
            return False
    
    @staticmethod
    async def create_group_currency(chat_id: int, currency_name: str, currency_symbol: str, owner_id: int):
        """Создать валюту для группы"""
        currency_data = {
            "_id": chat_id,
            "currency_name": currency_name,
            "currency_symbol": currency_symbol,
            "owner_id": owner_id,
            "created_at": datetime.utcnow(),
            "total_supply": 0,
            "daily_activity_score": 0,
            "exchange_rate_to_nc": 1.0,  # Начальный курс к NC
            "last_rate_update": datetime.utcnow(),
            "is_active": True
        }
        
        await db.group_currencies.update_one(
            {"_id": chat_id},
            {"$set": currency_data},
            upsert=True
        )
        return currency_data
    
    @staticmethod
    async def get_group_currency(chat_id: int) -> Optional[Dict]:
        """Получить валюту группы"""
        return await db.group_currencies.find_one({"_id": chat_id})
    
    @staticmethod
    async def update_exchange_rate(chat_id: int, new_rate: float):
        """Обновить курс обмена"""
        await db.group_currencies.update_one(
            {"_id": chat_id},
            {
                "$set": {
                    "exchange_rate_to_nc": new_rate,
                    "last_rate_update": datetime.utcnow()
                }
            }
        )
    
    @staticmethod
    async def update_activity_score(chat_id: int, score: int):
        """Обновить счет активности группы"""
        await db.group_currencies.update_one(
            {"_id": chat_id},
            {
                "$set": {
                    "daily_activity_score": score,
                    "last_activity_update": datetime.utcnow()
                }
            }
        )
    
    @staticmethod
    async def get_group_statistics(chat_id: int) -> Dict:
        """Получить общую статистику группы"""
        try:
            # Получаем общее количество пользователей в экономике
            total_users = await db.user_balances.count_documents({"chat_id": chat_id})
            
            # Получаем общий баланс всех пользователей
            pipeline = [
                {"$match": {"chat_id": chat_id}},
                {"$group": {
                    "_id": None,
                    "total_group_currency": {"$sum": "$group_currency"},
                    "total_neon_coins": {"$sum": "$neon_coins"},
                    "total_earned": {"$sum": "$total_earned"}
                }}
            ]
            
            result = await db.user_balances.aggregate(pipeline).to_list(length=1)
            
            if result:
                stats = result[0]
                return {
                    "total_users": total_users,
                    "total_group_currency": stats.get("total_group_currency", 0),
                    "total_neon_coins": stats.get("total_neon_coins", 0),
                    "total_earned": stats.get("total_earned", 0)
                }
            else:
                return {
                    "total_users": 0,
                    "total_group_currency": 0,
                    "total_neon_coins": 0,
                    "total_earned": 0
                }
                
        except Exception as e:
            logger.error(f"Error getting group statistics for chat {chat_id}: {e}")
            return {
                "total_users": 0,
                "total_group_currency": 0,
                "total_neon_coins": 0,
                "total_earned": 0
            }
    
    @staticmethod
    async def get_user_balance(chat_id: int, user_id: int) -> Dict:
        """Получить баланс пользователя"""
        try:
            balance = await db.user_balances.find_one({
                "chat_id": chat_id,
                "user_id": user_id
            })
            
            if not balance:
                # Создать новый баланс
                balance = {
                    "chat_id": chat_id,
                    "user_id": user_id,
                    "group_currency": 0,
                    "neon_coins": 0,
                    "total_earned": 0,
                    "last_daily_bonus": None,
                    "created_at": datetime.utcnow()
                }
                result = await db.user_balances.insert_one(balance)
                logger.info(f"Created new balance for user {user_id} in chat {chat_id}, inserted_id: {result.inserted_id}")
                
                # Возвращаем созданный баланс напрямую, а не делаем дополнительный запрос
                balance["_id"] = result.inserted_id
            else:
                logger.debug(f"Retrieved balance for user {user_id} in chat {chat_id}: GG={balance.get('group_currency', 0):.2f}, NC={balance.get('neon_coins', 0):.2f}")
            
            # Убеждаемся, что все поля существуют и имеют правильные типы
            balance.setdefault('group_currency', 0)
            balance.setdefault('neon_coins', 0)
            balance.setdefault('total_earned', 0)
            balance.setdefault('last_daily_bonus', None)
            
            # Преобразуем значения в float для сохранения дробных значений
            balance['group_currency'] = float(balance.get('group_currency', 0))
            balance['neon_coins'] = float(balance.get('neon_coins', 0))
            balance['total_earned'] = float(balance.get('total_earned', 0))
            
            return balance
            
        except Exception as e:
            logger.error(f"Error getting user balance for user {user_id} in chat {chat_id}: {e}")
            # Возвращаем базовый баланс в случае ошибки
            return {
                "chat_id": chat_id,
                "user_id": user_id,
                "group_currency": 0,
                "neon_coins": 0,
                "total_earned": 0,
                "last_daily_bonus": None,
                "created_at": datetime.utcnow()
            }
    
    @staticmethod
    async def update_user_balance(chat_id: int, user_id: int, group_currency: float = 0.0, neon_coins: float = 0.0, earned: float = 0.0):
        """Обновить баланс пользователя"""
        try:
            # Нормализуем входные значения в float
            try:
                gc = float(group_currency)
            except (TypeError, ValueError):
                gc = 0.0
            try:
                nc = float(neon_coins)
            except (TypeError, ValueError):
                nc = 0.0
            try:
                er = float(earned)
            except (TypeError, ValueError):
                er = 0.0

            # Убедимся, что документ существует
            existing_balance = await db.user_balances.find_one({
                "chat_id": chat_id,
                "user_id": user_id
            })

            if not existing_balance:
                new_balance = {
                    "chat_id": chat_id,
                    "user_id": user_id,
                    "group_currency": gc,
                    "neon_coins": nc,
                    "total_earned": er,
                    "last_daily_bonus": None,
                    "created_at": datetime.utcnow()
                }
                result = await db.user_balances.insert_one(new_balance)
                logger.info(f"Created new balance for user {user_id} in chat {chat_id}: GG={gc}, NC={nc}, Earned={er}")
                return True
            else:
                update_ops = {}
                inc = {}
                # Добавляем только ненулевые инкременты
                if gc != 0.0:
                    inc["group_currency"] = gc
                if nc != 0.0:
                    inc["neon_coins"] = nc
                if er != 0.0:
                    inc["total_earned"] = er

                if inc:
                    update_ops["$inc"] = inc
                    result = await db.user_balances.update_one(
                        {"chat_id": chat_id, "user_id": user_id},
                        update_ops
                    )
                    # Проверяем matched_count — документ найден
                    logger.info(f"Update result for user {user_id} in chat {chat_id}: matched={getattr(result, 'matched_count', 'n/a')}, modified={getattr(result, 'modified_count', 'n/a')}")
                    if getattr(result, "matched_count", 0) == 0:
                        logger.warning(f"Balance update failed - no matching document for user {user_id} in chat {chat_id}")
                        return False
                    return True
                else:
                    logger.debug(f"No balance changes to apply for user {user_id} in chat {chat_id}")
                    return True
                
        except Exception as e:
            logger.error(f"Error updating user balance for user {user_id} in chat {chat_id}: {e}")
            return False
    
    @staticmethod
    async def convert_currency(chat_id: int, user_id: int, from_amount: float, to_amount: float, from_symbol: str, to_symbol: str, conversion_type: str) -> bool:
        """Конвертировать валюту"""
        try:
            # Принудительно приводим к float
            from_amt = float(from_amount)
            to_amt = float(to_amount)

            balance = await EconomyDB.get_user_balance(chat_id, user_id)
            logger.info(f"Converting currency for user {user_id} in chat {chat_id}: {from_amt} {from_symbol} -> {to_amt} {to_symbol} (type: {conversion_type})")

            if conversion_type == "group_to_nc":
                if balance["group_currency"] >= from_amt:
                    success = await EconomyDB.update_user_balance(chat_id, user_id, -from_amt, to_amt, 0.0)
                    if success:
                        await EconomyDB.log_transaction(
                            chat_id, user_id, "conversion", from_amt, from_symbol,
                            f"Converted {from_amt:.2f} {from_symbol} to {to_amt:.2f} {to_symbol}"
                        )
                        logger.info(f"Successfully converted {from_amt:.2f} {from_symbol} to {to_amt:.2f} {to_symbol} for user {user_id}")
                        return True
                    else:
                        logger.warning(f"update_user_balance returned False for user {user_id} during group_to_nc")
                else:
                    logger.warning(f"Insufficient {from_symbol} balance for user {user_id}: has {balance['group_currency']:.2f}, needs {from_amt:.2f}")

            elif conversion_type == "nc_to_group":
                if balance["neon_coins"] >= from_amt:
                    success = await EconomyDB.update_user_balance(chat_id, user_id, to_amt, -from_amt, 0.0)
                    if success:
                        await EconomyDB.log_transaction(
                            chat_id, user_id, "conversion", from_amt, from_symbol,
                            f"Converted {from_amt:.2f} {from_symbol} to {to_amt:.2f} {to_symbol}"
                        )
                        logger.info(f"Successfully converted {from_amt:.2f} {from_symbol} to {to_amt:.2f} {to_symbol} for user {user_id}")
                        return True
                    else:
                        logger.warning(f"update_user_balance returned False for user {user_id} during nc_to_group")
                else:
                    logger.warning(f"Insufficient {from_symbol} balance for user {user_id}: has {balance['neon_coins']:.2f}, needs {from_amt:.2f}")

            return False
            
        except Exception as e:
            logger.error(f"Error converting currency for user {user_id} in chat {chat_id}: {e}")
            return False
    
    @staticmethod
    async def get_top_users(chat_id: int, limit: int = 10) -> List[Dict]:
        """Получить топ пользователей по балансу (исключая всех ботов)"""
        # Получаем всех пользователей с балансом
        cursor = db.user_balances.find(
            {"chat_id": chat_id},
            {"user_id": 1, "group_currency": 1, "neon_coins": 1, "total_earned": 1}
        ).sort("total_earned", -1)
        
        all_users = await cursor.to_list(length=None)
        
        # Фильтруем ботов (будет сделано в economy.py через Telegram API)
        return all_users
    
    @staticmethod
    async def log_transaction(chat_id: int, user_id: int, transaction_type: str, amount: int, currency: str, description: str = ""):
        """Записать транзакцию"""
        transaction = {
            "chat_id": chat_id,
            "user_id": user_id,
            "type": transaction_type,  # daily_bonus, achievement, conversion, etc.
            "amount": amount,
            "currency": currency,
            "description": description,
            "timestamp": datetime.utcnow()
        }
        
        await db.economy_transactions.insert_one(transaction)
    
    @staticmethod
    async def get_user_achievements(chat_id: int, user_id: int) -> List[Dict]:
        """Получить достижения пользователя"""
        achievements = await db.user_achievements.find({
            "chat_id": chat_id,
            "user_id": user_id
        }).to_list(length=None)
        
        return achievements
    
    @staticmethod
    async def add_achievement(chat_id: int, user_id: int, achievement_id: str, reward_amount: int, reward_currency: str):
        """Добавить достижение пользователю"""
        achievement = {
            "chat_id": chat_id,
            "user_id": user_id,
            "achievement_id": achievement_id,
            "reward_amount": reward_amount,
            "reward_currency": reward_currency,
            "earned_at": datetime.utcnow()
        }
        
        await db.user_achievements.insert_one(achievement)
        
        # Обновить баланс
        if reward_currency == "group":
            await EconomyDB.update_user_balance(chat_id, user_id, reward_amount, 0, reward_amount)
        elif reward_currency == "nc":
            await EconomyDB.update_user_balance(chat_id, user_id, 0, reward_amount, reward_amount)
        
        # Записать транзакцию
        await EconomyDB.log_transaction(
            chat_id, user_id, "achievement", reward_amount, reward_currency,
            f"Achievement: {achievement_id}"
        )
    
    @staticmethod
    async def can_claim_daily_bonus(chat_id: int, user_id: int) -> bool:
        """Проверить, может ли пользователь получить ежедневный бонус"""
        balance = await EconomyDB.get_user_balance(chat_id, user_id)
        
        if not balance.get("last_daily_bonus"):
            return True
        
        last_bonus = balance["last_daily_bonus"]
        now = datetime.utcnow()
        
        # Проверяем, прошло ли 24 часа
        return (now - last_bonus).total_seconds() >= 86400  # 24 часа в секундах
    
    @staticmethod
    async def claim_daily_bonus(chat_id: int, user_id: int, bonus_amount: int):
        """Выдать ежедневный бонус"""
        await EconomyDB.update_user_balance(chat_id, user_id, bonus_amount, 0, bonus_amount)
        
        await db.user_balances.update_one(
            {"chat_id": chat_id, "user_id": user_id},
            {"$set": {"last_daily_bonus": datetime.utcnow()}}
        )
        
        # Записать транзакцию
        await EconomyDB.log_transaction(
            chat_id, user_id, "daily_bonus", bonus_amount, "group",
            "Daily activity bonus"
        )
    
    @staticmethod
    async def fix_user_balance(chat_id: int, user_id: int) -> bool:
        """Исправить баланс пользователя - убедиться, что все поля существуют"""
        try:
            balance = await db.user_balances.find_one({
                "chat_id": chat_id,
                "user_id": user_id
            })
            
            if not balance:
                # Создаем новый баланс
                new_balance = {
                    "chat_id": chat_id,
                    "user_id": user_id,
                    "group_currency": 0,
                    "neon_coins": 0,
                    "total_earned": 0,
                    "last_daily_bonus": None,
                    "created_at": datetime.utcnow()
                }
                await db.user_balances.insert_one(new_balance)
                logger.info(f"Created new balance for user {user_id} in chat {chat_id}")
                return True
            else:
                # Проверяем и исправляем отсутствующие поля
                needs_update = False
                update_data = {}
                
                if 'group_currency' not in balance:
                    update_data['group_currency'] = 0
                    needs_update = True
                if 'neon_coins' not in balance:
                    update_data['neon_coins'] = 0
                    needs_update = True
                if 'total_earned' not in balance:
                    update_data['total_earned'] = 0
                    needs_update = True
                if 'last_daily_bonus' not in balance:
                    update_data['last_daily_bonus'] = None
                    needs_update = True
                if 'created_at' not in balance:
                    update_data['created_at'] = datetime.utcnow()
                    needs_update = True
                
                if needs_update:
                    await db.user_balances.update_one(
                        {"chat_id": chat_id, "user_id": user_id},
                        {"$set": update_data}
                    )
                    logger.info(f"Fixed balance fields for user {user_id} in chat {chat_id}: {update_data}")
                    return True
                else:
                    logger.debug(f"Balance for user {user_id} in chat {chat_id} is already correct")
                    return False
                    
        except Exception as e:
            logger.error(f"Error fixing user balance for user {user_id} in chat {chat_id}: {e}")
            return False
    
    @staticmethod
    async def fix_all_user_balances(chat_id: int) -> int:
        """Исправить балансы всех пользователей в группе"""
        try:
            # Получаем всех пользователей с балансами в группе
            cursor = db.user_balances.find({"chat_id": chat_id})
            all_balances = await cursor.to_list(length=None)
            
            fixed_count = 0
            
            for balance in all_balances:
                user_id = balance["user_id"]
                if await EconomyDB.fix_user_balance(chat_id, user_id):
                    fixed_count += 1
            
            logger.info(f"Fixed {fixed_count} balances in chat {chat_id}")
            return fixed_count
            
        except Exception as e:
            logger.error(f"Error fixing all user balances in chat {chat_id}: {e}")
            return 0

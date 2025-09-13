"""
Balance Fix Module
Модуль для исправления балансов пользователей
ВРЕМЕННЫЙ МОДУЛЬ - УДАЛИТЬ ПОСЛЕ ИСПОЛЬЗОВАНИЯ
"""

import logging
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.enums import ChatMemberStatus
from config import app
from language import load_language, get_group_language

# Импортируем EconomyDB после импорта app
try:
    from .database import EconomyDB
except ImportError:
    from modules.economy.database import EconomyDB

logger = logging.getLogger(__name__)

# Логируем загрузку модуля
logger.info("✅ Balance fix module loaded successfully")

@app.on_message(filters.command("fix_balances") & filters.group, group=100)
async def fix_balances_command(client: Client, message: Message):
    """Команда для исправления балансов всех пользователей в группе"""
    chat_id = message.chat.id
    user_id = message.from_user.id
    
    # Проверяем права администратора
    try:
        member = await client.get_chat_member(chat_id, user_id)
        if member.status not in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
            lang_code = await get_group_language(chat_id)
            lang = load_language(lang_code)
            return await message.reply(
                f"<blockquote>❌ {lang.get('economy_admin_only')}</blockquote>"
            )
    except Exception as e:
        logger.error(f"Error checking admin status: {e}")
        return
    
    # Исправляем все балансы
    try:
        fixed_count = await EconomyDB.fix_all_user_balances(chat_id)
        
        lang_code = await get_group_language(chat_id)
        lang = load_language(lang_code)
        await message.reply(
            f"<blockquote>✅ {lang.get('fix_balances_fixed_count', 'Исправлено балансов')}: {fixed_count}</blockquote>"
        )
        
        logger.info(f"Fixed {fixed_count} balances in chat {chat_id}")
        
    except Exception as e:
        logger.error(f"Error fixing balances: {e}")
        lang_code = await get_group_language(chat_id)
        lang = load_language(lang_code)
        await message.reply(
            f"<blockquote>❌ {lang.get('fix_balances_error', 'Произошла ошибка при исправлении балансов')}</blockquote>"
        )

@app.on_message(filters.command("fix_my_balance") & filters.group, group=100)
async def fix_my_balance_command(client: Client, message: Message):
    """Команда для исправления баланса конкретного пользователя"""
    chat_id = message.chat.id
    user_id = message.from_user.id
    
    try:
        # Исправляем баланс пользователя
        fixed = await EconomyDB.fix_user_balance(chat_id, user_id)
        
        lang_code = await get_group_language(chat_id)
        lang = load_language(lang_code)
        if fixed:
            await message.reply(
                f"<blockquote>✅ {lang.get('fix_balances_fixed')}</blockquote>"
            )
        else:
            await message.reply(
                f"<blockquote>ℹ️ {lang.get('fix_balances_no_fix_needed')}</blockquote>"
            )
        
        logger.info(f"Fixed balance for user {user_id} in chat {chat_id}: {fixed}")
        
    except Exception as e:
        logger.error(f"Error fixing user balance: {e}")
        lang_code = await get_group_language(chat_id)
        lang = load_language(lang_code)
        await message.reply(
            f"<blockquote>❌ {lang.get('fix_balances_error_user', 'Произошла ошибка при исправлении баланса')}</blockquote>"
        )

@app.on_message(filters.command("clear_economy") & filters.group, group=100)
async def clear_economy_command(client: Client, message: Message):
    """ВРЕМЕННАЯ КОМАНДА для полной очистки экономической системы"""
    chat_id = message.chat.id
    user_id = message.from_user.id
    
    # Проверяем права администратора
    try:
        member = await client.get_chat_member(chat_id, user_id)
        if member.status not in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
            lang_code = await get_group_language(chat_id)
            lang = load_language(lang_code)
            return await message.reply(
                f"<blockquote>❌ {lang.get('economy_admin_only')}</blockquote>"
            )
    except Exception as e:
        logger.error(f"Error checking admin status: {e}")
        return
    
    # Полная очистка экономической системы
    try:
        from config import db
        
        cleared_counts = {}
        total_cleared = 0
        
        # Очищаем все коллекции экономической системы (используем реальные имена коллекций)
        collections_to_clear = [
            ("user_balances", "Балансы пользователей"),
            ("group_currencies", "Настройки валют групп"),
            ("economy_transactions", "История транзакций"),
            ("user_achievements", "Достижения пользователей"),
            ("daily_bonuses", "Ежедневные бонусы")
        ]
        
        for collection_name, description in collections_to_clear:
            collection = db[collection_name]
            # Удаляем все документы из коллекции
            result = await collection.delete_many({})
            cleared_counts[collection_name] = result.deleted_count
            total_cleared += result.deleted_count
            logger.info(f"Cleared {result.deleted_count} documents from {collection_name} ({description})")
        
        lang_code = await get_group_language(chat_id)
        lang = load_language(lang_code)
        
        # Формируем отчет об очистке
        report = f"""
🗑️ <b>Экономическая система полностью очищена!</b>

📊 <b>Статистика очистки:</b>
"""
        for collection_name, count in cleared_counts.items():
            report += f"• {collection_name}: <code>{count}</code> документов\n"
        
        report += f"\n✅ <b>Всего очищено:</b> <code>{total_cleared}</code> документов"
        report += f"\n\n⚠️ <b>ВНИМАНИЕ:</b> Все данные экономической системы удалены!"
        report += f"\n🔄 Для продолжения работы создайте новую валюту командой /economy"
        
        await message.reply(report)
        
        logger.warning(f"ECONOMY SYSTEM COMPLETELY CLEARED in chat {chat_id} by user {user_id}")
        logger.warning(f"Total documents cleared: {total_cleared}")
        
    except Exception as e:
        logger.error(f"Error clearing economy system: {e}")
        lang_code = await get_group_language(chat_id)
        lang = load_language(lang_code)
        await message.reply(
            f"<blockquote>❌ Ошибка при очистке экономической системы: {str(e)}</blockquote>"
        )

@app.on_message(filters.command("clear_group_economy") & filters.group, group=100)
async def clear_group_economy_command(client: Client, message: Message):
    """ВРЕМЕННАЯ КОМАНДА для очистки экономической системы только текущей группы"""
    chat_id = message.chat.id
    user_id = message.from_user.id
    
    # Проверяем права администратора
    try:
        member = await client.get_chat_member(chat_id, user_id)
        if member.status not in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
            lang_code = await get_group_language(chat_id)
            lang = load_language(lang_code)
            return await message.reply(
                f"<blockquote>❌ {lang.get('economy_admin_only')}</blockquote>"
            )
    except Exception as e:
        logger.error(f"Error checking admin status: {e}")
        return
    
    # Очистка экономической системы только для текущей группы
    try:
        from config import db
        
        cleared_counts = {}
        total_cleared = 0
        
        # Очищаем балансы пользователей в этой группе (реальная коллекция: user_balances)
        users_result = await db.user_balances.delete_many({"chat_id": chat_id})
        cleared_counts["user_balances"] = users_result.deleted_count
        total_cleared += users_result.deleted_count
        
        # Очищаем настройки валюты группы (реальная коллекция: group_currencies)
        groups_result = await db.group_currencies.delete_many({"_id": chat_id})
        cleared_counts["group_currencies"] = groups_result.deleted_count
        total_cleared += groups_result.deleted_count
        
        # Очищаем транзакции в этой группе (реальная коллекция: economy_transactions)
        transactions_result = await db.economy_transactions.delete_many({"chat_id": chat_id})
        cleared_counts["economy_transactions"] = transactions_result.deleted_count
        total_cleared += transactions_result.deleted_count
        
        # Очищаем достижения пользователей в этой группе (реальная коллекция: user_achievements)
        achievements_result = await db.user_achievements.delete_many({"chat_id": chat_id})
        cleared_counts["user_achievements"] = achievements_result.deleted_count
        total_cleared += achievements_result.deleted_count
        
        # Очищаем ежедневные бонусы в этой группе (реальная коллекция: daily_bonuses)
        daily_bonuses_result = await db.daily_bonuses.delete_many({"chat_id": chat_id})
        cleared_counts["daily_bonuses"] = daily_bonuses_result.deleted_count
        total_cleared += daily_bonuses_result.deleted_count
        
        lang_code = await get_group_language(chat_id)
        lang = load_language(lang_code)
        
        # Формируем отчет об очистке
        report = f"""
🗑️ <b>Экономическая система группы очищена!</b>

📊 <b>Статистика очистки для группы:</b>
"""
        for collection_name, count in cleared_counts.items():
            report += f"• {collection_name}: <code>{count}</code> документов\n"
        
        report += f"\n✅ <b>Всего очищено:</b> <code>{total_cleared}</code> документов"
        report += f"\n\n⚠️ <b>ВНИМАНИЕ:</b> Все данные экономической системы этой группы удалены!"
        report += f"\n🔄 Для продолжения работы создайте новую валюту командой /economy"
        
        await message.reply(report)
        
        logger.warning(f"GROUP ECONOMY SYSTEM CLEARED in chat {chat_id} by user {user_id}")
        logger.warning(f"Total documents cleared: {total_cleared}")
        
    except Exception as e:
        logger.error(f"Error clearing group economy system: {e}")
        lang_code = await get_group_language(chat_id)
        lang = load_language(lang_code)
        await message.reply(
            f"<blockquote>❌ Ошибка при очистке экономической системы группы: {str(e)}</blockquote>"
        )

logger.info("✅ Команды /fix_balances, /fix_my_balance, /clear_economy и /clear_group_economy зарегистрированы")
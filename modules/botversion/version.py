"""
Developer Version Module
Модуль версий для разработчика
"""

import logging
import os
import glob
from datetime import datetime
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from config import app
from language import load_language, get_group_language

logger = logging.getLogger(__name__)

class DeveloperVersionManager:
    """Менеджер версий для разработчика"""
    
    def __init__(self):
        self.version_folder = "modules/botversion/versions"
    
    async def show_version(self, client: Client, message: Message):
        """Показать информацию о версии"""
        chat_id = message.chat.id
        lang_code = await get_group_language(chat_id)
        lang = load_language(lang_code)
        
        # Получаем список всех версий
        versions = await self.get_all_versions()
        latest_version = await self.get_latest_version()
        
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton(
                    f"📋 {lang.get('version_changelog', 'История изменений')}",
                    callback_data=f"version_changelog_{chat_id}"
                )
            ],
            [
                InlineKeyboardButton(
                    f"🔄 {lang.get('version_check_updates', 'Проверить обновления')}",
                    callback_data=f"version_check_{chat_id}"
                )
            ]
        ])
        
        text = f"""
🏷️ <b>{lang.get('version_title', 'Информация о версии')}</b>

📱 <b>Последняя версия:</b> <code>{latest_version}</code>
📊 <b>Всего версий:</b> {len(versions)}
📅 <b>Дата проверки:</b> {datetime.now().strftime('%d.%m.%Y %H:%M')}

👨‍💻 <b>Разработчик:</b> QEDDAR Team
📁 <b>Папка версий:</b> <code>{self.version_folder}</code>

💡 <b>Для просмотра изменений нажмите кнопку ниже</b>
        """
        
        await message.reply(text, reply_markup=keyboard)
    
    async def show_version_from_callback(self, client: Client, callback_query):
        """Показать информацию о версии из callback запроса"""
        chat_id = callback_query.message.chat.id
        lang_code = await get_group_language(chat_id)
        lang = load_language(lang_code)
        
        # Получаем список всех версий
        versions = await self.get_all_versions()
        latest_version = await self.get_latest_version()
        
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton(
                    f"📋 {lang.get('version_changelog', 'История изменений')}",
                    callback_data=f"version_changelog_{chat_id}"
                )
            ],
            [
                InlineKeyboardButton(
                    f"🔄 {lang.get('version_check_updates', 'Проверить обновления')}",
                    callback_data=f"version_check_{chat_id}"
                )
            ]
        ])
        
        text = f"""
🏷️ <b>{lang.get('version_title', 'Информация о версии')}</b>

📱 <b>Последняя версия:</b> <code>{latest_version}</code>
📊 <b>Всего версий:</b> {len(versions)}
📅 <b>Дата проверки:</b> {datetime.now().strftime('%d.%m.%Y %H:%M')}

👨‍💻 <b>Разработчик:</b> QEDDAR Team
📁 <b>Папка версий:</b> <code>{self.version_folder}</code>

💡 <b>Для просмотра изменений нажмите кнопку ниже</b>
        """
        
        try:
            await callback_query.edit_message_text(text, reply_markup=keyboard)
        except Exception as e:
            logger.error(f"Error editing version message: {e}")
            await callback_query.answer("Ошибка при загрузке информации о версии!", show_alert=True)
    
    async def show_changelog(self, client: Client, callback_query):
        """Показать историю изменений с компактными кнопками"""
        chat_id = callback_query.message.chat.id
        lang_code = await get_group_language(chat_id)
        lang = load_language(lang_code)
        
        # Получаем все версии
        versions = await self.get_all_versions()
        
        # Создаем кнопки для каждой версии (максимум 8 в ряд)
        keyboard_buttons = []
        for i, version_file in enumerate(versions):
            version_name = version_file.replace('.txt', '').replace('ver', '')
            keyboard_buttons.append(
                InlineKeyboardButton(
                    version_name,
                    callback_data=f"version_detail_{version_name}_{chat_id}"
                )
            )
        
        # Разбиваем кнопки по строкам (по 4 кнопки в ряд)
        keyboard_rows = []
        for i in range(0, len(keyboard_buttons), 4):
            keyboard_rows.append(keyboard_buttons[i:i+4])
        
        # Добавляем кнопку "Назад"
        keyboard_rows.append([
            InlineKeyboardButton(
                f"🔙 {lang.get('version_back', 'Назад')}",
                callback_data=f"version_back_{chat_id}"
            )
        ])
        
        keyboard = InlineKeyboardMarkup(keyboard_rows)
        
        text = f"""
📋 <b>{lang.get('version_changelog_title', 'История изменений')}</b>

📊 <b>Всего версий:</b> {len(versions)}

💡 <b>Выберите версию для просмотра деталей:</b>
        """
        
        try:
            await callback_query.edit_message_text(text, reply_markup=keyboard)
        except Exception as e:
            logger.error(f"Error editing changelog message: {e}")
            await callback_query.answer("Ошибка при загрузке истории изменений!", show_alert=True)
    
    async def show_version_detail(self, client: Client, callback_query, version_name: str):
        """Показать детали конкретной версии"""
        chat_id = callback_query.message.chat.id
        lang_code = await get_group_language(chat_id)
        lang = load_language(lang_code)
        
        # Читаем содержимое файла версии
        version_file = f"ver{version_name}.txt"
        content = await self.read_version_file(version_file)
        
        if not content:
            await callback_query.answer("Файл версии не найден!", show_alert=True)
            return
        
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton(
                    f"🔙 {lang.get('version_back', 'Назад')}",
                    callback_data=f"version_changelog_{chat_id}"
                )
            ]
        ])
        
        text = f"""
📋 <b>Детали версии {version_name}</b>

{content}
        """
        
        try:
            await callback_query.edit_message_text(text, reply_markup=keyboard)
        except Exception as e:
            logger.error(f"Error editing version detail message: {e}")
            await callback_query.answer("Ошибка при загрузке деталей версии!", show_alert=True)
    
    async def check_updates(self, client: Client, callback_query):
        """Проверить обновления"""
        chat_id = callback_query.message.chat.id
        lang_code = await get_group_language(chat_id)
        lang = load_language(lang_code)
        
        # Получаем все версии
        versions = await self.get_all_versions()
        latest_version = await self.get_latest_version()
        
        # Создаем кнопки для быстрого доступа к версиям
        keyboard_buttons = []
        for i, version_file in enumerate(versions[:6]):  # Показываем только последние 6 версий
            version_name = version_file.replace('.txt', '').replace('ver', '')
            keyboard_buttons.append(
                InlineKeyboardButton(
                    version_name,
                    callback_data=f"version_detail_{version_name}_{chat_id}"
                )
            )
        
        # Разбиваем кнопки по строкам (по 3 кнопки в ряд)
        keyboard_rows = []
        for i in range(0, len(keyboard_buttons), 3):
            keyboard_rows.append(keyboard_buttons[i:i+3])
        
        # Добавляем кнопки навигации
        keyboard_rows.append([
            InlineKeyboardButton(
                f"📋 {lang.get('version_changelog', 'История изменений')}",
                callback_data=f"version_changelog_{chat_id}"
            )
        ])
        keyboard_rows.append([
            InlineKeyboardButton(
                f"🔙 {lang.get('version_back', 'Назад')}",
                callback_data=f"version_back_{chat_id}"
            )
        ])
        
        keyboard = InlineKeyboardMarkup(keyboard_rows)
        
        text = f"""
🔄 <b>{lang.get('version_updates_title', 'Проверка обновлений')}</b>

📱 <b>Последняя версия:</b> <code>{latest_version}</code>
📊 <b>Всего версий:</b> {len(versions)}
📅 <b>Дата проверки:</b> {datetime.now().strftime('%d.%m.%Y %H:%M')}

💡 <b>Быстрый доступ к версиям:</b>
        """
        
        try:
            await callback_query.edit_message_text(text, reply_markup=keyboard)
        except Exception as e:
            logger.error(f"Error editing updates message: {e}")
            await callback_query.answer("Ошибка при проверке обновлений!", show_alert=True)
    
    async def get_all_versions(self):
        """Получить все файлы версий"""
        try:
            pattern = os.path.join(self.version_folder, "ver*.txt")
            version_files = glob.glob(pattern)
            # Сортируем по имени файла (версии)
            version_files.sort(reverse=True)
            return [os.path.basename(f) for f in version_files]
        except Exception as e:
            logger.error(f"Error getting all versions: {e}")
            return []
    
    async def get_latest_version(self):
        """Получить последнюю версию"""
        try:
            versions = await self.get_all_versions()
            if versions:
                latest_file = versions[0]
                return latest_file.replace('ver', '').replace('.txt', '')
            return "1.0.0"
        except Exception as e:
            logger.error(f"Error getting latest version: {e}")
            return "1.0.0"
    
    async def read_version_file(self, filename):
        """Читать содержимое файла версии"""
        try:
            file_path = os.path.join(self.version_folder, filename)
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    return f.read().strip()
            return None
        except Exception as e:
            logger.error(f"Error reading version file {filename}: {e}")
            return None
    
    async def handle_callback(self, client: Client, callback_query):
        """Обработчик callback запросов"""
        data = callback_query.data
        chat_id = callback_query.message.chat.id
        
        try:
            # Отвечаем на callback запрос
            await callback_query.answer()
            
            if data.startswith("version_changelog_"):
                await self.show_changelog(client, callback_query)
            elif data.startswith("version_check_"):
                await self.check_updates(client, callback_query)
            elif data.startswith("version_detail_"):
                # Извлекаем название версии из callback_data
                parts = data.split("_")
                if len(parts) >= 3:
                    version_name = parts[2]
                    await self.show_version_detail(client, callback_query, version_name)
            elif data.startswith("version_back_"):
                await self.show_version_from_callback(client, callback_query)
        except Exception as e:
            logger.error(f"Error in version callback handler: {e}")
            await callback_query.answer("Произошла ошибка!", show_alert=True)

# Создаем экземпляр менеджера
version_manager = DeveloperVersionManager()

# Команда для просмотра версии
@app.on_message(filters.command("version") & filters.group, group=15)
async def version_command(client: Client, message: Message):
    """Команда для просмотра версии"""
    await version_manager.show_version(client, message)

# Обработчик callback запросов
@app.on_callback_query(filters.regex("^version_"), group=15)
async def version_callback_handler(client: Client, callback_query):
    """Обработчик callback запросов версий"""
    try:
        await version_manager.handle_callback(client, callback_query)
    except Exception as e:
        logger.error(f"Error in version callback handler: {e}")
        try:
            await callback_query.answer("Произошла ошибка!", show_alert=True)
        except:
            pass

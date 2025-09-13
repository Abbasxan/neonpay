from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import FloodWait, UserIsBlocked, ChatWriteForbidden, PeerIdInvalid
from config import app, db, OWNER_ID
from language import get_user_language, load_language
import asyncio
import logging
import datetime
import re

# Состояния для FSM
WAITING_FOR_BROADCAST_TYPE = {}
WAITING_FOR_BROADCAST_MESSAGE = {}
WAITING_FOR_CONFIRMATION = {}
BROADCAST_DATA = {}

def clear_user_states(user_id):
    """Очищает все состояния пользователя"""
    WAITING_FOR_BROADCAST_TYPE.pop(user_id, None)
    WAITING_FOR_BROADCAST_MESSAGE.pop(user_id, None)
    WAITING_FOR_CONFIRMATION.pop(user_id, None)
    BROADCAST_DATA.pop(user_id, None)

async def send_message_with_error_handling(client, chat_id, text, reply_markup=None, max_retries=3):
    """Отправляет сообщение с обработкой ошибок и ограничением попыток"""
    for attempt in range(max_retries):
        try:
            await client.send_message(chat_id, text, reply_markup=reply_markup)
            return True
        except (UserIsBlocked, ChatWriteForbidden, PeerIdInvalid):
            return False
        except FloodWait as e:
            if attempt < max_retries - 1:
                await asyncio.sleep(min(e.value, 60))  # Максимум 60 секунд ожидания
                continue
            else:
                return False
        except Exception as e:
            logging.error(f"Error sending message to {chat_id}: {e}")
            if attempt < max_retries - 1:
                await asyncio.sleep(1)
                continue
            else:
                return False
    return False

async def safe_forward_message(client, message, chat_id):
    """Безопасно пересылает или копирует сообщение"""
    try:
        # Сначала пытаемся переслать
        await message.forward(chat_id)
        return True
    except Exception:
        try:
            # Если пересылка не удалась, копируем содержимое
            if message.text:
                await client.send_message(chat_id, message.text)
            elif message.photo:
                await client.send_photo(chat_id, message.photo.file_id, caption=message.caption)
            elif message.video:
                await client.send_video(chat_id, message.video.file_id, caption=message.caption)
            elif message.document:
                await client.send_document(chat_id, message.document.file_id, caption=message.caption)
            elif message.audio:
                await client.send_audio(chat_id, message.audio.file_id, caption=message.caption)
            elif message.voice:
                await client.send_voice(chat_id, message.voice.file_id, caption=message.caption)
            elif message.sticker:
                await client.send_sticker(chat_id, message.sticker.file_id)
            else:
                return False
            return True
        except Exception as e:
            logging.error(f"Failed to copy message to {chat_id}: {e}")
            return False

# Команда для начала рассылки
@app.on_message(filters.command("broadcast") & filters.user(OWNER_ID), group=0)
async def broadcast_command(client: Client, message: Message):
    user_id = message.from_user.id
    lang_code = await get_user_language(user_id)
    lang = load_language(lang_code)
    
    clear_user_states(user_id)
    
    # Запрашиваем тип рассылки
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton(lang.get('broadcast_to_users', 'İstifadəçilərə göndər'), callback_data="broadcast_users")],
        [InlineKeyboardButton(lang.get('broadcast_to_groups', 'Qruplara göndər'), callback_data="broadcast_groups")],
        [InlineKeyboardButton(lang.get('broadcast_to_all', 'Hamıya göndər'), callback_data="broadcast_all")],
        [InlineKeyboardButton(lang.get('cancel', 'Ləğv et'), callback_data="broadcast_cancel")]
    ])
    
    await message.reply(
        lang.get('broadcast_select_type', 'Reklam göndərmək istədiyiniz hədəfi seçin:'),
        reply_markup=keyboard
    )
    
    # Устанавливаем состояние
    WAITING_FOR_BROADCAST_TYPE[user_id] = True

# Обработчик выбора типа рассылки
@app.on_callback_query(filters.regex("^broadcast_(users|groups|all|cancel)$"), group=1)
async def broadcast_type_callback(client: Client, callback_query):
    user_id = callback_query.from_user.id
    
    if user_id != OWNER_ID or user_id not in WAITING_FOR_BROADCAST_TYPE:
        return
    
    lang_code = await get_user_language(user_id)
    lang = load_language(lang_code)
    
    broadcast_type = callback_query.data.split("_")[1]
    
    if broadcast_type == "cancel":
        clear_user_states(user_id)
        await callback_query.edit_message_text(lang.get('broadcast_cancelled', 'Reklam göndərmə ləğv edildi.'))
        return
    
    # Сохраняем тип рассылки
    BROADCAST_DATA[user_id] = {"type": broadcast_type}
    
    # Запрашиваем сообщение для рассылки
    await callback_query.edit_message_text(
        lang.get('broadcast_send_message', 'İndi göndərmək istədiyiniz mesajı yazın. Mətn, şəkil, video və ya digər media ola bilər.')
    )
    
    # Обновляем состояние
    del WAITING_FOR_BROADCAST_TYPE[user_id]
    WAITING_FOR_BROADCAST_MESSAGE[user_id] = True

@app.on_message(filters.private & filters.user(OWNER_ID), group=2)
async def broadcast_message_handler(client: Client, message: Message):
    user_id = message.from_user.id
    
    if user_id not in WAITING_FOR_BROADCAST_MESSAGE:
        return
    
    lang_code = await get_user_language(user_id)
    lang = load_language(lang_code)
    
    # Сохраняем сообщение
    BROADCAST_DATA[user_id]["message_id"] = message.id
    BROADCAST_DATA[user_id]["chat_id"] = message.chat.id
    
    # Получаем количество получателей
    broadcast_type = BROADCAST_DATA[user_id]["type"]
    
    try:
        if broadcast_type == "users":
            count = await db.users.count_documents({})
            recipients_type = lang.get('users', 'istifadəçi')
        elif broadcast_type == "groups":
            count = await db.groups.count_documents({})
            recipients_type = lang.get('groups', 'qrup')
        else:  # all
            users_count = await db.users.count_documents({})
            groups_count = await db.groups.count_documents({})
            count = users_count + groups_count
            recipients_type = lang.get('recipients', 'alıcı')
    except Exception as e:
        logging.error(f"Error counting recipients: {e}")
        await message.reply(lang.get('broadcast_error', 'Xəta baş verdi. Yenidən cəhd edin.'))
        clear_user_states(user_id)
        return
    
    # Запрашиваем подтверждение
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton(lang.get('confirm', 'Təsdiq et'), callback_data="broadcast_confirm")],
        [InlineKeyboardButton(lang.get('cancel', 'Ləğv et'), callback_data="broadcast_cancel_confirm")]
    ])
    
    await message.reply(
        lang.get('broadcast_confirm_message', 'Mesaj {count} {recipients_type} göndəriləcək. Təsdiq edirsiniz?').format(
            count=count,
            recipients_type=recipients_type
        ),
        reply_markup=keyboard
    )
    
    # Обновляем состояние
    del WAITING_FOR_BROADCAST_MESSAGE[user_id]
    WAITING_FOR_CONFIRMATION[user_id] = True

# Обработчик подтверждения рассылки
@app.on_callback_query(filters.regex("^broadcast_(confirm|cancel_confirm)$"), group=1)
async def broadcast_confirm_callback(client: Client, callback_query):
    user_id = callback_query.from_user.id
    
    if user_id != OWNER_ID or user_id not in WAITING_FOR_CONFIRMATION:
        return
    
    lang_code = await get_user_language(user_id)
    lang = load_language(lang_code)
    
    action = callback_query.data.split("_")[1]
    
    if action == "cancel_confirm":
        clear_user_states(user_id)
        await callback_query.edit_message_text(lang.get('broadcast_cancelled', 'Reklam göndərmə ləğv edildi.'))
        return
    
    # Начинаем рассылку
    await callback_query.edit_message_text(lang.get('broadcast_started', 'Reklam göndərmə başladı. Nəticələr haqqında məlumat veriləcək.'))
    
    asyncio.create_task(perform_broadcast(client, user_id, BROADCAST_DATA[user_id], lang))

async def perform_broadcast(client: Client, owner_id: int, broadcast_data: dict, lang):
    """Выполняет рассылку в фоновом режиме"""
    try:
        # Получаем данные для рассылки
        broadcast_type = broadcast_data["type"]
        message_id = broadcast_data["message_id"]
        chat_id = broadcast_data["chat_id"]
        
        # Получаем сообщение для пересылки
        try:
            message_to_forward = await client.get_messages(chat_id, message_id)
        except Exception as e:
            logging.error(f"Failed to get message for broadcast: {e}")
            await client.send_message(owner_id, lang.get('broadcast_message_error', 'Xəta: Mesaj tapılmadı.'))
            return
        
        # Счетчики
        successful = 0
        failed = 0
        
        # Время начала
        start_time = datetime.datetime.now()
        
        # Выполняем рассылку
        if broadcast_type in ["users", "all"]:
            # Рассылка пользователям
            try:
                users_cursor = db.users.find({}, {"_id": 1})
                async for user in users_cursor:
                    user_id = user["_id"]
                    if await safe_forward_message(client, message_to_forward, user_id):
                        successful += 1
                    else:
                        failed += 1
                    
                    await asyncio.sleep(0.3)
            except Exception as e:
                logging.error(f"Error during user broadcast: {e}")
        
        if broadcast_type in ["groups", "all"]:
            # Рассылка в группы
            try:
                groups_cursor = db.groups.find({}, {"_id": 1})
                async for group in groups_cursor:
                    group_id = group["_id"]
                    if await safe_forward_message(client, message_to_forward, group_id):
                        successful += 1
                    else:
                        failed += 1
                    
                    await asyncio.sleep(0.3)
            except Exception as e:
                logging.error(f"Error during group broadcast: {e}")
        
        # Время окончания
        end_time = datetime.datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        # Отправляем отчет
        report = f"""
<b>{lang.get('broadcast_completed', 'Reklam göndərmə tamamlandı')}</b>

<b>{lang.get('broadcast_successful', 'Uğurlu')}:</b> {successful}
<b>{lang.get('broadcast_failed', 'Uğursuz')}:</b> {failed}
<b>{lang.get('broadcast_total', 'Ümumi')}:</b> {successful + failed}
<b>{lang.get('broadcast_duration', 'Müddət')}:</b> {duration:.2f} {lang.get('seconds', 'saniyə')}
"""
        
        await client.send_message(owner_id, report)
        
    except Exception as e:
        logging.error(f"Critical error in broadcast: {e}")
        await client.send_message(owner_id, lang.get('broadcast_critical_error', 'Kritik xəta baş verdi.'))
    
    finally:
        clear_user_states(owner_id)
                

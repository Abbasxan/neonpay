import re
import logging
import asyncio
from pyrogram import Client, filters
from pyrogram.enums import ChatMemberStatus
from pyrogram.errors import UserAlreadyParticipant, ChatAdminRequired, UserNotMutualContact, FloodWait
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import app, db, userbot
from language import load_language, get_group_language
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

mention_cache = {}
cache_expiry = {}
CACHE_DURATION = timedelta(hours=1)  # Кэш на 1 час
MAX_CHECKS_PER_MESSAGE = 3  # Максимум 3 проверки API на сообщение

async def check_mention_type(username: str, client: Client) -> str:
    """
    Проверяет тип упоминания через ID анализ и Telegram API с кэшированием
    Возвращает: 'user', 'bot', 'channel', 'group', 'unknown'
    """
    clean_username = username.lstrip('@').lower()
    current_time = datetime.now()
    
    # Очищаем устаревший кэш
    expired_keys = [key for key, expiry in cache_expiry.items() if current_time > expiry]
    for key in expired_keys:
        mention_cache.pop(key, None)
        cache_expiry.pop(key, None)
    
    # Возвращаем из кэша если есть
    if clean_username in mention_cache:
        logger.debug(f"[ANTIREKLAM] Using cached result for @{clean_username}")
        return mention_cache[clean_username]
    
    try:
        entity = await client.get_chat(clean_username)
        entity_id = entity.id
        
        result = 'unknown'
        
        # Анализируем ID для определения типа
        if str(entity_id).startswith('-100'):
            # Суперчат (группа или канал)
            if entity.type.name == 'CHANNEL':
                result = 'channel'
            elif entity.type.name in ['GROUP', 'SUPERGROUP']:
                result = 'group'
            else:
                result = 'group'  # По умолчанию считаем группой если ID начинается с -100
        elif entity_id > 0:
            # Положительный ID - пользователь или бот
            if entity.type.name == 'PRIVATE':
                # Получаем информацию о пользователе для определения бота
                try:
                    user = await client.get_users(clean_username)
                    result = 'bot' if user.is_bot else 'user'
                except:
                    result = 'user'  # По умолчанию считаем пользователем
            else:
                result = 'user'
        else:
            # Отрицательный ID не начинающийся с -100 (обычная группа)
            result = 'group'
        
        logger.info(f"[ANTIREKLAM] @{clean_username} ID: {entity_id} -> Type: {result}")
        
        mention_cache[clean_username] = result
        cache_expiry[clean_username] = current_time + CACHE_DURATION
        
        return result
            
    except FloodWait as e:
        logger.warning(f"[ANTIREKLAM] FloodWait {e.value}s for @{clean_username}, returning unknown")
        return 'unknown'
    except Exception as e:
        logger.debug(f"[ANTIREKLAM] Cannot check mention type for @{username}: {e}")
        mention_cache[clean_username] = 'unknown'
        cache_expiry[clean_username] = current_time + timedelta(minutes=10)
        return 'unknown'

async def is_advertisement(text: str, chat_id: int, client: Client) -> bool:
    """Умный анализ сообщения на предмет рекламы с ограничениями API запросов"""
    if not text:
        return False
    
    # Безопасное преобразование текста
    try:
        text_lower = text.lower()
    except UnicodeDecodeError:
        # Если возникает ошибка кодировки, используем безопасный способ
        text_lower = str(text).lower()
    
    # Рекламные ключевые слова
    ad_keywords = [
        'kanal', 'channel', 'qoşul', 'join', 'abunə', 'subscribe', 'reklam', 'advertisement',
        'satış', 'sale', 'endirim', 'discount', 'pulsuz', 'free', 'bonus', 'qazanc', 'earn',
        'biznes', 'business', 'iş', 'work', 'gəlir', 'income', 'investisiya', 'investment'
    ]
    
    # Проверяем наличие HTTP/HTTPS ссылок (всегда реклама)
    try:
        if re.search(r'https?://[^\s]+', text, re.IGNORECASE):
            return True
        
        # Проверяем t.me ссылки (всегда реклама)
        if re.search(r't\.me/[^\s]+', text, re.IGNORECASE):
            return True
        
        # Проверяем веб-сайты (всегда реклама)
        if re.search(r'[^\s]+\.(com|ru|org|net|az|tr|de|uk|us|info|biz|co)[^\s]*', text, re.IGNORECASE):
            return True
    except UnicodeDecodeError:
        # Если возникает ошибка кодировки, используем безопасный способ
        safe_text = str(text)
        if re.search(r'https?://[^\s]+', safe_text, re.IGNORECASE):
            return True
        if re.search(r't\.me/[^\s]+', safe_text, re.IGNORECASE):
            return True
        if re.search(r'[^\s]+\.(com|ru|org|net|az|tr|de|uk|us|info|biz|co)[^\s]*', safe_text, re.IGNORECASE):
            return True
    
    # Находим все упоминания пользователей
    try:
        mentions = re.findall(r'@(\w+)', text, re.IGNORECASE)
    except UnicodeDecodeError:
        # Если возникает ошибка кодировки, используем безопасный способ
        mentions = re.findall(r'@(\w+)', str(text), re.IGNORECASE)
    
    if not mentions:
        return False
    
    mentions_to_check = mentions[:MAX_CHECKS_PER_MESSAGE]
    if len(mentions) > MAX_CHECKS_PER_MESSAGE:
        logger.info(f"[ANTIREKLAM] Limiting API checks to {MAX_CHECKS_PER_MESSAGE} mentions out of {len(mentions)}")
    
    suspicious_mentions = 0
    user_mentions = 0
    
    for mention in mentions_to_check:
        mention_type = await check_mention_type(mention, client)
        
        if mention_type == 'user':
            user_mentions += 1
            # Обычные пользователи - не реклама
            continue
        elif mention_type in ['bot', 'channel', 'group']:
            suspicious_mentions += 1
            # Боты, каналы, группы - подозрительно
        elif mention_type == 'unknown':
            mention_lower = mention.lower()
            is_suspicious = False
            
            # Проверяем на ключевые слова
            if any(keyword in mention_lower for keyword in ['channel', 'kanal', 'group', 'qrup', 'admin', 'bot']):
                is_suspicious = True
            
            # Проверяем на подозрительные паттерны имен
            # Случайные символы или необычные комбинации
            if len(mention) >= 8 and re.search(r'[a-z]{3,}[0-9]{2,}', mention_lower):
                is_suspicious = True
            
            # Повторяющиеся символы или паттерны
            if re.search(r'(.)\1{2,}', mention_lower) or re.search(r'(..)\1{2,}', mention_lower):
                is_suspicious = True
            
            # Смешанные языки или необычные комбинации
            if re.search(r'[a-z]+[0-9]+[a-z]+', mention_lower):
                is_suspicious = True
            
            # Очень длинные имена (обычно спам)
            if len(mention) > 15:
                is_suspicious = True
            
            # Имена состоящие только из случайных букв без гласных
            consonants_only = re.sub(r'[aeiouəıöü]', '', mention_lower)
            if len(consonants_only) == len(mention_lower) and len(mention) > 6:
                is_suspicious = True
            
            if is_suspicious:
                suspicious_mentions += 1
                logger.info(f"[ANTIREKLAM] Suspicious unknown mention detected: @{mention}")
    
    unchecked_mentions = len(mentions) - len(mentions_to_check)
    if unchecked_mentions > 0:
        # Анализируем непроверенные упоминания по именам
        for mention in mentions[MAX_CHECKS_PER_MESSAGE:]:
            mention_lower = mention.lower()
            is_suspicious = False
            
            if any(keyword in mention_lower for keyword in ['channel', 'kanal', 'group', 'qrup', 'admin', 'bot']):
                is_suspicious = True
            elif len(mention) >= 8 and re.search(r'[a-z]{3,}[0-9]{2,}', mention_lower):
                is_suspicious = True
            elif re.search(r'(.)\1{2,}', mention_lower) or re.search(r'(..)\1{2,}', mention_lower):
                is_suspicious = True
            elif re.search(r'[a-z]+[0-9]+[a-z]+', mention_lower):
                is_suspicious = True
            elif len(mention) > 15:
                is_suspicious = True
            else:
                consonants_only = re.sub(r'[aeiouəıöü]', '', mention_lower)
                if len(consonants_only) == len(mention_lower) and len(mention) > 6:
                    is_suspicious = True
            
            if is_suspicious:
                suspicious_mentions += 1
                logger.info(f"[ANTIREKLAM] Suspicious unchecked mention detected: @{mention}")
    
    # Если есть подозрительные упоминания, анализируем контекст
    if suspicious_mentions > 0:
        # Анализируем контекст вокруг упоминаний
        for mention in mentions:
            mention_pattern = f'@{re.escape(mention)}'
            match = re.search(mention_pattern, text, re.IGNORECASE)
            if match:
                start = max(0, match.start() - 20)
                end = min(len(text), match.end() + 20)
                try:
                    context = text[start:end].lower()
                except UnicodeDecodeError:
                    # Если возникает ошибка кодировки, используем безопасный способ
                    context = str(text)[start:end].lower()
                
                # Если рядом с упоминанием есть рекламные слова
                if any(keyword in context for keyword in ad_keywords):
                    return True
        
        # Проверяем общий контекст сообщения
        ad_keyword_count = sum(1 for keyword in ad_keywords if keyword in text_lower)
        if ad_keyword_count >= 1 and suspicious_mentions > 0:  # Рекламные слова + подозрительные упоминания
            return True
        
        # Если много подозрительных упоминаний без контекста
        if suspicious_mentions > 1:  # Снижено с 2 до 1
            return True
        
        # Если одно подозрительное упоминание и нет явных пользователей
        if suspicious_mentions >= 1 and user_mentions == 0:
            return True
    
    if user_mentions > 0 and suspicious_mentions == 0:
        # Проверяем только очень явные рекламные паттерны
        explicit_ad_patterns = [
            r'(qoşul|join|abunə|subscribe)\s*@\w+\s*(kanal|channel|qrup|group)',
            r'@\w+\s*(kanal|channel|qrup|group)\s*(da|də|de)\s*(qoşul|join)',
            r'(reklam|ad|advertisement)\s*@\w+'
        ]
        
        for pattern in explicit_ad_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        
        # Если много пользователей упомянуто с рекламными словами
        ad_keyword_count = sum(1 for keyword in ad_keywords if keyword in text_lower)
        if user_mentions > 3 and ad_keyword_count >= 2:
            return True
    
    # Если дошли до сюда, скорее всего это обычное упоминание пользователей
    return False

async def invite_userbot_to_group(chat_id):
    """Qoşulmuş userbot profilini qrupa əlavə edir və hüquqlar verməyi xatırladır"""
    if not userbot:
        logger.warning("[ANTIREKLAM] Userbot not configured")
        return False

    try:
        if not userbot.is_connected:
            logger.warning("[ANTIREKLAM] Userbot not connected")
            return False

        # Userbot məlumatı
        userbot_me = await userbot.get_me()
        userbot_username = userbot_me.username or f"User{userbot_me.id}"
        logger.info(f"[ANTIREKLAM] Userbot info: @{userbot_username} (ID: {userbot_me.id})")

        # Yoxlayırıq, artıq qrupdadırmı
        userbot_already_in_group = False
        try:
            member = await userbot.get_chat_member(chat_id, userbot_me.id)
            if member:
                logger.info(f"[ANTIREKLAM] Userbot artıq qrupdadır: {chat_id}")
                userbot_already_in_group = True
        except Exception:
            logger.info(f"[ANTIREKLAM] Userbot qrupda deyil: {chat_id}")

        # Botun admin hüquqlarını yoxlayırıq
        try:
            bot_member = await app.get_chat_member(chat_id, app.me.id)
            if bot_member.status not in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
                logger.warning(f"[ANTIREKLAM] Bot is not admin in chat {chat_id}, cannot add userbot")
                lang_code = await get_group_language(chat_id)
                lang = load_language(lang_code)
                await app.send_message(
                    chat_id,
                    f"<blockquote>{lang.get('antireklam_bot_not_admin')}</blockquote>"
                )
                return False
            
            # Botun add_members hüququnu yoxlayırıq
            if bot_member.privileges and not bot_member.privileges.can_invite_users:
                logger.warning(f"[ANTIREKLAM] Bot cannot invite users in chat {chat_id}")
                lang_code = await get_group_language(chat_id)
                lang = load_language(lang_code)
                await app.send_message(
                    chat_id,
                    f"<blockquote>{lang.get('antireklam_bot_cannot_invite')}</blockquote>"
                )
                return False
                
        except Exception as e:
            logger.error(f"[ANTIREKLAM] Failed to check bot permissions in chat {chat_id}: {e}")
            lang_code = await get_group_language(chat_id)
            lang = load_language(lang_code)
            await app.send_message(
                chat_id,
                f"<blockquote>{lang.get('antireklam_bot_permission_error')}</blockquote>"
            )
            return False

        # Əlavə etməyə cəhd - istifadəçi hesabını link vasitəsilə əlavə edirik
        if not userbot_already_in_group:
            try:
                invite_link = await app.create_chat_invite_link(chat_id, member_limit=1)
                await userbot.join_chat(invite_link.invite_link)
                logger.info(f"[ANTIREKLAM] Userbot link vasitəsilə qrupa qoşuldu: {chat_id}")
            except Exception as e:
                logger.error(f"[ANTIREKLAM] Userbot-u qoşmaq mümkün olmadı: {e}")
                
                # İnline düymə yaradırıq
                lang_code = await get_group_language(chat_id)
                lang = load_language(lang_code)
                button_url = f"https://t.me/{userbot_username}?startgroup=start&admin=delete_messages"
                keyboard = InlineKeyboardMarkup([
                    [InlineKeyboardButton(lang.get('antireklam_userbot_button', '➕ Asistenti əlavə et'), url=button_url)]
                ])
                
                await app.send_message(
                    chat_id,
                    f"<blockquote>{lang.get('antireklam_userbot_failed')}</blockquote>",
                    reply_markup=keyboard
                )
                return False

        # Mesaj göndəririk
        lang_code = await get_group_language(chat_id)
        lang = load_language(lang_code)
        
        # İnline düymə yaradırıq
        button_url = f"https://t.me/{userbot_username}?startgroup=start&admin=delete_messages"
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(lang.get('antireklam_userbot_button', '➕ Asistenti əlavə et'), url=button_url)]
        ])
        
        if userbot_already_in_group:
            message_text = f"<blockquote>{lang.get('antireklam_userbot_already_in_group')}</blockquote>"
        else:
            message_text = f"<blockquote>{lang.get('antireklam_userbot_added')}</blockquote>"
        
        await app.send_message(chat_id, message_text, reply_markup=keyboard)
        return True

    except Exception as e:
        logger.error(f"[ANTIREKLAM] Userbot dəvətində xəta: {e}")
        return False

async def delete_via_userbot(chat_id, message_id):
    """Удаляет сообщение через userbot"""
    if not userbot:
        return False

    try:
        if not userbot.is_connected:
            logger.warning(f"[ANTIREKLAM] Userbot not connected, cannot delete message")
            return False

        await userbot.delete_messages(chat_id, message_id)
        return True
    except Exception as e:
        logger.error(f"[ANTIREKLAM] Userbot delete failed: {e}")
        return False

if userbot:
    logger.info("[ANTIREKLAM] Registering userbot message handler")
    
    @userbot.on_message(filters.group & (filters.text | filters.caption), group=6)
    async def userbot_monitor_ads(client: Client, message):
        """Userbot мониторит все сообщения в группах и удаляет рекламу от ботов"""
        if not message.from_user:
            return

        chat_id = message.chat.id
        user_id = message.from_user.id
        text = message.text or message.caption or ""

        # Проверяем только сообщения от ботов
        if not message.from_user.is_bot:
            return

        try:
            main_bot_me = await app.get_me()
            if user_id == main_bot_me.id:
                logger.debug(f"[USERBOT] Ignoring message from main bot @{main_bot_me.username}")
                return
        except Exception as e:
            logger.error(f"[USERBOT] Failed to get main bot info: {e}")

        username = message.from_user.username or str(message.from_user.id)
        logger.info(f"[USERBOT] Checking bot message from @{username} in {chat_id}: {text[:50]}...")

        notification_phrases = ["Bot reklamı silindi", "Reklam mesajı silindi", "🤖🚫", "🚫"]
        if any(phrase in text for phrase in notification_phrases):
            logger.debug(f"[USERBOT] Ignoring notification message from @{username}")
            return

        if not await is_advertisement(text, chat_id, client):
            logger.info(f"[USERBOT] No advertisement detected in message from @{username}")
            return

        logger.info(f"[USERBOT] Advertisement detected in message from @{username}")

        # Проверяем включена ли антиреклама в группе
        group_data = await db.groups.find_one({"_id": chat_id}) or {}
        if not group_data.get("antireklam_enabled", True):
            logger.info(f"[USERBOT] Antireklam disabled in group {chat_id}")
            return

        logger.info(f"[USERBOT] Antireklam enabled, proceeding to delete message from @{username}")

        # Удаляем рекламное сообщение от бота
        try:
            await message.delete()
            logger.info(f"[USERBOT] ✅ Deleted bot spam from @{username} in {chat_id}")

            try:
                await db.deleted_messages.insert_one({
                    "chat_id": chat_id,
                    "user_id": user_id,
                    "message_id": message.id,
                    "type": "ad",
                    "reason": "Bot advertisement with links",
                    "timestamp": datetime.now(),
                    "deleted_by": "userbot"
                })
                logger.info(f"[USERBOT] Logged deleted bot ad for user {user_id} in {chat_id}")
            except Exception as e:
                logger.error(f"[USERBOT] Failed to log deleted message: {e}")

            try:
                lang_code = await get_group_language(chat_id)
                lang = load_language(lang_code)
                
                notice = await app.send_message(
                    chat_id, 
                    f"<blockquote>🤖🚫 {lang.get('bot_ad_deleted', 'Bot reklamı silindi.')}</blockquote>"
                )
                
            except Exception as e:
                logger.error(f"[USERBOT] Failed to send notice: {e}")
                
        except Exception as e:
            logger.error(f"[USERBOT] Cannot delete bot spam: {e}")

else:
    logger.warning("[ANTIREKLAM] Userbot not available, bot spam detection disabled")

@app.on_message(filters.group & (filters.text | filters.caption), group=5)
async def delete_ads(client: Client, message):
    if not message.from_user:
        return

    chat_id = message.chat.id
    user_id = message.from_user.id
    text = message.text or message.caption or ""

    if message.from_user.is_bot:
        return  # Боты обрабатываются через userbot

    if not await is_advertisement(text, chat_id, client):
        return

    group_data = await db.groups.find_one({"_id": chat_id}) or {}
    if not group_data.get("antireklam_enabled", True):
        return

    try:
        member = await app.get_chat_member(chat_id, user_id)
        is_admin = member.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]
        if is_admin:
            return  # Не удаляем сообщения от администраторов
    except Exception as e:
        logger.error(f"[ANTIREKLAM] Admin check failed: {e}")

    try:
        await message.delete()
        
        username = message.from_user.username or str(message.from_user.id)
        logger.info(f"[ANTIREKLAM] Deleted ad from user {username} in {chat_id}")
        
        try:
            await db.deleted_messages.insert_one({
                "chat_id": chat_id,
                "user_id": user_id,
                "message_id": message.id,
                "type": "ad",
                "reason": "Smart advertisement detection",
                "timestamp": datetime.now(),
                "deleted_by": "bot"
            })
            logger.info(f"[ANTIREKLAM] Logged deleted ad for user {user_id} in {chat_id}")
        except Exception as e:
            logger.error(f"[ANTIREKLAM] Failed to log deleted message: {e}")
        
        lang_code = await get_group_language(chat_id)
        lang = load_language(lang_code)
        
        # Отправляем временное уведомление
        notice = await client.send_message(
            chat_id, 
            f"<blockquote>🚫 {lang.get('ad_deleted', 'Reklam mesajı silindi.')}</blockquote>"
        )
        
           
    except Exception as e:
        logger.error(f"[ANTIREKLAM] Cannot delete ad: {e}")

@app.on_message(filters.command("antireklam") & filters.group, group=-1)
async def antireklam_command(client: Client, message):
    user = message.from_user
    if not user:
        return

    chat_id = message.chat.id
    lang_code = await get_group_language(chat_id)
    lang = load_language(lang_code)
    args = message.text.split()[1:]

    try:
        member = await app.get_chat_member(chat_id, user.id)
        is_admin = member.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]
    except Exception as e:
        logger.error(f"[ANTIREKLAM CMD] Admin check failed: {e}")
        return await message.reply(f"<blockquote>{lang.get('error_checking_admin', 'Admin statusunu yoxlaya bilmədim.')}</blockquote>")

    if not args:
        group_data = await db.groups.find_one({"_id": chat_id}) or {}
        is_enabled = group_data.get("antireklam_enabled", True)
        status_text = "Aktiv" if is_enabled else "Deaktiv"
        return await message.reply(f"<blockquote>{lang.get('antireklam_status', '🛡 AntiReklam Statusu: {status}').format(status=status_text)}</blockquote>")

    if not is_admin:
        return await message.reply(f"<blockquote>{lang.get('admin_only', 'Bu əmri yalnız adminlər istifadə edə bilər.')}</blockquote>")

    if args[0].lower() in ["on", "off"]:
        enabled = args[0].lower() == "on"
        await db.groups.update_one({"_id": chat_id}, {"$set": {"antireklam_enabled": enabled}}, upsert=True)

        if enabled and userbot and userbot.is_connected:
            await invite_userbot_to_group(chat_id)
        elif enabled and userbot and not userbot.is_connected:
            logger.warning(f"[ANTIREKLAM] Userbot not connected, cannot invite to group {chat_id}")
           
        msg = lang.get("antireklam_enabled" if enabled else "antireklam_disabled", "AntiReklam aktiv edildi." if enabled else "AntiReklam deaktiv edildi.")
        return await message.reply(f"<blockquote>✅ {msg}</blockquote>")

    return await message.reply(f"<blockquote>{lang.get('antireklam_usage', 'İstifadə: /antireklam on|off')}</blockquote>")
    

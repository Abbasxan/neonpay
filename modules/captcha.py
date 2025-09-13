# modules/captcha.py
import logging
import random
import asyncio
from datetime import datetime
from pyrogram import Client, filters
from pyrogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    ChatMemberUpdated,
    ChatPermissions,
)
from pyrogram.enums import ChatMemberStatus, ChatType
from config import app, db
from language import load_language, get_group_language
from modules.mute_utils import mute_user

logger = logging.getLogger(__name__)

# Временное хранилище активных капч: { "chatId_userId": {...} }
active_captchas: dict[str, dict] = {}


# -----------------------------
# Внутренние утилиты
# -----------------------------
def _captcha_key(chat_id: int, user_id: int) -> str:
    return f"{chat_id}_{user_id}"


async def generate_math_captcha() -> tuple[str, list[int], int]:
    """Генерирует простую математическую капчу (без отрицательных ответов)."""
    num1 = random.randint(1, 10)
    num2 = random.randint(1, 10)
    operation = random.choice(["+", "-", "*"])

    if operation == "-":
        # Избегаем отрицательных результатов
        if num2 > num1:
            num1, num2 = num2, num1

    if operation == "+":
        answer = num1 + num2
    elif operation == "-":
        answer = num1 - num2
    else:  # '*'
        answer = num1 * num2

    question = f"{num1} {operation} {num2} = ?"

    # Варианты
    options = {answer}
    while len(options) < 4:
        delta = random.randint(-10, 10)
        wrong = answer + delta
        if wrong >= 0:
            options.add(wrong)

    options = list(options)
    random.shuffle(options)
    correct_index = options.index(answer)
    return question, options, correct_index


async def create_captcha_keyboard(user_id: int, options: list[int]) -> InlineKeyboardMarkup:
    """Создаёт inline-клавиатуру. Укладываемся в лимит callback_data (<= 64 байт)."""
    # callback_data формат: "cap|<uid>|<optIndex>"
    # chat_id не кладём — возьмём его из callback_query.message.chat.id
    keyboard, row = [], []
    for i, option in enumerate(options):
        cb = f"cap|{user_id}|{i}"
        row.append(InlineKeyboardButton(str(option), callback_data=cb))
        if len(row) == 2:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)
    return InlineKeyboardMarkup(keyboard)


async def _restrict_until_solve(chat_id: int, user_id: int):
    """Ограничиваем пользователя до прохождения капчи."""
    try:
        # Проверяем, что пользователь не админ
        try:
            user_member = await app.get_chat_member(chat_id, user_id)
            if user_member.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
                logger.info("[CAPTCHA] User %s is admin, skipping restriction", user_id)
                return
        except Exception as e:
            logger.warning("[CAPTCHA] Failed to check user status: %s", e)
        
        await app.restrict_chat_member(
            chat_id,
            user_id,
            permissions=ChatPermissions(
                can_send_messages=False,
                can_send_media_messages=False,
                can_send_other_messages=False,
                can_add_web_page_previews=False,
            ),
        )
        logger.info("[CAPTCHA] User %s restricted in chat %s", user_id, chat_id)
    except Exception as e:
        logger.error("[CAPTCHA] Failed to restrict user %s in chat %s: %s", user_id, chat_id, e)
        raise


async def _unrestrict_after_solve(chat_id: int, user_id: int):
    """Снимаем ограничения после правильного ответа."""
    try:
        # Проверяем права бота
        try:
            bot_member = await app.get_chat_member(chat_id, "me")
            if bot_member.status not in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
                logger.warning("[CAPTCHA] Bot is not admin, cannot unrestrict user %s", user_id)
                return
        except Exception as e:
            logger.error("[CAPTCHA] Failed to check bot status: %s", e)
            return
        
        chat = await app.get_chat(chat_id)
        permissions = chat.permissions or ChatPermissions(
            can_send_messages=True,
            can_send_media_messages=True,
            can_send_other_messages=True,
            can_add_web_page_previews=True,
        )
        await app.restrict_chat_member(chat_id, user_id, permissions=permissions)
        logger.info("[CAPTCHA] User %s unrestricted in chat %s", user_id, chat_id)
    except Exception as e:
        logger.error("[CAPTCHA] Failed to unrestrict user %s in chat %s: %s", user_id, chat_id, e)
        raise


async def auto_mute_user(chat_id: int, user_id: int, timeout: int):
    """Авто-мут (или иное наказание) по истечении таймера капчи."""
    try:
        await asyncio.sleep(timeout)
        key = _captcha_key(chat_id, user_id)
        data = active_captchas.get(key)
        if not data:
            return  # Уже решено/очищено

        # Мутим 'навсегда' (реализация зависит от твоей mute_user)
        try:
            # Проверяем, что пользователь не админ
            try:
                user_member = await app.get_chat_member(chat_id, user_id)
                if user_member.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
                    logger.info("[CAPTCHA] User %s is admin, skipping mute", user_id)
                    return
            except Exception as e:
                logger.warning("[CAPTCHA] Failed to check user status for mute: %s", e)
            
            await mute_user(chat_id, user_id, None, "Не прошёл капчу")
        except Exception as e:
            logger.error("[CAPTCHA] mute_user failed for %s in %s: %s", user_id, chat_id, e)
            # Фолбэк: просто оставить ограничения (ничего не делаем)

        # Удаляем сообщение с капчей (не критично, если не получится)
        try:
            await app.delete_messages(chat_id, data["message_id"])
        except Exception:
            pass

        # Лог в БД
        try:
            await db.deleted_messages.insert_one(
                {
                    "chat_id": chat_id,
                    "user_id": user_id,
                    "reason": "captcha_failed",
                    "type": "permanent_mute",
                    "timestamp": datetime.now(),
                }
            )
        except Exception as e:
            logger.error("[CAPTCHA] DB insert failed: %s", e)

        # Уведомление в чат
        try:
            lang_code = await get_group_language(chat_id)
            lang = load_language(lang_code)
            await app.send_message(
                chat_id,
                f"🔇 {lang.get('captcha_failed')}",
            )
        except Exception as e:
            logger.error("[CAPTCHA] Failed to notify chat about auto mute: %s", e)

        # Очистка
        active_captchas.pop(key, None)
        logger.info("[CAPTCHA] Auto-muted user %s in chat %s (timeout)", user_id, chat_id)
    except asyncio.CancelledError:
        # Нормально: задача отменена при успешном решении
        logger.debug("[CAPTCHA] auto_mute_user cancelled for %s in %s", user_id, chat_id)
    except Exception as e:
        logger.error("[CAPTCHA] Error in auto_mute_user: %s", e)


async def send_captcha(chat_id: int, user_id: int, user_mention: str):
    """Создаёт и отправляет капчу, ставит таймер."""
    try:
        logger.info(f"[CAPTCHA DEBUG] Attempting to send captcha to user {user_id} in chat {chat_id}")
        
        group_data = await db.groups.find_one({"_id": chat_id}) or {}
        captcha_enabled = group_data.get("captcha_enabled", False)
        
        logger.info(f"[CAPTCHA DEBUG] Group data found: {bool(group_data)}")
        logger.info(f"[CAPTCHA DEBUG] Captcha enabled: {captcha_enabled}")
        
        if not captcha_enabled:
            logger.warning(f"[CAPTCHA DEBUG] Captcha disabled in chat {chat_id}")
            return

        logger.info(f"[CAPTCHA DEBUG] Attempting to restrict user {user_id}")
        
        # Проверяем права бота
        try:
            bot_member = await app.get_chat_member(chat_id, "me")
            if bot_member.status not in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
                logger.warning(f"[CAPTCHA DEBUG] Bot is not admin in chat {chat_id}, cannot send captcha")
                return
            
            # Проверяем, что у бота есть права на ограничение пользователей
            if not bot_member.privileges.can_restrict_members:
                logger.warning(f"[CAPTCHA DEBUG] Bot cannot restrict members in chat {chat_id}")
                return
        except Exception as e:
            logger.error(f"[CAPTCHA DEBUG] Failed to check bot status in chat {chat_id}: {e}")
            return
        
        # Ограничиваем до решения
        try:
            await _restrict_until_solve(chat_id, user_id)
        except Exception as e:
            logger.error(f"[CAPTCHA DEBUG] Failed to restrict user {user_id}: {e}")
            return

        # Генерация
        question, options, correct_index = await generate_math_captcha()
        keyboard = await create_captcha_keyboard(user_id, options)

        lang_code = await get_group_language(chat_id)
        lang = load_language(lang_code)

        timeout = int(group_data.get("captcha_timeout", 300))  # по умолчанию 5 минут
        caption_timeout_text = lang.get("captcha_timeout").format(timeout=timeout)

        captcha_text = (
            f"🤖 {lang.get('captcha_welcome')} {user_mention}\n\n"
            f"🔢 {lang.get('captcha_solve')}\n"
            f"**{question}**\n\n"
            f"⏰ {caption_timeout_text}\n"
            f"⚠️ {lang.get('captcha_warning')}"
        )

        # ⚡️ ВАЖНО: у объекта Message в Pyrogram v2 id называется message.id
        message = await app.send_message(chat_id, captcha_text, reply_markup=keyboard)

        logger.info(f"[CAPTCHA DEBUG] Captcha message sent successfully with ID: {message.id}")

        key = _captcha_key(chat_id, user_id)
        # Если ранее была активная капча (маловероятно), отменим её таймер
        old = active_captchas.get(key)
        if old and (task := old.get("task")) and not task.done():
            task.cancel()

        task = asyncio.create_task(auto_mute_user(chat_id, user_id, timeout))
        active_captchas[key] = {
            "message_id": message.id,
            "correct_index": correct_index,
            "timestamp": datetime.now(),
            "timeout": timeout,
            "task": task,
        }

        logger.info("[CAPTCHA] Sent to user %s in chat %s", user_id, chat_id)
    except Exception as e:
        logger.error(f"[CAPTCHA DEBUG] Error sending captcha to user {user_id} in chat {chat_id}: {e}", exc_info=True)


@app.on_chat_member_updated(group=1)
async def handle_new_member(_: Client, update: ChatMemberUpdated):
    """Обрабатывает вступление новых участников и отправляет капчу."""
    try:
        logger.info(f"[CAPTCHA DEBUG] Chat member update received for chat {update.chat.id if update.chat else 'None'}")
        
        # Интересуют только супергруппы/группы
        if update.chat and update.chat.type not in (ChatType.SUPERGROUP, ChatType.GROUP):
            logger.info(f"[CAPTCHA DEBUG] Ignoring update for chat type: {update.chat.type}")
            return

        new_cm = update.new_chat_member
        old_cm = update.old_chat_member

        logger.info(f"[CAPTCHA DEBUG] New member status: {new_cm.status if new_cm else 'None'}")
        logger.info(f"[CAPTCHA DEBUG] Old member status: {old_cm.status if old_cm else 'None'}")

        if not new_cm:
            logger.info("[CAPTCHA DEBUG] No new chat member data")
            return

        # Новый участник: стал MEMBER или RESTRICTED, а раньше был отсутствующим/left
        became_member = new_cm.status in (ChatMemberStatus.MEMBER, ChatMemberStatus.RESTRICTED)
        was_left = (old_cm is None) or (old_cm.status == ChatMemberStatus.LEFT)

        logger.info(f"[CAPTCHA DEBUG] Became member: {became_member}, Was left: {was_left}")

        if not (became_member and was_left):
            logger.info("[CAPTCHA DEBUG] User status change doesn't trigger captcha")
            return

        user = new_cm.user
        if not user or user.is_bot:
            logger.info(f"[CAPTCHA DEBUG] Ignoring bot or invalid user: {user.is_bot if user else 'No user'}")
            return

        chat_id = update.chat.id
        user_mention = f"@{user.username}" if user.username else (user.first_name or "user")
        
        logger.info(f"[CAPTCHA DEBUG] Triggering captcha for user {user.id} ({user_mention}) in chat {chat_id}")
        
        # Проверяем, что капча включена в группе
        try:
            group_data = await db.groups.find_one({"_id": chat_id}) or {}
            captcha_enabled = group_data.get("captcha_enabled", False)
            if not captcha_enabled:
                logger.info(f"[CAPTCHA DEBUG] Captcha disabled in chat {chat_id}")
                return
        except Exception as e:
            logger.error(f"[CAPTCHA DEBUG] Failed to check captcha settings for chat {chat_id}: {e}")
            return
        
        await send_captcha(chat_id, user.id, user_mention)
    except Exception as e:
        logger.error(f"[CAPTCHA DEBUG] Error in handle_new_member: {e}", exc_info=True)


@app.on_callback_query(filters.regex(r"^cap\|"))
async def handle_captcha_answer(_: Client, callback_query):
    """Обработка нажатий на варианты капчи."""
    try:
        parts = callback_query.data.split("|")
        # ["cap", "<user_id>", "<selected_index>"]
        if len(parts) != 3:
            lang_code = await get_group_language(callback_query.message.chat.id)
            lang = load_language(lang_code)
            return await callback_query.answer(lang.get('captcha_error'), show_alert=True)

        chat_id = callback_query.message.chat.id
        user_id = int(parts[1])
        selected_index = int(parts[2])

        # Только владелец своей капчи может отвечать
        if callback_query.from_user.id != user_id:
            lang_code = await get_group_language(chat_id)
            lang = load_language(lang_code)
            return await callback_query.answer(lang.get('captcha_not_yours'), show_alert=True)
        
        # Проверяем, что пользователь не админ
        try:
            user_member = await app.get_chat_member(chat_id, user_id)
            if user_member.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
                logger.info("[CAPTCHA] User %s is admin, skipping captcha", user_id)
                return await callback_query.answer("✅ Администратор освобожден от капчи!", show_alert=True)
        except Exception as e:
            logger.warning("[CAPTCHA] Failed to check user status: %s", e)

        key = _captcha_key(chat_id, user_id)
        data = active_captchas.get(key)
        if not data:
            lang_code = await get_group_language(chat_id)
            lang = load_language(lang_code)
            return await callback_query.answer(lang.get('captcha_expired'), show_alert=True)

        correct_index = data["correct_index"]
        lang_code = await get_group_language(chat_id)
        lang = load_language(lang_code)

        if selected_index == correct_index:
            # Отменяем таймер
            if (task := data.get("task")) and not task.done():
                task.cancel()

            # Разрешаем писать
            try:
                await _unrestrict_after_solve(chat_id, user_id)
            except Exception:
                lang_code = await get_group_language(chat_id)
                lang = load_language(lang_code)
                return await callback_query.answer(lang.get('captcha_error'), show_alert=True)

            # Правильный ответ — редактируем сообщение
            try:
                await callback_query.edit_message_text(
                    f"✅ {lang.get('captcha_success')}\n"
                    f"🎉 {lang.get('captcha_welcome_success')}"
                )
            except Exception:
                await callback_query.answer(lang.get('captcha_passed'), show_alert=True)

            # Очистка
            active_captchas.pop(key, None)
            logger.info("[CAPTCHA] User %s passed captcha in chat %s", user_id, chat_id)

        else:
            await callback_query.answer(lang.get('captcha_wrong_answer'), show_alert=True)

    except Exception as e:
        logger.error("[CAPTCHA] Error handling captcha answer: %s", e)
        try:
            lang_code = await get_group_language(callback_query.message.chat.id)
            lang = load_language(lang_code)
            await callback_query.answer(lang.get('captcha_error'), show_alert=True)
        except Exception:
            pass


@app.on_message(filters.command("captcha") & filters.group, group=0)
async def captcha_command(_: Client, message):
    """Команда управления капчей: /captcha, /captcha on|off, /captcha timeout <sec>"""
    user = message.from_user
    if not user:
        return

    chat_id = message.chat.id
    lang_code = await get_group_language(chat_id)
    lang = load_language(lang_code)
    args = message.text.split()[1:]

    # Проверка на администратора
    try:
        member = await app.get_chat_member(chat_id, user.id)
        is_admin = member.status in (ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER)
    except Exception as e:
        logger.error("[CAPTCHA CMD] Admin check failed: %s", e)
        return await message.reply(
            f"<blockquote>{lang.get('error_checking_admin')}</blockquote>"
        )

    # Без аргументов — статус
    if not args:
        group_data = await db.groups.find_one({"_id": chat_id}) or {}
        is_enabled = bool(group_data.get("captcha_enabled", False))
        timeout = int(group_data.get("captcha_timeout", 300))
        status_text = lang.get("on") if is_enabled else lang.get("off")
        return await message.reply(
            f"<blockquote>🤖 {lang.get('captcha_status').format(status=status_text)}\n"
            f"⏰ {lang.get('captcha_current_timeout').format(timeout=timeout)}</blockquote>"
        )

    # Дальше — только для админов
    if not is_admin:
        return await message.reply(
            f"<blockquote>{lang.get('admin_only')}</blockquote>"
        )

    sub = args[0].lower()
    if sub in ("on", "off"):
        enabled = sub == "on"
        await db.groups.update_one({"_id": chat_id}, {"$set": {"captcha_enabled": enabled}}, upsert=True)
        msg = lang.get(
            "captcha_enabled" if enabled else "captcha_disabled"
        )
        return await message.reply(f"<blockquote>✅ {msg}</blockquote>")

    if sub == "timeout":
        if len(args) < 2:
            return await message.reply(
                f"<blockquote>{lang.get('captcha_usage')}</blockquote>"
            )
        try:
            timeout = int(args[1])
            if timeout < 30 or timeout > 600:
                return await message.reply(
                    f"<blockquote>❌ {lang.get('captcha_timeout_range')}</blockquote>"
                )
            await db.groups.update_one(
                {"_id": chat_id}, {"$set": {"captcha_timeout": timeout}}, upsert=True
            )
            return await message.reply(
                f"<blockquote>✅ {lang.get('captcha_timeout_set').format(timeout=timeout)}</blockquote>"
            )
        except ValueError:
            return await message.reply(f"<blockquote>❌ {lang.get('invalid_number')}</blockquote>")

    # Хелп
    return await message.reply(
        f"<blockquote>{lang.get('captcha_usage')}</blockquote>"
    )
    

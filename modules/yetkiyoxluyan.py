import logging
from pyrogram import filters
from pyrogram.types import Message
from pyrogram.enums import ChatMemberStatus
from config import app
from language import get_group_language, load_language

# Настройка логгера
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@app.on_message(filters.command("admintest") & filters.group, group=0)
async def admin_test_handler(client, message: Message):
    try:
        if not message.from_user:
            logger.warning("Сообщение без from_user. Возможно, от анонимного администратора.")
            return

        user = message.from_user
        chat_id = message.chat.id
        user_id = user.id

        # Get group language
        lang_code = await get_group_language(chat_id)
        lang = load_language(lang_code)

        logger.info(f"Получена команда /admintest от {user.first_name} ({user.id}) в чате {chat_id}")

        user_member = await client.get_chat_member(chat_id, user_id)
        logger.info(f"Статус пользователя: {user_member.status}")

        bot = client.bot_info  # Загружается в start_bot()
        bot_member = await client.get_chat_member(chat_id, bot.id)
        logger.info(f"Статус бота: {bot_member.status}")

        user_status = user_member.status
        bot_status = bot_member.status

        user_is_admin = user_status in (ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER)
        bot_is_admin = bot_status in (ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER)

        perms = bot_member.privileges if bot_is_admin else None

        if perms:
            logger.info(f"Права бота — "
                        f"Удаление сообщений: {perms.can_delete_messages}, "
                        f"Ограничение участников: {perms.can_restrict_members}, "
                        f"Приглашения: {perms.can_invite_users}, "
                        f"Пин сообщений: {perms.can_pin_messages}")
        else:
            logger.warning("У бота нет прав администратора или privileges не определены.")

        # Build message using localized strings
        msg = f"""{lang.get("admin_test_title")}
<blockquote>
{lang.get("admin_test_user").format(first_name=user.first_name, user_id=user.id)}
{lang.get("admin_test_user_status").format(status=user_status)}
{lang.get("admin_test_user_admin").format(admin_status="✅" if user_is_admin else "❌")}

{lang.get("admin_test_bot").format(bot_name=bot.first_name, bot_id=bot.id)}
{lang.get("admin_test_bot_status").format(status=bot_status)}
{lang.get("admin_test_bot_admin").format(admin_status="✅" if bot_is_admin else "❌")}
</blockquote>
{lang.get("admin_test_permissions")}
{lang.get("admin_test_delete_messages").format(permission="✅" if perms and perms.can_delete_messages else "❌")}
{lang.get("admin_test_restrict_members").format(permission="✅" if perms and perms.can_restrict_members else "❌")}
{lang.get("admin_test_ban_members").format(permission="✅" if perms and perms.can_restrict_members else "❌")}
{lang.get("admin_test_invite_users").format(permission="✅" if perms and perms.can_invite_users else "❌")}
{lang.get("admin_test_pin_messages").format(permission="✅" if perms and perms.can_pin_messages else "❌")}
"""
        await message.reply(msg)

    except Exception as e:
        logger.exception("Произошла ошибка в обработчике /admintest")
        # Get language for error message
        try:
            lang_code = await get_group_language(message.chat.id)
            lang = load_language(lang_code)
            await message.reply(lang.get("admin_test_error"))
        except:
            await message.reply("⚠️ Gözlənilməz xəta baş verdi.")
        

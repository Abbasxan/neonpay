from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from config import app, users_collection, groups_collection, DEFAULT_LANGUAGE
import yaml
import os
from pyrogram.enums import ChatMemberStatus, ChatType
from pyrogram.errors import RPCError


# ──────── Утилиты интерфейса ─────────
async def show_language_menu(client, message: Message, target_id: int, is_group: bool, edit=False, callback_query: CallbackQuery = None):
    langs = get_available_languages()
    buttons = [[InlineKeyboardButton(text=name, callback_data=f"setlang:{code}")] for code, name in langs.items()]
    
    # Добавляем кнопку "Назад"
    lang_code = await get_group_language(target_id) if is_group else await get_user_language(target_id)
    lang = load_language(lang_code)
    back_button = InlineKeyboardButton(lang.get("back_button", "🔙 Geri"), callback_data="back_to_start")
    buttons.append([back_button])
    
    text = lang.get("change_language", "Choose your language:")
    markup = InlineKeyboardMarkup(buttons)

    if edit and callback_query:
        await callback_query.edit_message_text(text, reply_markup=markup)
    else:
        await message.reply(text, reply_markup=markup)


async def is_user_admin(client: Client, chat_id: int, user_id: int) -> bool:
    try:
        member = await client.get_chat_member(chat_id, user_id)
        return member.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]
    except RPCError as e:
        print(f"Error checking user admin status: {e}")
        return False




async def is_bot_admin(client: Client, chat_id: int) -> bool:
    try:
        chat = await client.get_chat(chat_id)
        print(f"Bot is checking admin status for chat: {chat_id} (Type: {chat.type})")
        
        # Проверяем, является ли чат группой, супергруппой или каналом
        if chat.type not in (ChatType.GROUP, ChatType.SUPERGROUP, ChatType.CHANNEL):
            return False

        member = await client.get_chat_member(chat_id, "me")
        print(f"Bot status: {member.status}")  # Выводим статус бота

        # Проверяем, является ли бот администратором
        is_admin = member.status in (ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER)
        print(f"Is bot admin: {is_admin}")  # Выводим результат проверки
        return is_admin
    
    except RPCError as e:
        print(f"[is_bot_admin error] {e}")
        return False



        
# ──────── Команды ─────────

@app.on_message(filters.command("lang"))
async def lang_cmd(client, message: Message):
    chat = message.chat
    user_id = message.from_user.id

    if chat.type == "private":
        await show_language_menu(client, message, user_id, is_group=False)
    else:
        if not await is_bot_admin(client, chat.id):
            lang_code = await get_group_language(chat.id)
            lang = load_language(lang_code)
            await message.reply(lang.get("bot_not_admin"))
            return

        if not await is_user_admin(client, chat.id, user_id):
            lang_code = await get_group_language(chat.id)
            lang = load_language(lang_code)
            await message.reply(lang.get("only_admin_change_lang"))
            return

        await show_language_menu(client, message, chat.id, is_group=True)


@app.on_callback_query(filters.regex(r"^setlang:(\w+)$"))
async def set_language_callback(client: Client, callback_query: CallbackQuery):
    lang_code = callback_query.data.split(":")[1]
    lang_data = load_language(lang_code)

    chat = callback_query.message.chat
    user_id = callback_query.from_user.id

    is_private = (chat.id == user_id)
    target_id = user_id if is_private else chat.id

    try:
        if not is_private and not await is_user_admin(client, chat.id, user_id):
            # Get current language for error message
            current_lang_code = await get_group_language(chat.id)
            current_lang = load_language(current_lang_code)
            await callback_query.answer(current_lang.get("only_admin_change_lang_alert"), show_alert=True)
            return

        target_collection = users_collection if is_private else groups_collection
        await target_collection.update_one({"_id": target_id}, {"$set": {"lang": lang_code}}, upsert=True)

        # Get current language for success message
        current_lang_code = await get_user_language(user_id) if is_private else await get_group_language(chat.id)
        current_lang = load_language(current_lang_code)
        await callback_query.answer(current_lang.get("change_success"))

        if is_private:
            # Для приватных чатов - возвращаем в главное меню
            from modules.start import build_start_keyboard
            bot_username = (await client.get_me()).username
            keyboard = build_start_keyboard(lang_data, bot_username)
            
            # Показываем главное меню с приветственным сообщением
            await callback_query.edit_message_text(
                lang_data.get("start_message").format(mention=callback_query.from_user.mention),
                reply_markup=keyboard
            )
        else:
            # Для групп - показываем сообщение об успешной смене языка
            await callback_query.edit_message_text(
                lang_data.get("language_changed_group").format(language_name=lang_data.get('language_name', lang_code))
            )

    except Exception as e:
        print(f"⚠️ Error updating language: {e}")
        # Get current language for error message
        current_lang_code = await get_user_language(user_id) if is_private else await get_group_language(chat.id)
        current_lang = load_language(current_lang_code)
        await callback_query.answer(current_lang.get("language_change_error"), show_alert=True)



@app.on_callback_query(filters.regex("^languages$"))
async def show_language_menu_callback(client, callback_query: CallbackQuery):
    await show_language_menu(client, callback_query.message, callback_query.from_user.id, is_group=False, edit=True, callback_query=callback_query)

# ──────── Работа с языками ─────────

def load_language(lang_code: str) -> dict:
    path = f"langs/{lang_code}.yml"
    try:
        with open(path, encoding="utf-8") as f:
            return yaml.safe_load(f)
    except Exception as e:
        print(f"⚠️ Error loading language {lang_code}: {e}")
        return {}

def get_available_languages() -> dict:
    langs = {}
    if not os.path.isdir("langs"):
        print("⚠️ 'langs' directory not found.")
        return langs

    for file in os.listdir("langs"):
        if file.endswith(".yml"):
            code = file[:-4]
            try:
                with open(f"langs/{file}", encoding="utf-8") as f:
                    data = yaml.safe_load(f)
                    langs[code] = data.get("language_name", code)
            except Exception as e:
                print(f"⚠️ Error parsing {file}: {e}")
    return langs


def default_language() -> str:
    langs = get_available_languages()
    return DEFAULT_LANGUAGE if DEFAULT_LANGUAGE in langs else next(iter(langs), "az")


async def get_user_language(user_id: int) -> str:
    user = await users_collection.find_one({"_id": user_id}) or {}
    lang = user.get("lang")
    return lang if lang in get_available_languages() else default_language()


async def get_group_language(chat_id: int) -> str:
    group = await groups_collection.find_one({"_id": chat_id}) or {}
    lang = group.get("lang")
    return lang if lang in get_available_languages() else default_language()


# ──────── Дополнительно ─────────

_vulgar_words_cache = {}
_vulgar_tries = {}

def load_vulgar_words(lang_code: str) -> set:
    if lang_code in _vulgar_words_cache:
        return _vulgar_words_cache[lang_code]

    path = f"modules/vulgarwords/{lang_code}.txt"
    try:
        with open(path, "r", encoding="utf-8") as f:
            words = {line.strip().lower() for line in f if line.strip()}
            _vulgar_words_cache[lang_code] = words
            return words
    except FileNotFoundError:
        _vulgar_words_cache[lang_code] = set()
        return set()

def get_vulgar_trie(lang_code: str) -> dict:
    if lang_code in _vulgar_tries:
        return _vulgar_tries[lang_code]

    words = load_vulgar_words(lang_code)
    trie = {}
    for word in words:
        current = trie
        for char in word:
            current = current.setdefault(char, {})
        current["*"] = True
    _vulgar_tries[lang_code] = trie
    return trie
    


async def get_language_for_message(message: Message) -> str:
    return await get_user_language(message.from_user.id) if message.chat.type == "private" else await get_group_language(message.chat.id)


async def get_text(chat_id: int, is_private: bool = True, lang_code: str = None) -> dict:
    if not lang_code:
        lang_code = await get_user_language(chat_id) if is_private else await get_group_language(chat_id)
    return load_language(lang_code)

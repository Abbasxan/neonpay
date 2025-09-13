from pyrogram import filters, Client
from pyrogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from config import (
    app, users_collection, DEV_ID, IDEA_ID, SUPPORT_CHAT,
    DEFAULT_LANGUAGE, LOG_ID, OTHER_BOTS
)
from language import load_language, get_user_language
from helpers.utils import get_user_info
from datetime import datetime

@app.on_message(filters.command("start"), group=0)
async def start_handler(client: Client, message: Message):
    user = message.from_user
    chat = message.chat
    is_private = chat.type == "private"
    user_id = user.id

    # Əgər start əmrində əlavə parametr varsa (məsələn: SPAM_123_456)
    args = message.text.split(maxsplit=1)
    start_param = args[1] if len(args) > 1 else ""

    if start_param.startswith("SPAM_"):
        await handle_spam_parameter(client, message, start_param)
        return

    if is_private:
        # İstifadəçini bazaya əlavə et və ya məlumatlarını yenilə
        result = await users_collection.update_one(
            {"_id": user_id},
            {
                "$set": {
                    "first_name": user.first_name,
                    "username": user.username,
                    "last_activity": datetime.utcnow()
                },
                "$setOnInsert": {
                    "lang": DEFAULT_LANGUAGE,
                    "join_date": datetime.utcnow()
                }
            },
            upsert=True
        )

        # Əgər bu yeni istifadəçidirsə, log qrupuna məlumat göndər
        if result.upserted_id and LOG_ID:
            try:
                # Get language for log message
                lang_code = await get_user_language(user_id)
                lang = load_language(lang_code)
                
                await app.send_message(
                    chat_id=LOG_ID,
                    text=lang.get("new_user_log").format(
                        user_id=user_id,
                        first_name=user.first_name,
                        username=user.username or '—',
                        date=datetime.utcnow().strftime('%d.%m.%Y %H:%M')
                    )
                )
            except Exception as e:
                print(f"[LOG ERROR] Log qrupuna mesaj göndərmək olmadı: {e}")

    # İstifadəçinin dilini götür və dil faylını yüklə
    lang_code = await get_user_language(user_id)
    lang = load_language(lang_code)

    # Start klaviaturasını qur
    keyboard = build_start_keyboard(lang, client.me.username)

    # Başlanğıc mesajını göndər
    await send_start_reply(message, lang, keyboard)
    


async def handle_spam_parameter(client: Client, message: Message, start_param: str):
    if message.chat.type == "private":
        return

    parts = start_param.split("_")
    if len(parts) != 3:
        return

    spam_chat_id = int(parts[1])
    spam_user_id = int(parts[2])

    if spam_user_id != message.from_user.id:
        return

    lang_code = await get_user_language(spam_user_id)
    lang = load_language(lang_code)

    try:
        chat = await client.get_chat(spam_chat_id)
        group_title = chat.title
    except:
        group_title = "qrup"

    warning_text = lang.get(
        "antispam_dm_warn",
        "Sən <b>{group}</b> qrupunda reklam paylaşdın. Bu, Qəddar tərəfindən qəbul edilmir!"
    ).format(group=group_title)

    await message.reply(warning_text)


def build_start_keyboard(lang: dict, bot_username: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(lang.get("add_to_group"), url=f"https://t.me/{bot_username}?startgroup=add")],
        [
            InlineKeyboardButton(lang.get("commands"), callback_data="commands"),
            InlineKeyboardButton(lang.get("features"), callback_data="features")
        ],
        [
            InlineKeyboardButton(lang.get("profile"), callback_data="account"),
            InlineKeyboardButton(lang.get("developer"), callback_data="developer"),
        ],
        [
            InlineKeyboardButton(lang.get("languages"), callback_data="languages"),
            InlineKeyboardButton(lang.get("other_bots"), callback_data="bots")
        ]
    ])


async def send_start_reply(message: Message, lang: dict, keyboard: InlineKeyboardMarkup):
    try:
        await message.reply(
            lang["start_message"].format(mention=message.from_user.mention),
            reply_markup=keyboard
        )
    except Exception as e:
        print(f"[START_HANDLER ERROR] {e}")


@app.on_callback_query(filters.regex("^commands$"), group=0)
async def commands_callback(client: Client, callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    lang = load_language(await get_user_language(user_id))
    
    await callback_query.message.edit_text(
        lang.get("commands_title") + "\n<blockquote>" + lang.get("commands_list") + "</blockquote>",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(lang.get("back_button"), callback_data="back")]])
    )

@app.on_callback_query(filters.regex("^features$"), group=0)
async def features_callback(client: Client, callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    lang = load_language(await get_user_language(user_id))
    
    await callback_query.message.edit_text(
        lang.get("features_title") + "\n<blockquote>" + lang.get("features_list") + "</blockquote>",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(lang.get("back_button"), callback_data="back")]])
    )

@app.on_callback_query(filters.regex("^developer$"), group=0)
async def developer_callback(client: Client, callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    lang = load_language(await get_user_language(user_id))

    dev_info = await get_user_info(client, DEV_ID)
    idea_info = await get_user_info(client, IDEA_ID)

    dev_url = f"https://t.me/{dev_info['username']}" if dev_info.get("username") else f"tg://user?id={dev_info['id']}"
    idea_url = f"https://t.me/{idea_info['username']}" if idea_info.get("username") else f"tg://user?id={idea_info['id']}"

    await callback_query.message.edit_text(
        lang.get("developer_title") + "\n<blockquote>" + 
        lang.get("developer_info").format(
            idea_url=idea_url,
            idea_name=idea_info['first_name'],
            dev_url=dev_url,
            dev_name=dev_info['first_name']
        ) + "</blockquote>",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton(f"🎯 {idea_info['first_name']}", url=idea_url),
             InlineKeyboardButton(f"👨‍💻 {dev_info['first_name']}", url=dev_url)],
            [InlineKeyboardButton(lang.get("support_group"), url=SUPPORT_CHAT)],
            [InlineKeyboardButton(lang.get("back_button"), callback_data="back")]
        ])
    )

@app.on_callback_query(filters.regex("^account$"), group=0)
async def account_callback(client: Client, callback_query: CallbackQuery):
    user = callback_query.from_user
    user_id = callback_query.from_user.id
    lang = load_language(await get_user_language(user_id))
    
    await callback_query.message.edit_text(
        lang.get("account_title") + "\n<blockquote>" + 
        lang.get("account_info").format(
            user_id=user.id,
            first_name=user.first_name,
            username=user.username if user.username else 'Yoxdur'
        ) + "</blockquote>",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(lang.get("back_button"), callback_data="back")]])
    )

@app.on_callback_query(filters.regex("^back$"), group=0)
async def back_callback(client: Client, callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    lang_code = await get_user_language(user_id)
    lang = load_language(lang_code)
    bot_username = client.me.username
    keyboard = build_start_keyboard(lang, bot_username)
    await callback_query.message.edit_text(
        lang.get("start_message").format(mention=callback_query.from_user.mention),
        reply_markup=keyboard
    )

@app.on_callback_query(filters.regex("^bots$"), group=0)
async def bots_callback(client: Client, callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    lang = load_language(await get_user_language(user_id))
    
    buttons = [
        [InlineKeyboardButton(f"{bot['name']} qrupa əlavə et", callback_data=f"bot_{key}")]
        for key, bot in OTHER_BOTS.items()
    ]
    buttons.append([InlineKeyboardButton(lang.get("back_button"), callback_data="back")])
    await callback_query.message.edit_text(
        lang.get("other_bots_title") + "\n<blockquote>" + lang.get("other_bots_info") + "</blockquote>",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

@app.on_callback_query(filters.regex("^bot_"))
async def single_bot_callback(client: Client, callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    lang = load_language(await get_user_language(user_id))
    
    key = callback_query.data.split("_", 1)[1]
    bot_info = OTHER_BOTS.get(key)
    if bot_info:
        await callback_query.message.edit_text(
            f"<b>{bot_info['name']}</b>\n\n"
            f"<blockquote>{bot_info['description']}</blockquote>",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton(f"➕ {bot_info['name']} qrupa əlavə et", url=f"https://t.me/{bot_info['username']}?startgroup=true")],
                [InlineKeyboardButton(lang.get("back_button"), callback_data="bots")]
            ])
        )
    else:
        await callback_query.answer(lang.get("bot_not_found"), show_alert=True)

@app.on_callback_query(filters.regex("^back_to_start$"))
async def back_to_start_callback(client: Client, callback_query: CallbackQuery):
    """Обработчик кнопки 'Назад' в главное меню"""
    user_id = callback_query.from_user.id
    lang_code = await get_user_language(user_id)
    lang = load_language(lang_code)
    bot_username = client.me.username
    keyboard = build_start_keyboard(lang, bot_username)
    
    await callback_query.message.edit_text(
        lang.get("start_message").format(mention=callback_query.from_user.mention),
        reply_markup=keyboard
    )
    

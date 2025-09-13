from pyrogram import filters, Client
from pyrogram.errors import RPCError
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from pyrogram.enums import ParseMode
from config import app, db
import logging
import html

logger = logging.getLogger(__name__)

game_collection = db["kagiz_game"]
choices = ["kagiz", "qayci", "das"]
emojis = {"kagiz": "📄", "qayci": "✂️", "das": "🪨"}


def game_buttons():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("📄 Kağız", callback_data="kagiz"),
            InlineKeyboardButton("✂️ Qayçı", callback_data="qayci"),
            InlineKeyboardButton("🪨 Daş", callback_data="das")
        ]
    ])


@app.on_message(filters.command("kagizqaycidas"), group=-1)
@app.on_callback_query(filters.regex("new_game"))
async def start_new_game(client: Client, event):
    if isinstance(event, Message):
        chat_id = event.chat.id
        send = event.reply
    else:  # CallbackQuery
        chat_id = event.message.chat.id
        send = lambda *args, **kwargs: client.send_message(chat_id, *args, **kwargs)
        await event.answer("Yeni oyun sorğusu.")
        try:
            await event.message.delete()
        except Exception:
            pass

    # Проверка активной игры
    game = await game_collection.find_one({"chat_id": chat_id})
    if game and (game.get("player1") is None or game.get("player2") is None or len(game.get("choices", {})) < 2):
        join_btn = InlineKeyboardMarkup([[InlineKeyboardButton("Qoşul", callback_data="join_game")]])
        return await send("✌️ Bu qrupda artıq aktiv oyun var! Ona qoşulun və ya tamamlayın.", reply_markup=join_btn)

    # Создание новой игры
    game = {"chat_id": chat_id, "player1": None, "player2": None, "choices": {}}
    await game_collection.replace_one({"chat_id": chat_id}, game, upsert=True)

    join_btn = InlineKeyboardMarkup([[InlineKeyboardButton("Qoşul", callback_data="join_game")]])
    await send("✌️ Yeni oyun başladı! Oyuna qoşulmaq üçün 'Qoşul' düyməsinə basın.", reply_markup=join_btn)


@app.on_callback_query(filters.regex("^join_game$"))
async def join_game(client: Client, query: CallbackQuery):
    chat_id = query.message.chat.id
    user_id = query.from_user.id

    game = await game_collection.find_one({"chat_id": chat_id})
    if not game:
        return await query.answer("Oyun tapılmadı.", show_alert=True)

    if user_id in [game.get("player1"), game.get("player2")]:
        return await query.answer("Sən artıq oyundasan.", show_alert=True)

    if game.get("player1") is None:
        await game_collection.update_one({"chat_id": chat_id}, {"$set": {"player1": user_id}})
        return await query.answer("Oyuna qoşuldun. İndi ikinci oyunçu gözlənilir.")

    elif game.get("player2") is None:
        await game_collection.update_one({"chat_id": chat_id}, {"$set": {"player2": user_id, "choices": {}}})

        p1_user = await client.get_users(game["player1"])
        p2_user = await client.get_users(user_id)

        try:
            await query.message.delete()
        except Exception:
            pass

        text = (
            f"✌️ Oyun başladı!\n\n"
            f"1-ci oyunçu: {p1_user.first_name} ❌\n"
            f"2-ci oyunçu: {p2_user.first_name} ❌\n\n"
            f"Zəhmət olmasa seçim edin:"
        )

        await client.send_message(chat_id, text, reply_markup=game_buttons())
        return await query.answer("Oyun başladı!")

    return await query.answer("Oyun artıq doludur.", show_alert=True)


@app.on_callback_query(filters.regex("^(kagiz|qayci|das)$"))
async def make_choice(client: Client, query: CallbackQuery):
    logger.info(f"Triggered choice callback '{query.data}' by {query.from_user.id} in chat {query.message.chat.id}")
    chat_id = query.message.chat.id

    game = await game_collection.find_one({"chat_id": chat_id})
    if not game or not game.get("player2"):
        return await query.answer("Oyun hələ başlamayıb.", show_alert=True)

    user_id = query.from_user.id
    if user_id not in [game["player1"], game["player2"]]:
        return await query.answer("Sən bu oyunun iştirakçısı deyilsən.", show_alert=True)

    if str(user_id) in game["choices"]:
        return await query.answer("Sən artıq seçim etmisən.", show_alert=True)

    game["choices"][str(user_id)] = query.data
    await game_collection.update_one({"chat_id": chat_id}, {"$set": {"choices": game["choices"]}})
    await query.answer(f"Seçimin qeydə alındı: {emojis[query.data]}")

    p1_user = await client.get_users(game["player1"])
    p2_user = await client.get_users(game["player2"])
    p1_status = "✅" if str(game["player1"]) in game["choices"] else "❌"
    p2_status = "✅" if str(game["player2"]) in game["choices"] else "❌"

    text = (
        f"✌️ Oyun başladı!\n\n"
        f"1-ci oyunçu: {html.escape(p1_user.first_name)} {p1_status}\n"
        f"2-ci oyunçu: {html.escape(p2_user.first_name)} {p2_status}\n\n"
        f"Zəhmət olmasa seçim edin:"
    )

    try:
        await query.message.edit_text(text, reply_markup=game_buttons())
    except RPCError:
        pass

    if len(game["choices"]) == 2:
        p1, p2 = game["player1"], game["player2"]
        c1, c2 = game["choices"][str(p1)], game["choices"][str(p2)]

        if c1 == c2:
            result = "Heç-heçə!"
        elif (c1 == "kagiz" and c2 == "das") or (c1 == "qayci" and c2 == "kagiz") or (c1 == "das" and c2 == "qayci"):
            result = f'Qalib: <a href="tg://user?id={p1}">{html.escape(p1_user.first_name)}</a>'
            await update_stats(p1, chat_id, True)
            await update_stats(p2, chat_id, False)
        else:
            result = f'Qalib: <a href="tg://user?id={p2}">{html.escape(p2_user.first_name)}</a>'
            await update_stats(p2, chat_id, True)
            await update_stats(p1, chat_id, False)

        result_markup = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔁 Revanş", callback_data="rematch_game"),
             InlineKeyboardButton("🎮 Yeni oyun", callback_data="new_game")]
        ])

        await query.message.reply(
            f"✌️ Nəticələr:\n"
            f"{html.escape(p1_user.first_name)}: {emojis[c1]}\n"
            f"{html.escape(p2_user.first_name)}: {emojis[c2]}\n\n"
            f"{result}",
            reply_markup=result_markup
        )

        # Сброс игры для реванша
        await game_collection.replace_one(
            {"chat_id": chat_id},
            {"chat_id": chat_id, "player1": p1, "player2": p2, "choices": {}},
            upsert=True
        )


@app.on_callback_query(filters.regex("rematch_game"))
async def rematch_game(client: Client, query: CallbackQuery):
    chat_id = query.message.chat.id
    user_id = query.from_user.id

    last_game = await game_collection.find_one({"chat_id": chat_id})
    if not last_game or not last_game.get("player1") or not last_game.get("player2"):
        return await query.answer("Revanş mümkün deyil.", show_alert=True)

    if user_id not in [last_game["player1"], last_game["player2"]]:
        return await query.answer("Yalnız əvvəlki oyunçular revanş başlada bilər.", show_alert=True)

    p1 = await client.get_users(last_game["player1"])
    p2 = await client.get_users(last_game["player2"])

    text = (
        f"🔁 Revanş başladı!\n\n"
        f"1-ci oyunçu: {p1.first_name} ❌\n"
        f"2-ci oyunçu: {p2.first_name} ❌\n\n"
        f"Zəhmət olmasa seçim edin:"
    )

    await client.send_message(chat_id, text, reply_markup=game_buttons())
    await query.answer("Revanş başladı!")


async def update_stats(user_id: int, chat_id: int, won: bool):
    collection = db["kagiz_stats"]
    field = "wins" if won else "losses"
    await collection.update_one(
        {"user_id": user_id, "chat_id": chat_id},
        {"$inc": {field: 1}},
        upsert=True
    )


@app.on_message(filters.command("top"), group=-1)
async def top_menu(_, message: Message):
    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🏆 Top Qruplar", callback_data="top_groups"),
            InlineKeyboardButton("🌍 Qlobal Top", callback_data="top_global")
        ]
    ])
    await message.reply("📊 Statistika kateqoriyasını seçin:", reply_markup=keyboard)


async def get_user_mention(client: Client, user_id: int):
    try:
        user = await client.get_users(user_id)
        name = html.escape(user.first_name or "İstifadəçi")
        return f'<a href="tg://user?id={user_id}">{name}</a>'
    except Exception:
        return f'<code>{user_id}</code>'


async def get_chat_title(client: Client, chat_id: int):
    try:
        chat = await client.get_chat(chat_id)
        return html.escape(chat.title or str(chat_id))
    except Exception:
        return str(chat_id)


@app.on_callback_query(filters.regex(r"top_"))
async def top_callback(client: Client, query: CallbackQuery):
    collection = db["kagiz_stats"]

    if query.data == "top_groups":
        pipeline = [
            {"$project": {
                "chat_id": 1,
                "user_id": 1,
                "wins": {"$ifNull": ["$wins", 0]},
                "losses": {"$ifNull": ["$losses", 0]}
            }},
            {"$group": {
                "_id": {"chat_id": "$chat_id", "user_id": "$user_id"},
                "wins": {"$sum": "$wins"},
                "losses": {"$sum": "$losses"}
            }},
            {"$project": {
                "chat_id": "$_id.chat_id",
                "user_id": "$_id.user_id",
                "wins": 1,
                "losses": 1,
                "score": {"$subtract": ["$wins", "$losses"]}
            }},
            {"$sort": {"score": -1, "wins": -1}},
            {"$limit": 10}
        ]

        cursor = collection.aggregate(pipeline)
        msg = "🏆 Qruplar üzrə ən yaxşı oyunçular:\n\n"
        i = 1
        async for row in cursor:
            chat_name = await get_chat_title(client, row["chat_id"])
            user_mention = await get_user_mention(client, row["user_id"])
            msg += (f"{i}. Qrup: <b>{chat_name}</b>\n"
                    f"   👤 Oyunçu: {user_mention}\n"
                    f"   ✅ Qələbələr: {row['wins']} | ❌ Məğlubiyyətlər: {row['losses']}\n\n")
            i += 1

    elif query.data == "top_global":
        pipeline = [
            {"$project": {
                "user_id": 1,
                "wins": {"$ifNull": ["$wins", 0]},
                "losses": {"$ifNull": ["$losses", 0]}
            }},
            {"$group": {
                "_id": "$user_id",
                "wins": {"$sum": "$wins"},
                "losses": {"$sum": "$losses"}
            }},
            {"$project": {
                "user_id": "$_id",
                "wins": 1,
                "losses": 1,
                "score": {"$subtract": ["$wins", "$losses"]}
            }},
            {"$sort": {"score": -1, "wins": -1}},
            {"$limit": 10}
        ]

        cursor = collection.aggregate(pipeline)
        msg = "🌍 Qlobal ən yaxşı oyunçular:\n\n"
        i = 1
        async for row in cursor:
            user_mention = await get_user_mention(client, row["user_id"])
            msg += f"{i}. {user_mention} — ✅ {row['wins']} | ❌ {row['losses']}\n"
            i += 1

    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🏆 Top Qruplar", callback_data="top_groups"),
            InlineKeyboardButton("🌍 Qlobal Top", callback_data="top_global")
        ]
    ])
    await query.message.edit_text(msg, reply_markup=keyboard, parse_mode=ParseMode.HTML)
    await query.answer()


@app.on_message(filters.command("mystats"), group=-1)
async def my_stats(client: Client, message: Message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    collection = db["kagiz_stats"]

    # --- Статистика по группе ---
    group_stats = await collection.find_one(
        {"chat_id": chat_id, "user_id": user_id},
        {"_id": 0, "wins": 1, "losses": 1}
    )
    group_wins = group_stats.get("wins", 0) if group_stats else 0
    group_losses = group_stats.get("losses", 0) if group_stats else 0
    group_games = group_wins + group_losses
    group_score = group_wins - group_losses

    # Групповой рейтинг
    pipeline_group_rank = [
        {"$match": {"chat_id": chat_id}},
        {"$project": {
            "user_id": 1,
            "wins": {"$ifNull": ["$wins", 0]},
            "losses": {"$ifNull": ["$losses", 0]},
            "score": {"$subtract": [{"$ifNull": ["$wins", 0]}, {"$ifNull": ["$losses", 0]}]}
        }},
        {"$sort": {"score": -1, "wins": -1}}
    ]
    cursor = collection.aggregate(pipeline_group_rank)
    group_rank = "—"
    i = 1
    async for row in cursor:
        if row["user_id"] == user_id:
            group_rank = str(i)
            break
        i += 1

    # --- Глобальная статистика ---
    pipeline_global_stats = [
        {"$match": {"user_id": user_id}},
        {"$project": {
            "wins": {"$ifNull": ["$wins", 0]},
            "losses": {"$ifNull": ["$losses", 0]}
        }},
        {"$group": {
            "_id": "$user_id",
            "wins": {"$sum": "$wins"},
            "losses": {"$sum": "$losses"}
        }},
        {"$project": {
            "wins": 1,
            "losses": 1,
            "score": {"$subtract": ["$wins", "$losses"]}
        }}
    ]
    cursor = collection.aggregate(pipeline_global_stats)
    global_stats = await cursor.to_list(length=1)
    if global_stats:
        global_wins = global_stats[0]["wins"]
        global_losses = global_stats[0]["losses"]
        global_games = global_wins + global_losses
        global_score = global_stats[0]["score"]
    else:
        global_wins = global_losses = global_games = global_score = 0

    # Глобальный рейтинг
    pipeline_global_rank = [
        {"$project": {
            "user_id": 1,
            "wins": {"$ifNull": ["$wins", 0]},
            "losses": {"$ifNull": ["$losses", 0]},
            "score": {"$subtract": [{"$ifNull": ["$wins", 0]}, {"$ifNull": ["$losses", 0]}]}
        }},
        {"$group": {
            "_id": "$user_id",
            "wins": {"$sum": "$wins"},
            "losses": {"$sum": "$losses"},
            "score": {"$sum": "$score"}
        }},
        {"$sort": {"score": -1, "wins": -1}}
    ]
    cursor = collection.aggregate(pipeline_global_rank)
    global_rank = "—"
    i = 1
    async for row in cursor:
        if row["_id"] == user_id:
            global_rank = str(i)
            break
        i += 1

    # --- Ответ ---
    name = html.escape(message.from_user.first_name)
    text = (
        f"📊 Statistikan — <b>{name}</b>\n\n"
        f"🏠 Bu qrup:\n"
        f"   ✅ Qələbələr: {group_wins}\n"
        f"   ❌ Məğlubiyyətlər: {group_losses}\n"
        f"   🎮 Oyunlar: {group_games}\n"
        f"   ⚖️ Balans: {group_score}\n"
        f"   🏅 Sıra: {group_rank}\n\n"
        f"🌍 Qlobal:\n"
        f"   ✅ Qələbələr: {global_wins}\n"
        f"   ❌ Məğlubiyyətlər: {global_losses}\n"
        f"   🎮 Oyunlar: {global_games}\n"
        f"   ⚖️ Balans: {global_score}\n"
        f"   🏅 Sıra: {global_rank}"
    )
    await message.reply(text, parse_mode=ParseMode.HTML)


@app.on_message(filters.command("kagizqayda"), group=-1)
async def kagiz_qayda_handler(_, message: Message):
    await message.reply(
        "<b>Kağız - Qayçı - Daş | Oyun Qaydası</b>\n\n"
        "🕹 <b>Oyuna başlamaq üçün:</b> /kagizqaycidas\n"
        "Komandanı yazan şəxs oyunçu kimi avtomatik qeydiyyatdan keçmir.\n"
        "İkinci oyunçu 'Qoşul' düyməsinə basaraq oyunçu kimi qoşulur.\n\n"
        "🧠 <b>Oyun qaydaları:</b>\n"
        "Hər iki oyunçu aşağıdakı seçimlərdən birini edir:\n"
        "📄 Kağız\n"
        "✂️ Qayçı\n"
        "🪨 Daş\n\n"
        "🏆 <b>Qələbə şərtləri:</b>\n"
        "- Kağız Daşı udur (Kağız Daşı örtür)\n"
        "- Daş Qayçını udur (Daş Qayçını sındırır)\n"
        "- Qayçı Kağızı udur (Qayçı Kağızı kəsir)\n\n"
        "🤖 <b>Bot nəticəni göstərir:</b>\n"
        "Bot hər iki seçimi müqayisə edərək qalibi müəyyən edir.\n"
        "Əgər hər iki oyunçu eyni seçimi edərsə, nəticə heç-heçə olur.\n\n"
        "🔄 <b>Oyun bitdikdən sonra:</b>\n"
        "Revanş üçün “🔁 Revanş” düyməsini klikləyə bilərsiniz.\n"
        "Yeni oyun başlamaq üçün “🎮 Yeni oyun” düyməsini klikləyin.\n\n"
        "📊 <b>Statistikanı görmək üçün:</b>\n"
        "/top — Qrup və qlobal top oyunçuların siyahısı."
    )
    

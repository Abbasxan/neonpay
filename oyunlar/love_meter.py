from pyrogram import filters
from pyrogram.types import Message
from config import app, db
import random
from datetime import datetime
from pyrogram.enums import ChatAction
import asyncio

MAX_LOVE = 100

def calculate_love_dynamic(previous_score: int = 0) -> int:
    if previous_score >= MAX_LOVE:
        return MAX_LOVE
    increase = random.randint(5, 20)
    return min(previous_score + increase, MAX_LOVE)

def get_pair_id(id1: int, id2: int) -> str:
    return "_".join(sorted([str(id1), str(id2)]))

LOVE_FEEDBACK = {
    (0, 10): [
        "Bu, sevgi yox, uzaq planetlər arasındakı məsafədir.",
        "Aranızda heç nə yoxdur, bəlkə də düşmənsiniz?",
        "Buz dövrü geri qayıdıb, hisslər donub."
    ],
    (11, 20): [
        "Zəif bir qığılcım... bəlkə dostluq?",
        "Ən azından bir salamlaşma var.",
        "Bəlkə vaxtla qaynayıb-qarışar?"
    ],
    (21, 30): [
        "Ortaq maraqlar tapılıb, amma ürəklər susur.",
        "Dostluqla başlayar, sevgi ilə bitər?",
        "Bir az maraq var, amma yetərli deyil."
    ],
    (31, 40): [
        "Bir göz qırpımı... bir təbəssüm.",
        "Ürəkdə yüngül titrəyiş hiss olunur.",
        "Bəlkə bu, başlanğıcdır?"
    ],
    (41, 50): [
        "Bərabərlik var... amma qığılcım lazımdır.",
        "Sevgi yarıyoldadır.",
        "Bu hisslər işlənməlidir!"
    ],
    (51, 60): [
        "Ürək artıq cavab verir.",
        "Burada bir şey var... bir az daha cəhd.",
        "Yaxşı başlanğıcdır!"
    ],
    (61, 70): [
        "Qəlblər yaxınlaşır, barmaq ucları toxunur.",
        "Bir az həyəcan, bir az utancaqlıq.",
        "Bu sevgi real ola bilər."
    ],
    (71, 80): [
        "Gözlər bir-birini tapdı.",
        "Sevgi çiçəklənir!",
        "Hisslər artıq gizlənmir."
    ],
    (81, 90): [
        "Bu iki insan bir-biri üçün yaradılıb.",
        "Qəlblər sinxron döyünür.",
        "Sevgi artıq özünü göstərir."
    ],
    (91, 99): [
        "Evlilik planları qurulur!",
        "Bu sevgi artıq partlayır!",
        "Gəlinlik, toy, xoşbəxt sonluq?"
    ],
    (100, 100): [
        "Sonsuz sevgi! Siz cütlüklərin krallısınız!",
        "100%! Sizin sevginiz tarix yazacaq!",
        "Bu qədər sevgi təhlükəli ola bilər!"
    ]
}

def get_feedback(score: int) -> str:
    for range_tuple, messages in LOVE_FEEDBACK.items():
        if range_tuple[0] <= score <= range_tuple[1]:
            return random.choice(messages)
    return "Sevgi metrinizi partlatdınız!"

def create_progress_bar(score: int, length: int = 10) -> str:
    filled = int(score / MAX_LOVE * length)
    empty = length - filled
    return "❤️" * filled + "🤍" * empty

async def show_typing(client, chat_id, seconds=2):
    for _ in range(seconds):
        await client.send_chat_action(chat_id, ChatAction.TYPING)
        await asyncio.sleep(1)

@app.on_message(filters.command("sevgi") & filters.group, group=-1)
async def love_command(client, message: Message):
    replied = message.reply_to_message
    cmd = message.command
    from_user = message.from_user
    to_user = None

    if len(cmd) >= 3:
        from_user = await client.get_users(cmd[1])
        to_user = await client.get_users(cmd[2])
    elif len(cmd) == 2 and replied:
        from_user = await client.get_users(cmd[1])
        to_user = replied.from_user
    elif replied:
        to_user = replied.from_user
    else:
        await message.reply_text("İstifadəçi tapılmadı. Komanda: <code>/love @ad</code> və ya kiməsə cavab ver.")
        return

    pair_id = get_pair_id(from_user.id, to_user.id)
    record = await db.love_attempts.find_one({"_id": pair_id})
    previous_score = record.get("score", 0) if record else 0
    attempt = (record.get("count", 0) + 1) if record else 1

    score = calculate_love_dynamic(previous_score)
    feedback = get_feedback(score)
    progress_bar = create_progress_bar(score)

    await show_typing(client, message.chat.id, seconds=2)

    text = (
        f"<b>Eşq Testi 💘</b>\n\n"
        f"<b>{from_user.first_name}</b> + <b>{to_user.first_name}</b> = ❤️\n"
        f"Eşq Faizi: <b>{score}%</b>\n"
        f"{progress_bar}\n\n"
        f"{feedback}\n\n"
        f"Bu sizin <b>{attempt}</b> cəhdinizdir."
    )

    await message.reply_text(text)

    await db.love_attempts.update_one(
        {"_id": pair_id},
        {
            "$set": {
                "count": attempt,
                "score": score,
                "createdAt": datetime.utcnow()
            }
        },
        upsert=True
    )
    

@app.on_message(filters.command("sevgitarixi") & filters.group, group=-1)
async def love_log(client, message: Message):
    user_id = message.from_user.id
    user_name = message.from_user.first_name

    # Bütün pair_id-lərdə user_id iştirak edirsə
    cursor1 = db.love_attempts.find({
        "_id": {"$regex": f"^{user_id}_"}
    })
    cursor2 = db.love_attempts.find({
        "_id": {"$regex": f"_{user_id}$"}
    })

    logs = await cursor1.to_list(length=50) + await cursor2.to_list(length=50)

    if not logs:
        await message.reply_text("Tarixçə tapılmadı.")
        return

    text = f"<b>{user_name} üçün eşq tarixçəsi:</b>\n\n"

    for record in logs:
        pair_ids = record["_id"].split("_")
        other_id = int(pair_ids[1]) if int(pair_ids[0]) == user_id else int(pair_ids[0])
        try:
            other_user = await client.get_users(other_id)
            other_name = other_user.first_name
        except Exception:
            other_name = f"ID:{other_id}"

        score = record.get("score", 0)
        count = record.get("count", 0)
        bar = create_progress_bar(score)

        text += (
            f"<blockquote>\n"
            f"<b>{user_name}</b> + <b>{other_name}</b>\n"
            f"Eşq Faizi: <b>{score}%</b>\n"
            f"{bar}\n"
            f"Cəhd sayı: <i>{count}</i>\n"
            f"</blockquote>\n\n"
        )

    await message.reply_text(text)
                

@app.on_message(filters.command("yasakelma") & filters.private, group=-1)
async def secret_love(client, message: Message):
    cmd = message.command
    if len(cmd) < 2:
        await message.reply_text(
            "İstifadə qaydası: /yasakelma <@istifadeci>\n"
            "Bu komanda nəticəni gizli şəkildə yalnız sənə göndərir."
        )
        return

    from_user = message.from_user
    from_user_id = from_user.id
    to_user_input = cmd[1]

    try:
        to_user_obj = await client.get_users(to_user_input)
        to_user_id = to_user_obj.id

        # qarşı tərəfin səni bloklamadığını yoxla
        block_info = await db.blocklist.find_one({"user_id": to_user_id})
        if block_info and from_user_id in block_info.get("blocked_users", []):
            await message.reply_text("Bağışla, bu istifadəçi səni bloklayıb və sən ona test göndərə bilməzsən.")
            return

        # əgər qarşı tərəf botu işlətməyibsə
        user_record = await db.users.find_one({"user_id": to_user_id})
        if not user_record:
            await client.send_message(
                from_user_id,
                f"{to_user_obj.first_name} hələ botu işə salmayıb. Zəhmət olmasa ona /start yazmağını xahiş et."
            )
            return

    except Exception:
        await message.reply_text("İstifadəçini tapmaq mümkün olmadı.")
        return

    pair_id = get_pair_id(from_user_id, to_user_id)
    record = await db.love_attempts.find_one({"_id": pair_id})
    previous_score = record.get("score", 0) if record else 0
    attempt = (record.get("count", 0) + 1) if record else 1

    score = calculate_love_dynamic(previous_score)
    feedback = get_feedback(score)
    progress_bar = create_progress_bar(score)

    await show_typing(client, message.chat.id, seconds=2)

    text = (
        f"<b>Gizli Eşq Testi 💘</b>\n\n"
        f"<blockquote>\n"
        f"<b>Sən</b> + <b>{to_user_obj.first_name}</b>\n"
        f"Eşq Faizi: <b>{score}%</b>\n"
        f"{progress_bar}\n"
        f"{feedback}\n"
        f"Cəhd sayı: <i>{attempt}</i>\n"
        f"</blockquote>"
    )

    await message.reply_text(text)
    await client.send_message(to_user_obj.id, text)

    await db.love_attempts.update_one(
        {"_id": pair_id},
        {
            "$set": {
                "count": attempt,
                "score": score,
                "createdAt": datetime.utcnow()
            }
        },
        upsert=True
    )
    
    

@app.on_message(filters.command("sifirla") & filters.private, group=-1)
async def reset_love_data(client, message: Message):
    if len(message.command) < 2:
        await message.reply_text("İstifadə: /sifirla @istifadeci və ya ID")
        return

    from_user_id = message.from_user.id
    target_input = message.command[1]

    try:
        target_user = await client.get_users(target_input)
        target_id = target_user.id

        pair_id = get_pair_id(from_user_id, target_id)

        result = await db.love_attempts.delete_one({"_id": pair_id})

        if result.deleted_count:
            await message.reply_text(f"{target_user.mention} ilə aranızdakı eşq tarixçəsi sıfırlandı.")
        else:
            await message.reply_text("Tarixçə tapılmadı və ya artıq silinib.")
    except Exception:
        await message.reply_text("İstifadəçini tapmaq mümkün olmadı. Düzgün tag və ya ID daxil edin.")


@app.on_message(filters.command("blokla") & filters.private, group=-1)
async def block_user(client, message: Message):
    if len(message.command) < 2:
        await message.reply_text("İstifadə: /blokla @istifadeci və ya ID")
        return

    blocker_id = message.from_user.id
    target_input = message.command[1]

    try:
        target_user = await client.get_users(target_input)
        target_id = target_user.id

        # DB-də blok siyahısına əlavə et
        await db.blocklist.update_one(
            {"user_id": blocker_id},
            {"$addToSet": {"blocked_users": target_id}},
            upsert=True
        )
        await message.reply_text(f"{target_user.mention} bloklandı.")
    except Exception:
        await message.reply_text("İstifadəçini tapmaq mümkün olmadı. Düzgün tag və ya ID daxil edin.")


@app.on_message(filters.command("unblok") & filters.private, group=-1)
async def unblock_user(client, message: Message):
    if len(message.command) < 2:
        await message.reply_text("İstifadə: /blokdan_cixar @istifadeci və ya ID")
        return

    unblocker_id = message.from_user.id
    target_input = message.command[1]

    try:
        target_user = await client.get_users(target_input)
        target_id = target_user.id

        await db.blocklist.update_one(
            {"user_id": unblocker_id},
            {"$pull": {"blocked_users": target_id}}
        )
        await message.reply_text(f"{target_user.mention} blokdan çıxarıldı.")
    except Exception:
        await message.reply_text("İstifadəçini tapmaq mümkün olmadı. Düzgün tag və ya ID daxil edin.")


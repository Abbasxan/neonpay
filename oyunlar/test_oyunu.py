from pyrogram import filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from config import app

# Вопросы теста с вариантами ответов и правильными ответами
questions = [
    {
        "question": "1. Əxlaq nədir?",
        "options": ["A) Davranış qaydası", "B) Yemək növü", "C) İdman növü", "D) Musiqi janrı"],
        "correct": "A"
    },
    {
        "question": "2. Yalan danışmaq doğrudurmu?",
        "options": ["A) Bəli", "B) Xeyr", "C) Bəzən", "D) Heç vaxt"],
        "correct": "B"
    },
    {
        "question": "3. Həqiqətə sadiq olmaq lazımdırmı?",
        "options": ["A) Bəli", "B) Xeyr", "C) Bəzən", "D) Heç vaxt"],
        "correct": "A"
    },
    {
        "question": "4. İnsanlara hörmət etmək vacibdirmi?",
        "options": ["A) Bəli", "B) Xeyr", "C) Yalnız dostlara", "D) Heç kimə"],
        "correct": "A"
    },
    {
        "question": "5. İnadçılıq yaxşıdır?",
        "options": ["A) Bəli", "B) Xeyr", "C) Bəzən", "D) Heç vaxt"],
        "correct": "C"
    },
    {
        "question": "6. Qəddar olmaq nə deməkdir?",
        "options": ["A) Acımasız olmaq", "B) Güclü olmaq", "C) Dost olmaq", "D) Yalan danışmaq"],
        "correct": "B"
    },
    {
        "question": "7. Sən ədalətlisən?",
        "options": ["A) Bəli", "B) Xeyr", "C) Bəzən", "D) Heç vaxt"],
        "correct": "A"
    },
    {
        "question": "8. Hər zaman doğru danışmaq lazımdırmı?",
        "options": ["A) Bəli", "B) Xeyr", "C) Bəzən", "D) Heç vaxt"],
        "correct": "A"
    },
    {
        "question": "9. Dostlara etibar etmək vacibdirmi?",
        "options": ["A) Bəli", "B) Xeyr", "C) Bəzən", "D) Heç vaxt"],
        "correct": "A"
    },
    {
        "question": "10. Qrup qaydalarına riayət etmək lazımdır?",
        "options": ["A) Bəli", "B) Xeyr", "C) Bəzən", "D) Heç vaxt"],
        "correct": "A"
    },
]

# Для хранения ответов пользователей (можно улучшить на БД)
user_answers = {}

@app.on_message(filters.command("qeddartest") & filters.group, group=-1)
async def start_qeddar_test(client, message):
    user_id = message.from_user.id
    chat_id = message.chat.id

    user_answers[user_id] = {"score": 0, "current": 0}
    await send_question(client, chat_id, user_id, 0)

async def send_question(client, chat_id, user_id, question_index):
    if question_index >= len(questions):
        score = user_answers[user_id]["score"]
        await send_test_result(client, chat_id, user_id, score)
        del user_answers[user_id]
        return

    q = questions[question_index]
    keyboard = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton(opt, callback_data=f"{user_id}:{question_index}:{opt[0]}")]
            for opt in q["options"]
        ]
    )

    await client.send_message(chat_id, f"{q['question']}", reply_markup=keyboard)

@app.on_callback_query(filters.regex(r"^\d+:\d+:[A-D]$"), group=25)
async def handle_test_answer(client, callback_query):
    try:
        data = callback_query.data.split(":")
        if len(data) != 3:
            return

        user_id, q_idx, answer = int(data[0]), int(data[1]), data[2]
        from_user_id = callback_query.from_user.id
        chat_id = callback_query.message.chat.id

        if user_id != from_user_id:
            await callback_query.answer("Bu test sənə aid deyil!", show_alert=True)
            return

        if user_id not in user_answers:
            await callback_query.answer("Test artıq bitib!", show_alert=True)
            return

        q = questions[q_idx]
        if answer == q["correct"]:
            user_answers[user_id]["score"] += 10

        user_answers[user_id]["current"] = q_idx + 1

        await callback_query.answer("Cavab qəbul olundu.")
        await callback_query.message.delete()

        await send_question(client, chat_id, user_id, q_idx + 1)
    except Exception as e:
        print(f"Error in test callback handler: {e}")
        try:
            await callback_query.answer("Xəta baş verdi!", show_alert=True)
        except:
            pass

async def send_test_result(client, chat_id, user_id, score):
    if score >= 80:
        msg = "Sən bu qrupun şərəfisən."
    elif score >= 50:
        msg = "Təmizsən, amma hələ zəif nöqtələrin var."
    else:
        msg = "Ədəbi öyrən, sonra gəl."

    await client.send_message(chat_id, f"📝 <b>Qəddar Test Nəticəsi</b>\n\nSənin balın: <b>{score}</b>/100\n{msg}")
  

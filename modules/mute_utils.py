from datetime import datetime, timedelta
from pyrogram.types import ChatPermissions
from config import app, scheduler
from language import get_text
import asyncio
import logging

async def mute_spammer(chat_id: int, user_id: int, duration_minutes: int = None):
    try:
        if duration_minutes is None or duration_minutes <= 0:
            # Мут без ограничения времени (навсегда)
            await app.restrict_chat_member(
                chat_id=chat_id,
                user_id=user_id,
                permissions=ChatPermissions(can_send_messages=False)
            )
        else:
            until_date = datetime.utcnow() + timedelta(minutes=duration_minutes)
            await app.restrict_chat_member(
                chat_id=chat_id,
                user_id=user_id,
                permissions=ChatPermissions(can_send_messages=False),
                until_date=until_date
            )
        return True
    except Exception:
        return False
        
async def mute_user(chat_id: int, user_id: int, duration_minutes: int = None, reason: str = None):
    try:
        # Если duration_minutes равно None или <= 0, мутим навсегда
        if duration_minutes is None or duration_minutes <= 0:
            # Мут без ограничения времени (навсегда)
            await app.restrict_chat_member(
                chat_id=chat_id,
                user_id=user_id,
                permissions=ChatPermissions(can_send_messages=False)
            )
            
            # Отправляем сообщение о постоянном муте
            try:
                from language import get_group_language, load_language
                lang_code = await get_group_language(chat_id)
                lang = load_language(lang_code)
                
                # Получаем информацию о пользователе
                try:
                    user = await app.get_users(user_id)
                    mention = f"<a href='tg://user?id={user_id}'>{user.first_name}</a>"
                except Exception:
                    mention = f"<a href='tg://user?id={user_id}'>User</a>"
                
                # Отправляем сообщение о постоянном муте
                await app.send_message(
                    chat_id,
                    f"{mention}\n{lang.get('captcha_permanent_mute', '<i>Qəddar bu istifadəçini əbədiyyətə qədər susdurdu.</i>')}"
                )
            except Exception as e:
                logging.error(f"[mute_user] Failed to send permanent mute message: {e}")
            
            return True

        until_date = datetime.utcnow() + timedelta(minutes=duration_minutes)

        await app.restrict_chat_member(
            chat_id=chat_id,
            user_id=user_id,
            permissions=ChatPermissions(can_send_messages=False),
            until_date=until_date
        )

        # Планируем размут через обёртку
        job_id = f"unmute_{chat_id}_{user_id}"
        
        # Проверяем, существует ли уже задание
        for job in scheduler.get_jobs():
            if job.id == job_id:
                job.remove()
                logging.info(f"[mute_user] Removed existing unmute job: {job_id}")
        
        # Добавляем новое задание
        job = scheduler.add_job(
            schedule_unmute_wrapper,
            "date",
            run_date=until_date,
            args=[chat_id, user_id, lang_code],
            id=job_id,
            replace_existing=True
        )

        logging.info(f"[mute_user] Muted user {user_id} in chat {chat_id} for {duration_minutes} minutes.")
        logging.info(f"[mute_user] Scheduled unmute job with ID: {job.id} to run at {until_date}.")
        
        # Сохраняем информацию о муте в базе данных
        try:
            from config import db
            await db.mutes.update_one(
                {"chat_id": chat_id, "user_id": user_id},
                {
                    "$set": {
                        "muted_until": until_date,
                        "muted_at": datetime.utcnow(),
                        "duration_minutes": duration_minutes,
                        "lang_code": lang_code
                    }
                },
                upsert=True
            )
        except Exception as e:
            logging.error(f"[mute_user] Failed to save mute info to database: {e}")
        
        return True

    except Exception as e:
        logging.error(f"[mute_user] Failed to mute user {user_id}: {e}")
        return False

def schedule_unmute_wrapper(chat_id: int, user_id: int, lang_code: str = "az"):
    # Оборачиваем асинхронную функцию
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            loop.create_task(auto_unmute(chat_id, user_id, lang_code))
        else:
            asyncio.run(auto_unmute(chat_id, user_id, lang_code))
    except Exception as e:
        logging.error(f"[schedule_unmute_wrapper] Error scheduling unmute: {e}")
        # Создаем новую задачу для повторной попытки через 1 минуту
        scheduler.add_job(
            schedule_unmute_wrapper,
            "date",
            run_date=datetime.utcnow() + timedelta(minutes=1),
            args=[chat_id, user_id, lang_code]
        )


async def auto_unmute(chat_id: int, user_id: int, lang_code: str = "az"):
    try:
        # Проверяем, действительно ли пользователь все еще замучен
        try:
            member = await app.get_chat_member(chat_id, user_id)
            if member.permissions and member.permissions.can_send_messages:
                logging.info(f"[auto_unmute] User {user_id} already has permission to send messages in chat {chat_id}.")
                return
        except Exception as e:
            logging.error(f"[auto_unmute] Failed to check user permissions: {e}")
        
        # Размучиваем пользователя
        await app.restrict_chat_member(
            chat_id,
            user_id,
            permissions=ChatPermissions(
                can_send_messages=True,
                can_send_media_messages=True,
                can_send_other_messages=True,
                can_add_web_page_previews=True
            )
        )

        # Получаем тексты на нужном языке
        texts = await get_text(chat_id, is_private=False, lang_code=lang_code)
        
        # Получаем информацию о пользователе
        try:
            user = await app.get_users(user_id)
            mention = f"<a href='tg://user?id={user_id}'>{user.first_name}</a>"
        except Exception as e:
            logging.error(f"[auto_unmute] Failed to get user info: {e}")
            mention = f"<a href='tg://user?id={user_id}'>User</a>"

        # Отправляем сообщение о размуте
        await app.send_message(
            chat_id,
            texts.get("auto_unmuted", "{mention} avtomatik olaraq susdurulmadan çıxarıldı.").format(mention=mention)
        )

        # Обновляем информацию в базе данных
        try:
            from config import db
            await db.mutes.update_one(
                {"chat_id": chat_id, "user_id": user_id},
                {"$set": {"unmuted_at": datetime.utcnow(), "active": False}}
            )
        except Exception as e:
            logging.error(f"[auto_unmute] Failed to update mute info in database: {e}")

        logging.info(f"[auto_unmute] Unmuted user {user_id} in chat {chat_id}.")
    except Exception as e:
        logging.error(f"[auto_unmute] Failed to unmute user {user_id}: {e}")

# Функция для проверки и размучивания пользователей, у которых истек срок мута
async def check_expired_mutes():
    try:
        from config import db
        now = datetime.utcnow()
        
        # Находим все активные муты, у которых истек срок
        expired_mutes = db.mutes.find({
            "muted_until": {"$lte": now},
            "active": True
        })
        
        async for mute in expired_mutes:
            chat_id = mute["chat_id"]
            user_id = mute["user_id"]
            lang_code = mute.get("lang_code", "az")
            
            # Размучиваем пользователя
            await auto_unmute(chat_id, user_id, lang_code)
    except Exception as e:
        logging.error(f"[check_expired_mutes] Error checking expired mutes: {e}")

# Добавляем периодическую задачу для проверки истекших мутов
scheduler.add_job(check_expired_mutes, 'interval', minutes=5)


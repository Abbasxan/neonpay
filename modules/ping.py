import time
import psutil
from datetime import datetime, timedelta
from pyrogram import Client, filters
from pyrogram.types import Message
from config import ADMINS, app
from language import get_group_language, get_user_language, load_language

# Время запуска бота
start_time = time.time()

@app.on_message(filters.command("ping") & (filters.private | filters.group))
async def ping_command(client: Client, message: Message):
    """Ping komandası - botun cavab müddətini yoxlayır"""
    start = time.time()
    
    # Определяем язык в зависимости от типа чата
    if message.chat.type == "private":
        # Для приватных чатов используем язык пользователя
        lang_code = await get_user_language(message.from_user.id)
    else:
        # Для групп используем язык группы
        lang_code = await get_group_language(message.chat.id)
    lang = load_language(lang_code)
    
    # Müvəqqəti mesaj göndər
    sent_message = await message.reply(lang.get("ping_checking"))
    
    # Cavab müddətini hesabla
    end = time.time()
    ping_time = round((end - start) * 1000, 2)
    
    # Sistem məlumatları
    cpu_usage = psutil.cpu_percent()
    memory = psutil.virtual_memory()
    memory_usage = memory.percent
    
    ping_text = f"""
{lang.get("ping_pong")}

{lang.get("ping_ping").format(ping_time=ping_time)}
{lang.get("ping_cpu").format(cpu_usage=cpu_usage)}
{lang.get("ping_ram").format(memory_usage=memory_usage)}
{lang.get("ping_status")}
    """
    
    await sent_message.edit_text(ping_text)

@app.on_message(filters.command("uptime") & (filters.private | filters.group))
async def uptime_command(client: Client, message: Message):
    """Uptime komandası - botun işləmə müddətini göstərir"""
    current_time = time.time()
    uptime_seconds = int(current_time - start_time)
    
    # Определяем язык в зависимости от типа чата
    if message.chat.type == "private":
        # Для приватных чатов используем язык пользователя
        lang_code = await get_user_language(message.from_user.id)
    else:
        # Для групп используем язык группы
        lang_code = await get_group_language(message.chat.id)
    lang = load_language(lang_code)
    
    # Vaxtı formatla
    uptime_delta = timedelta(seconds=uptime_seconds)
    days = uptime_delta.days
    hours, remainder = divmod(uptime_delta.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    
    uptime_text = f"""
{lang.get("uptime_title")}

{lang.get("uptime_days").format(days=days)}
{lang.get("uptime_hours").format(hours=hours)}
{lang.get("uptime_minutes").format(minutes=minutes)}
{lang.get("uptime_seconds").format(seconds=seconds)}

{lang.get("uptime_start_time").format(start_time=datetime.fromtimestamp(start_time).strftime('%d.%m.%Y %H:%M:%S'))}
"""
    
    await message.reply(uptime_text)

@app.on_message(filters.command("status") & (filters.private | filters.group))
async def status_command(client: Client, message: Message):
    """Status komandası - botun ətraflı statusunu göstərir"""
    if message.from_user.id not in ADMINS:
        return
    
    current_time = time.time()
    uptime_seconds = int(current_time - start_time)
    uptime_delta = timedelta(seconds=uptime_seconds)
    
    # Определяем язык в зависимости от типа чата
    if message.chat.type == "private":
        # Для приватных чатов используем язык пользователя
        lang_code = await get_user_language(message.from_user.id)
    else:
        # Для групп используем язык группы
        lang_code = await get_group_language(message.chat.id)
    lang = load_language(lang_code)
    
    # Sistem məlumatları
    cpu_usage = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    
    status_text = f"""
{lang.get("status_title")}

{lang.get("status_uptime").format(uptime=uptime_delta)}
{lang.get("status_cpu").format(cpu_usage=cpu_usage)}
{lang.get("status_ram").format(memory_percent=memory.percent, memory_used=memory.used // (1024**3), memory_total=memory.total // (1024**3))}
{lang.get("status_disk").format(disk_percent=disk.percent, disk_used=disk.used // (1024**3), disk_total=disk.total // (1024**3))}

{lang.get("status_python").format(python_version=psutil.version_info)}
{lang.get("status_pyrogram")}
{lang.get("status_connection")}
"""
    
    await message.reply(status_text)

print("✅ Ping modulu yükləndi")
  

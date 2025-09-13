from pyrogram.types import BotCommand
from config import app
from language import load_language
import logging

async def set_bot_commands(lang_code="az"):
    """Устанавливает команды бота с локализацией"""
    try:
        txt = load_language(lang_code)
        
        await app.set_bot_commands([
            BotCommand("start", txt.get('command_start', 'Start the bot')),
            BotCommand("noarqo", txt.get('command_noarqo', 'Profanity filter')),
            BotCommand("antijoin", txt.get('command_antijoin', 'Bans external fake accounts')),
            BotCommand("antispam", txt.get('command_antispam', 'Spam-Link filter')),
            BotCommand("chatbot", txt.get('command_chatbot', 'Artificial intelligence function')),
            BotCommand("help", txt.get('command_help', 'Available commands')),
            BotCommand("reload", txt.get('command_reload', 'Reload filter')),
            BotCommand("id", txt.get('command_id', 'Show ID')),
            BotCommand("economy", txt.get('command_economy', 'Economy system')),
            BotCommand("news", txt.get('command_news', 'Activity reports management')),
        ])
        print(txt.get('commands_set_success', '✅ Commands set successfully'))
    except Exception as e:
        txt = load_language(lang_code)
        print(txt.get('commands_set_fail', '❌ Could not set commands: {error}').format(error=str(e)))

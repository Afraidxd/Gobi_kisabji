import importlib
import asyncio
import time
import random
import re
from html import escape

from typing import Optional
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram import Update
from telegram.ext import Updater, CallbackQueryHandler
from telegram.ext import CommandHandler, MessageHandler, filters

from shivu import collection, top_global_groups_collection, group_user_totals_collection, user_collection, user_totals_collection, shivuu 
from shivu import application, LOGGER
from shivu.modules import ALL_MODULES

locks = {}
message_counters = {}
spam_counters = {}
last_characters = {}
sent_characters = {}
first_correct_guesses = {}
message_counts = {}

def escape_markdown(text):
    escape_chars = r'\*_`\\~>#+-=|{}.!'
    return re.sub(r'([%s])' % re.escape(escape_chars), r'\\\1', text)

async def fav(update: Update, context: CallbackContext) -> None:
    user_id = update.effective_user.id

    if not context.args:
        await update.message.reply_text('𝙋𝙡𝙚𝙖𝙨𝙚 𝙥𝙧𝙤𝙫𝙞𝙙𝙚 𝗖𝗮𝗿 𝙞𝙙...')
        return

    character_id = context.args[0]

    user = await user_collection.find_one({'id': user_id})
    if not user:
        await update.message.reply_text('𝙔𝙤𝙪 𝙝𝙖𝙫𝙚 𝙣𝙤𝙩 𝙂𝙤𝙩 𝘼𝙣𝙮 𝗖𝗮𝗿 𝙮𝙚𝙩...')
        return

    character = next((c for c in user['characters'] if c['id'] == character_id), None)
    if not character:
        await update.message.reply_text('ᴛʜɪs ᴄᴀʀ ɪs ɴᴏᴛ ɪɴ ʏᴏᴜʀ ᴄᴏʟʟᴇᴄᴛɪᴏɴ')
        return

    user['favorites'] = [character_id]

    await user_collection.update_one({'id': user_id}, {'$set': {'favorites': user['favorites']}})

    await update.message.reply_text(f'🥳 ᴄᴀʀ {character["name"]} ɪs ʏᴏᴜʀ ғᴀᴠᴏʀɪᴛᴇ ɴᴏᴡ...')

def main() -> None:
    """Run bot."""

    for module_name in ALL_MODULES:
        imported_module = importlib.import_module("shivu.modules." + module_name)

    application.add_handler(CommandHandler(["favorite"], fav, block=False))

    asyncio.create_task(shivuu.start())
    LOGGER.info("Bot started")

    application.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
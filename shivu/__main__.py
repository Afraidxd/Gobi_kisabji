import importlib
import time
import random
import re
import asyncio
from html import escape

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram import Update
from telegram.ext import CommandHandler, CallbackContext, MessageHandler, CallbackQueryHandler, filters

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

for module_name in ALL_MODULES:
    imported_module = importlib.import_module("shivu.modules." + module_name)

last_user = {}
warned_users = {}

def escape_markdown(text):
    escape_chars = r'\*_`\\~>#+-=|{}.!'
    return re.sub(r'([%s])' % re.escape(escape_chars), r'\\\1', text)


async def fav(update: Update, context: CallbackContext) -> None:
    user_id = update.effective_user.id

    if not context.args:
        await update.message.reply_text('Please provide a character ID.')
        return

    character_id = context.args[0]

    user = await user_collection.find_one({'id': user_id})
    if not user:
        await update.message.reply_text('You are not registered yet. Please use /register command to register.')
        return

    character = next((c for c in user.get('characters', []) if c['id'] == character_id), None)
    if not character:
        await update.message.reply_text('This character is not in your collection.')
        return

    user['favorites'] = [character_id]

    await user_collection.update_one({'id': user_id}, {'$set': {'favorites': user['favorites']}})

    await update.message.reply_text(f'Character {character["name"]} has been added to your favorites.')

def main() -> None:
    """Run bot."""
    application.add_handler(CommandHandler("favorite", fav, block=False))

    application.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    shivuu.start()
    main()
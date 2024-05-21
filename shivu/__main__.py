import importlib
import time
import random
import re
import asyncio
from html import escape

from typing import Optional
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram import Update
from telegram.ext import Updater, CallbackQueryHandler, CommandHandler, MessageHandler, filters, CallbackContext

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

async def is_registered(user_id):
    user = await user_collection.find_one({'id': user_id})
    return bool(user)

def registration_required(func):
    async def wrapper(update: Update, context: CallbackContext, *args, **kwargs):
        user_id = update.effective_user.id
        chat_type = update.message.chat.type
        if not await is_registered(user_id):
            if chat_type == 'private':
                await update.message.reply_text('You need to register first. Use /register to get started.')
            else:
                await update.message.reply_text('You have to register in the game first. Please start the bot in private chat and use /register.')
            return
        return await func(update, context, *args, **kwargs)
    return wrapper

async def register(update: Update, context: CallbackContext) -> None:
    user_id = update.effective_user.id
    user = await user_collection.find_one({'id': user_id})
    
    if user:
        await update.message.reply_text('You are already registered.')
        return

    new_user = {
        'id': user_id,
        'characters': [],
        'favorites': []
    }

    await user_collection.insert_one(new_user)
    await update.message.reply_text('You have been registered successfully!')

@registration_required
async def fav(update: Update, context: CallbackContext) -> None:
    user_id = update.effective_user.id

    if not context.args:
        await update.message.reply_text('Please provide Car ID...')
        return

    character_id = context.args[0]

    user = await user_collection.find_one({'id': user_id})
    character = next((c for c in user['characters'] if c['id'] == character_id), None)
    if not character:
        await update.message.reply_text('This car is not in your collection.')
        return

    user['favorites'] = [character_id]
    await user_collection.update_one({'id': user_id}, {'$set': {'favorites': user['favorites']}})
    await update.message.reply_text(f'🥳 Car {character["name"]} is your favorite now...')

def main() -> None:
    """Run bot."""
    application.add_handler(CommandHandler("register", register, block=False))
    application.add_handler(CommandHandler("favorite", fav, block=False))

    application.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    shivuu.start()
    LOGGER.info("Bot started")
    main()

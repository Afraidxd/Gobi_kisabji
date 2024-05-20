import re
import time
from html import escape
from cachetools import TTLCache
from pymongo import MongoClient, DESCENDING
import asyncio

from telegram import Update, InlineQueryResultPhoto
from telegram.ext import InlineQueryHandler, CallbackContext, CommandHandler 
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from shivu import user_collection, collection, application, db

# Function to replace unprintable characters
def replace_unprintable(text):
    # Replace unprintable characters with a space
    return re.sub(r'[^\x20-\x7E]', ' ', text)

async def details(update: Update, context: CallbackContext) -> None:
    try:
        args = context.args
        character_id = args[0]
    except (IndexError, ValueError):
        await update.message.reply_text("Please provide a valid character ID.")
        return

    character = await collection.find_one({'id': character_id})

    if character:
        # Replace unprintable characters in the character details
        character['name'] = replace_unprintable(character['name'])
        character['anime'] = replace_unprintable(character['anime'])
        character['rarity'] = replace_unprintable(character['rarity'])

        global_count = await user_collection.count_documents({'characters.id': character['id']})
        anime_characters = await collection.count_documents({'anime': character['anime']})

        caption = (
            f"<b>Look At This Car !!</b>\n\n"
            f"Name:<b> {character['name']}</b>\n"
            f"company: <b>{character['anime']}</b>\n"
            f"{character['rarity']}\n"
            f"🆔️: <b>{character['id']}</b>\n\n"
            f"<b>Globally Guessed {global_count} Times...</b>"
        )

        await update.message.reply_photo(
            photo=character['img_url'],
            caption=caption,
            parse_mode='HTML'
        )

    else:
        await update.message.reply_text("Character not found.")

application.add_handler(CommandHandler('details', detail))
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

# Define a lock for concurrency control
lock = asyncio.Lock()
# collection
db.characters.create_index([('id', DESCENDING)])
db.characters.create_index([('anime', DESCENDING)])
db.characters.create_index([('img_url', DESCENDING)])

# user_collection
db.user_collection.create_index([('characters.id', DESCENDING)])
db.user_collection.create_index([('characters.name', DESCENDING)])
db.user_collection.create_index([('characters.img_url', DESCENDING)])

all_characters_cache = TTLCache(maxsize=10000, ttl=36000)
user_collection_cache = TTLCache(maxsize=10000, ttl=60)

# Function to clear the caches
def clear_all_caches():
    all_characters_cache.clear()
    user_collection_cache.clear()

# Call the function to clear the caches
clear_all_caches()

async def inlinequery(update: Update, context: CallbackContext) -> None:
    async with lock:
        query = update.inline_query.query
        offset = int(update.inline_query.offset) if update.inline_query.offset else 0

        # Load 3 results per row
        results_per_row = 4
        results_per_page = 8
        start_index = offset
        end_index = offset + results_per_page

        if query.startswith('collection.'):
            user_id, *search_terms = query.split(' ')[0].split('.')[1], ' '.join(query.split(' ')[1:])
            if user_id.isdigit():
                if user_id in user_collection_cache:
                    user = user_collection_cache[user_id]
                else:
                    user = await user_collection.find_one({'id': int(user_id)})
                    user_collection_cache[user_id] = user

                if user:
                    all_characters = list({v['id']:v for v in user['characters']}.values())
                    if search_terms:
                        regex = re.compile(' '.join(search_terms), re.IGNORECASE)
                        all_characters = [character for character in all_characters if regex.search(character['name']) or regex.search(character['anime'])]
                else:
                    all_characters = []
            else:
                all_characters = []
        else:
            if query:
                regex = re.compile(query, re.IGNORECASE)
                all_characters = list(await collection.find({"$or": [{"name": regex}, {"anime": regex}]}).to_list(length=None))
            else:
                if 'all_characters' in all_characters_cache:
                    all_characters = all_characters_cache['all_characters']
                else:
                    all_characters = list(await collection.find({}).to_list(length=None))
                    all_characters_cache['all_characters'] = all_characters

        # Slice the characters based on the current offset and results per page
        characters = all_characters[start_index:end_index]

        if len(characters) > results_per_page:
            characters = characters[:results_per_page]
            next_offset = str(end_index)
        else:
            next_offset = str(end_index + len(characters) - results_per_page)

        results = []
        for character in characters:
            global_count = await user_collection.count_documents({'characters.id': character['id']})
            anime_characters = await collection.count_documents({'company': character['company']})

            if query.startswith('collection.'):
                user_character_count = sum(c['id'] == character['id'] for c in user['characters'])
                user_anime_characters = sum(c['company'] == character['company'] for c in user['characters'])
                caption = f"<b> Look At <a href='tg://user?id={user['id']}'>{(escape(user.get('first_name', user['id'])))}</a>'s Car </b>\n\n🏎: <b>{character['car name']} (x{user_character_count})</b>\n🏬: <b>{character['company']} ({user_anime_characters}/{anime_characters})</b>\n<b>{character['rarity']}</b>\n\n<b>🆔️:</b> {character['id']}"
            else:
                caption = f"<b>Look At This Car !!</b>\n\n🏎:<b> {character['car name']}</b>\n🏬: <b>{character['company']}</b>\n<b>{character['rarity']}</b>\n🆔️: <b>{character['id']}</b>\n\n<b>Globally Guessed {global_count} Times...</b>"
            results.append(
                InlineQueryResultPhoto(
                    thumbnail_url=character['img_url'],
                    id=f"{character['id']}_{time.time()}",
                    photo_url=character['img_url'],
                    caption=caption,
                    parse_mode='HTML',
                    photo_width=300,  # Adjust the width as needed
                    photo_height=300  # Adjust the height as needed
                )
            )

        await update.inline_query.answer(results, next_offset=next_offset, cache_time=5)

application.add_handler(InlineQueryHandler(inlinequery, block=False))
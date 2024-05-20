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
                        if search_terms[0].isdigit():  # Check if the search term is a digit (character ID)
                            all_characters = [character for character in all_characters if str(character['id']) == search_terms[0]]
                        else:
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
            anime_characters = await collection.count_documents({'anime': character['anime']})

            price = character.get('price', 'N/A')  # Get the price or set as 'N/A' if not available
            if query.startswith('collection.'):
                user_character_count = sum(c['id'] == character['id'] for c in user['characters'])
                user_anime_characters = sum(c['anime'] == character['anime'] for c in user['characters'])
                caption = (
                    f"<b> Look At <a href='tg://user?id={user['id']}'>{escape(user.get('first_name', user['id']))}</a>'s Character</b>\n\n"
                    f"🍃 𝙉𝘼𝙈𝙀 : <b>{character['name']} (x{user_character_count})</b>\n\n"
                    f"🍃 𝘾𝙊𝙈𝙋𝘼𝙉𝙔 : <b>{character['anime']} ({user_anime_characters}/{anime_characters})</b>\n\n"
                    f"🍃 𝙍𝘼𝙍𝙄𝙏𝙔 :<b>{character['rarity']}</b>\n\n<b>🍃 𝙋𝙍𝙄𝘾𝙀 : {price}🔖</b>\n\n"
                    f"<b>🆔️:</b> {character['id']} | "
                )
            else:
                caption = (
                    f"<b>ʟᴏᴏᴋ ᴀᴛ ᴛʜɪs ᴄᴀʀ !!</b>\n\n"
                    f"🍃 𝙉𝘼𝙈𝙀:<b> {character['name']}</b>\n\n"
                    f"🍃 𝘾𝙊𝙈𝙋𝘼𝙉𝙔 : <b>{character['anime']}</b>\n\n"
                    f"🍃 𝙍𝘼𝙍𝙄𝙏𝙔 :<b>{character['rarity']}</b>\n"
                    f"🆔️: <b>{character['id']}</b>\n\n"
                    f"<b>🍃 𝙋𝙍𝙄𝘾𝙀 : {price}🔖</b>\n\n"

                )

            keyboard = [[InlineKeyboardButton("ʜᴏᴡ ᴍᴀɴʏ ɪ ʜᴀᴠᴇ ❓", callback_data=f"check_{character['id']}")]]
            reply_markup = InlineKeyboardMarkup(keyboard)

            results.append(
                InlineQueryResultPhoto(
                    thumbnail_url=character['img_url'],
                    id=f"{character['id']}_{time.time()}",
                    photo_url=character['img_url'],
                    caption=caption,
                    parse_mode='HTML',
                    photo_width=300,  # Adjust the width as needed
                    photo_height=300,  # Adjust the height as needed
                    reply_markup=reply_markup 
                )
            )

        await update.inline_query.answer(results, next_offset=next_offset, cache_time=5)

application.add_handler(InlineQueryHandler(inlinequery, block=False))


async def check(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    user_id = query.from_user.id
    data = query.data.split('_')
    character_id = data[1]

    user_data = await user_collection.find_one({'id': user_id})
    characters = user_data.get('characters', [])
    quantity = sum(1 for char in characters if char['id'] == character_id)

    await query.answer(f"ʏᴏᴜ ʜᴀᴠᴇ {quantity} ᴏғ ᴛʜɪs ᴄᴀʀ.", show_alert=True)
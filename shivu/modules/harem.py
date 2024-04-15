from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CommandHandler, CallbackContext, CallbackQueryHandler
from telegram.ext.dispatcher import run_async
from itertools import groupby
import urllib.request
import re
import math
from html import escape 
import random

from shivu import collection, user_collection, application

@run_async
async def harem(update: Update, context: CallbackContext, page: int = 0) -> None:
    user_id = update.effective_user.id

    user = await user_collection.find_one({'id': user_id})
    if not user:
        if update.message:
            await update.message.reply_text('𝙔𝙤𝙪 𝙃𝙖𝙫𝙚 𝙉𝙤𝙩 𝙂𝙧𝙖𝙗 𝙖𝙣𝙮 𝙎𝙡𝙖𝙫𝙚 𝙔𝙚𝙩...')
        else:
            await update.callback_query.edit_message_text('You Don\'t have any car Yet')
        return

    characters = sorted(user['characters'], key=lambda x: (x['company'], x['id']))

    character_counts = {k: len(list(v)) for k, v in groupby(characters, key=lambda x: x['id'])}

    unique_characters = list({character['id']: character for character in characters}.values())

    total_pages = math.ceil(len(unique_characters) / 7)

    if page < 0 or page >= total_pages:
        page = 0

    harem_message = f"<b>{escape(update.effective_user.first_name)}'s Harem - Page {page+1}/{total_pages}</b>\n"

    current_characters = unique_characters[page*7:(page+1)*7]

    current_grouped_characters = {k: list(v) for k, v in groupby(current_characters, key=lambda x: x['company'])}

    for anime, characters in current_grouped_characters.items():
        harem_message += f'\n⥱ <b>{anime} {len(characters)}/{await collection.count_documents({"company": anime})}</b>\n'

        for character in characters:

            count = character_counts[character['id']]
            harem_message += f'➥{character["id"]}| {character["rarity"]} |{character["car name"]} ×{count}\n'

    total_count = len(user['characters'])

    keyboard = [[InlineKeyboardButton(f"See Collection ({total_count})", switch_inline_query_current_chat=f"collection.{user_id}")]]

    if total_pages > 1:

        nav_buttons = []
        if page > 0:
            nav_buttons.append(InlineKeyboardButton("◄", callback_data=f"harem:{page-1}:{user_id}"))
        if page < total_pages - 1:
            nav_buttons.append(InlineKeyboardButton("►", callback_data=f"harem:{page+1}:{user_id}"))
        keyboard.append(nav_buttons)

    reply_markup = InlineKeyboardMarkup(keyboard)

    if 'favorites' in user and user['favorites']:

        fav_character_id = user['favorites'][0]
        fav_character = next((c for c in user['characters'] if c['id'] == fav_character_id), None)

        if fav_character and 'img_url' in fav_character:
            if update.message:
                await update.message.reply_photo(photo=fav_character['img_url'], caption=harem_message, reply_markup=reply_markup, parse_mode=ParseMode.HTML)
            else:
                await update.callback_query.edit_message_caption(caption=harem_message, reply_markup=reply_markup, parse_mode=ParseMode.HTML)
        else:
            if update.message:
                await update.message.reply_text(harem_message, reply_markup=reply_markup, parse_mode=ParseMode.HTML)
            else:
                await update.callback_query.edit_message_text(text=harem_message, reply_markup=reply_markup, parse_mode=ParseMode.HTML)
    else:
        if update.message:
            await update.message.reply_text(harem_message, reply_markup=reply_markup, parse_mode=ParseMode.HTML)
        else:
            await update.callback_query.edit_message_text(text=harem_message, reply_markup=reply_markup, parse_mode=ParseMode.HTML)

@run_async
async def fav(update: Update, context: CallbackContext) -> None:
    user_id = update.effective_user.id

    user = await user_collection.find_one({'id': user_id})
    if not user:
        if update.message:
            await update.message.reply_text('𝙔𝙤𝙪 𝙃𝙖𝙫𝙚 𝙉𝙤𝙩 𝙂𝙧𝙖𝙗 𝙖𝙣𝙮 𝙎𝙡𝙖𝙫𝙚 𝙔𝙚𝙩...', parse_mode=ParseMode.HTML)
        else:
            await update.callback_query.edit_message_text('You Don\'t have any car Yet', parse_mode=ParseMode.HTML)
        return

    characters = user['characters']

    if not characters:
        if update.message:
            await update.message.reply_text('𝙄 𝙊𝙐 𝙎𝙁 𝙈𝙄 𝘽𝙊𝙓 𝘾𝙍𝙄𝙏𝙃𝙀 𝙒𝙊 𝙒𝙀 𝙂 𝙄 𝘼...', parse_mode=ParseMode.HTML)
        else:
            await update.callback_query.edit_message_text('You haven\'t added any cars to your collection yet...', parse_mode=ParseMode.HTML)
        return

    fav_character_id = user['favorites'][0]
    fav_character = next((c for c in characters if c['id'] == fav_character_id), None)

    if not fav_character:
        if update.message:
            await update.message.reply_text('𝙄 𝙊𝙐 𝙎𝙁 𝙈𝙄 𝙏𝙃𝙀 𝙒𝙊 𝙒𝙀 𝙂 𝙄 𝙉𝙀𝙒𝙎...', parse_mode=ParseMode.HTML)
        else:
            await update.callback_query.edit_message_text('You haven\'t set a favorite car yet...', parse_mode=ParseMode.HTML)
        return

    if 'img_url' in fav_character:
        if update.message:
            await update.message.reply_photo(photo=fav_character['img_url'], parse_mode=ParseMode.HTML)
        else:
            await update.callback_query.edit_message_caption(caption=fav_character['car name'], parse_mode=ParseMode.HTML)
    else:
        if update.message:
            await update.message.reply_text(fav_character['car name'], parse_mode=ParseMode.HTML)
        else:
            await update.callback_query.edit_message_text(text=fav_character['car name'], parse_mode=ParseMode.HTML)

@run_async
async def harem_callback(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    data = query.data

    _, page, user_id = data.split(':')

    page = int(page)
    user_id = int(user_id)

    if query.from_user.id != user_id:
        await query.answer("This is not your Nigga ", show_alert=True)
        return

    await harem(update, context, page)

application.add_handler(CommandHandler("collection", harem, block=False))
harem_handler = CallbackQueryHandler(harem_callback, pattern='^harem.*', block=False)
application.add_handler(harem_handler)

application.add_handler(CommandHandler("fav", fav, block=False))
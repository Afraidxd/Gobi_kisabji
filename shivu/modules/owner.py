import os
import random
import html

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CommandHandler, CallbackQueryHandler, CallbackContext

from shivu import (
    application, PHOTO_URL, OWNER_ID,
    user_collection, top_global_groups_collection, group_user_totals_collection,
    sudo_users as SUDO_USERS
)

photo = random.choice(PHOTO_URL)

async def send_leaderboard(context: CallbackContext, chat_id: int, leaderboard_message: str, photo_url: str, message_id: int = None):
    keyboard = [
        [
            InlineKeyboardButton("Top Group Users", callback_data='ctop'),
            InlineKeyboardButton("Top Groups", callback_data='topgc')
        ],
        [InlineKeyboardButton("Close", callback_data='close')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    if message_id:
        await context.bot.edit_message_media(
            media={'type': 'photo', 'media': photo_url, 'caption': leaderboard_message, 'parse_mode': 'HTML'},
            chat_id=chat_id,
            message_id=message_id,
            reply_markup=reply_markup
        )
    else:
        await context.bot.send_photo(chat_id=chat_id, photo=photo_url, caption=leaderboard_message, parse_mode='HTML', reply_markup=reply_markup)

async def global_leaderboard(update: Update, context: CallbackContext, query=None) -> None:
    cursor = top_global_groups_collection.aggregate([
        {"$project": {"group_name": 1, "count": 1}},
        {"$sort": {"count": -1}},
        {"$limit": 10}
    ])
    leaderboard_data = await cursor.to_list(length=10)

    leaderboard_message = "<b>TOP 10 GROUPS WHO GUESSED MOST CHARACTERS</b>\n\n"

    for i, group in enumerate(leaderboard_data, start=1):
        group_name = html.escape(group.get('group_name', 'Unknown'))

        if len(group_name) > 10:
            group_name = group_name[:15] + '...'
        count = group['count']
        leaderboard_message += f'{i}. <b>{group_name}</b> ➾ <b>{count}</b>\n'

    photo_url = random.choice(PHOTO_URL)

    if query:
        await send_leaderboard(context, query.message.chat_id, leaderboard_message, photo_url, query.message.message_id)
    else:
        await send_leaderboard(context, update.effective_chat.id, leaderboard_message, photo_url)

async def ctop(update: Update, context: CallbackContext, query=None) -> None:
    chat_id = update.effective_chat.id if update else query.message.chat_id

    cursor = group_user_totals_collection.aggregate([
        {"$match": {"group_id": chat_id}},
        {"$project": {"username": 1, "first_name": 1, "character_count": "$count"}},
        {"$sort": {"character_count": -1}},
        {"$limit": 10}
    ])
    leaderboard_data = await cursor.to_list(length=10)

    leaderboard_message = "<b>TOP 10 USERS WHO GUESSED CHARACTERS MOST TIME IN THIS GROUP</b>\n\n"

    for i, user in enumerate(leaderboard_data, start=1):
        username = user.get('username', 'Unknown')
        first_name = html.escape(user.get('first_name', 'Unknown'))

        if len(first_name) > 10:
            first_name = first_name[:15] + '...'
        character_count = user['character_count']
        leaderboard_message += f'{i}. <a href="https://t.me/{username}"><b>{first_name}</b></a> ➾ <b>{character_count}</b>\n'

    photo_url = random.choice(PHOTO_URL)

    if query:
        await send_leaderboard(context, query.message.chat_id, leaderboard_message, photo_url, query.message.message_id)
    else:
        await send_leaderboard(context, update.effective_chat.id, leaderboard_message, photo_url)

async def leaderboard(update: Update, context: CallbackContext, query=None) -> None:
    cursor = user_collection.aggregate([
        {"$match": {"characters": {"$exists": True, "$type": "array"}}},
        {"$project": {"username": 1, "first_name": 1, "character_count": {"$size": "$characters"}}},
        {"$sort": {"character_count": -1}},
        {"$limit": 10}
    ])

    leaderboard_data = await cursor.to_list(length=10)

    leaderboard_message = "<b>TOP 10 USERS WITH MOST CHARACTERS</b>\n\n"

    for i, user in enumerate(leaderboard_data, start=1):
        username = user.get('username', 'Unknown')
        first_name = html.escape(user.get('first_name', 'Unknown'))

        if len(first_name) > 10:
            first_name = first_name[:15] + '...'
        character_count = user['character_count']
        leaderboard_message += f'{i}. <a href="https://t.me/{username}"><b>{first_name}</b></a> ➾ <b>{character_count}</b>\n'

    photo_url = random.choice(PHOTO_URL)

    if query:
        await send_leaderboard(context, query.message.chat_id, leaderboard_message, photo_url, query.message.message_id)
    else:
        await send_leaderboard(context, update.effective_chat.id, leaderboard_message, photo_url)

async def button_handler(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()

    if query.data == 'top_users':
        await leaderboard(update, context, query=query)
    elif query.data == 'topgc':
        await global_leaderboard(update, context, query=query)
    elif query.data == 'ctop':
        await ctop(update, context, query=query)
    elif query.data == 'close':
        await query.message.delete()

async def top_command(update: Update, context: CallbackContext) -> None:
    await leaderboard(update, context)

application.add_handler(CommandHandler('top', top_command, block=False))
application.add_handler(CallbackQueryHandler(button_handler))

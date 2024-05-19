import importlib
import time
import random
import re
import asyncio
from html import escape

from typing import Optional
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram import Update
from telegram.ext import Updater, CallbackQueryHandler
from telegram.ext import CommandHandler, MessageHandler, filters

from telegram.ext import CommandHandler, CallbackContext, MessageHandler, CallbackQueryHandler, filters

from shivu import collection, top_global_groups_collection, group_user_totals_collection, user_collection, user_totals_collection, shivuu 
from shivu import application, LOGGER
from shivu.modules import ALL_MODULES


# Define the send_leaderboard_message function
async def send_leaderboard_message(context: CallbackContext, chat_id: int, message: str, photo_url: str, message_id: int = None):
    keyboard = [
        [InlineKeyboardButton("Close", callback_data='lb_close')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    if message_id:
        await context.bot.edit_message_caption(
            chat_id=chat_id,
            message_id=message_id,
            caption=message,
            reply_markup=reply_markup
        )
    else:
        await context.bot.send_photo(chat_id=chat_id, photo=photo_url, caption=message, reply_markup=reply_markup)

# Define the mtop function
async def mtop(update: Update, context: CallbackContext):
    # Fetch top users sorted by 'vers' balance
    top_users = await user_collection.find({}, {'id': 1, 'first_name': 1, 'last_name': 1, 'vers': 1}).sort('vers', -1).limit(10).to_list(10)

    top_users_message = (
        "┌─────═━┈┈━═─────┐\n"
        "Top 10 Vers Users:\n"
        "───────────────────\n"
    )

    for i, user in enumerate(top_users, start=1):
        first_name = user.get('first_name', 'Unknown')
        last_name = user.get('last_name', '')
        user_id = user.get('id', 'Unknown')
        full_name = f"{first_name} {last_name}".strip()

        if user_id != 'Unknown':
            user_link = f'{full_name} (ID: {user_id})'
        else:
            user_link = full_name

        top_users_message += f"{i}. {user_link} - Ŧ{user.get('balance', 0):,}\n"

    top_users_message += (
        "───────────────────\n"
        "└─────═━┈┈━═─────┘"
    )

    photo_url = "https://telegra.ph/file/3474a548e37ab8f0604e8.jpg"
    photo_response = requests.get(photo_url)

    if photo_response.status_code == 200:
        photo_data = io.BytesIO(photo_response.content)
        await send_leaderboard_message(context, update.effective_chat.id, top_users_message, photo_url)
    else:
        await update.message.reply_text("Failed to download photo")

# Define the button handler function
async def button_handler(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()

    if query.data == 'lb_close':
        await query.message.delete()

# Add the command and callback handlers
application.add_handler(CommandHandler("tops", mtop))
application.add_handler(CallbackQueryHandler(button_handler))
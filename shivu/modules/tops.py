import importlib
import time
import random
import re
import asyncio
import io
import requests
from html import escape

from typing import Optional
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Updater, CallbackQueryHandler, CommandHandler, MessageHandler, filters, CallbackContext

from shivu import collection, top_global_groups_collection, group_user_totals_collection, user_collection, user_totals_collection, shivuu 
from shivu import application, LOGGER
from shivu.modules import ALL_MODULES

# Define the send_leaderboard_message function
async def send_leaderboard_message(context: CallbackContext, chat_id: int, message: str, photo_url: str, message_id: int = None):
    keyboard = [
        [InlineKeyboardButton("Close", callback_data='saleslist')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    if message_id:
        await context.bot.edit_message_caption(
            chat_id=chat_id,
            message_id=message_id,
            caption=message,
            reply_markup=reply_markup,
            parse_mode='HTML'
        )
    else:
        await context.bot.send_photo(
            chat_id=chat_id,
            photo=photo_url,
            caption=message,
            reply_markup=reply_markup,
            parse_mode='HTML'
        )

# Define the mtop function
async def mtop(update: Update, context: CallbackContext):
    top_users = await user_collection.find({}, {'id': 1, 'username': 1, 'first_name': 1, 'last_name': 1, 'balance': 1}).sort('balance', -1).limit(10).to_list(10)

    top_users_message = """
┌─────═━┈┈━═─────┐
Top 10 Token Users:
───────────────────
"""

    for i, user in enumerate(top_users, start=1):
        first_name = user.get('first_name', 'Unknown')
        last_name = user.get('last_name', '')
        username = user.get('username', None)
        user_id = user.get('id', 'Unknown')
        full_name = f"{first_name} {last_name}".strip()

        if username:
            user_link = f'<a href="https://t.me/{username}">{escape(full_name)}</a>'
        else:
            user_link = f'<a href="tg://user?id={user_id}">{escape(full_name)}</a>'

        top_users_message += f"{i}. {user_link} - Ŧ{user.get('balance', 0):,}\n"

    top_users_message += """
───────────────────
└─────═━┈┈━═─────┘
"""

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

    if query.data == 'tlb_close':
        await query.message.delete()

# Add the command and callback handlers
application.add_handler(CommandHandler("mtop", mtop))

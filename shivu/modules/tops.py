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
async def send_leaderboard_message(context: CallbackContext, chat_id: int, message: str, message_id: int = None):
    if message_id:
        await context.bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text=message,
            parse_mode='HTML'
        )
    else:
        await context.bot.send_message(
            chat_id=chat_id,
            text=message,
            parse_mode='HTML'
        )

# Define the mtop function
async def mtop(update: Update, context: CallbackContext):
    top_users = await user_collection.find({}, {'id': 1, 'username': 1, 'first_name': 1, 'last_name': 1, 'balance': 1}).sort('balance', -1).limit(10).to_list(10)

    top_users_message = """
┌─────═━🏎━═─────┐
𝚃𝚘𝚙 10 𝚞𝚜𝚎𝚛𝚜 𝚠𝚒𝚝𝚑 𝚑𝚒𝚐𝚑𝚎𝚜𝚝 𝚝𝚘𝚔𝚎𝚗𝚜:
───────────────────
"""

    for i, user in enumerate(top_users, start=1):
        first_name = user.get('first_name', '')
        last_name = user.get('last_name', '')
        username = user.get('username', None)
        balance = user.get('balance', 0)

        if username:
            user_link = f'<a href="https://t.me/{username}">{escape(first_name)} {escape(last_name)}</a>'
        else:
            user_link = f'{escape(first_name)} {escape(last_name)}'

        top_users_message += f"{i}. {user_link} - Ŧ{balance:,}\n"

    top_users_message += """
───────────────────
└─────═━🏎━═─────┘
"""

    await update.message.reply_text(top_users_message, parse_mode='HTML')

# Add the command handler
application.add_handler(CommandHandler("tops", mtop))

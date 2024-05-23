import importlib
import re

from telegram import Update
from telegram.ext import CommandHandler, CallbackContext

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

last_user = {}
warned_users = {}
started_users = set()  # Keep track of users who have started the bot in private


async def mtop(update: Update, context: CallbackContext):
    top_users = await user_collection.find({}, {'id': 1, 'username': 1, 'first_name': 1, 'last_name': 1, 'balance': 1}).sort('balance', -1).limit(10).to_list(10)
    
    # Log the retrieved documents for debugging
    LOGGER.info(f"Retrieved top users: {top_users}")

    top_users_message = """
┌─────═━🏎━═─────┐
𝚃𝚘𝚙 10 𝚞𝚜𝚎𝚛𝚜 𝚠𝚒𝚝𝚑 𝚑𝚒𝚐𝚑𝚎𝚜𝚝 𝚝𝚘𝚔𝚎𝚗𝚜:
───────────────────
"""

    for i, user in enumerate(top_users, start=1):
        first_name = user.get('first_name') or 'Unknown'
        last_name = user.get('last_name') or ''
        username = user.get('username')
        user_id = user.get('id') or 'Unknown'
        full_name = f"{first_name} {last_name}".strip()

        if username:
            user_link = f'<a href="https://t.me/{username}">{escape(full_name)}</a>'
        else:
            user_link = f'<a href="tg://user?id={user_id}">{escape(full_name)}</a>'

        top_users_message += f"{i}. {user_link} - Ŧ{user.get('balance', 0):,}\n"

    top_users_message += """
───────────────────
└─────═━🏎━═─────┘
"""

    photo_url = "https://telegra.ph/file/044cf17e444fcb931ec97.jpg"
    photo_response = requests.get(photo_url)

    if photo_response.status_code == 200:
        photo_data = io.BytesIO(photo_response.content)
        await send_leaderboard_message(context, update.effective_chat.id, top_users_message, photo_url)
    else:
        await update.message.reply_text("Failed to download photo")

application.add_handler(CommandHandler("tops", mtop))
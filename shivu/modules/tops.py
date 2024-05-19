import io
import requests
import random
import html

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CommandHandler, CallbackContext

from shivu import application, user_collection, PHOTO_URL

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
            parse_mode='HTML',
            reply_markup=reply_markup
        )
    else:
        await context.bot.send_photo(chat_id=chat_id, photo=photo_url, caption=message, parse_mode='HTML', reply_markup=reply_markup)

async def mtop(update: Update, context: CallbackContext):
    top_users = await user_collection.find({}, {'id': 1, 'first_name': 1, 'last_name': 1, 'balance': 1}).sort('balance', -1).limit(10).to_list(10)

    top_users_message = (
        "┌─────═━┈┈━═─────┐\n"
        "Top 10 Token Users:\n"
        "───────────────────\n"
    )

    for i, user in enumerate(top_users, start=1):
        first_name = html.escape(user.get('first_name', 'Unknown'))
        user_id = user.get('id', 'Unknown')

        if user_id != 'Unknown':
            user_link = f'<a href="tg://user?id={user_id}">{first_name}</a>'
        else:
            user_link = first_name

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

async def button_handler(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()

    if query.data == 'lb_close':
        await query.message.delete()

application.add_handler(CommandHandler("tops", mtop))
application.add_handler(CallbackQueryHandler(button_handler))
import os
import random
import html

from pyrogram import filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram import Update
from telegram.ext import CommandHandler, CallbackContext


from shivu import shivuu 
from shivu import (application, PHOTO_URL, OWNER_ID,
                    user_collection, top_global_groups_collection, top_global_groups_collection, 
                    group_user_totals_collection)

from Grabber import sudo_users as SUDO_USERS 
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CallbackQueryHandler
from telegram.ext import *

async def global_leaderboard(update: Update, context: CallbackContext) -> None:

    cursor = top_global_groups_collection.aggregate([
        {"$project": {"group_name": 1, "count": 1}},
        {"$sort": {"count": -1}},
        {"$limit": 10}
    ])
    leaderboard_data = await cursor.to_list(length=10)

    leaderboard_message = "<b> ◈ 🌍 gℓσвαℓ gяσυρ ℓєα∂єявσαя∂</b>\n\n┏━┅┅┄┄⟞⟦🌐⟧⟝┄┄┉┉━┓\n"

    for i, group in enumerate(leaderboard_data, start=1):
        group_name = html.escape(group.get('group_name', 'Unknown'))

        if len(group_name) > 10:
            group_name = group_name[:12] + '...'
        count = group['count']
        leaderboard_message += f'┣{i}. <b>{group_name}</b> ⇒ <code>{count}</code>\n'
        u177 = leaderboard_message + f'┗━┅┅┄┄⟞⟦🌐⟧⟝┄┄┉┉━┛'

    photo_url = random.choice(PHOTO_URL)

    # Setup inline buttons
    keyboard = [[InlineKeyboardButton("🗑️", callback_data='delete')]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Send message with inline buttons
    message = await update.message.reply_photo(photo=photo_url, caption=u177, parse_mode='HTML', reply_markup=reply_markup)

    # Store the message ID for later deletion
    context.user_data['message_to_delete'] = message.message_id

async def button(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    if query.data == 'delete':
        # Delete the message using the stored message ID
        message_to_delete = context.user_data.get('message_to_delete')
        if message_to_delete:
            try:
                await context.bot.delete_message(chat_id=query.message.chat_id, message_id=message_to_delete)
            except Exception as e:
                print(f"Error deleting message: {e}")
        else:
            print()

async def ctop(update: Update, context: CallbackContext) -> None:
    chat_id = update.effective_chat.id

    cursor = group_user_totals_collection.aggregate([
        {"$match": {"group_id": chat_id}},
        {"$project": {"username": 1, "first_name": 1, "character_count": "$count"}},
        {"$sort": {"character_count": -1}},
        {"$limit": 10}
    ])
    leaderboard_data = await cursor.to_list(length=10)

    leaderboard_message = "<b> ◈ 👑˼Chat Leaderboard </b>\n\n┏━┅┅┄┄⟞⟦👑⟧⟝┄┄┉┉━┓\n"

    for i, user in enumerate(leaderboard_data, start=1):
        username = user.get('username', 'Unknown')
        first_name = html.escape(user.get('first_name', 'Unknown'))

        if len(first_name) > 10:
            first_name = first_name[:12] + '...'
        character_count = user['character_count']
        leaderboard_message += f'┣ {i}. <a href="https://t.me/{username}"><b>{first_name}</b></a> ⇒ <code>{character_count}</code>\n'
        koka = leaderboard_message + f'┗━┅┅┄┄⟞⟦👑⟧⟝┄┄┉┉━┛'
    photo_url = random.choice(PHOTO_URL)

    # Setup inline buttons
    keyboard = [[InlineKeyboardButton("🚮", callback_data='delete')]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Send message with inline buttons
    message = await update.message.reply_photo(photo=photo_url, caption=koka , parse_mode='HTML', reply_markup=reply_markup)

    # Store the message ID for later deletion
    context.user_data['message_to_delete'] = message.message_id

async def button(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    if query.data == 'delete':
        # Delete the message using the stored message ID
        message_to_delete = context.user_data.get('message_to_delete')
        if message_to_delete:
            try:
                await context.bot.delete_message(chat_id=query.message.chat_id, message_id=message_to_delete)
            except Exception as e:
                print(f"Error deleting message: {e}")
        else:
            print()

async def leaderboard(update: Update, context: CallbackContext) -> None:

    cursor = user_collection.aggregate([
        {"$project": {"username": 1, "first_name": 1, "character_count": {"$size": "$characters"}}},
        {"$sort": {"character_count": -1}},
        {"$limit": 10}
    ])
    leaderboard_data = await cursor.to_list(length=10)

    leaderboard_message = "<b>◈ 🌍 gℓσвαℓ Rαηкєяѕ</b>\n\n┏━┅┅┄┄⟞⟦🌍⟧⟝┄┄┉┉━┓\n"

    for i, user in enumerate(leaderboard_data, start=1):
        username = user.get('username', 'Unknown')
        first_name = html.escape(user.get('first_name', 'Unknown'))

        if len(first_name) > 10:
            first_name = first_name[:12] + '...'
        character_count = user['character_count']
        leaderboard_message += f'┣ {i}. <a href="https://t.me/{username}"><b>{first_name}</b></a> ➾ <code>{character_count}</code>\n'
        u178 = leaderboard_message + f'┗━┅┅┄┄⟞⟦🌐⟧⟝┄┄┉┉━┛'
    photo_url = random.choice(PHOTO_URL)

    # Setup inline buttons
    keyboard = [[InlineKeyboardButton("🚮", callback_data='delete')]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Send message with inline buttons
    message = await update.message.reply_photo(photo=photo_url, caption=u178, parse_mode='HTML', reply_markup=reply_markup)

    # Store the message ID for later deletion
    context.user_data['message_to_delete'] = message.message_id

async def button(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    if query.data == 'delete':
        # Delete the message using the stored message ID
        message_to_delete = context.user_data.get('message_to_delete')
        if message_to_delete:
            try:
                await context.bot.delete_message(chat_id=query.message.chat_id, message_id=message_to_delete)
            except Exception as e:
                print(f"Error deleting message: {e}")
        else:
            print()


async def stats(update: Update, context: CallbackContext) -> None:

    if update.effective_user.id != OWNER_ID:
        await update.message.reply_text("You are not authorized to use this command.")
        return


    user_count = await user_collection.count_documents({})


    group_count = await group_user_totals_collection.distinct('group_id')


    await update.message.reply_text(f'Total Users: {user_count}\nTotal groups: {len(group_count)}')




async def send_users_document(update: Update, context: CallbackContext) -> None:
    if str(update.effective_user.id) not in SUDO_USERS:
        update.message.reply_text('only For Sudo users...')
        return
    cursor = user_collection.find({})
    users = []
    async for document in cursor:
        users.append(document)
    user_list = ""
    for user in users:
        user_list += f"{user['first_name']}\n"
    with open('users.txt', 'w') as f:
        f.write(user_list)
    with open('users.txt', 'rb') as f:
        await context.bot.send_document(chat_id=update.effective_chat.id, document=f)
    os.remove('users.txt')

async def send_groups_document(update: Update, context: CallbackContext) -> None:
    if str(update.effective_user.id) not in SUDO_USERS:
        update.message.reply_text('Only For Sudo users...')
        return
    cursor = top_global_groups_collection.find({})
    groups = []
    async for document in cursor:
        groups.append(document)
    group_list = ""
    for group in groups:
        group_list += f"{group['group_name']}\n"
        group_list += "\n"
    with open('groups.txt', 'w') as f:
        f.write(group_list)
    with open('groups.txt', 'rb') as f:
        await context.bot.send_document(chat_id=update.effective_chat.id, document=f)
    os.remove('groups.txt')

application.add_handler(CommandHandler('ctop', ctop, block=False))
application.add_handler(CommandHandler('stats', stats, block=False))
application.add_handler(CommandHandler('TopGroups', global_leaderboard, block=False))

application.add_handler(CommandHandler('list', send_users_document, block=False))
application.add_handler(CommandHandler('groups', send_groups_document, block=False))


application.add_handler(CommandHandler('top', leaderboard, block=False))
application.add_handler(CallbackQueryHandler(button))
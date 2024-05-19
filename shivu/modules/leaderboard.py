import os
import random
import html

from telegram import Update
from telegram.ext import CommandHandler, CallbackContext

from shivu import (
    application, PHOTO_URL, OWNER_ID,
    user_collection, top_global_groups_collection, group_user_totals_collection,
    sudo_users as SUDO_USERS
)

photo = random.choice(PHOTO_URL)

async def broadcast(update: Update, context: CallbackContext) -> None:
    if str(update.effective_user.id) == OWNER_ID:
        if update.message.reply_to_message is None:
            await update.message.reply_text('Please reply to a message to broadcast.')
            return

        all_users = await user_collection.find({}).to_list(length=None)
        all_groups = await group_user_totals_collection.find({}).to_list(length=None)

        unique_user_ids = set(user['id'] for user in all_users if 'id' in user)
        unique_group_ids = set(group['group_id'] for group in all_groups)

        total_sent = 0
        total_failed = 0

        for user_id in unique_user_ids:
            try:
                await context.bot.forward_message(chat_id=user_id, from_chat_id=update.effective_chat.id, message_id=update.message.reply_to_message.message_id)
                total_sent += 1
            except Exception:
                total_failed += 1

        for group_id in unique_group_ids:
            try:
                await context.bot.forward_message(chat_id=group_id, from_chat_id=update.effective_chat.id, message_id=update.message.reply_to_message.message_id)
                total_sent += 1
            except Exception:
                total_failed += 1

        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f'Broadcast report:\n\nTotal messages sent successfully: {total_sent}\nTotal messages failed to send: {total_failed}'
        )
    else:
        await update.message.reply_text('Only Murat Can use')

async def stats(update: Update, context: CallbackContext) -> None:
    if str(update.effective_user.id) not in OWNER_ID:
        update.message.reply_text('only For Sudo users...')
        return

    user_count = await user_collection.count_documents({}) + 500
    group_count = len(await group_user_totals_collection.distinct('group_id')) + 350

    await update.message.reply_text(f'Total Users: {user_count}\nTotal groups: {group_count}')

async def send_users_document(update: Update, context: CallbackContext) -> None:
    if str(update.effective_user.id) not in SUDO_USERS:
        update.message.reply_text('only For Sudo users...')
        return

    cursor = user_collection.find({})
    users = [document async for document in cursor]
    user_list = '\n'.join(user.get('first_name', 'Unknown') for user in users)

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
    groups = [document async for document in cursor]
    group_list = '\n'.join(group['group_name'] for group in groups)

    with open('groups.txt', 'w') as f:
        f.write(group_list)

    with open('groups.txt', 'rb') as f:
        await context.bot.send_document(chat_id=update.effective_chat.id, document=f)

    os.remove('groups.txt')


application.add_handler(CommandHandler('stats', stats, block=False))
application.add_handler(CommandHandler('broadcast', broadcast, block=False))
application.add_handler(CommandHandler('list', send_users_document, block=False))
application.add_handler(CommandHandler('groups', send_groups_document, block=False))
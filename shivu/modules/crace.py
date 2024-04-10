from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CommandHandler, CallbackContext, CallbackQueryHandler
from shivu import application, user_collection
import random

async def get_user_balance(user_id):
    user_balance = await user_collection.find_one({'id': user_id}, projection={'balance': 1})
    return user_balance.get('balance', 0) if user_balance else 0

async def update_user_balance(user_id, amount):
    await user_collection.update_one({'id': user_id}, {'$inc': {'balance': amount}})

async def crace(update: Update, context: CallbackContext):
    replied_user = update.message.reply_to_message.from_user if update.message.reply_to_message else None

    if not replied_user:
        update.message.reply_text("Please reply to a user you want to challenge for a race.")
        return

    replied_user_id = replied_user.id

    race_amount = random.randint(10000, 100000)

    replied_user_balance = await get_user_balance(replied_user_id)

    if replied_user_balance < race_amount:
        update.message.reply_text(f"The replied user must have a minimum balance of {race_amount} coins to participate.")
        return

    keyboard = [[InlineKeyboardButton("Yes", callback_data=f'crace_yes|{race_amount}|{replied_user_id}')]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    update.message.reply_text(f"Do you want to race for {race_amount} coins?", reply_markup=reply_markup)

async def crace_callback(update: Update, context: CallbackContext):
    query = update.callback_query
    user_id = query.from_user.id

    data = query.data.split('|')
    if data[0] == 'crace_yes':
        race_amount = int(data[1])
        replied_user_id = int(data[2])

        user_balance = await get_user_balance(user_id)
        replied_user_balance = await get_user_balance(replied_user_id)

        if user_balance >= race_amount and replied_user_balance >= race_amount:
            await update_user_balance(user_id, -race_amount)
            await update_user_balance(replied_user_id, -race_amount)

            winner = random.choice([user_id, replied_user_id])
            await update_user_balance(winner, 2 * race_amount)

            query.answer()
            query.message.reply_text(f"User {winner} wins the race! Congratulations. {2 * race_amount} coins transferred to the winner.")
        else:
            query.answer()
            query.message.reply_text("Not enough balance to proceed with the race.")
    else:
        query.answer()
        query.message.reply_text("Race cancelled.")

application.add_handler(CommandHandler("crace", crace))
application.add_handler(CallbackQueryHandler(crace_callback))

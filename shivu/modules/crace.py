from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CommandHandler, CallbackContext, CallbackQueryHandler
from shivu import application, user_collection
import random

# Helper function to get user balance
async def get_user_balance(user_id):
    user_balance = await user_collection.find_one({'id': user_id}, projection={'balance': 1})
    return user_balance.get('balance', 0) if user_balance else 0

# Helper function to update user balance
async def update_user_balance(user_id, amount):
    await user_collection.update_one({'id': user_id}, {'$inc': {'balance': amount}})

def crace(update: Update, context: CallbackContext):
    replied_user = update.message.reply_to_message.from_user
    replied_user_id = replied_user.id

    # Check if the replied user exists and has a balance of at least 10000 coins
    replied_user_balance = await get_user_balance(replied_user_id)
    if replied_user_balance >= 10000:
        keyboard = [[InlineKeyboardButton("Yes", callback_data='crace_yes')],
                    [InlineKeyboardButton("No", callback_data='crace_no')]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        update.message.reply_text("Do you want to race?", reply_markup=reply_markup)
    else:
        update.message.reply_text("Replied user must have a minimum balance of 10,000 coins to participate in the race.")

def crace_callback(update: Update, context: CallbackContext):
    query = update.callback_query
    user_id = query.from_user.id

    if query.data == 'crace_yes':
        replied_user_id = query.message.reply_to_message.from_user.id
        race_amount = random.randint(10000, 100000)

        user_balance = await get_user_balance(user_id)
        replied_user_balance = await get_user_balance(replied_user_id)

        if user_balance >= race_amount and replied_user_balance >= race_amount:
            # Deduct the race amount from both participants
            await update_user_balance(user_id, -race_amount)
            await update_user_balance(replied_user_id, -race_amount)

            winner = random.choice([user_id, replied_user_id])

            # Transfer all coins to the winner
            await update_user_balance(winner, 2 * race_amount)

            query.answer()
            query.message.reply_text(f"User {winner} wins the race! Congratulations!")
        else:
            query.answer()
            query.message.reply_text("Not enough balance to proceed with the race.")
    else:
        query.answer()
        query.message.reply_text("Race cancelled.")

# Add the /crace command and its callback handler
application.add_handler(CommandHandler("crace", crace))
application.add_handler(CallbackQueryHandler(crace_callback))
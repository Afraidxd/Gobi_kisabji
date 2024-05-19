from telegram.ext import CommandHandler, CallbackQueryHandler
from shivu import application, user_collection
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
import random

# Command handler for starting the RPS game
async def rps(update, context):
    try:
        amount = int(context.args[0])
        if amount < 1:
            raise ValueError("Invalid bet amount.")
    except (IndexError, ValueError):
        await update.message.reply_text("Use /rps [amount] with a positive integer.")
        return

    user_id = update.effective_user.id
    user_balance = await user_collection.find_one({'id': user_id}, projection={'balance': 1})

    if not user_balance or user_balance.get('balance', 0) < amount:
        await update.message.reply_text("Insufficient balance to make the bet.")
        return

    keyboard = [
        [InlineKeyboardButton("ʀᴏᴄᴋ 🪨", callback_data='rock'),
         InlineKeyboardButton("ᴘᴀᴘᴇʀ 📄", callback_data='paper')],
        [InlineKeyboardButton("sᴄɪssᴏʀs ✂️", callback_data='scissors')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    message = await update.message.reply_text("Choose your move:", reply_markup=reply_markup)

    context.user_data['amount'] = amount
    context.user_data['message_id'] = message.message_id

# Callback query handler for processing the RPS game result
async def rps_button(update, context):
    query = update.callback_query
    choice = query.data

    if choice == 'play_again':
        await play_again(query, context)
        return

    amount = context.user_data.get('amount')
    if amount is None:
        await query.answer("No bet amount found.")
        return

    user_id = update.effective_user.id
    user_balance = await user_collection.find_one({'id': user_id}, projection={'balance': 1})

    if not user_balance or user_balance.get('balance', 0) < amount:
        await query.answer("Insufficient balance to make the bet.")
        return

    computer_choice = random.choice(['rock', 'paper', 'scissors'])

    result_message, balance_change = determine_winner(choice, computer_choice, amount)

    await user_collection.update_one({'id': user_id}, {'$inc': {'balance': balance_change}})

    updated_balance = await user_collection.find_one({'id': user_id}, projection={'balance': 1})

    await query.message.edit_text(
        f"You chose {choice.capitalize()} and the computer chose {computer_choice.capitalize()}\n\n"
        f"{result_message} Your updated balance is {updated_balance['balance']}\n\nPlay again?",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("ᴘʟᴀʏ ᴀɢᴀɪɴ🔄", callback_data='play_again')]])
    )

# Function to determine the winner of the RPS game
def determine_winner(user_choice, computer_choice, bet_amount):
    if user_choice == computer_choice:
        return "It's a tie!", 0
    elif (user_choice == 'rock' and computer_choice == 'scissors') or \
         (user_choice == 'paper' and computer_choice == 'rock') or \
         (user_choice == 'scissors' and computer_choice == 'paper'):
        return "🎉 ʏᴏᴜ ᴡᴏɴ!", bet_amount
    else:
        return "😔You lost!", -bet_amount

# Function to handle the 'play again' action
async def play_again(query, context):
    keyboard = [
        [InlineKeyboardButton("ʀᴏᴄᴋ 🪨", callback_data='rock'),
         InlineKeyboardButton("ᴘᴀᴘᴇʀ 📄", callback_data='paper')],
        [InlineKeyboardButton("sᴄɪssᴏʀs ✂️", callback_data='scissors')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.message.edit_text("Choose your move:", reply_markup=reply_markup)

# Adding the handlers to the application
application.add_handler(CommandHandler("rps", rps))
application.add_handler(CallbackQueryHandler(rps_button))

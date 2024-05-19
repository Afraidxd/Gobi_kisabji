import random
import html

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CommandHandler, CallbackQueryHandler, CallbackContext

from shivu import application, user_collection

async def rps(update: Update, context: CallbackContext):
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
        [InlineKeyboardButton("ʀᴏᴄᴋ 🪨", callback_data='rps_rock'),
         InlineKeyboardButton("ᴘᴀᴘᴇʀ 📄", callback_data='rps_paper')],
        [InlineKeyboardButton("sᴄɪssᴏʀs ✂️", callback_data='rps_scissors')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    message = await update.message.reply_text("Choose your move:", reply_markup=reply_markup)

    context.user_data['amount'] = amount
    context.user_data['message_id'] = message.message_id

async def rps_button(update: Update, context: CallbackContext):
    query = update.callback_query
    choice = query.data

    if not choice.startswith("rps_"):  # Check if the callback data starts with "rps_"
        return

    choice = choice.replace("rps_", "")  # Remove the "rps_" prefix from the choice

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
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("ᴘʟᴀʏ ᴀɢᴀɪɴ🔄", callback_data='rps_play_again')]])
    )

def determine_winner(user_choice, computer_choice, bet_amount):
    if user_choice == computer_choice:
        return "It's a tie!", 0
    elif (user_choice == 'rock' and computer_choice == 'scissors') or \
         (user_choice == 'paper' and computer_choice == 'rock') or \
         (user_choice == 'scissors' and computer_choice == 'paper'):
        return "🎉 ʏᴏᴜ ᴡᴏɴ!", bet_amount
    else:
        return "😔 You lost!", -bet_amount

async def play_again(query, context):
    keyboard = [
        [InlineKeyboardButton("ʀᴏᴄᴋ 🪨", callback_data='rps_rock'),
         InlineKeyboardButton("ᴘᴀᴘᴇʀ 📄", callback_data='rps_paper')],
        [InlineKeyboardButton("sᴄɪssᴏʀs ✂️", callback_data='rps_scissors')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.message.edit_text("Choose your move:", reply_markup=reply_markup)

application.add_handler(CommandHandler("rps", rps))
application.add_handler(CallbackQueryHandler(rps_button))

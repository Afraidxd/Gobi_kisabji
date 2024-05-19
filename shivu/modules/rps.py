from telegram.ext import CommandHandler, CallbackQueryHandler
from shivu import application, user_collection
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
import random

async def rps(update, context):
    try:
        amount = int(context.args[0])
        if amount < 1:
            raise ValueError("Invalid bet amount.")
    except (IndexError, ValueError):
        await update.message.reply_text("Use /rps [amount]")
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

async def rps_button(update, context):
    query = update.callback_query
    choice = query.data

    if choice == 'play_again':
        await play_again(update, context)
        return

    amount = context.user_data.get('amount')
    user_id = update.effective_user.id
    user_balance = await user_collection.find_one({'id': user_id}, projection={'balance': 1})

    if not user_balance or user_balance.get('balance', 0) < amount:
        await query.answer("Insufficient balance to make the bet.")
        return

    computer_choice = random.choice(['rock', 'paper', 'scissors'])

    if choice == computer_choice:
        result_message = "It's a tie!"
    elif (choice == 'rock' and computer_choice == 'scissors') or \
         (choice == 'paper' and computer_choice == 'rock') or \
         (choice == 'scissors' and computer_choice == 'paper'):
        result_message = "🎉 ʏᴏᴜ ᴡᴏɴ!"
        await user_collection.update_one({'id': user_id}, {'$inc': {'balance': amount}})
    else:
        result_message = "😔You lost!"
        await user_collection.update_one({'id': user_id}, {'$inc': {'balance': -amount}})


    updated_balance = await user_collection.find_one({'id': user_id}, projection={'balance': 1})

    await query.message.edit_text(
        f"You chose {choice.capitalize()} and the computer chose {computer_choice.capitalize()}\n\n.\n{result_message} Your updated balance is {updated_balance['balance']}\n\nPlay again?",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("ᴘʟᴀʏ ᴀɢᴀɪɴ🔄", callback_data='play_again')]])
    )

async def play_again(update, context):
    query = update.callback_query

    keyboard = [
        [InlineKeyboardButton("ʀᴏᴄᴋ 🪨", callback_data='rock'),
         InlineKeyboardButton("ᴘᴀᴘᴇʀ 📄", callback_data='paper')],
        [InlineKeyboardButton("sᴄɪssᴏʀs ✂️", callback_data='scissors')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.message.edit_text("Choose your move:", reply_markup=reply_markup)

application.add_handler(CommandHandler("rps", rps))
from shivu import user_collection, application

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext, CommandHandler, CallbackQueryHandler
import random
from datetime import datetime
import asyncio

# Dictionary to store last propose times and challenges
challenges = {}

async def start_race_challenge(update: Update, context: CallbackContext):
    # Check if the message is a reply
    if not update.message.reply_to_message:
        await update.message.reply_text("Please reply to a user's message to challenge them to a race.")
        return

    challenged_user_id = update.message.reply_to_message.from_user.id
    challenger_id = update.effective_user.id

    # Check if the user is trying to challenge themselves
    if challenged_user_id == challenger_id:
        await update.message.reply_text("You cannot challenge yourself!")
        return

    challenger_name = update.effective_user.first_name
    amount = 10  # Default amount, you can change it as per your preference

    # Check balance of both users
    challenger_balance = await user_collection.find_one({'id': challenger_id}, projection={'balance': 1})
    challenged_balance = await user_collection.find_one({'id': challenged_user_id}, projection={'balance': 1})

    if not challenger_balance or challenger_balance.get('balance', 0) < amount:
        await update.message.reply_text("You do not have enough tokens to challenge.")
        return

    if not challenged_balance or challenged_balance.get('balance', 0) < amount:
        await update.message.reply_text("The challenged user does not have enough tokens.")
        return

    # Store the challenge
    challenges[challenged_user_id] = {
        'challenger': challenger_id,
        'challenger_name': challenger_name,
        'amount': amount,
        'timestamp': datetime.now()
    }

    # Notify the challenged user
    keyboard = [
        [
            InlineKeyboardButton("Accept", callback_data=f"race_accept_{challenger_id}_{challenged_user_id}"),
            InlineKeyboardButton("Decline", callback_data=f"race_decline_{challenger_id}_{challenged_user_id}")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_to_message.reply_text(
        f"You have been challenged by {challenger_name} to a race for Ŧ{amount} tokens! Do you accept?",
        reply_markup=reply_markup
    )

async def race_accept(update: Update, context: CallbackContext):
    query = update.callback_query
    challenged_user_id = update.effective_user.id

    callback_data = query.data.split('_')
    challenger_id = int(callback_data[2])

    if challenged_user_id not in challenges:
        await query.answer("Challenge not found!", show_alert=True)
        return

    if challenges[challenged_user_id]['challenger'] != challenger_id:
        await query.answer("This challenge is not for you!", show_alert=True)
        return

    challenge_data = challenges[challenged_user_id]
    await start_race(query, context, challenger_id, challenged_user_id, challenge_data['amount'], challenge_data['challenger_name'])

async def start_race(query, context: CallbackContext, challenger_id: int, challenged_user_id: int, amount: int, challenger_name: str):
    # Deduct tokens from both users
    await user_collection.update_one({'id': challenger_id}, {'$inc': {'balance': -amount}})
    await user_collection.update_one({'id': challenged_user_id}, {'$inc': {'balance': -amount}})

    # Race simulation
    await asyncio.sleep(2)  # 2-second delay
    await context.bot.send_message(chat_id=challenged_user_id, text="🏁 The race has started! 🏁")
    await asyncio.sleep(2)  # 2-second delay

    # Determine the winner
    if random.random() < 0.5:
        winner_id = challenger_id
        loser_id = challenged_user_id
        winner_name = challenger_name
    else:
        winner_id = challenged_user_id
        loser_id = challenger_id
        winner_name = (await user_collection.find_one({'id': challenged_user_id})).get('first_name', 'User')

    reward = 2 * amount
    await user_collection.update_one({'id': winner_id}, {'$inc': {'balance': reward}})

    winner_message = f"🎉 Congratulations, {winner_name}! 🎉\nYou won the race and earned Ŧ{reward} tokens."
    loser_message = "Better luck next time, you lost the race."

    await context.bot.send_message(chat_id=winner_id, text=winner_message)
    await context.bot.send_message(chat_id=loser_id, text=loser_message)

    # Clean up the challenge
    del challenges[challenged_user_id]

async def race_decline(update: Update, context: CallbackContext):
    query = update.callback_query
    challenged_user_id = query.from_user.id

    callback_data = query.data.split('_')
    challenger_id = int(callback_data[2])

    if challenged_user_id in challenges and challenges[challenged_user_id]['challenger'] == challenger_id:
        await query.edit_message_text("Challenge declined.")
        del challenges[challenged_user_id]
    else:
        await query.edit_message_text("Challenge not found or already expired.")

application.add_handler(CommandHandler("race", start_race_challenge))
application.add_handler(CallbackQueryHandler(race_accept, pattern=r'^race_accept_'))
application.add_handler(CallbackQueryHandler(race_decline, pattern=r'^race_decline_'))

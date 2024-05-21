from shivu import user_collection, application 
from telegram import Update, InlineKeyboardButton as IKB, InlineKeyboardMarkup as IKM, MessageEntity
from telegram.ext import CallbackContext, CommandHandler, CallbackQueryHandler
import random
from datetime import datetime, timedelta
import asyncio

# Dictionary to store last propose times and challenges
challenges = {}
race_cooldowns = {}

async def start_race_challenge(update: Update, context: CallbackContext):
    # Check if the message is a reply and contains a mention
    if not update.message.reply_to_message or not update.message.entities:
        await update.message.reply_text("Please mention another user to challenge them to a race.")
        return

    mentioned_user_id = None
    for entity in update.message.entities:
        if entity.type == MessageEntity.MENTION:
            username = update.message.text[entity.offset + 1:entity.offset + entity.length]
            user = await context.bot.get_chat(username)
            mentioned_user_id = user.id if user else None
            break
        elif entity.type == MessageEntity.TEXT_MENTION:
            mentioned_user_id = entity.user.id
            break

    if not mentioned_user_id:
        await update.message.reply_text("Please mention another user to challenge them to a race.")
        return

    challenger_id = update.effective_user.id
    challenged_id = mentioned_user_id
    challenger_name = update.effective_user.first_name
    amount = 10  # Default amount, you can change it as per your preference

    # Check if the user is trying to race themselves
    if challenger_id == challenged_id:
        await update.message.reply_text("You cannot challenge yourself to a race!")
        return

    # Check balances
    challenger_balance = await user_collection.find_one({'id': challenger_id}, projection={'balance': 1})
    challenged_balance = await user_collection.find_one({'id': challenged_id}, projection={'balance': 1})

    if not challenger_balance or challenger_balance.get('balance', 0) < amount:
        await update.message.reply_text("You do not have enough tokens to challenge.")
        return

    if not challenged_balance or challenged_balance.get('balance', 0) < amount:
        await update.message.reply_text("The challenged user does not have enough tokens.")
        return

    now = datetime.now()
    if challenger_id in race_cooldowns and (now - race_cooldowns[challenger_id]) < timedelta(minutes=1):
        await update.message.reply_text("Please wait 1 minute before using /race again.")
        return
    if challenged_id in race_cooldowns and (now - race_cooldowns[challenged_id]) < timedelta(minutes=1):
        await update.message.reply_text("The opponent needs to wait 1 minute before racing again.")
        return

    # Store the challenge
    challenges[challenged_id] = {
        'challenger': challenger_id,
        'challenger_name': challenger_name,
        'amount': amount,
        'timestamp': datetime.now()
    }

    # Notify the challenged user
    keyboard = [
        [
            IKB("Accept", callback_data=f"race_accept_{challenger_id}"),
            IKB("Decline", callback_data=f"race_decline_{challenger_id}")
        ]
    ]
    reply_markup = IKM(keyboard)
    await update.message.reply_text(
        f"You have been challenged by {challenger_name} to a race for Ŧ{amount} tokens! Do you accept?",
        reply_markup=reply_markup
    )

async def race_accept(update: Update, context: CallbackContext):
    query = update.callback_query
    challenged_id = update.effective_user.id

    if challenged_id not in challenges:
        await query.answer("Challenge not found!", show_alert=True)
        return

    challenge_data = challenges[challenged_id]
    challenger_id = challenge_data['challenger']

    # Start the race
    await start_race(query, challenger_id, challenged_id, challenge_data['amount'], challenge_data['challenger_name'])

async def start_race(query, challenger_id: int, challenged_id: int, amount: int, challenger_name: str):
    # Deduct tokens from both users
    await user_collection.update_one({'id': challenger_id}, {'$inc': {'balance': -amount}})
    await user_collection.update_one({'id': challenged_id}, {'$inc': {'balance': -amount}})

    # Race simulation
    await query.edit_message_text(text="🏁 The race has started! 🏁")
    await asyncio.sleep(2)  # 2-second delay

    # Determine the winner
    if random.random() < 0.5:
        winner_id = challenger_id
        loser_id = challenged_id
        winner_name = challenger_name
    else:
        winner_id = challenged_id
        loser_id = challenger_id
        winner_name = (await user_collection.find_one({'id': challenged_id})).get('first_name', 'User')

    reward = 2 * amount
    await user_collection.update_one({'id': winner_id}, {'$inc': {'balance': reward}})

    winner_message = f"🎉 Congratulations, {winner_name}! 🎉\nYou won the race and earned Ŧ{reward} tokens."
    loser_message = "Better luck next time, you lost the race."

    await query.bot.send_message(chat_id=winner_id, text=winner_message)
    await query.bot.send_message(chat_id=loser_id, text=loser_message)

    # Clean up the challenge and set cooldowns
    del challenges[challenged_id]
    now = datetime.now()
    race_cooldowns[challenger_id] = now
    race_cooldowns[challenged_id] = now

async def race_decline(update: Update, context: CallbackContext):
    query = update.callback_query
    challenged_id = query.from_user.id

    if challenged_id in challenges:
        await query.edit_message_text("Challenge declined.")
        del challenges[challenged_id]
    else:
        await query.edit_message_text("Challenge not found or already expired.")

# Add the command handler and callback query handlers to the application
application.add_handler(CommandHandler("race", start_race_challenge))
application.add_handler(CallbackQueryHandler(race_accept, pattern=r'^race_accept_\d+$'))
application.add_handler(CallbackQueryHandler(race_decline, pattern=r'^race_decline_\d+$'))
from shivu import user_collection, application
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext, CommandHandler, CallbackQueryHandler
import random
from datetime import datetime, timedelta
import asyncio
from telegram.error import Forbidden

# Dictionary to store challenges and cooldown times
challenges = {}
last_match_time = {}

async def start_match_challenge(update: Update, context: CallbackContext):
    if update.message.chat.type not in ['group', 'supergroup']:
        await update.message.reply_text("This command can only be used in a group chat.")
        return

    # Check if the message is a reply
    if not update.message.reply_to_message:
        await update.message.reply_text("Please reply to a user's message to challenge them to a match.")
        return

    args = context.args
    if not args or not args[0].isdigit() or int(args[0]) <= 0:
        await update.message.reply_text("Usage: /match [amount]")
        return

    amount = int(args[0])
    challenged_user_id = update.message.reply_to_message.from_user.id
    challenger_id = update.effective_user.id

    # Check if the user is trying to challenge themselves
    if challenged_user_id == challenger_id:
        await update.message.reply_text("You cannot challenge yourself!")
        return

    # Check cooldown period
    current_time = datetime.now()
    cooldown_period = timedelta(minutes=5)
    if (challenger_id in last_match_time and current_time < last_match_time[challenger_id] + cooldown_period) or \
       (challenged_user_id in last_match_time and current_time < last_match_time[challenged_user_id] + cooldown_period):
        remaining_time_challenger = (last_match_time.get(challenger_id, current_time) + cooldown_period - current_time).seconds // 60
        remaining_time_challenged = (last_match_time.get(challenged_user_id, current_time) + cooldown_period - current_time).seconds // 60
        await update.message.reply_text(
            f"One of the users is in cooldown period. Please wait {max(remaining_time_challenger, remaining_time_challenged)} minutes before challenging again."
        )
        return

    challenger_name = update.effective_user.first_name
    challenged_name = update.message.reply_to_message.from_user.first_name

    # Check balance of both users
    challenger_balance = await user_collection.find_one({'id': challenger_id}, projection={'balance': 1})
    challenged_balance = await user_collection.find_one({'id': challenged_user_id}, projection={'balance': 1})

    if not challenger_balance or challenger_balance.get('balance', 0) < amount:
        await update.message.reply_text("You do not have enough tokens to challenge.")
        return

    if not challenged_balance or challenged_balance.get('balance', 0) < amount:
        await update.message.reply_text("The challenged user does not have enough tokens to accept the challenge.")
        return

    # Store the challenge
    challenges[challenged_user_id] = {
        'challenger': challenger_id,
        'challenger_name': challenger_name,
        'challenged_name': challenged_name,
        'amount': amount,
        'timestamp': datetime.now(),
        'chat_id': update.message.chat_id,
        'message_id': update.message.message_id,
        'challenger_lives': 3,
        'challenged_lives': 3,
        'turn': challenger_id,
        'bullets': ['live', 'live', 'live', 'blank', 'blank'],
    }

    # Notify the challenged user
    keyboard = [
        [
            InlineKeyboardButton("Accept", callback_data=f"match_accept_{challenger_id}_{challenged_user_id}"),
            InlineKeyboardButton("Decline", callback_data=f"match_decline_{challenger_id}_{challenged_user_id}")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_to_message.reply_text(
        f"You have been challenged by {challenger_name} to a match for {amount} tokens! Do you accept?",
        reply_markup=reply_markup
    )

async def match_accept(update: Update, context: CallbackContext):
    query = update.callback_query
    challenged_user_id = update.effective_user.id

    callback_data = query.data.split('_')
    challenger_id = int(callback_data[2])

    if challenged_user_id not in challenges:
        await query.answer("You cannot accept this challenge as it no longer exists.", show_alert=True)
        return

    if challenges[challenged_user_id]['challenger'] != challenger_id:
        await query.answer("This challenge is not for you.", show_alert=True)
        return

    challenge_data = challenges[challenged_user_id]
    await start_match(query, context, challenger_id, challenged_user_id, challenge_data['amount'], challenge_data['challenger_name'], challenge_data['challenged_name'], challenge_data['chat_id'], challenge_data['message_id'])

async def start_match(query, context: CallbackContext, challenger_id: int, challenged_user_id: int, amount: int, challenger_name: str, challenged_name: str, chat_id: int, message_id: int):
    try:
        # Edit the original challenge message
        await query.edit_message_text(text="The match has begun!")
    except Forbidden as e:
        await context.bot.send_message(chat_id=chat_id, text="Unable to start the match due to a messaging error. Ensure both users have interacted with the bot.")
        return

    # Deduct tokens from both users
    await user_collection.update_one({'id': challenger_id}, {'$inc': {'balance': -amount}})
    await user_collection.update_one({'id': challenged_user_id}, {'$inc': {'balance': -amount}})

    challenge_data = challenges[challenged_user_id]
    await prompt_shoot(context, challenge_data['turn'], chat_id, challenger_name, challenged_name, challenger_id, challenged_user_id)

async def prompt_shoot(context: CallbackContext, turn_user_id: int, chat_id: int, challenger_name: str, challenged_name: str, challenger_id: int, challenged_user_id: int):
    turn_user_name = challenger_name if turn_user_id == challenger_id else challenged_name

    keyboard = [
        [
            InlineKeyboardButton("Shoot Myself", callback_data=f"shoot_self_{turn_user_id}_{challenger_id}_{challenged_user_id}"),
            InlineKeyboardButton("Shoot Opponent", callback_data=f"shoot_opponent_{turn_user_id}_{challenger_id}_{challenged_user_id}")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await context.bot.send_message(chat_id, text=f"{turn_user_name}, it's your turn! Choose your action:", reply_markup=reply_markup)

async def handle_shoot(update: Update, context: CallbackContext):
    query = update.callback_query
    callback_data = query.data.split('_')

    action = callback_data[0]
    shooter_id = int(callback_data[1])
    challenger_id = int(callback_data[2])
    challenged_user_id = int(callback_data[3])
    
    if challenged_user_id not in challenges:
        await query.answer("This match no longer exists.", show_alert=True)
        return

    challenge_data = challenges[challenged_user_id]

    if challenge_data['turn'] != shooter_id:
        await query.answer("It's not your turn.", show_alert=True)
        return

    bullets = challenge_data['bullets']
    random.shuffle(bullets)
    bullet = bullets.pop()
    
    if action == "shoot_self":
        if bullet == "live":
            if shooter_id == challenge_data['challenger']:
                challenge_data['challenger_lives'] -= 1
            else:
                challenge_data['challenged_lives'] -= 1
            challenge_data['turn'] = challenger_id if shooter_id == challenged_user_id else challenged_user_id
        # If blank, shooter gets another turn
    elif action == "shoot_opponent":
        if bullet == "live":
            if shooter_id == challenge_data['challenger']:
                challenge_data['challenged_lives'] -= 1
            else:
                challenge_data['challenger_lives'] -= 1
            # Shooter gets another turn if hitting opponent with live bullet
        else:
            challenge_data['turn'] = challenger_id if shooter_id == challenged_user_id else challenged_user_id

    # Check if game is over
    if challenge_data['challenger_lives'] <= 0 or challenge_data['challenged_lives'] <= 0:
        winner_id = challenger_id if challenge_data['challenged_lives'] <= 0 else challenged_user_id
        loser_id = challenged_user_id if winner_id == challenger_id else challenger_id
        await context.bot.send_message(challenge_data['chat_id'], text=f"{challenge_data['challenger_name']} and {challenge_data['challenged_name']} have finished their match. The winner is {challenge_data['challenger_name'] if winner_id == challenger_id else challenge_data['challenged_name']}!")
        await user_collection.update_one({'id': winner_id}, {'$inc': {'balance': amount * 2}})
        del challenges[challenged_user_id]
    else:
        challenge_data['bullets'] = bullets  # Update bullets after round
        await prompt_shoot(context, challenge_data['turn'], challenge_data['chat_id'], challenge_data['challenger_name'], challenge_data['challenged_name'], challenger_id, challenged_user_id)

# Add command handlers to the application
application.add_handler(CommandHandler('match', start_match_challenge))
application.add_handler(CallbackQueryHandler(match_accept, pattern=r'^match_accept_'))
application.add_handler(CallbackQueryHandler(handle_sh

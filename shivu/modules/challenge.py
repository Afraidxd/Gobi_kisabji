import asyncio
from telegram.ext import CommandHandler
from telegram import Update
import random
from datetime import datetime, timedelta
from shivu import collection, user_collection, user_totals_collection , application 

last_propose_times = {}
proposing_users = {}

async def propose(update, context):
    user_id = update.effective_user.id

    user_balance = await user_collection.find_one({'id': user_id}, projection={'balance': 1})

    if not user_balance or user_balance.get('balance', 0) < 20000:
        await update.message.reply_text("You need at least 20000 tokens to challenge.")
        proposing_users[user_id] = False  # Setting to False if balance requirement is not met
        return

    if proposing_users.get(user_id):
        await update.message.reply_text("You are already proposing. Please wait for the current proposal to finish.")
        proposing_users[user_id] = False  # Setting to False if user is already proposing
        return
    else:
        proposing_users[user_id] = True

    last_propose_time = last_propose_times.get(user_id)
    if last_propose_time:
        time_since_last_propose = datetime.now() - last_propose_time
        if time_since_last_propose < timedelta(minutes=5):
            remaining_cooldown = timedelta(minutes=5) - time_since_last_propose
            remaining_cooldown_minutes = remaining_cooldown.total_seconds() // 60
            remaining_cooldown_seconds = remaining_cooldown.total_seconds() % 60
            await update.message.reply_text(f"Cooldown! Please wait {int(remaining_cooldown_minutes)}m {int(remaining_cooldown_seconds)}s before challengeing again.")
            proposing_users[user_id] = False  # Setting to False if cooldown is active
            return

    await user_collection.update_one({'id': user_id}, {'$inc': {'balance': -10000}})

    proposal_message = "Challenge accepted"
    photo_path = 'https://telegra.ph/file/6abcb8278a66a11778841.jpg'
    await update.message.reply_photo(photo=photo_path, caption=proposal_message)

    await asyncio.sleep(2)

    await update.message.reply_text("Race has started")

    await asyncio.sleep(2)

    if random.random() < 0.6:
        rejection_message = "You lost"
        rejection_photo_path = 'https://telegra.ph/file/b94d4950840f4360b7b1d.jpg'
        await update.message.reply_photo(photo=rejection_photo_path, caption=rejection_message)
    else:
        all_characters = list(await collection.find({}).to_list(length=None))
        character = random.choice(all_characters)
        await user_collection.update_one({'id': user_id}, {'$push': {'characters': character}})
        await update.message.reply_photo(photo=character['img_url'],caption=f" congratulations you won here is your reward {character['name']} ")

    last_propose_times[user_id] = datetime.now()
    proposing_users[user_id] = False  # Setting to False after the proposal process completes

application.add_handler(CommandHandler("challenge", propose, block=False))
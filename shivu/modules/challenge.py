import asyncio
from telegram.ext import CommandHandler
from shivu import application, user_collection, collection
from telegram import Update
import random
from datetime import datetime, timedelta

# Dictionary to store last propose times
last_propose_times = {}
last_command_time = {}

async def race(update, context):
    user_id = update.effective_user.id
    user_balance = await user_collection.find_one({'id': user_id}, projection={'balance': 1})

    if not user_balance or user_balance.get('balance', 0) < 60000:
        await update.message.reply_text("You need at least 60000 tokens to challenge.")
        return

    last_propose_time = last_propose_times.get(user_id)
    if last_propose_time:
        time_since_last_propose = datetime.now() - last_propose_time
        if time_since_last_propose < timedelta(minutes=5):
            remaining_cooldown = timedelta(minutes=5) - time_since_last_propose
            remaining_cooldown_minutes = remaining_cooldown.total_seconds() // 60
            remaining_cooldown_seconds = remaining_cooldown.total_seconds() % 60
            await update.message.reply_text(f"Cooldown! Please wait {int(remaining_cooldown_minutes)}m {int(remaining_cooldown_seconds)}s before proposing again.")
            return

    await user_collection.update_one({'id': user_id}, {'$inc': {'balance': -50000}})

    proposal_message = "Challenge Accepted "
    photo_path = 'https://telegra.ph/file/938a03f66ce32dfeaee87.jpg'  # Replace with your photo path
    await update.message.reply_photo(photo=photo_path, caption=proposal_message)

    await asyncio.sleep(2)

    await update.message.reply_text("Race has started")

    await asyncio.sleep(2)

    selected_rarity = ["💮 Mythic", "💪 challenge edition"]  # Define the selected rarity here

    filtered_characters = await collection.find({'rarity': {'$in': selected_rarity}}).to_list(length=None)
    
    if not filtered_characters:
        await update.message.reply_text("No characters found with the specified rarity.")
        return

    character = random.choice(filtered_characters)

    await user_collection.update_one({'id': user_id}, {'$push': {'characters': character}})
    await update.message.reply_photo(photo=character['img_url'], caption=f"Congratulations! You won {character['rarity']} {character['car name']} as a reward.")

    last_propose_times[user_id] = datetime.now()

application.add_handler(CommandHandler("challenge", race, block=False))

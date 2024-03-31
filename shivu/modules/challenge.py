import asyncio
from telegram.ext import CommandHandler
from telegram import Update
import random
from datetime import datetime, timedelta
from shivu import collection, user_collection, user_totals_collection, shivuu, application

# Dictionary to store last propose times
last_propose_times = {}

async def race(update, context):
    # Check if the user has 50000 tokens
    user_id = update.effective_user.id
    user_balance = await user_collection.find_one({'id': user_id}, projection={'balance': 1})

    if not user_balance or user_balance.get('balance', 0) < 50000:
        await update.message.reply_text("You need at least 50000 tokens to propose.")
        return

    # Check last propose time and cooldown
    last_propose_time = last_propose_times.get(user_id)
    if last_propose_time:
        time_since_last_propose = datetime.now() - last_propose_time
        if time_since_last_propose < timedelta(minutes=5):
            remaining_cooldown = timedelta(minutes=5) - time_since_last_propose
            remaining_cooldown_minutes = remaining_cooldown.total_seconds() // 60
            remaining_cooldown_seconds = remaining_cooldown.total_seconds() % 60
            await update.message.reply_text(f"Cooldown! Please wait {int(remaining_cooldown_minutes)}m {int(remaining_cooldown_seconds)}s before proposing again.")
            return

    # Deduct the propose fee of 50000 tokens
    await user_collection.update_one({'id': user_id}, {'$inc': {'balance': -50000}})

    # Send the proposal message with a photo path
    proposal_message = "Challenge Accepted"
    photo_path = 'https://telegra.ph/file/694053e32528dbcd5f1cf.jpg'  # Replace with your photo path
    await update.message.reply_photo(photo=photo_path, caption=proposal_message)

    await asyncio.sleep(2)  # 2-second delay

    # Send the proposal text
    await update.message.reply_text("Race has started")

    await asyncio.sleep(2)  # 2-second delay

    # Generate a random result (60% chance of rejection, 40% chance of acceptance)
    if random.random() < 0.6:
        rejection_message = "You lost"
        rejection_photo_path = 'https://telegra.ph/fil/6e77ba2f79c4788fedc1a.jpg'  # Replace with rejection photo path
        await update.message.reply_photo(photo=rejection_photo_path, caption=rejection_message)
    else:
import random

selected_rarity = random.choices(["💮 Mythic", "💪 Challenge Edition"], weights=[0.6, 0.4], k=1)[0]

filtered_characters = [character for character in all_characters if character['rarity'] == selected_rarity]
if not filtered_characters:
    await update.message.reply_text(f"No characters found with the specified rarity: {selected_rarity}")
    return

character = random.choice(filtered_characters)
await user_collection.update_one({'id': user_id}, {'$push': {'characters': character}})
await update.message.reply_photo(photo=character['img_url'], caption=f"Congratulations You won a {character['rearity']} Car {character['car name']} As reward")


    # Update last propose time
    last_propose_times[user_id] = datetime.now()

# Add the CommandHandler to the application
application.add_handler(CommandHandler("changetime", race, block=False))
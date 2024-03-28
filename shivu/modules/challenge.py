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
    # Check if the user has 20000 tokens
    user_id = update.effective_user.id
    user_balance = await user_collection.find_one({'id': user_id}, projection={'balance': 1})

    if not user_balance or user_balance.get('balance', 0) < 20000:
        await update.message.reply_text("You need at least 20000 tokens to propose.")
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

    # Deduct the propose fee of 10000 tokens
    await user_collection.update_one({'id': user_id}, {'$inc': {'balance': -10000}})

    # Send the proposal message with a photo path
    proposal_message = "✨ 𝐅𝐢𝐧𝐚𝐥𝐥𝐲 𝐭𝐡𝐞 𝐭𝐢𝐦𝐞 𝐡𝐚𝐬 𝐜𝐨𝐦𝐞 ✨"
    photo_path = 'https://graph.org/file/deda08aefd8c0e1540fcd.jpg'  # Replace with your photo path
    await update.message.reply_photo(photo=photo_path, caption=proposal_message)

    await asyncio.sleep(2)  # 2-second delay

    # Send the proposal text
    await update.message.reply_text("𝐏𝐫𝐨𝐩𝐨𝐬𝐞𝐢𝐧𝐠 𝐡𝐞𝐫 💍")

    await asyncio.sleep(2)  # 2-second delay

    # Filter characters based on rarity (assuming rarity is stored in the character document)
    selected_rarity = ["💮 limited edition", "🏎 Race edition"]  # Specify the rarity you want to select characters from
    filtered_characters = await collection.find({'rarity': selected_rarity}).to_list(length=None)

    if not filtered_characters:
        await update.message.reply_text("No characters found with the specified rarity.")
        return

    # Select a random character from the filtered list
    character = random.choice(filtered_characters)

    # Add the selected character to the user's collection
    await user_collection.update_one({'id': user_id}, {'$push': {'characters': character}})
    await update.message.reply_photo(photo=character['img_url'], caption=f"Congratulations! You won {character['car name']} as a reward.")

    # Update last propose time
    last_propose_times[user_id] = datetime.now()

application.add_handler(CommandHandler("crace", race, block=False))

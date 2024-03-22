import asyncio
from telegram.ext import CommandHandler
from shivu import application, user_collection,collection
from telegram import Update
import random
from datetime import datetime, timedelta

# Dictionary to store last propose times
last_propose_times = {}

async def propose(update, context):
    # Check if the user has 20000 tokens
    user_id = update.effective_user.id
    user_balance = await user_collection.find_one({'id': user_id}, projection={'balance': 1})

    if not user_balance or user_balance.get('balance', 0) < 20000:
        await update.message.reply_text("𝗬𝗼𝘂 𝗻𝗲𝗲𝗱 𝗮𝘁 𝗹𝗲𝗮𝘀𝘁 𝟮𝟬𝟬𝟬𝟬 𝘁𝗼𝗸𝗲𝗻𝘀 𝘁𝗼 𝗿𝗮𝗰𝗲.")
        return

    # Check last propose time and cooldown
    last_propose_time = last_propose_times.get(user_id)
    if last_propose_time:
        time_since_last_propose = datetime.now() - last_propose_time
        if time_since_last_propose < timedelta(minutes=5):
            remaining_cooldown = timedelta(minutes=5) - time_since_last_propose
            remaining_cooldown_minutes = remaining_cooldown.total_seconds() // 60
            remaining_cooldown_seconds = remaining_cooldown.total_seconds() % 60
            await update.message.reply_text(f"𝗖𝗼𝗼𝗹𝗱𝗼𝘄𝗻! 𝗣𝗹𝗲𝗮𝘀𝗲 𝘄𝗮𝗶𝘁 {int(remaining_cooldown_minutes)}m {int(remaining_cooldown_seconds)}s 𝗯𝗲𝗳𝗼𝗿𝗲 𝗿𝗮𝗰𝗶𝗻𝗴 𝗮𝗴𝗮𝗶𝗻.")
            return

    # Deduct the propose fee of 10000 tokens
    await user_collection.update_one({'id': user_id}, {'$inc': {'balance': -10000}})
    # Send the proposal message with a photo path
    proposal_message = "𝗥𝗮𝗰𝗲 𝗶𝘀 𝗴𝗼𝗶𝗻𝗴 𝘁𝗼 𝗯𝗲 𝘀𝘁𝗮𝗿𝘁"
    photo_path = 'https://telegra.ph/file/4834a7d4e963b85626bd5.jpg'  # Replace with your photo path
    await update.message.reply_photo(photo=photo_path, caption=proposal_message)

    await asyncio.sleep(2)  # 2-second delay

    # Send the proposal text
    await update.message.reply_text("𝗥𝗮𝗰𝗲 𝗵𝗮𝘀 𝘀𝘁𝗮𝗿𝘁𝗲𝗱 ")

    await asyncio.sleep(2)  # 2-second delay

    # Generate a random result (60% chance of rejection, 40% chance of acceptance)
    if random.random() < 0.6:
        rejection_message = "𝗕𝗲𝘁𝘁𝗲𝗿 𝗹𝘂𝗰𝗸 𝗻𝗲𝘅𝘁 𝘁𝗶𝗺𝗲,𝗬𝗼𝘂 𝗹𝗼𝘀𝘁 𝘁𝗵𝗲 𝗿𝗮𝗰𝗲"
        rejection_photo_path = 'https://telegra.ph/file/561d51ab44101c27bc893.jpg'  # Replace with rejection photo path
        await update.message.reply_photo(photo=rejection_photo_path, caption=rejection_message)
    else:
    random_reward = random.randint(30000, 90000)
    monster_image = 'https://telegra.ph/file/f95f2d9755b89e16c7123.jpg'
    await user_collection.update_one(
        {'id': user_id},
        {'$inc': {'balance': random_reward}}
    )
    last_command_time[user_id] = datetime.utcnow()
    await update.message.reply_photo(photo=monster_image, caption=f"Congratulations You won the race here is Your reward Ŧ{random_reward} tokens.")

#Update last propose time

last_propose_times[user_id] = datetime.now()

# Add the CommandHandler to the application
application.add_handler(CommandHandler("race", propose, block=False))

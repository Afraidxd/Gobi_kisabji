from telegram.ext import CommandHandler
from shivu import application, user_collection
import random
import asyncio
import logging

logger = logging.getLogger(__name__)

participants = []
race_started = False
RACE_FEE = 10000
REMINDER_INTERVAL = 30  # in seconds

async def srace(update: Update):
    try:
        await update.message.reply_text(f"🏎️ A thrilling car race is organized! Participation fee is {RACE_FEE} tokens. Use /participate to join within 50 seconds.")
        await timeout_race(update)
    except Exception as e:
        logger.error(f"An error occurred in srace: {e}")

async def participate(update: Update):
    try:
        user_id = update.effective_user.id
        user_balance = await user_collection.find_one({'id': user_id}, projection={'balance': 1})

        if not user_balance or user_balance.get('balance', 0) < RACE_FEE:
            await update.message.reply_text("❌ You don't have enough tokens to participate.")
            return

        participants.append(update.effective_user.first_name)
        await user_collection.update_one({'id': user_id}, {'$inc': {'balance': -RACE_FEE}})
        await update.message.reply_text("✅ You have joined the race!")
    except Exception as e:
        logger.error(f"An error occurred in participate: {e}")

async def timeout_race(update: Update):
    try:
        global participants

        await asyncio.sleep(50)

        if len(participants) < 2:
            await update.message.reply_text("❌ Not enough participants to start the race.")
            participants = []
            return

        await update.message.reply_text("⏰ Time's up! The race will start now.")
        await start_race(update)
    except Exception as e:
        logger.error(f"An error occurred in timeout_race: {e}")

async def start_race(update: Update):
    try:
        global race_started

        if race_started:
            await update.message.reply_text("❌ Race has already started.")
            return

        race_started = True
        winner = random.choice(participants)
        prize = len(participants) * RACE_FEE

        for participant in participants:
            user_id = await user_collection.find_one({'first_name': participant}, projection={'id': 1})
            await user_collection.update_one({'id': user_id['id']}, {'$inc': {'balance': prize // len(participants)})

        await update.message.reply_text(f"🏁 The race has ended! 🏆 The winner is {winner} and each participant receives {prize // len(participants)} tokens.")

        participants.clear()
        race_started = False
    except Exception as e:
        logger.error(f"An error occurred in start_race: {e}")

async def remind_to_join(update: Update):
    try:
        if len(participants) < 2:
            return

        await update.message.reply_text("🏁 Join the race before time runs out! 🏎️")
    except Exception as e:
        logger.error(f"An error occurred in remind_to_join: {e}")

application.add_handler(CommandHandler("srace", srace, block=False))
application.add_handler(CommandHandler("participate", participate, block=False))

# Start the reminder loop
asyncio.create_task(remind_to_join(None))

application.run()
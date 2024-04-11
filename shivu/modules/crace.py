from shivu import application, user_collection
import random
import asyncio

participants = []
race_started = False

async def srace(update):
    await update.message.reply_text("🏎️ A thrilling car race is organized! Participation fee is 10000 tokens. Use /participate to join within 50 seconds.")
    asyncio.create_task(timeout_race(update))

async def participate(update):
    user_id = update.effective_user.id
    user_balance = await user_collection.find_one({'id': user_id}, projection={'balance': 1})

    if not user_balance or user_balance.get('balance', 0) < 10000:
        await update.message.reply_text("❌ You don't have enough tokens to participate.")
        return

    participants.append(update.effective_user.first_name)
    await user_collection.update_one({'id': user_id}, {'$inc': {'balance': -10000}})
    await update.message.reply_text("✅ You have joined the race!")

async def timeout_race(update):
    global participants

    await asyncio.sleep(50)

    if len(participants) < 2:
        await update.message.reply_text("❌ Not enough participants to start the race.")
        participants = []
        return

    await update.message.reply_text("⏰ Time's up! The race will start now.")
    await start_race(update)

async def start_race(update):
    global race_started

    if race_started:
        await update.message.reply_text("❌ Race has already started.")
        return

    race_started = True
    winner = random.choice(participants)
    prize = len(participants) * 10000

    for participant in participants:
        user_id = await user_collection.find_one({'first_name': participant}, projection={'id': 1})
        await user_collection.update_one({'id': user_id['id']}, {'$inc': {'balance': prize // len(participants)})

    await update.message.reply_text(f"🏁 The race has ended! 🏆 The winner is {winner} and each participant receives {prize // len(participants)} tokens.")

    participants.clear()
    race_started = False

async def remind_to_join(update):
    if len(participants) < 2:
        return

    await update.message.reply_text("🏁 Join the race before time runs out! 🏎️")

application.add_handler(srace)
application.add_handler(participate)

# Start the reminder loop
asyncio.create_task(remind_to_join())

application.run()

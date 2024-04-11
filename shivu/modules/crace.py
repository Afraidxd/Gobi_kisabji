from telegram.ext import CommandHandler
from shivu import application, user_collection, dispatcher
import random

participants = []
race_started = False

async def srace(update, context):
    await update.message.reply_text("🏎️ A thrilling car race is organized! Participation fee is 10000 tokens. Use /participate to join within 50 seconds.")

    # Set a timer for 50 seconds to allow users to join the race
    context.job_queue.run_once(timeout_race, 50, context={'update': update})

async def participate(update, context):
    user_id = update.effective_user.id
    user_balance = await user_collection.find_one({'id': user_id}, projection={'balance': 1})

    if not user_balance or user_balance.get('balance', 0) < 10000:
        await update.message.reply_text("❌ You don't have enough tokens to participate.")
        return

    participants.append(update.effective_user.first_name)
    await user_collection.update_one({'id': user_id}, {'$inc': {'balance': -10000}})
    await update.message.reply_text("✅ You have joined the race!")

async def timeout_race(context):
    global participants

    if len(participants) < 2:
        await context['update'].message.reply_text("❌ Not enough participants to start the race.")
        participants = []
        return

    await context['update'].message.reply_text("⏰ Time's up! The race will start now.")
    await start_race(context['update'], context)

async def start_race(update, context):
    global race_started

    if race_started:
        await update.message.reply_text("❌ Race has already started.")
        return

    race_started = True
    winner = random.choice(participants)
    prize = len(participants) * 10000

    for participant in participants:
        user_id = await user_collection.find_one({'first_name': participant}, projection={'id': 1})
        await user_collection.update_one({'id': user_id['id']}, {'$inc': {'balance': prize // len(participants)}})

    await update.message.reply_text(f"🏁 The race has ended! 🏆 The winner is {winner} and each participant receives {prize // len(participants)} tokens.")

    participants.clear()
    race_started = False

async def remind_to_join(context):
    if len(participants) < 2:
        return

    await context.bot.send_message(context.job.context['update'].effective_chat.id, "🏁 Join the race before time runs out! 🏎️")

application.add_handler(CommandHandler("srace", srace, block=False))
application.add_handler(CommandHandler("participate", participate, block=False))

dispatcher.add_handler(dispatcher.job_queue.run_repeating(remind_to_join, interval=10, first=10, context={'update': update}))

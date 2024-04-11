import asyncio
import random
from telegram import Update
from shivu import application, user_collection
from telegram.ext import CommandHandler, CallbackContext

participants = []
race_started = False
srace_used = False

async def srace(update: Update, context: CallbackContext):
    global srace_used
    await update.message.reply_text("🏎️ A thrilling car race is organized! Participation fee is 10000 tokens. Use /participate to join within 50 seconds.")
    context.job_queue.run_once(timeout_race, 50, context={'update': update})
    srace_used = True

async def participate(update: Update, context: CallbackContext):
    global srace_used

    if not srace_used:
        await update.message.reply_text("❌ The /srace command must be used first before participating.")
        return

    user_id = update.effective_user.id
    user_balance = await user_collection.find_one({'id': user_id}, projection={'balance': 1})

    if any(participant['id'] == user_id for participant in participants):
        await update.message.reply_text("❌ You have already joined the race.")
        return

    if not user_balance or user_balance.get('balance', 0) < 10000:
        await update.message.reply_text("❌ You don't have enough tokens to participate.")
        return

    participants.append({'id': user_id, 'name': update.effective_user.first_name})
    await user_collection.update_one({'id': user_id}, {'$inc': {'balance': -10000}})
    await update.message.reply_text("✅ You have joined the race!")

async def timeout_race(context: CallbackContext):
    global participants

    if len(participants) < 2:
        await context.bot.send_message(context.job.context['update'].message.chat_id, "❌ Not enough participants to start the race.")
        participants = []
        return

    context.job_queue.run_repeating(remind_to_join, interval=10, first=10, context=context)
    await asyncio.sleep(50)

    await start_race(context.job.context['update'], context)

async def start_race(update: Update, context: CallbackContext):
    global race_started

    if race_started:
        await update.message.reply_text("❌ Race has already started.")
        return

    race_started = True
    winner = random.choice([participant['name'] for participant in participants])
    prize = len(participants) * 10000

    for participant in participants:
        await user_collection.update_one({'id': participant['id']}, {'$inc': {'balance': prize // len(participants)}})

    await update.message.reply_text(f"🏁 The race has ended! 🏆 The winner is {winner} and each participant receives {prize // len(participants)} tokens.")

    participants.clear()
    race_started = False
    srace_used = False

async def remind_to_join(context: CallbackContext):
    if len(participants) < 2:
        return

    await context.bot.send_message(context.job.context['update'].message.chat_id, "🏁 Join the race before time runs out! 🏎️")

application.add_handler(CommandHandler("srace", srace))
application.add_handler(CommandHandler("participate", participate))


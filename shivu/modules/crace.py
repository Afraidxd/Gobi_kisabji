import asyncio
import random
from shivu import application, user_collection
from telegram.ext import CommandHandler

PARTICIPATION_FEE = 10000
TIMEOUT_DURATION = 50
REMIND_INTERVAL = 10

participants: list = []
race_started: bool = False
srace_used: bool = False

async def srace(update, context):
    await update.message.reply_text("🏎️ A thrilling car race is organized! Participation fee is {} tokens. Use /participate to join within {} seconds.".format(PARTICIPATION_FEE, TIMEOUT_DURATION))
    context.job_queue.run_once(timeout_race, TIMEOUT_DURATION)
    global srace_used
    srace_used = True

async def participate(update, context):
    global srace_used

    if not srace_used:
        await update.message.reply_text("❌ The /srace command must be used first before participating.")
        return

    user_id = update.effective_user.id
    user_balance = await user_collection.find_one({'id': user_id}, projection={'balance': 1})

    if user_id in [p['id'] for p in participants]:
        await update.message.reply_text("❌ You have already joined the race.")
        return

    if not user_balance or user_balance.get('balance', 0) < PARTICIPATION_FEE:
        await update.message.reply_text("❌ You don't have enough tokens to participate.")
        return

    participants.append({'id': user_id, 'name': update.effective_user.first_name})
    await user_collection.update_one({'id': user_id}, {'$inc': {'balance': -PARTICIPATION_FEE}})
    await update.message.reply_text("✅ You have joined the race!")

async def timeout_race(context):
    global participants

    if len(participants) < 2:
        await context['update'].message.reply_text("❌ Not enough participants to start the race.")
        participants = []
        return

    await context.job_queue.run_repeating(remind_to_join, interval=REMIND_INTERVAL, first=REMIND_INTERVAL)
    await asyncio.sleep(TIMEOUT_DURATION)

    await start_race(context['update'], context)

async def start_race(update, context):
    global race_started

    if race_started:
        await update.message.reply_text("❌ Race has already started.")
        return

    race_started = True
    winner = random.choice([p['name'] for p in participants])
    prize = len(participants) * 10000

    for participant in participants:
        await user_collection.update_one({'id': participant['id']}, {'$inc': {'balance': prize // len(participants)}})

    await update.message.reply_text(f"🏁 The race has ended! 🏆 The winner is {winner} and each participant receives {prize // len(participants)} tokens.")

    participants = []
    race_started = False
    srace_used = False

async def remind_to_join(context):
    if len(participants) < 2:
        return

    await context.bot.send_message(context.job.context['update'].effective_chat.id, "🏁 Join the race before time runs out! 🏎️")

application.add_handler(CommandHandler("srace", srace, block=False))
application.add_handler(CommandHandler("participate", participate, block=False))
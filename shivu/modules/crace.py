import asyncio
import random
from typing import List, Dict

from pyrogram import Client, filters
from pyrogram.types import Message

from shivu import application, user_collection

config: Dict[str, bool | List[Dict[str, str]]] = {
    'race_started': False,
    'srace_used': False,
    'participants': [],
}

async def srace(update: Message, context: CallbackContext):
    await update.reply_text("🏎️ A thrilling car race is organized! Participation fee is 10000 tokens. Use /participate to join within 50 seconds.")
    context.job_queue.run_once(timeout_race, 50, context={'update': update})

async def participate(client: Client, update: Message):
    if not config['srace_used']:
        await update.reply_text("❌ The /srace command must be used first before participating.")
        return

    user_id = update.from_user.id
    user_balance = await user_collection.find_one({'id': user_id}, projection={'balance': 1})

    if any(participant['id'] == user_id for participant in config['participants']):
        await update.reply_text("❌ You have already joined the race.")
        return

    if not user_balance or user_balance.get('balance', 0) < 10000:
        await update.reply_text("❌ You don't have enough tokens to participate.")
        return

    config['participants'].append({'id': user_id, 'name': update.from_user.first_name})
    await user_collection.update_one({'id': user_id}, {'$inc': {'balance': -10000}})
    await update.reply_text("✅ You have joined the race!")

async def timeout_race(context):
    update = context.job.context.get('update')

    if len(config['participants']) < 2:
        await update.reply_text("❌ Not enough participants to start the race.")
        config['participants'] = []
        return

    await context.job_queue.run_repeating(remind_to_join, interval=10, first=10, context={'update': update})
    await asyncio.sleep(50)
    await start_race(update, context)

async def start_race(update: Message, context: CallbackContext):
    if config['race_started']:
        await update.reply_text("❌ Race has already started.")
        return

    config['race_started'] = True
    winner = random.choice([p['name'] for p in config['participants']])
    prize = len(config['participants']) * 10000

    for participant in config['participants']:
        await user_collection.update_one({'id': participant['id']}, {'$inc': {'balance': prize // len(config['participants'])}})

    await update.reply_text(f"🏁 The race has ended! 🏆 The winner is {winner} and each participant receives {prize // len(config['participants'])} tokens.")

    config['participants'] = []
    config['race_started'] = False
    config['srace_used'] = False

async def remind_to_join(context):
    update = context.job.context.get('update')

    if len(config['participants']) < 2:
        return

    await update.reply_text("🏁 Join the race before time runs out! 🏎️")

application.add_handler(CommandHandler("srace", srace, block=False))
application.add_handler(CommandHandler("participate", participate, block=False))
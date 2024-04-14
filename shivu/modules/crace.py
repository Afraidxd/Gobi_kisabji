import asyncio
import random
from pyrogram import Client, filters
from pyrogram.types import Message
from telegram.ext import CommandHandler 

from shivu import application, user_collection

config = {
    'race_started': False,
    'srace_used': False,
    'participants': [],
}

async def srace(client: Client, message: Message):
    await message.reply_text("🏎️ A thrilling car race is organized! Participation fee is 10000 tokens. Use /participate to join within 50 seconds.")
    await asyncio.sleep(50)
    if len(config['participants']) < 2:
        await message.reply_text("❌ Not enough participants to start the race.")
        config['participants'] = []
        return
    await start_race(message, client)

async def participate(client: Client, message: Message):
    if not config['srace_used']:
        await message.reply_text("❌ The /srace command must be used first before participating.")
        return

    user_id = message.from_user.id
    user_balance = await user_collection.find_one({'id': user_id}, projection={'balance': 1})

    if any(participant['id'] == user_id for participant in config['participants']):
        await message.reply_text("❌ You have already joined the race.")
        return

    if not user_balance or user_balance.get('balance', 0) < 10000:
        await message.reply_text("❌ You don't have enough tokens to participate.")
        return

    config['participants'].append({'id': user_id, 'name': message.from_user.first_name})
    await user_collection.update_one({'id': user_id}, {'$inc': {'balance': -10000}})
    await message.reply_text("✅ You have joined the race!")

async def start_race(message: Message, client: Client):
    if config['race_started']:
        await message.reply_text("❌ Race has already started.")
        return

    config['race_started'] = True
    winner = random.choice([p['name'] for p in config['participants']])
    prize = len(config['participants']) * 10000

    for participant in config['participants']:
        await user_collection.update_one({'id': participant['id']}, {'$inc': {'balance': prize // len(config['participants'])}})

    await message.reply_text(f"🏁 The race has ended! 🏆 The winner is {winner} and each participant receives {prize // len(config['participants'])} tokens.")

    config['participants'] = []
    config['race_started'] = False
    config['srace_used'] = False

application.add_handler(CommandHandler("srace", srace, block=False))
application.add_handler(CommandHandler("participate", participate, block=False))
import asyncio
import random
from typing import Dict, List

from pyrogram import Client, filters
from pyrogram.types import Message

from shivu import application, user_collection

class RaceContext:
    def __init__(self):
        self.race_started = False
        self.srace_used = False
        self.participants: Dict[int, str] = {}

race_context = RaceContext()

@application.on_message(filters.command("srace"))
async def srace(client: Client, message: Message):
    if race_context.srace_used:
        await message.reply_text("❌ The /srace command has already been used.")
        return

    await message.reply_text("🏎️ A thrilling car race is organized! Participation fee is 10000 tokens. Use /participate to join within 50 seconds.")
    await asyncio.sleep(50)

    if len(race_context.participants) < 2:
        await message.reply_text("❌ Not enough participants to start the race.")
        race_context.participants = {}
        return

    await client.job_queue.run_repeating(remind_to_join, interval=10, first=10, context={'message': message})
    await asyncio.sleep(50)
    await start_race(message, client)
    race_context.srace_used = False
    race_context.participants = {}

@application.on_message(filters.command("participate"))
async def participate(client: Client, message: Message):
    if not race_context.srace_used:
        await message.reply_text("❌ The /srace command must be used first before participating.")
        return

    user_id = message.from_user.id
    user_balance = await user_collection.find_one({'id': user_id}, projection={'balance': 1})

    if user_id in race_context.participants:
        await message.reply_text("❌ You have already joined the race.")
        return

    if not user_balance or user_balance.get('balance', 0) < 10000:
        await message.reply_text("❌ You don't have enough tokens to participate.")
        return

    race_context.participants[user_id] = message.from_user.first_name
    await user_collection.update_one({'id': user_id}, {'$inc': {'balance': -10000}})
    await message.reply_text("✅ You have joined the race!")

async def timeout_race(context):
    message = context.job.context.get('message')

    if len(race_context.participants) < 2:
        await message.reply_text("❌ Not enough participants to start the race.")
        race_context.participants = {}
        return

    await context.job_queue.run_repeating(remind_to_join, interval=10, first=10, context={'message': message})
    await asyncio.sleep(50)
    await start_race(message, context.bot)

async def start_race(message: Message, bot: Client):
    if race_context.race_started:
        await message.reply_text("❌ Race has already started.")
        return

    race_context.race_started = True
    winner = random.choice([p for p in race_context.participants.values()])
    prize = len(race_context.participants) * 10000

    for participant_id, participant_name in race_context.participants.items():
        await user_collection.update_one({'id': participant_id}, {'$inc': {'balance': prize // len(race_context.participants)}})

    await message.reply_text(f"🏁 The race has ended! 🏆 The winner is {winner} and each participant receives {prize // len(race_context.participants)} tokens.")

   
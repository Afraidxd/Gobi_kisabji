import asyncio
import random
from typing import List, Dict

import pyrogram
from pyrogram.errors import RpcError
from pyrogram.handlers import MessageHandler
from pyrogram.types import Update
from pyrogram.filters import command

from shivu import application, user_collection

participants: List[Dict[str, str]] = []
race_started: bool = False
srace_used: bool = False

async def srace(client: pyrogram.Client, message: Update):
    global srace_used

    if srace_used:
        await message.reply_text("❌ The /srace command can only be used once.")
        return

    srace_used = True

    await message.reply_text("🏎️ A thrilling car race is organized! Participation fee is 10000 tokens. Use /participate to join within 50 seconds.")

    await asyncio.sleep(50)

    try:
        await start_race(client, message)
    except RpcError as e:
        await message.reply_text(f"❌ Error starting the race: {e}")
        participants = []
        race_started = False
        srace_used = False


async def participate(client: pyrogram.Client, message: Update):
    user_id = message.from_user.id
    user_balance = await user_collection.find_one({'id': user_id}, projection={'balance': 1})

    if any(participant['id'] == user_id for participant in participants):
        await message.reply_text("❌ You have already joined the race.")
        return

    if not user_balance or user_balance.get('balance', 0) < 10000:
        await message.reply_text("❌ You don't have enough tokens to participate.")
        return

    participants.append({'id': user_id, 'name': message.from_user.first_name})
    await user_collection.update_one({'id': user_id}, {'$inc': {'balance': -10000}})
    await message.reply_text("✅ You have joined the race!")


async def start_race(client: pyrogram.Client, message: Update):
    global race_started

    if race_started:
        await message.reply_text("❌ Race has already started.")
        return

    race_started = True

    prize = len(participants) * 10000

    winner = random.choice([participant['name'] for participant in participants])

    for participant in participants:
        try:
            await user_collection.update_one({'id': participant['id']}, {'$inc': {'balance': prize // len(participants)}})
        except RpcError as e:
            await message.reply_text(f"❌ Error updating balance for participant {participant['name']}: {e}")

    await message.reply_text(f"🏁 The race has ended! 🏆 The winner is {winner} and each participant receives {prize // len(participants)} tokens.")

    participants.clear()
    race_started = False
    srace_used = False


async def remind_to_join(client: pyrogram.Client, message: Update):
    if len(participants) < 2:
        return

    await message.reply_text("🏁 Join the race before time runs out! 🏎️")


application.add_handler(MessageHandler(command("srace"), srace))
application.add_handler(MessageHandler(command("participate"), participate))

async def main():
    await application.start()
    await application.idle()


if __name__ == "__main__":
    asyncio.run(main())
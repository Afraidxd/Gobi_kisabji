from pyrogram.errors import RaisedException
from pyrogram.ext import CommandHandler, Filters, MessageHandler
from pyrogram.handlers import BaseHandler
from pyrogram.types import Message

from shivu import application, user_collection

RACE_FEE = 10000

class ParticipantHandler(BaseHandler):
    async def check(self, update: Update) -> bool:
        if update.effective_chat.type != 'private':
            return False
        if not await user_collection.find_one({'id': update.effective_user.id}):
            await user_collection.insert_one({'id': update.effective_user.id, 'balance': 0})
        return True

    async def handle(self, update: Update):
        user_id = update.effective_user.id
        user_balance = await user_collection.find_one({'id': user_id}, projection={'balance': 1})

        if user_balance.get('balance', 0) < RACE_FEE:
            await update.message.reply_text("Insufficient balance to participate in the race.")
            return

        await user_collection.update_one({'id': user_id}, {'$inc': {'balance': -RACE_FEE}})
        await update.message.reply_text("You have joined the race!")

@application.on_message(Filters.command('srace'))
async def start_race(client, message: Message):
    try:
        await application.send_message(message.chat.id, "A car race is organized! Participants fees are 10000 tokens. Use /participate to join.")
        await application.send_message(message.chat.id, "Waiting for participants...")

        participants = []
        for _ in range(2):
            participant = await application.send_message(message.chat.id, "Type /participate to join the race.")
            await ParticipantHandler.handle(participant)
            participants.append(participant.from_user.id)

        await application.send_message(message.chat.id, f"Race started!\nLeft time: 50 sec")

        # Simulate the race
        for _ in range(5):
            await application.send_message(message.chat.id, "Left time: 10 sec")
            await application.sleep(10)

        winner = random.choice(participants)
        await application.send_message(message.chat.id, f"The race has started!\n\nThe winner is <b>{winner}</b>!")

        # Distribute the prize
        total_fees = RACE_FEE * len(participants)
        prize = int(total_fees * 0.7)
        await application.send_message(message.chat.id, f"The prize is {prize} tokens!")

        for participant in participants:
            if participant == winner:
                await application.send_message(message.chat.id, f"<b>{participant}</b> has won {prize} tokens!")
            else:
                await application.send_message(message.chat.id, f"<b>{participant}</b> has won 0 tokens.")

    except RaisedException as e:
        print(f"Error: {e}")

@application.on_message(Filters.command('participate'))
async def join_race(client, message: Message):
    try:
        await ParticipantHandler.handle(message)
    except RaisedException as e:
        print(f"Error: {e}")
        await message.reply_text("You have already joined the race.")
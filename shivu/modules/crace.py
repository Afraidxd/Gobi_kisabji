from shivu import application, user_collection
import random
import asyncio

participants = []
race_started = False

class SRaceHandler:
    async def __call__(self, update):
        await update.message.reply_text("🏎️ A thrilling car race is organized! Participation fee is 10000 tokens. Use /participate to join within 50 seconds.")
        asyncio.create_task(timeout_race(update))

class ParticipateHandler:
    async def __call__(self, update):
        user_id = update.effective_user.id
        user_balance = await user_collection.find_one({'id': user_id}, projection={'balance': 1})

        if not user_balance or user_balance.get('balance', 0) < 10000:
            await update.message.reply_text("❌ You don't have enough tokens to participate.")
            return

        participants.append(update.effective_user.first_name)
        await user_collection.update_one({'id': user_id}, {'$inc': {'balance': -10000}})
        await update.message.reply_text("✅ You have joined the race!")

async def timeout_race(update):
    await asyncio.sleep(50)
    if len(participants) > 1:
        winner = random.choice(participants)
        await update.message.reply_text(f"🏁 The race is over! The winner is: {winner}")
    else:
        await update.message.reply_text("Not enough participants. Race canceled.")

srace_handler = SRaceHandler()
participate_handler = ParticipateHandler()

application.add_handler(srace_handler, command='srace')
application.add_handler(participate_handler, command='participate')

application.run()

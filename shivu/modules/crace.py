from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CommandHandler, CallbackContext, CallbackQueryHandler
from shivu import application, user_collection
import random
import asyncio

participants = []

async def update_user_balance(user_id, amount):
    await user_collection.update_one({'id': user_id}, {'$inc': {'balance': amount}})

def srace(update: Update, context: CallbackContext):
    async def start_race():
        await asyncio.sleep(50)
        if len(participants) < 2:
            update.message.reply_text("No user joined the race.")
        else:
            winner_id = random.choice(participants)
            total_coins = 10000 * len(participants)
            winner_reward = int(0.7 * total_coins)
            await update_user_balance(winner_id, winner_reward)
            winner_name = await user_collection.find_one({'id': winner_id}, projection={'name': 1})
            for user_id in participants:
                await update_user_balance(user_id, -10000)
                user_name = await user_collection.find_one({'id': user_id}, projection={'name': 1})
                await application.bot.send_message(chat_id=user_id, text=f"Race has started! Winner is {winner_name}. You have been refunded your participation fee.")

    asyncio.create_task(start_race())
    update.message.reply_text("A car race is organized with a participant fee of 10000 tokens. Use /participate to join. You have 50 seconds to participate.")

async def participate(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    user_balance = await user_collection.find_one({'id': user_id}, projection={'balance': 1})

    if not user_balance or user_balance.get('balance', 0) < 10000:
        update.message.reply_text("You don't have enough tokens to participate.")
        return

    if user_id not in participants:
        participants.append(user_id)
    
    update.message.reply_text("You have joined the race!")
    await update_user_balance(user_id, -10000)

application.add_handler(CommandHandler("srace", srace))
application.add_handler(CommandHandler("participate", participate))

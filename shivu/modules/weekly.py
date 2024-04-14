from telegram.ext import CommandHandler
from shivu import application, user_collection
from telegram import Update
import random

async def sbet(update, context):
    # Parse the amount from the command
    try:
        amount = int(context.args[0])
        if amount <= 0:
            raise ValueError("Amount must be greater than zero.")
    except (IndexError, ValueError):
        await update.message.reply_text("Use /bet <amount>")
        return

    user_id = update.effective_user.id
    user_balance = await user_collection.find_one({'id': user_id}, projection={'balance': 1})

    if not user_balance or user_balance.get('balance', 0) < amount:
        await update.message.reply_text("Insufficient balance to make the bet.")
        return

    if random.random() < 0.4:
        won_amount = 2 * amount
        await user_collection.update_one({'id': user_id}, {'$inc': {'balance': won_amount + amount}})
        updated_balance = user_balance.get('balance', 0) + won_amount
        await update.message.reply_text(
            f"🎉 Congratulations! You won {won_amount}!\n\n💰 Your updated balance is \033[1;32;40m{updated_balance}\033[0m."
        )
    else:
        await user_collection.update_one({'id': user_id}, {'$inc': {'balance': -amount}})
        updated_balance = user_balance.get('balance', 0) - amount
        await update.message.reply_text(
            f"😔 You lost {amount}.\n\n💸 Your updated balance is \033[1;31;40m{updated_balance}\033[0m."
        )

application.add_handler(CommandHandler("bet", sbet, block=False))

from telegram.ext import CommandHandler
from shivu import application, user_collection
from telegram import Update
from datetime import datetime, timedelta
import asyncio
# Dictionary to store last payment times
last_payment_times = {}
from shivu import collection, user_collection, application

from shivu import shivuu as app

from itertools import groupby


async def balance(update, context):
    # Retrieve user balance and total collections from the database (replace this with your actual database query)
    user_id = update.effective_user.id
    user_balance = await user_collection.find_one({'id': user_id}, projection={'balance': 1})

    if user_balance:
        balance_amount = user_balance.get('balance', 0)
        if balance_amount >= 1000000:
            balance_display = f"{balance_amount // 1000000}m"
        elif balance_amount >= 1000:
            balance_display = f"{balance_amount // 1000}k"
        else:
            balance_display = f"Ŧ{balance_amount} Tokens"


        balance_message = f"Balance: {balance_display}"
    else:
        balance_message = "Claim bonus first using /bonus and /wbonus "

    await update.message.reply_text(balance_message)

async def pay(update, context):
    sender_id = update.effective_user.id

    # Check if the command was a reply
    if not update.message.reply_to_message:
        await update.message.reply_text("Please reply to a user to /pay.")
        return

    # Extract the recipient's user ID
    recipient_id = update.message.reply_to_message.from_user.id

    # Prevent user from paying themselves
    if sender_id == recipient_id:
        await update.message.reply_text("You can't pay yourself.")
        return

    # Parse the amount from the command
    try:
        amount = int(context.args[0])
        if amount <= 0:
            raise ValueError("Amount must be greater than zero.")
    except (IndexError, ValueError):
        await update.message.reply_text("Use /pay <amount>")
        return

    # Check if the sender has enough balance
    sender_balance = await user_collection.find_one({'id': sender_id}, projection={'balance': 1})
    if not sender_balance or sender_balance.get('balance', 0) < amount:
        await update.message.reply_text("Insufficient balance to make the payment.")
        return

    # Check last payment time and cooldown
    last_payment_time = last_payment_times.get(sender_id)
    if last_payment_time:
        time_since_last_payment = datetime.now() - last_payment_time
        if time_since_last_payment < timedelta(minutes=10):
            cooldown_time = timedelta(minutes=10) - time_since_last_payment
            formatted_cooldown = format_timedelta(cooldown_time)
            await update.message.reply_text(f"Cooldown! You can pay again in `{formatted_cooldown}`.")
            return

    # Perform the payment
    await user_collection.update_one({'id': sender_id}, {'$inc': {'balance': -amount}})
    await user_collection.update_one({'id': recipient_id}, {'$inc': {'balance': amount}}, upsert=True)

    # Update last payment time
    last_payment_times[sender_id] = datetime.now()

    # Fetch updated sender balance
    updated_sender_balance = await user_collection.find_one({'id': sender_id}, projection={'balance': 1})

    # Reply with payment success and updated balance
    await update.message.reply_text(
        f"Payment Successful! You Paid Ŧ{amount} Tokens to {update.message.reply_to_message.from_user.username}. "
    )


async def mtop(update, context):
    top_users = await user_collection.find({}, projection={'id': 1, 'first_name': 1, 'last_name': 1, 'balance': 1}).sort('balance', -1).limit(10).to_list(10)

    top_users_message = "Top 10 Users With Highest Tokens\n\n"
    for i, user in enumerate(top_users, start=1):
        first_name = user.get('first_name', 'Unknown')
        last_name = user.get('last_name', '')
        user_id = user.get('id', 'Unknown')

        print(f"First Name: {first_name}, Last Name: {last_name}")

        if first_name != 'Unknown' and last_name != '':
            full_name = f"{first_name} {last_name}"
        else:
            full_name = first_name

        top_users_message += f"{i}. <a href='tg://user?id={user_id}'>{full_name}</a>, 💸{user.get('balance', 0)} Tokens\n"

    photo_path = 'https://telegra.ph/file/14cb27c83d171bd125de4.jpg'
    await update.message.reply_photo(photo=photo_path, caption=top_users_message, parse_mode='HTML')



async def daily_reward(update, context):
    user_id = update.effective_user.id

    # Check if the user already claimed the daily reward today
    user_data = await user_collection.find_one({'id': user_id}, projection={'last_daily_reward': 1, 'balance': 1})

    if user_data:
        last_claimed_date = user_data.get('last_daily_reward')

        if last_claimed_date and last_claimed_date.date() == datetime.utcnow().date():
            time_since_last_claim = datetime.utcnow() - last_claimed_date
            time_until_next_claim = timedelta(days=1) - time_since_last_claim
            formatted_time_until_next_claim = format_timedelta(time_until_next_claim)
            await update.message.reply_text(f"You already claimed your today's reward. Come back Tomorrow!\nTime Until Next Claim: `{formatted_time_until_next_claim}`.")
            return

    await user_collection.update_one(
        {'id': user_id},
        {'$inc': {'balance': 50000}, '$set': {'last_daily_reward': datetime.utcnow()}},
        upsert=True
    )

    await update.message.reply_text("Congratulations! You claimed 50000 Tokens")


def format_timedelta(td: timedelta) -> str:
    seconds = td.total_seconds()
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return "{:02}h {:02}m {:02}s".format(int(hours), int(minutes), int(seconds))

async def weekly(update, context):
    user_id = update.effective_user.id

    # Check if the user already claimed the weekly bonus this week
    user_data = await user_collection.find_one({'id': user_id}, projection={'last_weekly_bonus': 1, 'balance': 1})

    if user_data:
        last_claimed_date = user_data.get('last_weekly_bonus')

        if last_claimed_date and last_claimed_date.date() >= (datetime.utcnow() - timedelta(days=7)).date():
            time_since_last_claim = datetime.utcnow() - last_claimed_date
            time_until_next_claim = timedelta(days=7) - time_since_last_claim
            formatted_time_until_next_claim = format_timedelta(time_until_next_claim)
            await update.message.reply_text(f"You already claimed your weekly bonus for this week. Come back next week!\nTime Until Next Claim: `{formatted_time_until_next_claim}`.")
            return

    await user_collection.update_one(
        {'id': user_id},
        {'$inc': {'balance': 100000}, '$set': {'last_weekly_bonus': datetime.utcnow()}},
        upsert=True
    )

    await update.message.reply_text("Congratulations! You claimed 100000 Tokens as your weekly bonus.")


application.add_handler(CommandHandler("bonus", daily_reward, block=False))
application.add_handler(CommandHandler("wbonus", weekly, block=False))
application.add_handler(CommandHandler("bal", balance, block=False))
application.add_handler(CommandHandler("pay", pay, block=False))
application.add_handler(CommandHandler("tops", mtop, block=False))
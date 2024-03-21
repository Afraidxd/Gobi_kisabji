from telegram.ext import CommandHandler
from shivu import application, user_collection
from telegram import Update
from datetime import datetime, timedelta
import asyncio
# Dictionary to store last payment times
last_payment_times = {}

async def balance(update, context):
    # Retrieve user balance from the database (replace this with your actual database query)
    user_id = update.effective_user.id
    user_balance = await user_collection.find_one({'id': user_id}, projection={'balance': 1})
   
    if user_balance:
        balance_amount = user_balance.get('balance', 0)
        balance_message = f"Your Coin Balance is: 〄{balance_amount}"
    else:
        balance_message = "garb some Cars first."

    await update.message.reply_photo(photo=
photo_path1, caption=balance_message, parse_mode='HTML')

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
    await user_collection.update_one({'id': recipient_id}, {'$inc': {'balance': amount}})

    # Update last payment time
    last_payment_times[sender_id] = datetime.now()

    # Fetch updated sender balance
    updated_sender_balance = await user_collection.find_one({'id': sender_id}, projection={'balance': 1})

    # Reply with payment success and updated balance
    await update.message.reply_text(
        f"Payment Successful! You Paid {amount} Tokens to {update.message.reply_to_message.from_user.username}. "
    )


async def mtop(update, context):
    # Retrieve the top 10 users with the highest balance
    top_users = await user_collection.find({}, projection={'id': 1, 'first_name': 1, 'last_name': 1, 'balance': 1}).sort('balance', -1).limit(10).to_list(10)

    # Create a message with the top users
    top_users_message = "Top 10 Users With Highest Tokens\n\n"
    for i, user in enumerate(top_users, start=1):
        first_name = user.get('first_name', 'Unknown')
        last_name = user.get('last_name', '')
        user_id = user.get('id', 'Unknown')

        # Concatenate first_name and last_name if last_name is available
        full_name = f"{first_name} {last_name}" if last_name else first_name

        top_users_message += f"{i}. <a href='tg://user?id={user_id}'>{full_name}</a>, 💸{user.get('balance', 0)} Tokens\n"
    # Send the photo and include the top_users_message in the caption
    photo_path = 'https://te.legra.ph/file/ce017c623256a631be42f.jpg'
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
        {'$inc': {'balance': 50000}, '$set': {'last_daily_reward': datetime.utcnow()}}
    )

    await update.message.reply_text("Congratulations! You claimed 50000 Tokens")


def format_timedelta(td: timedelta) -> str:
    seconds = td.total_seconds()
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return "{:02}h {:02}m {:02}s".format(int(hours), int(minutes), int(seconds))


from datetime import datetime, timedelta

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
        await update.message.reply_text("Use /sbet <amount>")
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
            f"You bet {amount} coins and won! You came back with {won_amount} coins. Your updated balance is {updated_balance}."
        )
    else:
        await user_collection.update_one({'id': user_id}, {'$inc': {'balance': -amount}})
        updated_balance = user_balance.get('balance', 0) - amount
        await update.message.reply_text(
            f"You bet {amount} coins and lost! You came back without {amount} coins. Your updated balance is {updated_balance}."
        )

import asyncio
from telegram.ext import CommandHandler
from shivu import application, user_collection
from telegram import Update
import random
from datetime import datetime, timedelta

# Dictionary to store last propose times
last_propose_times = {}

async def propose(update, context):
    # Check if the user has 20000 tokens
    user_id = update.effective_user.id
    user_balance = await user_collection.find_one({'id': user_id}, projection={'balance': 1})

    if not user_balance or user_balance.get('balance', 0) < 20000:
        await update.message.reply_text("You need at least 20000 tokens to propose.")
        return

    # Check last propose time and cooldown
    last_propose_time = last_propose_times.get(user_id)
    if last_propose_time:
        time_since_last_propose = datetime.now() - last_propose_time
        if time_since_last_propose < timedelta(minutes=5):
            remaining_cooldown = timedelta(minutes=5) - time_since_last_propose
            remaining_cooldown_minutes = remaining_cooldown.total_seconds() // 60
            remaining_cooldown_seconds = remaining_cooldown.total_seconds() % 60
            await update.message.reply_text(f"Cooldown! Please wait {int(remaining_cooldown_minutes)}m {int(remaining_cooldown_seconds)}s before proposing again.")
            return

    # Deduct the propose fee of 10000 tokens
    await user_collection.update_one({'id': user_id}, {'$inc': {'balance': -10000}})

    # Send the proposal message with a photo path
    proposal_message = "✨ 𝐅𝐢𝐧𝐚𝐥𝐥𝐲 𝐭𝐡𝐞 𝐭𝐢𝐦𝐞 𝐡𝐚𝐬 𝐜𝐨𝐦𝐞 ✨"
    photo_path = 'https://graph.org/file/deda08aefd8c0e1540fcd.jpg'  # Replace with your photo path
    await update.message.reply_photo(photo=photo_path, caption=proposal_message)

    await asyncio.sleep(2)  # 2-second delay

    # Send the proposal text
    await update.message.reply_text("𝐏𝐫𝐨𝐩𝐨𝐬𝐞𝐢𝐧𝐠 𝐡𝐞𝐫 💍")

    await asyncio.sleep(2)  # 2-second delay

    # Generate a random result (60% chance of rejection, 40% chance of acceptance)
    if random.random() < 0.6:
        rejection_message = "𝐒𝐡𝐞 𝐬𝐥𝐚𝐩𝐩𝐞𝐝 𝐲𝐨𝐮 𝐚𝐧𝐝 𝐫𝐮𝐧 𝐚𝐰𝐚𝐲😂"
        rejection_photo_path = 'https://graph.org/file/3e392dc74f4b428828664.jpg'  # Replace with rejection photo path
        await update.message.reply_photo(photo=rejection_photo_path, caption=rejection_message)
    else:
        await update.message.reply_text("Congratulations! She accepted you.")

    # Update last propose time
    last_propose_times[user_id] = datetime.now()

# Add the CommandHandler to the application
application.add_handler(CommandHandler("propose", propose, block=False))

application.add_handler(CommandHandler("sbet", sbet, block=False))
application.add_handler(CommandHandler("bonus", daily_reward, block=False))
application.add_handler(CommandHandler("wallet", balance, block=False))
application.add_handler(CommandHandler("spay", pay, block=False))
application.add_handler(CommandHandler("tops", mtop, block=False))

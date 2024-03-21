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
        balance_message = f"𝗬𝗼𝘂𝗿 𝗰𝘂𝗿𝗿𝗲𝗻𝘁 𝗯𝗮𝗹𝗮𝗻𝗰𝗲 𝗶𝘀: ꜩ{balance_amount}"
    else:
        balance_message = "𝗚𝗮𝗿𝗯 𝘀𝗼𝗺𝗲 𝗰𝗮𝗿𝘀 𝗳𝗶𝗿𝘀𝘁."

    await update.message.reply_text(balance_message)

async def pay(update, context):
    sender_id = update.effective_user.id

    # Check if the command was a reply
    if not update.message.reply_to_message:
        await update.message.reply_text("𝗣𝗹𝗲𝗮𝘀𝗲 𝗿𝗲𝗽𝗹𝘆 𝘁𝗼 𝗮 𝘂𝘀𝗲𝗿 𝘁𝗼 /pay.")
        return

    # Extract the recipient's user ID
    recipient_id = update.message.reply_to_message.from_user.id

    # Prevent user from paying themselves
    if sender_id == recipient_id:
        await update.message.reply_text("𝗬𝗼𝘂 𝗰𝗮𝗻'𝘁 𝗽𝗮𝘆 𝘆𝗼𝘂𝗿𝘀𝗲𝗹𝗳.")
        return

    # Parse the amount from the command
    try:
        amount = int(context.args[0])
        if amount <= 0:
            raise ValueError("𝗔𝗺𝗼𝘂𝗻𝘁 𝗺𝘂𝘀𝘁 𝗯𝗲 𝗴𝗿𝗲𝗮𝘁𝗲𝗿 𝘁𝗵𝗮𝗻 𝘇𝗲𝗿𝗼.")
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
        f"𝗣𝗮𝘆𝗺𝗲𝗻𝘁 𝗦𝘂𝗰𝗰𝗲𝘀𝘀𝗳𝘂𝗹! 𝗬𝗼𝘂 𝗣𝗮𝗶𝗱 {amount} 𝗧𝗼𝗸𝗲𝗻𝘀 𝘁𝗼 {update.message.reply_to_message.from_user.username}. "
    )


async def mtop(update, context):
    # Retrieve the top 10 users with the highest balance
    top_users = await user_collection.find({}, projection={'id': 1, 'first_name': 1, 'last_name': 1, 'balance': 1}).sort('balance', -1).limit(10).to_list(10)

    # Create a message with the top users
    top_users_message = "𝗧𝗼𝗽 𝟭𝟬 𝗨𝘀𝗲𝗿𝘀 𝗪𝗶𝘁𝗵 𝗛𝗶𝗴𝗵𝗲𝘀𝘁 𝗧𝗼𝗸𝗲𝗻𝘀\n\n"
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
            await update.message.reply_text(f"𝗬𝗼𝘂 𝗮𝗹𝗿𝗲𝗮𝗱𝘆 𝗰𝗹𝗮𝗶𝗺𝗲𝗱 𝘆𝗼𝘂𝗿 𝘁𝗼𝗱𝗮𝘆'𝘀 𝗿𝗲𝘄𝗮𝗿𝗱. 𝗖𝗼𝗺𝗲 𝗯𝗮𝗰𝗸 𝗧𝗼𝗺𝗼𝗿𝗿𝗼𝘄!\n𝗧𝗶𝗺𝗲 𝗨𝗻𝘁𝗶𝗹 𝗡𝗲𝘅𝘁 𝗖𝗹𝗮𝗶𝗺: `{formatted_time_until_next_claim}`.")
            return

    await user_collection.update_one(
        {'id': user_id},
        {'$inc': {'balance': 50000}, '$set': {'last_daily_reward': datetime.utcnow()}}
    )

    await update.message.reply_text("𝗖𝗼𝗻𝗴𝗿𝗮𝘁𝘂𝗹𝗮𝘁𝗶𝗼𝗻𝘀! 𝗬𝗼𝘂 𝗰𝗹𝗮𝗶𝗺𝗲𝗱 𝟱𝟬𝟬𝟬𝟬 𝗧𝗼𝗸𝗲𝗻𝘀")


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
        await update.message.reply_text("Use /bet <amount>")
        return
    user_id = update.effective_user.id
    user_balance = await user_collection.find_one({'id': user_id}, projection={'balance': 1})

    if not user_balance or user_balance.get('balance', 0) < amount:
        await update.message.reply_text("𝗜𝗻𝘀𝘂𝗳𝗳𝗶𝗰𝗶𝗲𝗻𝘁 𝗯𝗮𝗹𝗮𝗻𝗰𝗲 𝘁𝗼 𝗺𝗮𝗸𝗲 𝘁𝗵𝗲 𝗯𝗲𝘁.")
        return
    if random.random() < 0.4:
        won_amount = 2 * amount
        await user_collection.update_one({'id': user_id}, {'$inc': {'balance': won_amount + amount}})
        updated_balance = user_balance.get('balance', 0) + won_amount
        await update.message.reply_text(
            f"𝗖𝗼𝗻𝗴𝗿𝗮𝘁𝘂𝗹𝗮𝘁𝗶𝗼𝗻𝘀 𝘆𝗼𝘂 𝘄𝗼𝗻 {won_amount} coins./n𝗬𝗼𝘂𝗿 𝗻𝗲𝘄 𝗯𝗮𝗹𝗮𝗻𝗰𝗲 𝗶𝘀 {updated_balance}."
        )
    else:
        await user_collection.update_one({'id': user_id}, {'$inc': {'balance': -amount}})
        updated_balance = user_balance.get('balance', 0) - amount
        await update.message.reply_text(
            f"𝗕𝗲𝘁𝘁𝗲𝗿 𝗹𝘂𝗰𝗸 𝗻𝗲𝘅𝘁 𝘁𝗶𝗺𝗲 𝘆𝗼𝘂 𝗹𝗼𝘀𝘁{amount} coins./n𝗬𝗼𝘂𝗿 𝗻𝗲𝘄 𝗯𝗮𝗹𝗮𝗻𝗰𝗲 𝗶𝘀 {updated_balance}."
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
        await update.message.reply_text("𝗬𝗼𝘂 𝗻𝗲𝗲𝗱 𝗮𝘁 𝗹𝗲𝗮𝘀𝘁 𝟮𝟬𝟬𝟬𝟬 𝘁𝗼𝗸𝗲𝗻𝘀 𝘁𝗼 𝗿𝗮𝗰𝗲.")
        return

    # Check last propose time and cooldown
    last_propose_time = last_propose_times.get(user_id)
    if last_propose_time:
        time_since_last_propose = datetime.now() - last_propose_time
        if time_since_last_propose < timedelta(minutes=5):
            remaining_cooldown = timedelta(minutes=5) - time_since_last_propose
            remaining_cooldown_minutes = remaining_cooldown.total_seconds() // 60
            remaining_cooldown_seconds = remaining_cooldown.total_seconds() % 60
            await update.message.reply_text(f"𝗖𝗼𝗼𝗹𝗱𝗼𝘄𝗻! 𝗣𝗹𝗲𝗮𝘀𝗲 𝘄𝗮𝗶𝘁 {int(remaining_cooldown_minutes)}m {int(remaining_cooldown_seconds)}s 𝗯𝗲𝗳𝗼𝗿𝗲 𝗿𝗮𝗰𝗶𝗻𝗴 𝗮𝗴𝗮𝗶𝗻.")
            return

    # Deduct the propose fee of 10000 tokens
    await user_collection.update_one({'id': user_id}, {'$inc': {'balance': -10000}})

    # Send the proposal message with a photo path
    proposal_message = "𝗥𝗮𝗰𝗲 𝗶𝘀 𝗴𝗼𝗶𝗻𝗴 𝘁𝗼 𝗯𝗲 𝘀𝘁𝗮𝗿𝘁"
    photo_path = 'https://graph.org/file/deda08aefd8c0e1540fcd.jpg'  # Replace with your photo path
    await update.message.reply_photo(photo=photo_path, caption=proposal_message)

    await asyncio.sleep(2)  # 2-second delay

    # Send the proposal text
    await update.message.reply_text("𝗥𝗮𝗰𝗲 𝗵𝗮𝘀 𝘀𝘁𝗮𝗿𝘁𝗲𝗱 ")

    await asyncio.sleep(2)  # 2-second delay

    # Generate a random result (60% chance of rejection, 40% chance of acceptance)
    if random.random() < 0.6:
        rejection_message = "𝗕𝗲𝘁𝘁𝗲𝗿 𝗹𝘂𝗰𝗸 𝗻𝗲𝘅𝘁 𝘁𝗶𝗺𝗲,𝗬𝗼𝘂 𝗹𝗼𝘀𝘁 𝘁𝗵𝗲 𝗿𝗮𝗰𝗲"
        rejection_photo_path = 'https://graph.org/file/3e392dc74f4b428828664.jpg'  # Replace with rejection photo path
        await update.message.reply_photo(photo=rejection_photo_path, caption=rejection_message)
    else:
        await update.message.reply_text("𝗖𝗼𝗻𝗴𝗿𝗮𝘁𝘂𝗹𝗮𝘁𝗶𝗼𝗻𝘀! 𝗬𝗼𝘂 𝘄𝗼𝗻 𝘁𝗵𝗲 𝗿𝗮𝗰𝗲.")

    # Update last propose time
    last_propose_times[user_id] = datetime.now()

# Add the CommandHandler to the application
application.add_handler(CommandHandler("propose", propose, block=False))

application.add_handler(CommandHandler("bet", sbet, block=False))
application.add_handler(CommandHandler("bonus", daily_reward, block=False))
application.add_handler(CommandHandler("bal", balance, block=False))
application.add_handler(CommandHandler("pay", pay, block=False))
application.add_handler(CommandHandler("tops", mtop, block=False))
from telegram.ext import CommandHandler
from shivu import application, user_collection
from telegram import Update
from datetime import datetime, timedelta
import asyncio

# Dictionary to store last payment times
last_payment_times = {}
from shivu import collection, user_collection, application
from telegram.ext import CallbackContext
import random 
from shivu import shivuu as app

# URL for default profile image
default_profile_image = "https://telegra.ph/file/342e5da6524b7ed1524c3.jpg"

# Formatting function for large numbers
def format_number(num):
    if num >= 10**15:
        return f"{num // 10**15}q"
    elif num >= 10**12:
        return f"{num // 10**12}t"
    elif num >= 10**9:
        return f"{num // 10**9}b"
    elif num >= 10**6:
        return f"{num // 10**6}m"
    elif num >= 10**3:
        return f"{num // 10**3}k"
    else:
        return str(num)

async def balance(update, context):
    user_id = update.effective_user.id

    user_data = await user_collection.find_one({'id': user_id}, projection={'balance': 1, 'characters': 1})
    profile = update.effective_user

    if user_data:
        user_balance = user_data.get('balance', 0)
        characters = user_data.get('characters', [])

        coins_rank = await user_collection.count_documents({'balance': {'$gt': user_balance}}) + 1

        total_characters = len(characters)
        all_characters = await collection.find({}).to_list(length=None)
        total_database_characters = len(all_characters)

        balance_info = (
            f"\n\n💰 ᴄᴏɪɴꜱ: Ŧ{format_number(user_balance)}"
            f"\n🏅 ᴄᴏɪɴꜱ ʀᴀɴᴋ: {coins_rank}"
            f"\n🎭 ᴄʜᴀʀᴀᴄᴛᴇʀꜱ: {total_characters}/{total_database_characters}"
        )

        balance_message = (
            f"ʏᴏᴜʀ ʙᴀʟᴀɴᴄᴇ ɪɴғᴏ\n"
            f"===================\n"
            f"👤 ɴᴀᴍᴇ: {profile.full_name}\n"
            f"🆔 ɪᴅ: {profile.id}"
            f"{balance_info}"
            f"\n==================="
        )

        photos = await context.bot.get_user_profile_photos(user_id)
        if photos.photos:
            photo_file = photos.photos[0][-1].file_id
            await update.message.reply_photo(photo=photo_file, caption=balance_message)
        else:
            await update.message.reply_photo(default_profile_image, caption=balance_message)
    else:
        balance_message = "Claim your bonus first using /bonus and /wbonus"
        await update.message.reply_text(balance_message)

async def pay(update, context):
    sender_id = update.effective_user.id

    if not update.message.reply_to_message:
        await update.message.reply_text("⚠️ Please reply to a user to /pay.")
        return

    recipient_id = update.message.reply_to_message.from_user.id

    if sender_id == recipient_id:
        await update.message.reply_text("⚠️ You can't pay yourself.")
        return

    try:
        amount_str = context.args[0]
        if "+" in amount_str:
            base_amount_str, additional_str = amount_str.split("+")
            base_amount = int(base_amount_str)
            additional = int(additional_str)
            amount = base_amount * (10 ** len(additional_str)) + additional
        else:
            amount = int(amount_str)
        if amount <= 0:
            raise ValueError("Amount must be greater than zero.")
    except (IndexError, ValueError):
        await update.message.reply_text("⚠️ Use /pay <amount>")
        return

    sender_balance = await user_collection.find_one({'id': sender_id}, projection={'balance': 1})
    if not sender_balance or sender_balance.get('balance', 0) < amount:
        await update.message.reply_text("❌ Insufficient balance to make the payment.")
        return

    last_payment_time = last_payment_times.get(sender_id)
    if last_payment_time:
        time_since_last_payment = datetime.now() - last_payment_time
        if time_since_last_payment < timedelta(minutes=10):
            cooldown_time = timedelta(minutes=10) - time_since_last_payment
            formatted_cooldown = format_timedelta(cooldown_time)
            await update.message.reply_text(f"⌛ Cooldown! You can pay again in `{formatted_cooldown}`.")
            return

    await user_collection.update_one({'id': sender_id}, {'$inc': {'balance': -amount}})
    await user_collection.update_one({'id': recipient_id}, {'$inc': {'balance': amount}}, upsert=True)

    last_payment_times[sender_id] = datetime.now()

    await update.message.reply_text(
        f"✅ Payment Successful! You Paid Ŧ{amount} Tokens to {update.message.reply_to_message.from_user.username}. "
    )

async def daily_reward(update, context):
    user_id = update.effective_user.id

    user_data = await user_collection.find_one({'id': user_id}, projection={'last_daily_reward': 1, 'balance': 1})

    if user_data:
        last_claimed_date = user_data.get('last_daily_reward')

        if last_claimed_date and last_claimed_date.date() == datetime.utcnow().date():
            time_since_last_claim = datetime.utcnow() - last_claimed_date
            time_until_next_claim = timedelta(days=1) - time_since_last_claim
            formatted_time_until_next_claim = format_timedelta(time_until_next_claim)
            await update.message.reply_text(f"⏳ You already claimed your today's reward. Come back Tomorrow!\n🕒 Time Until Next Claim: `{formatted_time_until_next_claim}`.")
            return

    await user_collection.update_one(
        {'id': user_id},
        {'$inc': {'balance': 50000}, '$set': {'last_daily_reward': datetime.utcnow()}},
        upsert=True
    )

    await update.message.reply_text("🎉 Congratulations! You claimed Ŧ50000 Tokens")

def format_timedelta(td: timedelta) -> str:
    seconds = td.total_seconds()
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return "{:02}h {:02}m {:02}s".format(int(hours), int(minutes), int(seconds))

async def weekly(update, context):
    user_id = update.effective_user.id

    user_data = await user_collection.find_one({'id': user_id}, projection={'last_weekly_bonus': 1, 'balance': 1})

    if user_data:
        last_claimed_date = user_data.get('last_weekly_bonus')

        if last_claimed_date and last_claimed_date.date() >= (datetime.utcnow() - timedelta(days=7)).date():
            time_since_last_claim = datetime.utcnow() - last_claimed_date
            time_until_next_claim = timedelta(days=7) - time_since_last_claim
            formatted_time_until_next_claim = format_timedelta(time_until_next_claim)
            await update.message.reply_text(f"⏳ You already claimed your weekly bonus for this week. Come back next week!\n🕒 Time Until Next Claim: `{formatted_time_until_next_claim}`.")
            return

    await user_collection.update_one(
        {'id': user_id},
        {'$inc': {'balance': 100000}, '$set': {'last_weekly_bonus': datetime.utcnow()}},
        upsert=True
    )

    await update.message.reply_text("🎉 Congratulations! You claimed Ŧ100000 Tokens as your weekly bonus.")

application.add_handler(CommandHandler("bonus", daily_reward, block=False))
application.add_handler(CommandHandler("wbonus", weekly, block=False))
application.add_handler(CommandHandler("bal", balance, block=False))
application.add_handler(CommandHandler("pay", pay, block=False))
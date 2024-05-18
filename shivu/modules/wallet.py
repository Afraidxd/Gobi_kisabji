from telegram.ext import CommandHandler
from shivu import application, user_collection
from telegram import Update
from datetime import datetime, timedelta
import asyncio
import requests
import io
from itertools import groupby
from telegram.ext import CommandHandler, CallbackContext
# Dictionary to store last payment times
last_payment_times = {}

async def balance(update, context):
    user_id = update.effective_user.id

    user_data = await user_collection.find_one({'id': user_id}, projection={'balance': 1, 'bank_balance': 1, 'gems': 1, 'characters': 1, 'profile_media': 1, 'gender': 1})

    profile = update.effective_user

    if user_data:
        user_balance = user_data.get('balance', 0)
        bank_balance = user_data.get('bank_balance', 0)
        gems = user_data.get('gems', 0)
        characters = user_data.get('characters', [])
        profile_media = user_data.get('profile_media')
        gender = user_data.get('gender')

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

        coins_rank = await user_collection.count_documents({'balance': {'$gt': user_balance}}) + 1
        total_characters = len(characters)
        
        # Counting the total number of characters for the specific user
        total_database_characters = await user_collection.count_documents({'characters': {'$exists': True}})

        gender_icon = '👦🏻' if gender == 'male' else '👧🏻' if gender == 'female' else '🏳️‍🌈'

        balance_message = (
            f"\t\t 𝐃𝐫𝐢𝐯𝐞𝐫 𝐋𝐢𝐜𝐞𝐧𝐜𝐞\n\n"
            f"ɴᴀᴍᴇ: {profile.full_name} [{gender_icon}]\n"
            f"ɪᴅ: <code>{profile.id}</code>\n\n"
            f"ᴄᴏɪɴꜱ: Ŧ<code>{format_number(user_balance)}</code> coins\n"
            f"ʙᴀɴᴋ: Ŧ<code>{format_number(bank_balance)}</code> coins\n"
            f"ᴄᴏɪɴꜱ ʀᴀɴᴋ: <code>{coins_rank}</code>\n"
            f"ᴄʜᴀʀᴀᴄᴛᴇʀꜱ: <code>{total_characters}</code>/<code>{total_database_characters}</code>\n"
        )

        photo_file = profile_media or (await context.bot.get_user_profile_photos(user_id)).photos[0][-1].file_id if (await context.bot.get_user_profile_photos(user_id)).photos else None

        if photo_file:
            await update.message.reply_photo(photo=photo_file, caption=balance_message, parse_mode='HTML')
        else:
            await update.message.reply_photo("https://graph.org/file/7ff03ebae9abc95c94a16.jpg", caption=balance_message, parse_mode='HTML')
    else:
        await update.message.reply_text("Claim bonus first using /bonus and /wbonus")

async def pay(update, context):
    sender_id = update.effective_user.id

    if not update.message.reply_to_message:
        await update.message.reply_text("Please reply to a user to /pay.")
        return

    recipient_id = update.message.reply_to_message.from_user.id

    if sender_id == recipient_id:
        await update.message.reply_text("You can't pay yourself.")
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
        await update.message.reply_text("Use /pay <amount>")
        return

    sender_balance = await user_collection.find_one({'id': sender_id}, projection={'balance': 1})
    if not sender_balance or sender_balance.get('balance', 0) < amount:
        await update.message.reply_text("Insufficient balance to make the payment.")
        return

    last_payment_time = last_payment_times.get(sender_id)
    if last_payment_time:
        time_since_last_payment = datetime.now() - last_payment_time
        if time_since_last_payment < timedelta(minutes=10):
            cooldown_time = timedelta(minutes=10) - time_since_last_payment
            formatted_cooldown = format_timedelta(cooldown_time)
            await update.message.reply_text(f"Cooldown! You can pay again in `{formatted_cooldown}`.")
            return

    await user_collection.update_one({'id': sender_id}, {'$inc': {'balance': -amount}})
    await user_collection.update_one({'id': recipient_id}, {'$inc': {'balance': amount}}, upsert=True)

    last_payment_times[sender_id] = datetime.now()

    await update.message.reply_text(
        f"Payment Successful! You Paid Ŧ{amount} Tokens to {update.message.reply_to_message.from_user.username}."
    )


async def mtop(update: Update, context: CallbackContext):
    top_users = await user_collection.find({}, {'id': 1, 'first_name': 1, 'last_name': 1, 'balance': 1}).sort('balance', -1).limit(10).to_list(10)

    top_users_message = """
Top 10 Token Users:
───────────────────
"""

    for i, user in enumerate(top_users, start=1):
        first_name = user.get('first_name', 'Unknown')
        user_id = user.get('id', 'Unknown')

        if user_id != 'Unknown':
            user_link = f'<a href="tg://user?id={user_id}">{first_name}</a>'
        else:
            user_link = first_name

        top_users_message += f"{i}. {user_link} - Ŧ{user.get('balance', 0):,}\n"

    top_users_message += """
───────────────────
"""

    photo_url = "https://telegra.ph/file/3474a548e37ab8f0604e8.jpg"
    photo_response = requests.get(photo_url)

    if photo_response.status_code == 200:
        photo_data = io.BytesIO(photo_response.content)
        await update.message.reply_photo(photo=photo_data, caption=top_users_message, parse_mode='Markdown')
    else:
        await update.message.reply_text("Failed to download photo")

application.add_handler(CommandHandler("mtop", mtop))

async def daily_reward(update, context):
    user_id = update.effective_user.id

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

    await update.message.reply_text("Congratulations! You claimed Ŧ50000 Tokens")

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
            await update.message.reply_text(f"You already claimed your weekly bonus for this week. Come back next week!\nTime Until Next Claim: `{formatted_time_until_next_claim}`.")
            return

    await user_collection.update_one(
        {'id': user_id},
        {'$inc': {'balance': 100000}, '$set': {'last_weekly_bonus': datetime.utcnow()}},
        upsert=True
    )

    await update.message.reply_text("Congratulations! You claimed Ŧ100000 Tokens as your weekly bonus.")

async def set_profile_media(update, context):
    if update.message.reply_to_message and update.message.reply_to_message.photo:
        file_id = update.message.reply_to_message.photo[-1].file_id
        user_id = update.effective_user.id
        await user_collection.update_one({'id': user_id}, {'$set': {'profile_media': file_id}})
        await update.message.reply_text("Profile media set successfully!")
    else:
        await update.message.reply_text("Please reply to a message containing a photo to set it as your profile media.")

async def delete_profile_media(update, context):
    user_id = update.effective_user.id
    await user_collection.update_one({'id': user_id}, {'$unset': {'profile_media': 1}})
    await update.message.reply_text("Profile media deleted successfully!")

application.add_handler(CommandHandler("setprofilemedia", set_profile_media))
application.add_handler(CommandHandler("deleteprofilemedia", delete_profile_media))
application.add_handler(CommandHandler("bonus", daily_reward, block=False))
application.add_handler(CommandHandler("wbonus", weekly, block=False))
application.add_handler(CommandHandler("sprofile", balance, block=False))
application.add_handler(CommandHandler("spay", pay, block=False))
application.add_handler(CommandHandler("tops", mtop, block=False))

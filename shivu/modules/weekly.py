from telegram.ext import CommandHandler
from shivu import application, user_collection
from telegram import Update
from datetime import datetime, timedelta
import asyncio
# Dictionary to store last payment times
last_payment_times = {}

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

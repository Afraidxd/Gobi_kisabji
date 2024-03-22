from telegram.ext import CommandHandler
from shivu import application, user_collection
from telegram import Update
from datetime import datetime, timedelta

# Dictionary to store last payment times
last_payment_times = {}

async def weekly_reward(update, context):
    user_id = update.effective_user.id

    # Check if the user already claimed the weekly reward this week
    user_data = await user_collection.find_one({'id': user_id}, projection={'last_weekly_reward': 1, 'balance': 1})

    if user_data:
        last_claimed_date = user_data.get('last_weekly_reward')

        if last_claimed_date:
            time_since_last_claim = datetime.utcnow() - last_claimed_date
            if time_since_last_claim < timedelta(days=7):
                remaining_time = timedelta(days=7) - time_since_last_claim
                await update.message.reply_text(f"You have already claimed your weekly reward. Please come back in {format_timedelta(remaining_time)}.")
                return

    await user_collection.update_one(
        {'id': user_id},
        {'$inc': {'balance': 100000}, '$set': {'last_weekly_reward': datetime.utcnow()}}
    )

    await update.message.reply_text("Congratulations! You claimed 100,000 Tokens as your weekly reward.")

def format_timedelta(td: timedelta) -> str:
    days = td.days
    hours, remainder = divmod(td.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    
    if days > 0:
        return f"{days} day{'s' if days > 1 else ''} {hours:02}h {minutes:02}m {seconds:02}s"
    else:
        return f"{hours:02}h {minutes:02}m {seconds:02}s"


application.add_handler(CommandHandler("wbonus", weekly_reward, block=False))
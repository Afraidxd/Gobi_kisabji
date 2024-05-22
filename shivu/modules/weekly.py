from telegram.ext import CommandHandler
from shivu import application, user_collection
from telegram import Update
from datetime import datetime, timedelta
import random

DAILY_MAX_EARNINGS = 1_000_000_000_000_000
TOTAL_MAX_EARNINGS = 500_000_000_000_000_000
MAX_BETS = 50
COOLDOWN_PERIOD = timedelta(minutes=30)

async def sbet(update, context):
    user_id = update.effective_user.id
    current_time = datetime.utcnow()

    # Fetch user data from the database, specific to this betting module
    user_data = await user_collection.find_one(
        {'id': user_id},
        projection={'balance': 1, 'module_earnings': 1, 'module_bets': 1, 'module_last_bet_time': 1, 'module_daily_earnings': 1, 'module_last_reset': 1}
    )

    if not user_data:
        # Initialize user data if not found
        user_data = {
            'id': user_id,
            'balance': 0,
            'module_earnings': 0,
            'module_bets': 0,
            'module_last_bet_time': datetime.min,
            'module_daily_earnings': 0,
            'module_last_reset': current_time
        }
        await user_collection.insert_one(user_data)

    # Reset daily earnings at midnight UTC
    if user_data['module_last_reset'].date() < current_time.date():
        user_data['module_daily_earnings'] = 0
        await user_collection.update_one({'id': user_id}, {'$set': {'module_daily_earnings': 0, 'module_last_reset': current_time}})

    # Check if the user is in cooldown period
    if user_data['module_bets'] >= MAX_BETS:
        remaining_cooldown = (user_data['module_last_bet_time'] + COOLDOWN_PERIOD) - current_time
        if remaining_cooldown > timedelta(0):
            await update.message.reply_text(
                f"You have reached your bet limit. Please wait {remaining_cooldown} before betting again.\n"
                f"Remaining bets: 0"
            )
            return
        else:
            # Reset the bet count after cooldown
            await user_collection.update_one({'id': user_id}, {'$set': {'module_bets': 0}})
            user_data['module_bets'] = 0

    # Parse the amount from the command
    try:
        amount = int(context.args[0])
        if amount <= 0:
            raise ValueError("Amount must be greater than zero.")
    except (IndexError, ValueError):
        await update.message.reply_text("Use /bet <amount>")
        return

    # Check user's balance
    if user_data.get('balance', 0) < amount:
        await update.message.reply_text("Insufficient balance to make the bet.")
        return

    # Check if the user has reached the total earning limit for this module
    if user_data.get('module_earnings', 0) >= TOTAL_MAX_EARNINGS:
        await update.message.reply_text("You have reached your total earning limit. Please use your balance for betting again.")
        return

    # Check if the user has reached the daily earning limit for this module
    if user_data.get('module_daily_earnings', 0) >= DAILY_MAX_EARNINGS:
        await update.message.reply_text("You have reached your daily earning limit. Please come back tomorrow to bet again.")
        return

    # Perform the bet
    if random.random() < 0.5:
        won_amount = 2 * amount
        potential_daily_earnings = user_data.get('module_daily_earnings', 0) + won_amount
        potential_total_earnings = user_data.get('module_earnings', 0) + won_amount
        
        # Ensure earnings do not exceed limits
        if potential_daily_earnings > DAILY_MAX_EARNINGS:
            won_amount = DAILY_MAX_EARNINGS - user_data.get('module_daily_earnings', 0)
        if potential_total_earnings > TOTAL_MAX_EARNINGS:
            won_amount = TOTAL_MAX_EARNINGS - user_data.get('module_earnings', 0)
        
        await user_collection.update_one(
            {'id': user_id},
            {
                '$inc': {
                    'balance': won_amount,
                    'module_earnings': won_amount,
                    'module_daily_earnings': won_amount,
                    'module_bets': 1
                },
                '$set': {'module_last_bet_time': current_time}
            }
        )
        updated_balance = user_data.get('balance', 0) + won_amount
        remaining_bets = MAX_BETS - (user_data['module_bets'] + 1)
        await update.message.reply_text(
            f"🎉 Congratulations! You won {won_amount}!\n\n"
            f"💰 Your updated balance is {updated_balance}.\n"
            f"🕒 Remaining bets: {remaining_bets}"
        )
    else:
        await user_collection.update_one(
            {'id': user_id},
            {
                '$inc': {
                    'balance': -amount,
                    'module_bets': 1
                },
                '$set': {'module_last_bet_time': current_time}
            }
        )
        updated_balance = user_data.get('balance', 0) - amount
        remaining_bets = MAX_BETS - (user_data['module_bets'] + 1)
        await update.message.reply_text(
            f"❌ You lost {amount}.\n\n"
            f"💰 Your updated balance is {updated_balance}.\n"
            f"🕒 Remaining bets: {remaining_bets}"
        )

application.add_handler(CommandHandler("bet", sbet, block=False))
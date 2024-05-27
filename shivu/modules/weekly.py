from telegram.ext import CommandHandler
from shivu import application, user_collection
from telegram import Update
from datetime import datetime, timedelta
import random
from . import add_balance as add, deduct_balance as deduct, show_balance as show
MAX_BETS = 50
COOLDOWN_PERIOD = timedelta(minutes=30)

def format_timedelta(td):
    minutes, seconds = divmod(td.seconds, 60)
    return f"{minutes} minute(s) and {seconds} second(s)"

async def sbet(update, context):
    user_id = update.effective_user.id
    current_time = datetime.utcnow()

    # Fetch user data from the database, specific to this betting module
    user_data = await user_collection.find_one(
        {'id': user_id},
        projection={'balance': 1, 'module_earnings': 1, 'module_bets': 1, 'module_last_bet_time': 1, 'module_daily_earnings': 1, 'module_last_reset': 1}
    )

    # Initialize missing fields if necessary
    if not user_data:
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
    else:
        if 'module_earnings' not in user_data:
            user_data['module_earnings'] = 0
        if 'module_bets' not in user_data:
            user_data['module_bets'] = 0
        if 'module_last_bet_time' not in user_data:
            user_data['module_last_bet_time'] = datetime.min
        if 'module_daily_earnings' not in user_data:
            user_data['module_daily_earnings'] = 0
        if 'module_last_reset' not in user_data:
            user_data['module_last_reset'] = current_time

    # Reset daily earnings at midnight UTC
    if user_data['module_last_reset'].date() < current_time.date():
        user_data['module_daily_earnings'] = 0
        await user_collection.update_one(
            {'id': user_id}, 
            {'$set': {'module_daily_earnings': 0, 'module_last_reset': current_time}}
        )

    # Check if the user is in cooldown period
    if user_data['module_bets'] >= MAX_BETS:
        remaining_cooldown = (user_data['module_last_bet_time'] + COOLDOWN_PERIOD) - current_time
        if remaining_cooldown > timedelta(0):
            formatted_time = format_timedelta(remaining_cooldown)
            await update.message.reply_text(
                f"ʏᴏᴜ ʜᴀᴠᴇ ʀᴇᴀᴄʜᴇᴅ ʏᴏᴜʀ ʙᴇᴛ ʟɪᴍɪᴛ. ᴘʟᴇᴀsᴇ ᴡᴀɪᴛ {formatted_time} ʙᴇғᴏʀᴇ ʙᴇᴛᴛɪɴɢ ᴀɢᴀɪɴ.\n\n"
                f"Remaining bets: {MAX_BETS - user_data['module_bets']}"
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
            raise ValueError("ᴀᴍᴏᴜɴᴛ ᴍᴜsᴛ ʙᴇ ɢʀᴇᴀᴛᴇʀ ᴛʜᴀɴ ᴢᴇʀᴏ.")
    except (IndexError, ValueError):
        await update.message.reply_text("Use /bet [ᴀᴍᴏᴜɴᴛ]")
        return

    # Adjust bet amount based on profit percentage
    if 'last_profit' in user_data:
        profit_percentage = user_data['last_profit']
        adjusted_amount = int(amount * (1 + profit_percentage))
    else:
        adjusted_amount = amount

    # Check user's balance
    balance = await show(user_id)
    if balance < adjusted_amount:
        await update.message.reply_text("ɪɴsᴜғғɪᴄɪᴇɴᴛ ʙᴀʟᴀɴᴄᴇ ᴛᴏ ᴍᴀᴋᴇ ᴛʜᴇ ʙᴇᴛ.")
        return

    # Perform the bet
    if random.random() < 0.5:
        won_amount = 2 * amount
        profit_percentage = (won_amount - amount) / amount
        await add(user_id, won_amount)
        await user_collection.update_one(
            {'id': user_id},
            {
                '$inc': {
                    'module_earnings': won_amount,
                    'module_daily_earnings': won_amount,
                    'module_bets': 1
                },
                '$set': {'module_last_bet_time': current_time, 'last_profit': profit_percentage}
            }
        )
        updated_balance = await show(user_id) + won_amount
        remaining_bets = MAX_BETS - (user_data['module_bets'] + 1)
        await update.message.reply_text(
            f"ᴄᴏɴɢʀᴀᴛᴜʟᴀᴛɪᴏɴs! ʏᴏᴜ ᴡᴏɴ {won_amount}!\n\n"
            f"ʏᴏᴜʀ ᴜᴘᴅᴀᴛᴇᴅ ʙᴀʟᴀɴᴄᴇ ɪs {updated_balance}.\n\n"
            f"ʀᴇᴍᴀɪɴɪɴɢ ʙᴇᴛs: {remaining_bets}"
        )
    else:
        await deduct(user_id, amount)
        await user_collection.update_one(
            {'id': user_id},
            {
                '$inc': {
                    'module_bets': 1
                },
                '$set': {'module_last_bet_time': current_time}
            }
        )
        updated_balance = await show(user_id) - amount
        remaining_bets = MAX_BETS - (user_data['module_bets'] + 1)
        await update.message.reply_text(
            f"ᴏᴏᴘs! ʏᴏᴜ ʟᴏsᴛ {amount}.\n\n"
            f"ʏᴏᴜʀ ᴜᴘᴅᴀᴛᴇᴅ ʙᴀʟᴀɴᴄᴇ ɪs: {updated_balance}.\n\n"
            f"ʀᴇᴍᴀɪɴɪɴɢ ʙᴇᴛs: {remaining_bets}"
        )

application.add_handler(CommandHandler("bet", sbet, block=False))

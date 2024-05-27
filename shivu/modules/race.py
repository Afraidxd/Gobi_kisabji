from shivu import user_collection, application

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext, CommandHandler, CallbackQueryHandler
import random
from datetime import datetime, timedelta
import asyncio
from telegram.error import Forbidden
from . import add_balance as add, show_balance as show, deduct_balance as deduct 

# Dictionary to store challenges and cooldown times
challenges = {}
last_race_time = {}

async def start_race_challenge(update: Update, context: CallbackContext):
    if update.message.chat.type not in ['group', 'supergroup']:
        await update.message.reply_text("This command can only be used in a group chat.")
        return

    # Check if the message is a reply
    if not update.message.reply_to_message:
        await update.message.reply_text("ᴘʟᴇᴀsᴇ ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴜsᴇʀ's ᴍᴇssᴀɢᴇ ᴛᴏ ᴄʜᴀʟʟᴇɴɢᴇ ᴛʜᴇᴍ ᴛᴏ ᴀ ʀᴀᴄᴇ.")
        return

    args = context.args
    if not args or not args[0].isdigit() or int(args[0]) <= 0:
        await update.message.reply_text("ᴜsᴀɢᴇ /ʀᴀᴄᴇ [ᴀᴍᴏᴜɴᴛ]")
        return

    amount = int(args[0])
    challenged_user_id = update.message.reply_to_message.from_user.id
    challenger_id = update.effective_user.id

    # Check if the user is trying to challenge themselves
    if challenged_user_id == challenger_id:
        await update.message.reply_text("ʏᴏᴜ ᴄᴀɴɴᴏᴛ ᴄʜᴀʟʟᴇɴɢᴇ ʏᴏᴜʀsᴇʟғ!")
        return

    # Check cooldown period
    current_time = datetime.now()
    cooldown_period = timedelta(minutes=10)
    if (challenger_id in last_race_time and current_time < last_race_time[challenger_id] + cooldown_period) or \
       (challenged_user_id in last_race_time and current_time < last_race_time[challenged_user_id] + cooldown_period):
        remaining_time_challenger = (last_race_time.get(challenger_id, current_time) + cooldown_period - current_time).seconds // 60
        remaining_time_challenged = (last_race_time.get(challenged_user_id, current_time) + cooldown_period - current_time).seconds // 60
        await update.message.reply_text(
            f"One of the users is in cooldown period. Please wait {max(remaining_time_challenger, remaining_time_challenged)} minutes before racing again."
        )
        return

    challenger_name = update.effective_user.first_name
    challenged_name = update.message.reply_to_message.from_user.first_name

    # Check balance of both users
    challenger_balance = await show(challenger_id)
    challenged_balance = await show(challenged_user_id)

    if not challenger_balance < amount:
        await update.message.reply_text("ʏᴏᴜ ᴅᴏ ɴᴏᴛ ʜᴀᴠᴇ ᴇɴᴏᴜɢʜ ᴛᴏᴋᴇɴs ᴛᴏ ᴄʜᴀʟʟᴇɴɢᴇ.")
        return

    if not challenged_balance or challenged_balance.get('balance', 0) < amount:
        await update.message.reply_text("ᴅᴏɴ'ᴛ ᴛᴀɢ ʙᴏᴛ ᴏʀ ᴘᴏᴏʀ ᴜsᴇʀ ʏᴏᴜ ɴɪɢɢᴀ!")
        return

    
    challenges[challenged_user_id] = {
        'challenger': challenger_id,
        'challenger_name': challenger_name,
        'challenged_name': challenged_name,
        'amount': amount,
        'timestamp': datetime.now(),
        'chat_id': update.message.chat_id,
        'message_id': update.message.message_id
    }

    # Notify the challenged user
    keyboard = [
        [
            InlineKeyboardButton("ᴀᴄᴄᴇᴘᴛ", callback_data=f"race_accept_{challenger_id}_{challenged_user_id}"),
            InlineKeyboardButton("ᴅᴇᴄʟɪɴᴇ", callback_data=f"race_decline_{challenger_id}_{challenged_user_id}")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_to_message.reply_text(
        f"ʏᴏᴜ ʜᴀᴠᴇ ʙᴇᴇɴ ᴄʜᴀʟʟᴇɴɢᴇᴅ ʙʏ {challenger_name} ᴛᴏ ᴀ ʀᴀᴄᴇ ғᴏʀ {amount} ᴛᴏᴋᴇɴs! ᴅᴏ ʏᴏᴜ ᴀᴄᴄᴇᴘᴛ?",
        reply_markup=reply_markup
    )

async def race_accept(update: Update, context: CallbackContext):
    query = update.callback_query
    challenged_user_id = update.effective_user.id

    callback_data = query.data.split('_')
    challenger_id = int(callback_data[2])

    if challenged_user_id not in challenges:
        await query.answer("ʏᴏᴜ ᴄᴀɴ'ᴛ ᴀᴄᴄᴇᴘᴛ ɪᴛ ᴏʀ ᴄʜᴀʟʟᴇɴɢᴇ ɴᴏᴛ ғᴏᴜɴᴅ!", show_alert=True)
        return

    if challenges[challenged_user_id]['challenger'] != challenger_id:
        await query.answer("ᴛʜɪs ᴄʜᴀʟʟᴇɴɢᴇ ɪs ɴᴏᴛ ғᴏʀ ʏᴏᴜ!", show_alert=True)
        return

    challenge_data = challenges[challenged_user_id]
    await start_race(query, context, challenger_id, challenged_user_id, challenge_data['amount'], challenge_data['challenger_name'], challenge_data['challenged_name'], challenge_data['chat_id'], challenge_data['message_id'])

async def start_race(query, context: CallbackContext, challenger_id: int, challenged_user_id: int, amount: int, challenger_name: str, challenged_name: str, chat_id: int, message_id: int):
    try:
        # Edit the original challenge message
        await query.edit_message_text(text="🏁 ᴛʜᴇ ʀᴀᴄᴇ ʜᴀs sᴛᴀʀᴛᴇᴅ! 🏁")
    except Forbidden as e:
        await context.bot.send_message(chat_id=chat_id, text="Unable to start the race due to a messaging error. Ensure both users have interacted with the bot.")
        return

    # Deduct tokens from both users
    await deduct(challenger_id}, amount)
    await deduct(challenged_user_id,  amount)

    # Race simulation
    await asyncio.sleep(2)  # 2-second delay

    # Determine the winner
    if random.random() < 0.5:
        winner_id = challenger_id
        loser_id = challenged_user_id
        winner_name = challenger_name
        loser_name = challenged_name
    else:
        winner_id = challenged_user_id
        loser_id = challenger_id
        winner_name = challenged_name
        loser_name = challenger_name

    reward = 2 * amount
    await add(winner_id, reward)

    result_message = (
        f"🎉 ᴄᴏɴɢʀᴀᴛᴜʟᴀᴛɪᴏɴs, [{winner_name}](tg://user?id={winner_id})! 🎉\n"
        f"ʏᴏᴜ ᴡᴏɴ ᴛʜᴇ ʀᴀᴄᴇ ᴀɴᴅ ᴇᴀʀɴᴇᴅ {reward} ᴛᴏᴋᴇɴs.\n\n"
        f"😢 ʙᴇᴛᴛᴇʀ ʟᴜᴄᴋ ɴᴇxᴛ ᴛɪᴍᴇ, [{loser_name}](tg://user?id={loser_id}). ʏᴏᴜ ʟᴏsᴛ ᴛʜᴇ ʀᴀᴄᴇ ᴀɴᴅ ᴛʜᴇ {amount} ᴛᴏᴋᴇɴs."
    )

    try:
        # Send the result message to the group chat as a reply to the original challenge message
        await context.bot.send_message(chat_id=chat_id, text=result_message, reply_to_message_id=message_id, parse_mode='Markdown')
    except Forbidden:
        pass  # Silently handle if the bot can't message one of the users

    # Clean up the challenge and update last race time
    del challenges[challenged_user_id]
    last_race_time[challenger_id] = datetime.now()
    last_race_time[challenged_user_id] = datetime.now()

async def race_decline(update: Update, context: CallbackContext):
    query = update.callback_query
    challenged_user_id = query.from_user.id

    callback_data = query.data.split('_')
    challenger_id = int(callback_data[2])

    if challenged_user_id in challenges and challenges[challenged_user_id]['challenger'] == challenger_id:
        await query.edit_message_text("Challenge declined.")
        del challenges[challenged_user_id]
    else:
        await query.answer("Challenge not found or already expired.", show_alert=True)

application.add_handler(CommandHandler("race", start_race_challenge))

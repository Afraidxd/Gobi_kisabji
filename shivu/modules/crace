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

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CommandHandler, CallbackQueryHandler

import random

async def crace(update, context):
    # Get the replied user's ID
    replied_user_id = update.message.reply_to_message.from_user.id
    
    # Check if the replied user exists and has a balance
    replied_user_balance = await user_collection.find_one({'id': replied_user_id}, projection={'balance': 1})
    
    if replied_user_balance:
        replied_user_balance_amount = replied_user_balance.get('balance', 0)
        
        if replied_user_balance_amount >= 10000:
            keyboard = [[InlineKeyboardButton("Yes", callback_data='crace_yes')],
                        [InlineKeyboardButton("No", callback_data='crace_no')]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text("Do you want to race?", reply_markup=reply_markup)
        else:
            await update.message.reply_text("Replied user must have a minimum balance of 10,000 coins to participate in the race.")
    else:
        await update.message.reply_text("Replied user not found in the database.")

async def crace_callback(update, context):
    query = update.callback_query
    user_id = query.from_user.id
    
    if query.data == 'crace_yes':
        # Deduct the race amount from both users' balances
        replied_user_id = query.message.reply_to_message.from_user.id
        race_amount = random.randint(10000, 100000)  # Random race amount between 10,000 and 100,000 coins
        
        await user_collection.update_one({'id': user_id}, {'$inc': {'balance': -race_amount}})
        await user_collection.update_one({'id': replied_user_id}, {'$inc': {'balance': -race_amount}})
        
        # Choose a winner randomly
        winner = random.choice([user_id, replied_user_id])
        
        # Transfer all coins to the winner
        await user_collection.update_one({'id': winner}, {'$inc': {'balance': 2 * race_amount}})
        
        await query.answer()
        await query.message.reply_text(f"User {winner} wins the race! Congratulations!")
    else:
        await query.answer()
        await query.message.reply_text("Race cancelled.")

# Add a command handler for /crace and a message handler for handling inline keyboard callbacks
crace_handler = CommandHandler('crace', crace)
dispatcher.add_handler(crace_handler)

crace_callback_handler = CallbackQueryHandler(crace_callback, pattern='^crace_')
dispatcher.add_handler(crace_callback_handler)



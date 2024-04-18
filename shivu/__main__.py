from typing import List, Dict
import importlib
import time
import random
import re
import asyncio
from html import escape
import random 

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram import Update
from telegram.ext import CommandHandler, CallbackContext, MessageHandler, CallbackQueryHandler, filters

from shivu import collection, top_global_groups_collection, group_user_totals_collection, user_collection, user_totals_collection, shivuu
from shivu import application, LOGGER
from shivu.modules import ALL_MODULES

locks = {}
message_counters = {}
spam_counters = {}
last_characters = {}
sent_characters = {}
first_correct_guesses = {}
message_counts = {}

for module_name in ALL_MODULES:
    imported_module = importlib.import_module("shivu.modules." + module_name)


last_user = {}
warned_users = {}


def escape_markdown(text):
    escape_chars = r'\*_`\\~>#+-=|{}.!'
    return re.sub(r'([%s])' % re.escape(escape_chars), r'\\\1', text)


async def message_counter(update: Update, context: CallbackContext) -> None:
    chat_id = str(update.effective_chat.id)
    user_id = update.effective_user.id

    if chat_id not in locks:
        locks[chat_id] = asyncio.Lock()
    lock = locks[chat_id]

    async with lock:

        chat_frequency = await user_totals_collection.find_one({'chat_id': chat_id})
        if chat_frequency:
            message_frequency = chat_frequency.get('message_frequency', 100)
        else:
            message_frequency = 100

        if chat_id in last_user and last_user[chat_id]['user_id'] == user_id:
            last_user[chat_id]['count'] += 1
            if last_user[chat_id]['count'] >= 10:

                if user_id in warned_users and time.time() - warned_users[user_id] < 600:
                    return
                else:

                    await update.message.reply_text(
                        f"⚠️ Don't Spam {update.effective_user.first_name}...\nYour Messages Will be Ignored for 10 Minutes...")
                    warned_users[user_id] = time.time()
                    return
        else:
            last_user[chat_id] = {'user_id': user_id, 'count': 1}

        if chat_id in message_counts:
            message_counts[chat_id] += 1
        else:
            message_counts[chat_id] = 1

        if message_counts[chat_id] % message_frequency == 0:
            await send_image(update, context)

            message_counts[chat_id] = 0




async def send_image(update: Update, context: CallbackContext) -> None:
    chat_id = update.effective_chat.id

    rarities_prices = {
        '⚪ Common': (10000, 20000),
        '🟣 Rare': (10000, 40000),
        '🟢 Medium': (10000, 30000),
        '🟡 Legendary': (20000, 50000)
    }

    all_characters = list(await collection.find({'rarity': {'$in': rarities_prices.keys()}}).to_list(length=None))

    if chat_id not in sent_characters:
        sent_characters[chat_id] = []

    if len(sent_characters[chat_id]) == len(all_characters):
        sent_characters[chat_id] = []

    character = random.choice([c for c in all_characters if c['id'] not in sent_characters[chat_id]])

    sent_characters[chat_id].append(character['id'])
    last_characters[chat_id] = character

    if chat_id in first_correct_guesses:
        del first_correct_guesses[chat_id]

    price_range = rarities_prices[character['rarity']]
    price = random.randint(price_range[0], price_range[1])

    keyboard = [[InlineKeyboardButton("Name 🔥", callback_data='car_name')]]

    await context.bot.send_photo(
        chat_id=chat_id,
        photo=character['img_url'],
        caption=f"A New {character['rarity']} Car Appeared...\nPrice: {price} coins\nGuess the name and add it to your collection!",
        parse_mode='HTML',
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def guess(update: Update, context: CallbackContext) -> None:
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id

    if chat_id not in last_characters:
        return

    if chat_id in first_correct_guesses:
        await update.message.reply_text(f'❌ Already guessed by another user...')
        return

    guess = ' '.join(context.args).lower() if context.args else ''

    if "()" in guess or "&" in guess.lower():
        await update.message.reply_text("Invalid characters in your guess.")
        return

    name_parts = last_characters[chat_id]['car name'].lower().split()

    if sorted(name_parts) == sorted(guess.split()) or any(part == guess for part in name_parts):
        first_correct_guesses[chat_id] = user_id

        price = last_characters[chat_id].get('price', 0)
        
        user_balance = await user_collection.find_one({'id': user_id}, projection={'balance': 1})

        if user_balance and user_balance.get('balance', 0) >= price:
            if random.random() < 0.7:  # 70% chance of winning
                await user_collection.update_one({'id': user_id}, {'$inc': {'balance': -price}})
                await user_collection.update_one({'id': user_id}, {'$push': {'characters': last_characters[chat_id]}})
                await update.message.reply_text(f"Congratulations! You won the car!\nYou've been charged {price} coins.")
            else:
                await update.message.reply_text("Unfortunately, you lost the race. Try again next time!")
        else:
            await update.message.reply_text("You don't have enough coins to buy this car.")

    else:
        await update.message.reply_text('Incorrect guess. Try again!')


async def button_click(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    car_name = last_characters.get(query.message.chat_id, {}).get('car name', 'Unknown Car')
    await query.answer(text=f"The car name is: {car_name}", show_alert=True)


# In your main function or setup code
application.add_handler(CallbackQueryHandler(button_click, pattern='^car_name$'))



async def fav(update: Update, context: CallbackContext) -> None:
    user_id = update.effective_user.id


    if not context.args:
        await update.message.reply_text('𝙋𝙡𝙚𝙖𝙨𝙚 𝙥𝙧𝙤𝙫𝙞𝙙𝙚 𝘾𝙖𝙧 𝙞𝙙...')
        return

    character_id = context.args[0]


    user = await user_collection.find_one({'id': user_id})
    if not user:
        await update.message.reply_text('𝙔𝙤𝙪 𝙝𝙖𝙫𝙚 𝙣𝙤𝙩 𝙂𝙤𝙩 𝘼𝙣𝙮 𝘾𝙖𝙧 𝙮𝙚𝙩...')
        return


    character = next((c for c in user['characters'] if c['id'] == character_id), None)
    if not character:
        await update.message.reply_text('𝙏𝙝𝙞𝙨 𝘾𝙖𝙧 𝙞𝙨 𝙉𝙤𝙩 𝙄𝙣 𝙮𝙤𝙪𝙧 𝙂𝙖𝙧𝙖𝙜𝙚')
        return


    user['favorites'] = [character_id]


    await user_collection.update_one({'id': user_id}, {'$set': {'favorites': user['favorites']}})

    await update.message.reply_text(f'🥳𝘾𝙖𝙧 {character["car name"]} 𝙄𝙨 𝙎𝙚𝙩 𝙤𝙣 𝙔𝙤𝙪𝙧 𝙁𝙞𝙧𝙨𝙩 𝙛𝙡𝙤𝙤𝙧 𝙣𝙤𝙬...')


def main() -> None:
    """Run bot."""

    application.add_handler(CommandHandler(["guess"], guess, block=False))
    application.add_handler(CommandHandler("fav", fav, block=False))
    application.add_handler(MessageHandler(filters.ALL, message_counter, block=False))
    application.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    shivuu.start()
    LOGGER.info("Bot started")
    main()

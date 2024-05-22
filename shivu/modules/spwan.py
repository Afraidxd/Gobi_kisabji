import importlib
import time
import random
import re
import asyncio
from html import escape

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




rarity_emojis = {
    "⚪ Common": "⚪",
    "🟣 Rare": "🟣",
    "🟡 Legendary": "🟡",
    "🟢 Medium": "🟢",
    "💮 Mythic": "💮",
    "🔮 Limited edition": "🔮",
    "🫧 Special": "🫧"
}

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

    all_characters = list(await collection.find({}).to_list(length=None))

    if chat_id not in sent_characters:
        sent_characters[chat_id] = []

    if len(sent_characters[chat_id]) == len(all_characters):
        sent_characters[chat_id] = []

    # Filter out Limited edition if already sent today
    if chat_id in limited_edition_sent and time.time() - limited_edition_sent[chat_id] < 86400:
        available_characters = [c for c in all_characters if c['rarity'] != 'Limited edition' and c['id'] not in sent_characters[chat_id]]
    else:
        available_characters = [c for c in all_characters if c['id'] not in sent_characters[chat_id]]

    if not available_characters:
        return  # No available characters to send

    character = random.choice(available_characters)

    # Update sent characters and last character data
    sent_characters[chat_id].append(character['id'])
    last_characters[chat_id] = character

    # Track Limited edition character sending time
    if character['rarity'] == 'Limited edition':
        limited_edition_sent[chat_id] = time.time()

    # Remove first correct guess if any
    if chat_id in first_correct_guesses:
        del first_correct_guesses[chat_id]

    keyboard = [[InlineKeyboardButton("ɴᴀᴍᴇ 🔥", callback_data='name')]]

    await context.bot.send_photo(
        chat_id=chat_id,
        photo=character['img_url'],
        caption=f"ᴀ ɴᴇᴡ ᴄᴀʀ ᴀᴘᴘᴇᴀʀ {rarity_emojis.get(character['rarity'], '')} ᴜsᴇ /guess (ɴᴀᴍᴇ) ᴀɴᴅ ᴍᴀᴋᴇ ɪᴛ ʏᴏᴜʀs \n\n⚠️ ɴᴏᴛᴇ ᴡʜᴇɴ ʏᴏᴜ ᴄʟɪᴄᴋ ᴏɴ ɴᴀᴍᴇ ʙᴜᴛᴛᴏɴ ʙᴏᴛ ᴡɪʟʟ ᴅᴇᴅᴜᴄᴛ 10ᴋ ᴄᴏɪɴ ᴇᴠᴇʀʏᴛɪᴍᴇ",
        parse_mode='HTML',
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def button_click(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    user_id = query.from_user.id
    chat_id = query.message.chat_id

    # Get user balance
    user_balance = await get_user_balance(user_id)

    if user_balance is not None:
        if user_balance >= 10000:
            await user_collection.update_one({"id": user_id}, {"$inc": {"balance": -10000}})
            name = last_characters.get(chat_id, {}).get('name', 'Unknown car')
            await query.answer(text=f"ᴛʜᴇ ᴄᴀʀ ɴᴀᴍᴇ ɪs: {name}", show_alert=True)
        else:
            await query.answer(text="ʏᴏᴜ ᴅᴏɴ'ᴛ ʜᴀᴠᴇ sᴜғғɪᴄɪᴇɴᴛ ʙᴀʟᴀɴᴄᴇ.", show_alert=True)
    else:
        await user_collection.insert_one({"id": user_id, "balance": 50000})
        name = last_characters.get(chat_id, {}).get('name', 'Unknown car')
        await query.answer(text=f"ᴡᴇʟᴄᴏᴍᴇ, ᴜsᴇʀ ! ʏᴏᴜ'ᴠᴇ ʙᴇᴇɴ ᴀᴅᴅᴇᴅ ᴛᴏ ᴏᴜʀ sʏsᴛᴇᴍ ᴡɪᴛʜ ᴀɴ ɪɴɪᴛɪᴀʟ ʙᴀʟᴀɴᴄᴇ ᴏғ 50ᴋ", show_alert=True)

async def get_user_balance(user_id: int) -> int:
    user = await user_collection.find_one({"id": user_id})
    return user.get("balance") if user else None

# Add the following handler to your application
application.add_handler(CommandHandler("start", message_counter))
application.add_handler(CallbackQueryHandler(button_click))


async def guess(update: Update, context: CallbackContext) -> None:
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id

    if chat_id not in last_characters:
        return

    if chat_id in first_correct_guesses:
        await update.message.reply_text(f'❌ 𝘼𝙡𝙧𝙚𝙖𝙙𝙮 𝙜𝙪𝙚𝙨𝙨𝙚𝙙 𝙗𝙮 𝙎𝙤𝙢𝙚𝙤𝙣𝙚 𝙚𝙡𝙨𝙚..')
        return

    guess = ' '.join(context.args).lower() if context.args else ''

    if "()" in guess or "&" in guess.lower():
        await update.message.reply_text("𝙉𝙖𝙝𝙝 𝙔𝙤𝙪 𝘾𝙖𝙣'𝙩 𝙪𝙨𝙚 𝙏𝙝𝙞𝙨 𝙏𝙮𝙥𝙚𝙨 𝙤𝙛 𝙬𝙤𝙧𝙙𝙨 ❌️")
        return

    name_parts = last_characters[chat_id]['name'].lower().split()

    if sorted(name_parts) == sorted(guess.split()) or any(part == guess for part in name_parts):
        first_correct_guesses[chat_id] = user_id

        user = await user_collection.find_one({'id': user_id})
        if user:
            update_fields = {}
            if hasattr(update.effective_user, 'username') and update.effective_user.username != user.get('username'):
                update_fields['username'] = update.effective_user.username
            if update.effective_user.first_name != user.get('first_name'):
                update_fields['first_name'] = update.effective_user.first_name
            if update_fields:
                await user_collection.update_one({'id': user_id}, {'$set': update_fields})

            await user_collection.update_one({'id': user_id}, {'$push': {'characters': last_characters[chat_id]}})

        elif hasattr(update.effective_user, 'username'):
            await user_collection.insert_one({
                'id': user_id,
                'username': update.effective_user.username,
                'first_name': update.effective_user.first_name,
                'characters': [last_characters[chat_id]],
            })

        group_user_total = await group_user_totals_collection.find_one({'user_id': user_id, 'group_id': chat_id})
        if group_user_total:
            update_fields = {}
            if hasattr(update.effective_user, 'username') and update.effective_user.username != group_user_total.get('username'):
                update_fields['username'] = update.effective_user.username
            if update.effective_user.first_name != group_user_total.get('first_name'):
                update_fields['first_name'] = update.effective_user.first_name
            if update_fields:
                await group_user_totals_collection.update_one({'user_id': user_id, 'group_id': chat_id}, {'$set': update_fields})

            await group_user_totals_collection.update_one({'user_id': user_id, 'group_id': chat_id}, {'$inc': {'count': 1}})

        else:
            await group_user_totals_collection.insert_one({
                'user_id': user_id,
                'group_id': chat_id,
                'username': update.effective_user.username,
                'first_name': update.effective_user.first_name,
                'count': 1,
            })

        group_info = await top_global_groups_collection.find_one({'group_id': chat_id})
        if group_info:
            update_fields = {}
            if update.effective_chat.title != group_info.get('group_name'):
                update_fields['group_name'] = update.effective_chat.title
            if update_fields:
                await top_global_groups_collection.update_one({'group_id': chat_id}, {'$set': update_fields})

            await top_global_groups_collection.update_one({'group_id': chat_id}, {'$inc': {'count': 1}})

        else:
            await top_global_groups_collection.insert_one({
                'group_id': chat_id,
                'group_name': update.effective_chat.title,
                'count': 1,
            })

        keyboard = [[InlineKeyboardButton(f"𝘾𝙖𝙧𝙨 🔥", switch_inline_query_current_chat=f"collection.{user_id}")]]
        await update.message.reply_text(f'<b><a href="https://justpaste.it/redirect/cia8f/https%3A%2F%2Ftguser%3Fid%3D%7Buser_id%7D">{escape(update.effective_user.first_name)}</a></b> 𝙔𝙤𝙪 𝙂𝙤𝙩 𝙉𝙚𝙬 𝘾𝙖𝙧🫧 \n🌸𝗡𝗔𝗠𝗘: <b>{last_characters[chat_id]["name"]}</b> \n🧩𝘾𝙤𝙢𝙥𝙖𝙣𝙮: <b>{last_characters[chat_id]["anime"]}</b> \n𝗥𝗔𝗜𝗥𝗧𝗬: <b>{last_characters[chat_id]["rarity"]}</b>\n\n⛩ 𝘾𝙝𝙚𝙘𝙠 𝙮𝙤𝙪𝙧 /collection 𝙉𝙤𝙬', parse_mode='HTML', reply_markup=InlineKeyboardMarkup(keyboard))

    else:
        await update.message.reply_text('𝙋𝙡𝙚𝙖𝙨𝙚 𝙒𝙧𝙞𝙩𝙚 𝘾𝙤𝙧𝙧𝙚𝙘𝙩 𝙉𝙖𝙢𝙚... ❌️')

application.add_handler(CommandHandler(["guess"], guess, block=False))
application.add_handler(MessageHandler(filters.ALL, message_counter, block=False))
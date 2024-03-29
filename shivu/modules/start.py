import importlib
import time
import random
import re
import asyncio
from html import escape 

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from telegram import Update
from telegram.ext import CommandHandler, CallbackContext, MessageHandler, filters, CallbackQueryHandler

from shivu import collection, top_global_groups_collection, group_user_totals_collection, user_collection, user_totals_collection, shivuu
from shivu import application, PHOTO_URL, SUPPORT_CHAT, UPDATE_CHAT, BOT_USERNAME, db, GROUP_ID, LOGGER
from shivu import pm_users as collection 
from shivu.modules import ALL_MODULES

async def start(update: Update, context: CallbackContext) -> None:
    user_id = update.effective_user.id
    first_name = update.effective_user.first_name
    username = update.effective_user.username

    user_data = await collection.find_one({"_id": user_id})

    if user_data is None:

        await collection.insert_one({"_id": user_id, "first_name": first_name, "username": username})

        await context.bot.send_message(chat_id=GROUP_ID, text=f"<a href='tg://user?id={user_id}'>{first_name}</a> STARTED THE BOT", parse_mode='HTML')
    else:

        if user_data['first_name'] != first_name or user_data['username'] != username:

            await collection.update_one({"_id": user_id}, {"$set": {"first_name": first_name, "username": username}})



    if update.effective_chat.type== "private":


        caption = f"""
        ***𝐇𝐞𝐲 𝐭𝐡𝐞𝐫𝐞! {update.effective_user.first_name} 🌻***
              
***𝗜 𝗮𝗺 𝗖𝗮𝗿 𝗚𝗿𝗮𝗯𝗯𝗲𝗿 𝗚𝗮𝗻𝗲 𝗕𝗼𝘁 𝗮𝗱𝗱 𝗺𝗲 𝗶𝗻 𝘆𝗼𝘂𝗿 𝗴𝗿𝗼𝘂𝗽 𝗮𝗻𝗱 𝗽𝗿𝗲𝘀𝘀 𝗵𝗲𝗹𝗽 𝘀𝗲𝗰𝘁𝗶𝗼𝗻 𝘁𝗼 𝘀𝗲𝗲 𝗰𝗼𝗺𝗺𝗮𝗻𝗱

𝗥𝗲𝗮𝗿𝗶𝘁𝘆 𝗘𝘅𝗽𝗹𝗮𝗻𝗮𝘁𝗶𝗼𝗻 

𝗬𝗼𝘂 𝘄𝗶𝗹𝗹 𝗴𝗲𝘁 𝘁𝗵𝗲𝘀𝗲 𝗯𝘆 𝗴𝘂𝗲𝘀𝘀𝗶𝗻𝗴 
⚪️ 𝗖𝗼𝗺𝗺𝗼𝗻  
🟣 𝗥𝗮𝗿𝗲         
🟡 𝗟𝗲𝗴𝗲𝗻𝗱𝗮𝗿𝘆
🟢 𝗠𝗲𝗱𝗶𝘂𝗺.    
💮 𝗠𝘆𝘁𝗵𝗶𝗰

𝗬𝗼𝘂 𝘄𝗶𝗹𝗹 𝗴𝗲𝘁 𝘁𝗵𝗲𝘀𝗲 𝗯𝘆 𝗰𝗼𝗺𝗺𝗮𝗻𝗱 /𝗰𝗵𝗮𝗹𝗹𝗲𝗻𝗴𝗲 
💪 𝗰𝗵𝗮𝗹𝗹𝗲𝗻𝗴𝗲 𝗲𝗱𝗶𝘁𝗶𝗼𝗻 
💮 𝗠𝘆𝘁𝗵𝗶𝗰

𝗬𝗼𝘂 𝘄𝗶𝗹𝗹 𝗴𝗲𝘁 𝘁𝗵𝗶𝘀 𝗯𝘆 𝗯𝗶𝗱𝗱𝗶𝗻𝗴 𝗳𝗼𝗿 𝘁𝗵𝗶𝘀 𝗬𝗼𝘂 𝗵𝗮𝘃𝗲 𝘁𝗼 𝗷𝗼𝗶𝗻 𝘀𝘂𝗽𝗽𝗼𝗿𝘁

🫧 𝗔𝘂𝗰𝘁𝗶𝗼𝗻 𝗲𝗱𝗶𝘁𝗶𝗼𝗻***
               """
        keyboard = [
            [InlineKeyboardButton("𝐀ᴅᴅ 𝐌ᴇ", url=f'http://t.me/Grabyourcar_bot?startgroup=new')],
            [InlineKeyboardButton("𝐇ᴇʟᴘ", callback_data='help'),
             InlineKeyboardButton("𝐒ᴜᴘᴘᴏʀᴛ", url=f'https://t.me/{SUPPORT_CHAT}')],
            [InlineKeyboardButton("𝗨𝗣𝗗𝗔𝗧𝗘𝗦", url=f'https://t.me/BotupdateXD')],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        photo_url = random.choice(PHOTO_URL)

        await context.bot.send_photo(chat_id=update.effective_chat.id, photo=photo_url, caption=caption, reply_markup=reply_markup, parse_mode='markdown')

    else:
        photo_url = random.choice(PHOTO_URL)
        keyboard = [

            [InlineKeyboardButton("𝐇ᴇʟᴘ", callback_data='help'),
             InlineKeyboardButton("𝐒ᴜᴘᴘᴏʀᴛ", url=f'https://t.me/carbotsupport')],

        ]

        reply_markup = InlineKeyboardMarkup(keyboard)
        await context.bot.send_photo(chat_id=update.effective_chat.id, photo=photo_url, caption="𝐯𝐫𝐨𝐨𝐨𝐨𝐨𝐨𝐨𝐦 ! 𝐈 𝐚𝐦 𝐚𝐥𝐢𝐯𝐞",reply_markup=reply_markup )

async def button(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()

    if query.data == 'help':
        help_text = """
    ***Help Section :***
***/guess: To Guess car (only works in group)
/fav: Add Your fav
/trade : To trade Characters
/gift: Give any Character from Your Collection to another user.. (only works in groups)
/collection: To see Your Collection
/topgroups : See Top Groups.. Ppl Guesses Most in that Groups
/top: Too See Top Users
/ctop : Your ChatTop
/changetime: Change Character appear time (only works in Groups)
/bal : To Check Your Balance 
/bonus : To claim daily bonus 
/wbonus: To claim weekly bonus
/pay : to give your coin to another user
/race: to race car and win random amount of coin between (30000-90000)
/challenge: To win 💪 challenge edition car 
/buy : to buy car to see prices do /store***
   """
        help_keyboard = [[InlineKeyboardButton("Back", callback_data='back')]]
        reply_markup = InlineKeyboardMarkup(help_keyboard)

        await context.bot.edit_message_caption(chat_id=update.effective_chat.id, message_id=query.message.message_id, caption=help_text, reply_markup=reply_markup, parse_mode='markdown')

    elif query.data == 'back':

        caption = f"""
        ***Hey there! {update.effective_user.first_name}*** 🌻
        
***𝗜 𝗮𝗺 𝗖𝗮𝗿 𝗚𝗿𝗮𝗯𝗯𝗲𝗿 𝗚𝗮𝗻𝗲 𝗕𝗼𝘁 𝗮𝗱𝗱 𝗺𝗲 𝗶𝗻 𝘆𝗼𝘂𝗿 𝗴𝗿𝗼𝘂𝗽 𝗮𝗻𝗱 𝗽𝗿𝗲𝘀𝘀 𝗵𝗲𝗹𝗽 𝘀𝗲𝗰𝘁𝗶𝗼𝗻 𝘁𝗼 𝘀𝗲𝗲 𝗰𝗼𝗺𝗺𝗮𝗻𝗱

𝗥𝗲𝗮𝗿𝗶𝘁𝘆 𝗘𝘅𝗽𝗹𝗮𝗻𝗮𝘁𝗶𝗼𝗻 

𝗬𝗼𝘂 𝘄𝗶𝗹𝗹 𝗴𝗲𝘁 𝘁𝗵𝗲𝘀𝗲 𝗯𝘆 𝗴𝘂𝗲𝘀𝘀𝗶𝗻𝗴 
⚪️ 𝗖𝗼𝗺𝗺𝗼𝗻  
🟣 𝗥𝗮𝗿𝗲         
🟡 𝗟𝗲𝗴𝗲𝗻𝗱𝗮𝗿𝘆
🟢 𝗠𝗲𝗱𝗶𝘂𝗺.    
💮 𝗠𝘆𝘁𝗵𝗶𝗰

𝗬𝗼𝘂 𝘄𝗶𝗹𝗹 𝗴𝗲𝘁 𝘁𝗵𝗲𝘀𝗲 𝗯𝘆 𝗰𝗼𝗺𝗺𝗮𝗻𝗱 /𝗰𝗵𝗮𝗹𝗹𝗲𝗻𝗴𝗲 
💪 𝗰𝗵𝗮𝗹𝗹𝗲𝗻𝗴𝗲 𝗲𝗱𝗶𝘁𝗶𝗼𝗻 
💮 𝗠𝘆𝘁𝗵𝗶𝗰

𝗬𝗼𝘂 𝘄𝗶𝗹𝗹 𝗴𝗲𝘁 𝘁𝗵𝗶𝘀 𝗯𝘆 𝗯𝗶𝗱𝗱𝗶𝗻𝗴 𝗳𝗼𝗿 𝘁𝗵𝗶𝘀 𝗬𝗼𝘂 𝗵𝗮𝘃𝗲 𝘁𝗼 𝗷𝗼𝗶𝗻 𝘀𝘂𝗽𝗽𝗼𝗿𝘁

🫧 𝗔𝘂𝗰𝘁𝗶𝗼𝗻 𝗲𝗱𝗶𝘁𝗶𝗼𝗻***
        """
        keyboard = [
            [InlineKeyboardButton("𝐀ᴅᴅ 𝐌ᴇ", url=f'http://t.me/Grabyourcar_bot?startgroup=new')],
            [InlineKeyboardButton("𝐇ᴇʟᴘ", callback_data='help'),
             InlineKeyboardButton("𝐒ᴜᴘᴘᴏʀᴛ", url=f'https://t.me/botsupportXD')],
            [InlineKeyboardButton("𝐎ᴡɴᴇʀ", url=f'https://t.me/ownerxd')],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await context.bot.edit_message_caption(chat_id=update.effective_chat.id, message_id=query.message.message_id, caption=caption, reply_markup=reply_markup, parse_mode='markdown')

application.add_handler(CallbackQueryHandler(button, pattern='^help$|^back$', block=False))
start_handler = CommandHandler('start', start, block=False)
application.add_handler(start_handler)

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
        ***Hey there! {update.effective_user.first_name} 🌻***
              
***i Am Grab 'Car Grabber Bot.. Add Me in You're Group And I will send Random Cars in group after every 100 messages and who guessed that car name Correct.. I will add That 🚗 in That user's Collection.. Tap on help Button To See All Commands***
               """
        keyboard = [
            [InlineKeyboardButton("𝐀ᴅᴅ 𝐌ᴇ", url=f'http://t.me/Grabyourcar_bot?startgroup=new')],
            [InlineKeyboardButton("𝐇ᴇʟᴘ", callback_data='help'),
             InlineKeyboardButton("𝐒ᴜᴘᴘᴏʀᴛ", url=f'https://t.me/{SUPPORT_CHAT}')],
            [InlineKeyboardButton("𝐎ᴡɴᴇʀ", url=f'https://t.me/ownerxd')],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        photo_url = random.choice(PHOTO_URL)

        await context.bot.send_photo(chat_id=update.effective_chat.id, photo=photo_url, caption=caption, reply_markup=reply_markup, parse_mode='markdown')

    else:
        photo_url = random.choice(PHOTO_URL)
        keyboard = [

            [InlineKeyboardButton("𝐇ᴇʟᴘ", callback_data='help'),
             InlineKeyboardButton("𝐒ᴜᴘᴘᴏʀᴛ", url=f'https://t.me/botsupportXD')],

        ]

        reply_markup = InlineKeyboardMarkup(keyboard)
        await context.bot.send_photo(chat_id=update.effective_chat.id, photo=photo_url, caption="𝐯𝐫𝐨𝐨𝐨𝐨𝐨𝐨𝐨𝐦 ! 𝐈 𝐚𝐦 𝐚𝐥𝐢𝐯𝐞",reply_markup=reply_markup )

async def button(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()

    if query.data == 'help':
        help_text = """
    ***Help Section :***
    
***/guess: To Guess character (only works in group)***
***/fav: Add Your fav***
***/trade : To trade Characters***
***/gift: Give any Character from Your Collection to another user.. (only works in groups)***
***/collection: To see Your Collection***
***/topgroups : See Top Groups.. Ppl Guesses Most in that Groups***
***/top: Too See Top Users***
***/ctop : Your ChatTop***
***/changetime: Change Character appear time (only works in Groups)***

    ***Game Section :***

*/𝗯𝗮𝗹: 𝗧𝗼 𝗖𝗵𝗲𝗰𝗸 𝗬𝗼𝘂𝗿𝗕𝗮𝗹𝗮𝗻𝗰𝗲*
*/𝗯𝗲𝘁: 𝗧𝗼 𝗯𝗲𝘁 𝘆𝗼𝘂𝗿 𝗰𝗼𝗶𝗻*
*/𝗯𝗼𝗻𝘂𝘀 : 𝗧𝗼 𝗰𝗹𝗮𝗶𝗺 𝗬𝗼𝘂𝗿 𝗱𝗮𝗶𝗹𝘆 𝗯𝗼𝗻𝘂𝘀*
*/𝗽𝗮𝘆 :  𝘁𝗼 𝗴𝗶𝘃𝗲 𝘆𝗼𝘂𝗿 𝗰𝗼𝗶𝗻 𝘁𝗼 𝗮𝗻𝗼𝘁𝗵𝗲𝗿 𝘂𝘀𝗲𝗿 *
*/𝘁𝗼𝗽𝘀 : 𝗧𝗼 𝘀𝗲𝗲 𝘁𝗼𝗽 𝗰𝗼𝗶𝗻 𝗵𝗼𝗹𝗱𝗲𝗿𝘀*
*/𝗿𝗮𝗰𝗲 : 𝘁𝗼 𝗿𝗮𝗰𝗲 𝗰𝗮𝗿 𝗮𝗻𝗱 𝘄𝗶𝗻 𝗿𝗮𝗻𝗱𝗼𝗺 𝗰𝗮𝗿 ( 𝗨𝗻𝗱𝗲𝗿 𝗺𝗮𝗶𝗻𝘁𝗲𝗻𝗮𝗻𝗰𝗲 𝗱𝗼𝗻'𝘁 𝘂𝘀𝗲 𝘆𝗼𝘂𝗿 𝗰𝗼𝗶𝗻 𝘄𝗶𝗹𝗹 𝗱𝗲𝗱𝘂𝗰𝘁)*
*/𝗯𝘂𝘆 : 𝘁𝗼 𝗯𝘂𝘆 𝗰𝗮𝗿𝘀 𝘁𝗼 𝘀𝗲𝗲 𝗽𝗿𝗶𝗰𝗲𝘀 𝗱𝗼 /𝘀𝘁𝗼𝗿𝗲*
   """
        help_keyboard = [[InlineKeyboardButton("Back", callback_data='back')]]
        reply_markup = InlineKeyboardMarkup(help_keyboard)

        await context.bot.edit_message_caption(chat_id=update.effective_chat.id, message_id=query.message.message_id, caption=help_text, reply_markup=reply_markup, parse_mode='markdown')

    elif query.data == 'back':

        caption = f"""
        ***Hey there! {update.effective_user.first_name}*** 🌻
        
***i Am Car Grabber bot.. Add Me in You're Group And I will send Random Car in group after every 100 messages and who guessed that car 🚗 name Correct.. I will add That car 🏎 in That user's Collection.. Tap on help Button To See All Commands***
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

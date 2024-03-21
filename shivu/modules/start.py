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
              
***𝐢 𝐀𝐦 𝐆𝐫𝐚𝐛 '𝐂𝐚𝐫 𝐆𝐫𝐚𝐛𝐛𝐞𝐫 𝐁𝐨𝐭.. 𝐀𝐝𝐝 𝐌𝐞 𝐢𝐧 𝐘𝐨𝐮'𝐫𝐞 𝐆𝐫𝐨𝐮𝐩 𝐀𝐧𝐝 𝐈 𝐰𝐢𝐥𝐥 𝐬𝐞𝐧𝐝 𝐑𝐚𝐧𝐝𝐨𝐦 𝐂𝐚𝐫𝐬 𝐢𝐧 𝐠𝐫𝐨𝐮𝐩 𝐚𝐟𝐭𝐞𝐫 𝐞𝐯𝐞𝐫𝐲 100 𝐦𝐞𝐬𝐬𝐚𝐠𝐞𝐬 𝐚𝐧𝐝 𝐰𝐡𝐨 𝐠𝐮𝐞𝐬𝐬𝐞𝐝 𝐭𝐡𝐚𝐭 𝐜𝐚𝐫 𝐧𝐚𝐦𝐞 𝐂𝐨𝐫𝐫𝐞𝐜𝐭.. 𝐈 𝐰𝐢𝐥𝐥 𝐚𝐝𝐝 𝐓𝐡𝐚𝐭 🏎 𝐢𝐧 𝐓𝐡𝐚𝐭 𝐮𝐬𝐞𝐫'𝐬 𝐂𝐨𝐥𝐥𝐞𝐜𝐭𝐢𝐨𝐧.. 𝐓𝐚𝐩 𝐨𝐧 𝐡𝐞𝐥𝐩 𝐁𝐮𝐭𝐭𝐨𝐧 𝐓𝐨 𝐒𝐞𝐞 𝐀𝐥𝐥 𝐂𝐨𝐦𝐦𝐚𝐧𝐝𝐬***
               """
        keyboard = [
            [InlineKeyboardButton("𝐀ᴅᴅ 𝐌ᴇ", url=f'http://t.me/Grabyourcar_bot?startgroup=new')],
            [InlineKeyboardButton("𝐇ᴇʟᴘ", callback_data='help'),
             InlineKeyboardButton("𝐒ᴜᴘᴘᴏʀᴛ", url=f'https://t.me/BotsupportXD')],
            [InlineKeyboardButton("𝗢ᴡɴᴇʀ", url=f'https://t.me/ownerxd'),
           InlineKeyboardButton("𝐔ᴘᴅᴀᴛᴇ", url=f'https://t.me/BotupdateXD')],
           [InlineKeyboardButton("game", callback_data='game')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        photo_url = random.choice(PHOTO_URL)

        await context.bot.send_photo(chat_id=update.effective_chat.id, photo=photo_url, caption=caption, reply_markup=reply_markup, parse_mode='markdown')

    else:
        photo_url = random.choice(PHOTO_URL)
        keyboard = [

            [InlineKeyboardButton("𝐇ᴇʟᴘ", callback_data='help'),
             InlineKeyboardButton("𝐒ᴜᴘᴘᴏʀᴛ", url=f'https://t.me/{SUPPORT_CHAT}')],

        ]

        reply_markup = InlineKeyboardMarkup(keyboard)
        await context.bot.send_photo(chat_id=update.effective_chat.id, photo=photo_url, caption="𝐯𝐫𝐨𝐨𝐨𝐨𝐨𝐨𝐨𝐦 ! 𝐈 𝐚𝐦 𝐚𝐥𝐢𝐯𝐞",reply_markup=reply_markup )

async def button(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()

    if query.data == 'help':
        help_text = """
    ***Help Section :***
    
***/guess: 𝗧𝗼 𝗚𝘂𝗲𝘀𝘀 𝐂𝐚𝐫 (𝗼𝗻𝗹𝘆 𝘄𝗼𝗿𝗸𝘀 𝗶𝗻 𝗴𝗿𝗼𝘂𝗽)***
***/fav: 𝐀𝐝𝐝 𝐘𝐨𝐮𝐫 𝐟𝐚𝐯***
***/trade : 𝐓𝐨 𝐭𝐫𝐚𝐝𝐞 𝐂𝐚𝐫***
***/gift: 𝐆𝐢𝐯𝐞 𝐚𝐧𝐲 𝐂𝐚𝐫 𝐟𝐫𝐨𝐦 𝐘𝐨𝐮𝐫 𝐂𝐨𝐥𝐥𝐞𝐜𝐭𝐢𝐨𝐧 𝐭𝐨 𝐚𝐧𝐨𝐭𝐡𝐞𝐫 𝐮𝐬𝐞𝐫.. (𝐨𝐧𝐥𝐲 𝐰𝐨𝐫𝐤𝐬 𝐢𝐧 𝐠𝐫𝐨𝐮𝐩𝐬)***
***/collection: 𝐓𝐨 𝐬𝐞𝐞 𝐘𝐨𝐮𝐫 𝐠𝐚𝐫𝐚𝐠𝐞***
***/topgroups : 𝐒𝐞𝐞 𝐓𝐨𝐩 𝐆𝐫𝐨𝐮𝐩𝐬.. 𝐏𝐩𝐥 𝐆𝐮𝐞𝐬𝐬𝐞𝐬 𝐌𝐨𝐬𝐭 𝐢𝐧 𝐭𝐡𝐚𝐭 𝐆𝐫𝐨𝐮𝐩𝐬***
***/top : 𝐓𝐨𝐨 𝐒𝐞𝐞 𝐓𝐨𝐩 𝐔𝐬𝐞𝐫𝐬***
***/ctop : 𝐓𝐨𝐨 𝐒𝐞𝐞 𝐘𝐨𝐮𝐫 𝐂𝐡𝐚𝐭 𝐓𝐨𝐩***
***/changetime: 𝐂𝐡𝐚𝐧𝐠𝐞 𝐂𝐡𝐚𝐫𝐚𝐜𝐭𝐞𝐫 𝐚𝐩𝐩𝐞𝐚𝐫 𝐭𝐢𝐦𝐞 (𝐨𝐧𝐥𝐲 𝐰𝐨𝐫𝐤𝐬 𝐢𝐧 𝐆𝐫𝐨𝐮𝐩𝐬)***
   """
        help_keyboard = [[InlineKeyboardButton("𝐁ᴀᴄᴋ ➲", callback_data='back')]]
        reply_markup = InlineKeyboardMarkup(help_keyboard)

if query.data == 'game':
        game_text = """
    *Game Section :*
    
*/𝗯𝗮𝗹: 𝗧𝗼 𝗖𝗵𝗲𝗰𝗸 𝗬𝗼𝘂𝗿𝗕𝗮𝗹𝗮𝗻𝗰𝗲*
*/𝗯𝗲𝘁: 𝗧𝗼 𝗯𝗲𝘁 𝘆𝗼𝘂𝗿 𝗰𝗼𝗶𝗻*
*/𝗯𝗼𝗻𝘂𝘀 : 𝗧𝗼 𝗰𝗹𝗮𝗶𝗺 𝗬𝗼𝘂𝗿 𝗱𝗮𝗶𝗹𝘆 𝗯𝗼𝗻𝘂𝘀*
*/𝗽𝗮𝘆 :  𝘁𝗼 𝗴𝗶𝘃𝗲 𝘆𝗼𝘂𝗿 𝗰𝗼𝗶𝗻 𝘁𝗼 𝗮𝗻𝗼𝘁𝗵𝗲𝗿 𝘂𝘀𝗲𝗿 *
*/𝘁𝗼𝗽𝘀 : 𝗧𝗼 𝘀𝗲𝗲 𝘁𝗼𝗽 𝗰𝗼𝗶𝗻 𝗵𝗼𝗹𝗱𝗲𝗿𝘀*
*/𝗿𝗮𝗰𝗲 : 𝘁𝗼 𝗿𝗮𝗰𝗲 𝗰𝗮𝗿 𝗮𝗻𝗱 𝘄𝗶𝗻 𝗿𝗮𝗻𝗱𝗼𝗺 𝗰𝗮𝗿 ( 𝗨𝗻𝗱𝗲𝗿 𝗺𝗮𝗶𝗻𝘁𝗲𝗻𝗮𝗻𝗰𝗲 𝗱𝗼𝗻'𝘁 𝘂𝘀𝗲 𝘆𝗼𝘂𝗿 𝗰𝗼𝗶𝗻 𝘄𝗶𝗹𝗹 𝗱𝗲𝗱𝘂𝗰𝘁)*
*/𝗯𝘂𝘆 : 𝘁𝗼 𝗯𝘂𝘆 𝗰𝗮𝗿𝘀 𝘁𝗼 𝘀𝗲𝗲 𝗽𝗿𝗶𝗰𝗲𝘀 𝗱𝗼 /𝘀𝘁𝗼𝗿𝗲*

game_keyboard = [[InlineKeyboardButton("𝐁ᴀᴄᴋ ➲", callback_data='back')]]
        reply_markup = InlineKeyboardMarkup(game_keyboard)

        await context.bot.edit_message_caption(chat_id=update.effective_chat.id, message_id=query.message.message_id, caption=help_text, reply_markup=reply_markup, parse_mode='markdown')

    elif query.data == 'back':

        caption = f"""
        ***𝐇𝐞𝐲 𝐭𝐡𝐞𝐫𝐞! {update.effective_user.first_name}*** 🌻
        
***𝐢 𝐀𝐦 𝐆𝐫𝐚𝐛 '𝐂𝐚𝐫 𝐆𝐫𝐚𝐛𝐛𝐞𝐫 𝐁𝐨𝐭.. 𝐀𝐝𝐝 𝐌𝐞 𝐢𝐧 𝐘𝐨𝐮'𝐫𝐞 𝐆𝐫𝐨𝐮𝐩 𝐀𝐧𝐝 𝐈 𝐰𝐢𝐥𝐥 𝐬𝐞𝐧𝐝 𝐑𝐚𝐧𝐝𝐨𝐦 𝐂𝐚𝐫𝐬 𝐢𝐧 𝐠𝐫𝐨𝐮𝐩 𝐚𝐟𝐭𝐞𝐫 𝐞𝐯𝐞𝐫𝐲 100 𝐦𝐞𝐬𝐬𝐚𝐠𝐞𝐬 𝐚𝐧𝐝 𝐰𝐡𝐨 𝐠𝐮𝐞𝐬𝐬𝐞𝐝 𝐭𝐡𝐚𝐭 𝐜𝐚𝐫 𝐧𝐚𝐦𝐞 𝐂𝐨𝐫𝐫𝐞𝐜𝐭.. 𝐈 𝐰𝐢𝐥𝐥 𝐚𝐝𝐝 𝐓𝐡𝐚𝐭 🏎 𝐢𝐧 𝐓𝐡𝐚𝐭 𝐮𝐬𝐞𝐫'𝐬 𝐠𝐚𝐫𝐚𝐠𝐞.. 𝐓𝐚𝐩 𝐨𝐧 𝐡𝐞𝐥𝐩 𝐁𝐮𝐭𝐭𝐨𝐧 𝐓𝐨 𝐒𝐞𝐞 𝐀𝐥𝐥 𝐂𝐨𝐦𝐦𝐚𝐧𝐝𝐬***
        """
        keyboard = [
            [InlineKeyboardButton("𝐀ᴅᴅ 𝐌ᴇ", url=f'http://t.me/Grabyourcar_bot?startgroup=new')],
            [InlineKeyboardButton("𝐇ᴇʟᴘ", callback_data='help'),
             InlineKeyboardButton("𝐒ᴜᴘᴘᴏʀᴛ", url=f'https://t.me/{SUPPORT_CHAT}')],
            [InlineKeyboardButton("𝗢ᴡɴᴇʀ", url=f'https://t.me/ownerxd')],
            [InlineKeyboardButton("game", callback_data='game')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await context.bot.edit_message_caption(chat_id=update.effective_chat.id, message_id=query.message.message_id, caption=caption, reply_markup=reply_markup, parse_mode='markdown')

application.add_handler(CallbackQueryHandler(button, pattern='^help$|^back$', block=False))
application.add_handler(CallbackQueryHandler(button, pattern='^game$|^back$', block=False))
start_handler = CommandHandler('start', start, block=False)
application.add_handler(start_handler)

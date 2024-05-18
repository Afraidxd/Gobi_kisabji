import random
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackContext, CallbackQueryHandler, CommandHandler
from shivu import application, PHOTO_URL, SUPPORT_CHAT, db, GROUP_ID

collection = db['total_pm_users']

async def start(update: Update, context: CallbackContext) -> None:
    user_id = update.effective_user.id
    first_name = update.effective_user.first_name
    username = update.effective_user.username

    user_data = await collection.find_one({"_id": user_id})

    if user_data is None:
        await collection.insert_one({"_id": user_id, "first_name": first_name, "username": username})
        await context.bot.send_message(chat_id=GROUP_ID, text=f"#𝐍𝐄𝐖 𝐔𝐒𝐄𝐑\nΔ 𝖨𝖣 : {user_id}\nΔ 𝖡𝖸 : {first_name}", parse_mode='HTML')
    else:
        if user_data['first_name'] != first_name or user_data['username'] != username:
            await collection.update_one({"_id": user_id}, {"$set": {"first_name": first_name, "username": username}})

    caption = f"""
    ***ʜᴇʏ ᴛʜᴇʀᴇ! {first_name}***\n
    ***ɪ am ᴄᴀʀ ɢʀᴀʙʙᴇʀ ʙᴏᴛ. ᴀᴅᴅ ᴍᴇ ᴛᴏ ʏᴏᴜʀ ɢʀᴏᴜᴘ ᴀɴᴅ ᴛᴀᴘ ᴏɴ ᴛʜᴇ ʜᴇʟᴘ ʙᴜᴛᴛᴏɴ ᴛᴏ ᴅɪꜱᴄᴏᴠᴇʀ ᴀʟʟ ᴍʏ ғᴇᴀᴛᴜʀᴇꜱ ᴀɴᴅ ᴄᴏᴍᴍᴀɴᴅꜱ. ʟᴇᴛ'ꜱ ʀᴀᴄᴇ ᴛᴏ ᴛʜᴇ ᴛᴏᴘ!***\n
    """

    photo_url = random.choice(PHOTO_URL)

    keyboard = [
        [InlineKeyboardButton("ᴀᴅᴅ ᴍᴇ ᴛᴏ ʏᴏᴜʀ ɢʀᴏᴜᴘ", url=f'https://t.me/getyourcar_bot?startgroup=new')],
        [InlineKeyboardButton("ᴄʜᴀɴɴᴇʟ", url='https://t.me/BotupdateXD'), InlineKeyboardButton("ɢʀᴏᴜᴘ", url=SUPPORT_CHAT)],
        [InlineKeyboardButton("ʜᴇʟᴘ", callback_data='help'), InlineKeyboardButton("ᴄʀᴇᴅɪᴛꜱ", callback_data='credits')]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await context.bot.send_photo(chat_id=update.effective_chat.id, photo=photo_url, caption=caption, reply_markup=reply_markup, parse_mode='markdown')

async def button(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()

    if query.data == 'help':
        help_text = """
        ***ᴄʜᴏᴏsᴇ ᴀ ᴄᴀᴛᴇɢᴏʀʏ:***
1. ᴜsᴇʀ
2. ɢᴀᴍᴇs
        """
        help_keyboard = [
            [InlineKeyboardButton("ᴜsᴇʀ", callback_data='user_help'), InlineKeyboardButton("ɢᴀᴍᴇs", callback_data='games_help')],
            [InlineKeyboardButton("ʙᴀᴄᴋ", callback_data='back')]
        ]
        reply_markup = InlineKeyboardMarkup(help_keyboard)

        await query.edit_message_caption(caption=help_text, reply_markup=reply_markup, parse_mode='markdown')

    elif query.data == 'user_help':
        user_help_text = """
        ***ᴜsᴇʀ ᴄᴏᴍᴍᴀɴᴅs:***

***/guess: ᴛᴏ ɢᴜᴇss ᴄᴀʀ (ᴏɴʟʏ ᴡᴏʀᴋs ɪɴ ɢʀᴏᴜᴘ)***
***/favorite: ᴛᴏ sᴇʟᴇᴄᴛ ʏᴏᴜʀ ғᴀᴠᴏʀɪᴛᴇ ᴄᴀʀ***
***/trade : ᴛᴏ ᴛʀᴀᴅᴇ ᴄᴀʀs ᴡɪᴛʜ ᴏᴛʜᴇʀ ᴜsᴇʀs***
***/gift: ᴛᴏ ɢɪғᴛ ᴀɴʏ ᴄᴀʀ ᴛᴏ ᴀɴᴏᴛʜᴇʀ ᴜsᴇʀ.. (ᴏɴʟʏ ᴡᴏʀᴋs ɪɴ ɢʀᴏᴜᴘs)***
***/collection: ᴛᴏ sᴇᴇ ʏᴏᴜʀ ᴄᴀʀs ᴄᴏʟʟᴇᴄᴛɪᴏɴ***
***/tops: ᴛᴏ sᴇᴇ ᴛᴏᴘ ᴄᴏɪɴ ʜᴏʟᴅᴇʀs***
***/top: ᴛᴏ sᴇᴇ ᴛᴏᴘ ᴄᴀʀ ʜᴏʟᴅᴇʀs ***
***/changetime: ᴄʜᴀɴɢᴇ ᴄᴀʀ ᴀᴘᴘᴇᴀʀ ᴛɪᴍᴇ (ᴏɴʟʏ ᴡᴏʀᴋs ɪɴ ɢʀᴏᴜᴘs)***
        """
        user_help_keyboard = [[InlineKeyboardButton("ʙᴀᴄᴋ", callback_data='help')]]
        reply_markup = InlineKeyboardMarkup(user_help_keyboard)

        await query.edit_message_caption(caption=user_help_text, reply_markup=reply_markup, parse_mode='markdown')

    elif query.data == 'games_help':
        games_help_text = """
        ***ɢᴀᴍᴇ ᴄᴏᴍᴍᴀɴᴅs:***

***/bal: ᴛᴏ ᴄʜᴇᴄᴋ ʏᴏᴜʀ ʙᴀʟᴀɴᴄᴇ***
***/challenge: ᴄʜᴀɴᴄᴇ ᴛᴏ ᴡɪɴ 1 ʀᴀɴᴅᴏᴍ ᴄᴀʀ ***
***/bonus: ᴛᴏ ᴄʟᴀɪᴍ ᴅᴀɪʟʏ ʙᴏɴᴜs ***
***/wbonus: ᴛᴏ ᴄʟᴀɪᴍ ᴡᴇᴇᴋʟʏ ʙᴏɴᴜs***
***/store: To buy from daily store***
***/race: ᴛᴏ ᴡɪɴ sᴏᴍᴇ ᴛᴏᴋᴇɴs ʙᴇᴛᴡᴇᴇɴ 10ᴋ - 50ᴋ ***
***/bet: ᴛᴏ ʙᴇᴛ sᴏᴍᴇ ᴛᴏᴋᴇɴs***
***/pay: ᴛᴏ ɢɪᴠᴇ ʏᴏᴜʀ ᴄᴏɪɴ ᴛᴏ ᴀɴᴏᴛʜᴇʀ ᴜsᴇʀ***
***/rps: ᴛᴏ ᴘʟᴀʏ ʀᴏᴄᴋ ᴘᴀᴘᴇʀ sᴄɪssᴏʀs ᴜsɪɴɢ ᴛᴏᴋᴇɴs***
        """
        games_help_keyboard = [[InlineKeyboardButton("ʙᴀᴄᴋ", callback_data='help')]]
        reply_markup = InlineKeyboardMarkup(games_help_keyboard)

        await query.edit_message_caption(caption=games_help_text, reply_markup=reply_markup, parse_mode='markdown')

    elif query.data == 'credits':
        credits_text = """
        ***Credits:***

ᴀ ᴛᴇʟᴇɢʀᴀᴍ ᴘʀɪᴠᴀᴛᴇ ɢᴀᴍᴇ ʙᴏᴛ\n
ᴡʀɪᴛᴛᴇɴ ɪɴ ᴩʏᴛʜᴏɴ ᴡɪᴛʜ ᴛʜᴇ ʜᴇʟᴩ ᴏғ [ᴩʏʀᴏɢʀᴀᴍ](https://github.com/pyrogram/pyrogram) [ᴩʏᴛʜᴏɴ-ᴛᴇʟᴇɢʀᴀᴍ-ʙᴏᴛ](https://github.com/python-telegram-bot/python-telegram-bot) ᴀɴᴅ ᴜsɪɴɢ [ᴍᴏɴɢᴏ](https://cloud.mongodb.com) ᴀs ᴅᴀᴛᴀʙᴀsᴇ.

ʜᴇʀᴇ ᴀʀᴇ ᴍʏ ᴅᴇᴠᴇʟᴏᴘᴇʀꜱ:
        
✪ : [𝙰ʟᴇx](https://t.me/ipcxd)
✪ : [𝐃𝐞𝐥𝐭𝐚](https://t.me/Notrealgeek)
        """
        credits_keyboard = [[InlineKeyboardButton("ʙᴀᴄᴋ", callback_data='back')]]
        reply_markup = InlineKeyboardMarkup(credits_keyboard)

        await query.edit_message_caption(caption=credits_text, reply_markup=reply_markup, parse_mode='markdown')

    elif query.data == 'back':
        start_text = f"""
        ***Hey there! {update.effective_user.first_name}***\n
        ***I am ᴄᴀʀ ɢʀᴀʙʙᴇʀ ʙᴏᴛ. ᴀᴅᴅ ᴍᴇ ᴛᴏ ʏᴏᴜʀ ɢʀᴏᴜᴘ ᴀɴᴅ ᴛᴀᴘ ᴏɴ ᴛʜᴇ ʜᴇʟᴘ ʙᴜᴛᴛᴏɴ ᴛᴏ ᴅɪꜱᴄᴏᴠᴇʀ ᴀʟʟ ᴍʏ ғᴇᴀᴛᴜʀᴇꜱ ᴀɴᴅ ᴄᴏᴍᴍᴀɴᴅꜱ. ʟᴇᴛ'ꜱ ʀᴀᴄᴇ ᴛᴏ ᴛʜᴇ ᴛᴏᴘ!***\n
        """

        photo_url = random.choice(PHOTO_URL)
        keyboard = [
            [InlineKeyboardButton("ᴀᴅᴅ ᴍᴇ ᴛᴏ ʏᴏᴜʀ ɢʀᴏᴜᴘ", url=f'https://t.me/Grab_Yourslave_bot?startgroup=new')],
            [InlineKeyboardButton("ᴄʜᴀɴɴᴇʟ", url='https://t.me/BotupdateXD'), InlineKeyboardButton("ɢʀᴏᴜᴘ", url='https://t.me/BotsupportXD')],
            [InlineKeyboardButton("ʜᴇʟᴘ", callback_data='help'), InlineKeyboardButton("ᴄʀᴇᴅɪᴛꜱ", callback_data='credits')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_caption(caption=start_text, reply_markup=reply_markup, parse_mode='markdown')

# Ensure the callback query handler pattern matches the possible callback data
application.add_handler(CallbackQueryHandler(button, pattern='^(help|credits|back|user_help|games_help)$'))
start_handler = CommandHandler('start', start)
application.add_handler(start_handler)

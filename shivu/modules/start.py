import random
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackContext, CallbackQueryHandler, CommandHandler
from Grabber import application, PHOTO_URL, SUPPORT_CHAT, db, GROUP_ID

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
    ***Hey there! {update.effective_user.first_name}***\n
    ***ɪ ᴀᴍ ꜱʟᴀᴠᴇꜱ ɢʀᴀʙʙᴇʀ ʙᴏᴛ ᴀᴅᴅ ᴍᴇ ɪɴ ʏᴏᴜ'ʀᴇ ɢʀᴏᴜᴘ ᴀɴᴅ ᴛᴀᴘ ᴏɴ ʜᴇʟᴘ ʙᴜᴛᴛᴏɴ ᴛᴏ ꜱᴇᴇ ᴀʟʟ ᴄᴏᴍᴍᴀɴᴅS***\n
    """

    photo_url = random.choice(PHOTO_URL)

    if update.effective_chat.type == "private":
        keyboard = [
            [InlineKeyboardButton("ᴀᴅᴅ ᴍᴇ ᴛᴏ ʏᴏᴜʀ ɢʀᴏᴜᴘ", url=f'https://t.me/Grab_Yourslave_bot?startgroup=new')],
            [InlineKeyboardButton("ᴄʜᴀɴɴᴇʟ", url=f'https://t.me/BotupdateXD'), InlineKeyboardButton("ɢʀᴏᴜᴘ", url=f'{SUPPORT_CHAT}')],
            [InlineKeyboardButton("ʜᴇʟᴘ", callback_data='help'), InlineKeyboardButton("ᴄʀᴇᴅɪᴛꜱ", callback_data='credits')]
        ]
    else:
        keyboard = [
            [InlineKeyboardButton("ᴀᴅᴅ ᴍᴇ ᴛᴏ ʏᴏᴜʀ ɢʀᴏᴜᴘ", url=f'https://t.me/Grab_Yourslave_bot?startgroup=new')],
            [InlineKeyboardButton("ᴄʜᴀɴɴᴇʟ", url=f'https://t.me/BotupdateXD'), InlineKeyboardButton("ɢʀᴏᴜᴘ", url=f'{SUPPORT_CHAT}')],
            [InlineKeyboardButton("ʜᴇʟᴘ", callback_data='help'), InlineKeyboardButton("ᴄʀᴇᴅɪᴛꜱ", callback_data='credits')]
        ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await context.bot.send_photo(chat_id=update.effective_chat.id, photo=photo_url, caption=caption, reply_markup=reply_markup, parse_mode='markdown')

async def button(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()

    if query.data == 'help':
        help_text = """
        ***Choose a category:***

        1. USER
        2. GAMES
        """
        help_keyboard = [
            [InlineKeyboardButton("USER", callback_data='user_help'), InlineKeyboardButton("GAMES", callback_data='games_help')],
            [InlineKeyboardButton("Back", callback_data='back')]
        ]
        reply_markup = InlineKeyboardMarkup(help_keyboard)

        await context.bot.edit_message_caption(chat_id=update.effective_chat.id, message_id=query.message.message_id, caption=help_text, reply_markup=reply_markup, parse_mode='markdown')

    elif query.data == 'user_help':
        user_help_text = """
        ***User Commands:***

        ***/grab: To Guess waifu (only works in group)***
        ***/marry: To marry a waifu and make it favorite***
        ***/strade : To trade slaves with other users***
        ***/sgift: Give any slaves to another user.. (only works in groups)***
        ***/slaves: To see Your slaves collection***
        ***/tops: Too See Top coin Users***
        ***/ctop: To see top character grabbers ***
        ***/propose: Too propose a random waifu***
        ***/sinv: To check current token balance***
        ***/spay: To pay other users from you own balance***
        ***/changetime: Change slaves appear time (only works in Groups)***
        """
        user_help_keyboard = [[InlineKeyboardButton("Back", callback_data='help')]]
        reply_markup = InlineKeyboardMarkup(user_help_keyboard)

        await context.bot.edit_message_caption(chat_id=update.effective_chat.id, message_id=query.message.message_id, caption=user_help_text, reply_markup=reply_markup, parse_mode='markdown')

    elif query.data == 'games_help':
        games_help_text = """
        ***Game Commands:***

        ***/sexplore: To explore and find random loots***
        ***/scrime: Do random crime ***
        ***/shunt: To hunt in the wild 💀💀 ***
        ***/bonus: To claim daily bonus***
        ***/store: To buy from daily store***
        ***/mines: To mine some ores***
        ***/mode: To toggle between safe and war mode***
        ***/sfight: To fight a user***
        ***/rps: To play rock paper and scissors ***
        ***/sbet: To bet some balance***
        """
        games_help_keyboard = [[InlineKeyboardButton("Back", callback_data='help')]]
        reply_markup = InlineKeyboardMarkup(games_help_keyboard)

        await context.bot.edit_message_caption(chat_id=update.effective_chat.id, message_id=query.message.message_id, caption=games_help_text, reply_markup=reply_markup, parse_mode='markdown')

    elif query.data == 'credits':
        credits_text = """
        ***Credits:***

        ᴀ ᴛᴇʟᴇɢʀᴀᴍ ᴘʀɪᴠᴀᴛᴇ ɢᴀᴍᴇ ʙᴏᴛ\n
        ᴡʀɪᴛᴛᴇɴ ɪɴ ᴩʏᴛʜᴏɴ ᴡɪᴛʜ ᴛʜᴇ ʜᴇʟᴩ ᴏғ [ᴩʏʀᴏɢʀᴀᴍ](https://github.com/pyrogram/pyrogram) [ᴩʏᴛʜᴏɴ-ᴛᴇʟᴇɢʀᴀᴍ-ʙᴏᴛ](https://github.com/python-telegram-bot/python-telegram-bot) ᴀɴᴅ ᴜsɪɴɢ [ᴍᴏɴɢᴏ](https://cloud.mongodb.com) ᴀs ᴅᴀᴛᴀʙᴀsᴇ.

        ʜᴇʀᴇ ᴀʀᴇ ᴍʏ ᴅᴇᴠᴇʟᴏᴘᴇʀꜱ:
        
        Δ : [Alpha](https://t.me/ShutupKeshav)
        Δ : [𝐃𝐞𝐥𝐭𝐚](https://t.me/Notrealgeek)
        """
        credits_keyboard = [[InlineKeyboardButton("Back", callback_data='help')]]
        reply_markup = InlineKeyboardMarkup(credits_keyboard)

        await context.bot.edit_message_caption(chat_id=update.effective_chat.id, message_id=query.message.message_id, caption=credits_text, reply_markup=reply_markup, parse_mode='markdown')

    elif query.data == 'back':
        start_text = """
        ***Hey there! {first_name}***\n
        ***ɪ ᴀᴍ ꜱʟᴀᴠᴇꜱ ɢʀᴀʙʙᴇʀ ʙᴏᴛ ᴀᴅᴅ ᴍᴇ ɪɴ ʏᴏᴜ'ʀᴇ ɢʀᴏᴜᴘ ᴀɴᴅ ᴛᴀᴘ ᴏɴ ʜᴇʟᴘ ʙᴜᴛᴛᴏɴ ᴛᴏ ꜱᴇᴇ ᴀʟʟ ᴄᴏᴍᴍᴀɴᴅS***\n
        """.format(first_name=update.effective_user.first_name)

        photo_url = random.choice(PHOTO_URL)
        keyboard = [
            [InlineKeyboardButton("ᴀᴅᴅ ᴍᴇ ᴛᴏ ʏᴏᴜʀ ɢʀᴏᴜᴘ", url=f'https://t.me/Grab_Yourslave_bot?startgroup=new')],
            [InlineKeyboardButton("ᴄʜᴀɴɴᴇʟ", url=f'https://t.me/BotupdateXD'), InlineKeyboardButton("ɢʀᴏᴜᴘ", url=f'{SUPPORT_CHAT}')],
            [InlineKeyboardButton("ʜᴇʟᴘ", callback_data='help'), InlineKeyboardButton("ᴄʀᴇᴅɪᴛꜱ", callback_data='credits')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await context.bot.edit_message_caption(chat_id=update.effective_chat.id, message_id=query.message.message_id, caption=start_text, reply_markup=reply_markup, parse_mode='markdown')

# application.add_handler(CallbackQueryHandler(button, pattern='^help$|^credits$|^back$|^user_help$|^games_help$'))
start_handler = CommandHandler('start', start)
application.add_handler(start_handler)
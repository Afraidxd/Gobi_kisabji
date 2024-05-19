from shivu import application
from telegram.ext import CallbackQueryHandler, CommandHandler
from telegram import Update

from .ptb_store import store_callback_handler, terminate, start_ag
from .harem import harem_callback
from .start import button
from .saleslist import sales_list_callback
from .owner import button_handler
from .rps import rps_button
from .spwan import button_click

# Ensure the button_click function is defined or imported
async def button_click(update: Update, context):
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
        name = last_characters.get(chat_id, {}).get('name', 'Unknown slave')
        await query.answer(text=f"ᴡᴇʟᴄᴏᴍᴇ, ᴜsᴇʀ ! ʏᴏᴜ'ᴠᴇ ʙᴇᴇɴ ᴀᴅᴅᴇᴅ ᴛᴏ ᴏᴜʀ sʏsᴛᴇᴍ ᴡɪᴛʜ ᴀɴ ɪɴɪᴛɪᴀʟ ʙᴀʟᴀɴᴄᴇ ᴏғ 50ᴋ", show_alert=True)

async def get_user_balance(user_id: int) -> int:
    user = await user_collection.find_one({"id": user_id})
    return user.get("balance") if user else None

async def cbq(update: Update, context):
    query = update.callback_query
    data = query.data

    if data.startswith('saleslist') or data.startswith('saleslist:close'):
        await sales_list_callback(update, context)
    elif data.startswith(('buy', 'pg', 'charcnf/', 'charback/')):
        await store_callback_handler(update, context)
    elif data.startswith('terminate'):
        await terminate(update, context)
    elif data.startswith('startwordle'):
        await start_ag(update, context)
    elif data.startswith('harem'):
        await harem_callback(update, context)
    elif data.startswith('lb_'):
        await button_handler(update, context)
    elif data in ('rock', 'paper', 'scissors', 'play_again'):
        await rps_button(update, context)
    elif data.startswith(('help', 'credits', 'back', 'user_help', 'game_help')): 
        await button(update, context)
    elif data == 'name':  # Add condition to handle 'name' pattern
        await button_click(update, context)

application.add_handler(CallbackQueryHandler(cbq, pattern='.*'))

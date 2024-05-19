# button_click.py (or wherever it is defined)
from telegram import Update
from telegram.ext import CallbackContext

# Ensure user_collection and last_characters are properly imported/defined
from .database import user_collection, last_characters

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
        await query.answer(text=f"ᴡᴇʟᴄᴏᴍᴇ, ᴜsᴇʀ! ʏᴏᴜ'ᴠᴇ ʙᴇᴇɴ ᴀᴅᴅᴇᴅ ᴛᴏ ᴏᴜʀ sʏsᴛᴇᴍ ᴡɪᴛʜ ᴀɴ ɪɴɪᴛɪᴀʟ ʙᴀʟᴀɴᴄᴇ ᴏғ 50ᴋ", show_alert=True)

async def get_user_balance(user_id: int) -> int:
    user = await user_collection.find_one({"id": user_id})
    return user.get("balance") if user else None

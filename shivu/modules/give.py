from pyrogram import filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from shivu import user_collection, shivuu

DEV_LIST = [6919722801, 6942997609]  # List of developer IDs

@shivuu.on_message(filters.command("give"))
async def gift(client, message):
    if message.from_user.id not in DEV_LIST:
        await message.reply_text("You are not authorized to use this command.")
        return

    if not message.reply_to_message:
        await message.reply_text("Please reply to a message to gift a character.")
        return

    receiver_id = message.reply_to_message.from_user.id
    receiver_username = message.reply_to_message.from_user.username
    receiver_first_name = message.reply_to_message.from_user.first_name

    if len(message.command) != 2:
        await message.reply_text("You need to provide a character ID!")
        return

    character_id = message.command[1]

    gift = {
        'receiver_id': receiver_id,
        'receiver_username': receiver_username,
        'receiver_first_name': receiver_first_name,
        'character': character_id
    }

    if receiver:
        await user_collection.update_one({'id': receiver_id}, {'$push': {'characters': gift['character']}})
    else:
        await user_collection.insert_one({
            'id': receiver_id,
            'username': gift['receiver_username'],
            'first_name': gift['receiver_first_name'],
            'characters': [gift['character']],
        })

    await message.reply_text(f"You have successfully gifted a character to [{gift['receiver_first_name']}](tg://user?id={receiver_id})!")
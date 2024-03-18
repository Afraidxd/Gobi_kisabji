from pyrogram import filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from shivu import user_collection, shivuu

pending_trades = {}


@shivuu.on_message(filters.command("trade"))
async def trade(client, message):
    sender_id = message.from_user.id

    if not message.reply_to_message:
        await message.reply_text("𝐘𝐨𝐮 𝐧𝐞𝐞𝐝 𝐭𝐨 𝐫𝐞𝐩𝐥𝐲 𝐭𝐨 𝐚 𝐮𝐬𝐞𝐫'𝐬 𝐦𝐞𝐬𝐬𝐚𝐠𝐞 𝐭𝐨 𝐭𝐫𝐚𝐝𝐞 𝐚 𝐜𝐚𝐫!")
        return

    receiver_id = message.reply_to_message.from_user.id

    if sender_id == receiver_id:
        await message.reply_text("𝐘𝐨𝐮 𝐜𝐚𝐧'𝐭 𝐭𝐫𝐚𝐝𝐞 𝐚 𝐜𝐚𝐫 𝐰𝐢𝐭𝐡 𝐲𝐨𝐮𝐫𝐬𝐞𝐥𝐟!")
        return

    if len(message.command) != 3:
        await message.reply_text("𝐘𝐨𝐮 𝐧𝐞𝐞𝐝 𝐭𝐨 𝐩𝐫𝐨𝐯𝐢𝐝𝐞 𝐭𝐰𝐨 𝐜𝐚𝐫 𝐈𝐃𝐬!")
        return

    sender_character_id, receiver_character_id = message.command[1], message.command[2]

    sender = await user_collection.find_one({'id': sender_id})
    receiver = await user_collection.find_one({'id': receiver_id})

    sender_character = next((character for character in sender['characters'] if character['id'] == sender_character_id), None)
    receiver_character = next((character for character in receiver['characters'] if character['id'] == receiver_character_id), None)

    if not sender_character:
        await message.reply_text("𝐘𝐨𝐮 𝐝𝐨𝐧'𝐭 𝐡𝐚𝐯𝐞 𝐭𝐡𝐞 𝐜𝐚𝐫 𝐲𝐨𝐮'𝐫𝐞 𝐭𝐫𝐲𝐢𝐧𝐠 𝐭𝐨 𝐭𝐫𝐚𝐝𝐞!")
        return

    if not receiver_character:
        await message.reply_text("𝐓𝐡𝐞 𝐨𝐭𝐡𝐞𝐫 𝐮𝐬𝐞𝐫 𝐝𝐨𝐞𝐬𝐧'𝐭 𝐡𝐚𝐯𝐞 𝐭𝐡𝐞 𝐜𝐚𝐫 𝐭𝐡𝐞𝐲'𝐫𝐞 𝐭𝐫𝐲𝐢𝐧𝐠 𝐭𝐨 𝐭𝐫𝐚𝐝𝐞!")
        return






    if len(message.command) != 3:
        await message.reply_text("/trade [Your Character ID] [Other User Character ID]!")
        return

    sender_character_id, receiver_character_id = message.command[1], message.command[2]

    
    pending_trades[(sender_id, receiver_id)] = (sender_character_id, receiver_character_id)

    
    keyboard = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("𝐂𝐨𝐧𝐟𝐢𝐫𝐦 𝐓𝐫𝐚𝐝𝐞", callback_data="confirm_trade")],
            [InlineKeyboardButton("𝐂𝐚𝐧𝐜𝐞𝐥 𝐓𝐫𝐚𝐝𝐞", callback_data="cancel_trade")]
        ]
    )

    await message.reply_text(f"{message.reply_to_message.from_user.mention}, do you accept this trade?", reply_markup=keyboard)


@shivuu.on_callback_query(filters.create(lambda _, __, query: query.data in ["confirm_trade", "cancel_trade"]))
async def on_callback_query(client, callback_query):
    receiver_id = callback_query.from_user.id

    
    for (sender_id, _receiver_id), (sender_character_id, receiver_character_id) in pending_trades.items():
        if _receiver_id == receiver_id:
            break
    else:
        await callback_query.answer("This is not for you!", show_alert=True)
        return

    if callback_query.data == "confirm_trade":
        
        sender = await user_collection.find_one({'id': sender_id})
        receiver = await user_collection.find_one({'id': receiver_id})

        sender_character = next((character for character in sender['characters'] if character['id'] == sender_character_id), None)
        receiver_character = next((character for character in receiver['characters'] if character['id'] == receiver_character_id), None)

        
        
        sender['characters'].remove(sender_character)
        receiver['characters'].remove(receiver_character)

        
        await user_collection.update_one({'id': sender_id}, {'$set': {'characters': sender['characters']}})
        await user_collection.update_one({'id': receiver_id}, {'$set': {'characters': receiver['characters']}})

        
        sender['characters'].append(receiver_character)
        receiver['characters'].append(sender_character)

        
        await user_collection.update_one({'id': sender_id}, {'$set': {'characters': sender['characters']}})
        await user_collection.update_one({'id': receiver_id}, {'$set': {'characters': receiver['characters']}})

        
        del pending_trades[(sender_id, receiver_id)]

        await callback_query.message.edit_text(f"𝐘𝐨𝐮 𝐡𝐚𝐯𝐞 𝐬𝐮𝐜𝐜𝐞𝐬𝐬𝐟𝐮𝐥𝐥𝐲 𝐭𝐫𝐚𝐝𝐞𝐝 𝐲𝐨𝐮𝐫 𝐜𝐚𝐫 𝐰𝐢𝐭𝐡 {callback_query.message.reply_to_message.from_user.mention}!")

    elif callback_query.data == "cancel_trade":
        
        del pending_trades[(sender_id, receiver_id)]

        await callback_query.message.edit_text("❌️ 𝐒𝐚𝐝 𝐭𝐫𝐚𝐝𝐞 𝐂𝐚𝐧𝐜𝐞𝐥𝐥𝐞𝐝......")




pending_gifts = {}


@shivuu.on_message(filters.command("gift"))
async def gift(client, message):
    sender_id = message.from_user.id

    if not message.reply_to_message:
        await message.reply_text("𝐘𝐨𝐮 𝐧𝐞𝐞𝐝 𝐭𝐨 𝐫𝐞𝐩𝐥𝐲 𝐭𝐨 𝐚 𝐮𝐬𝐞𝐫'𝐬 𝐦𝐞𝐬𝐬𝐚𝐠𝐞 𝐭𝐨 𝐠𝐢𝐟𝐭 𝐚 𝐜𝐚𝐫!")
        return

    receiver_id = message.reply_to_message.from_user.id
    receiver_username = message.reply_to_message.from_user.username
    receiver_first_name = message.reply_to_message.from_user.first_name

    if sender_id == receiver_id:
        await message.reply_text("𝐘𝐨𝐮 𝐜𝐚𝐧'𝐭 𝐠𝐢𝐟𝐭 𝐚 𝐜𝐚𝐫 𝐭𝐨 𝐲𝐨𝐮𝐫𝐬𝐞𝐥𝐟!")
        return

    if len(message.command) != 2:
        await message.reply_text("𝐘𝐨𝐮 𝐧𝐞𝐞𝐝 𝐭𝐨 𝐩𝐫𝐨𝐯𝐢𝐝𝐞 𝐚 𝐜𝐚𝐫 𝐈𝐃!")
        return

    character_id = message.command[1]

    sender = await user_collection.find_one({'id': sender_id})

    character = next((character for character in sender['characters'] if character['id'] == character_id), None)

    if not character:
        await message.reply_text("𝐘𝐨𝐮 𝐝𝐨𝐧'𝐭 𝐡𝐚𝐯𝐞 𝐭𝐡𝐢𝐬 𝐜𝐚𝐫 𝐢𝐧 𝐲𝐨𝐮𝐫 𝐆𝐚𝐫𝐚𝐠𝐞!")
        return

    
    pending_gifts[(sender_id, receiver_id)] = {
        'character': character,
        'receiver_username': receiver_username,
        'receiver_first_name': receiver_first_name
    }

    
    keyboard = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("𝐂𝐨𝐧𝐟𝐢𝐫𝐦 𝐆𝐢𝐟𝐭", callback_data="confirm_gift")],
            [InlineKeyboardButton("𝐂𝐚𝐧𝐜𝐞𝐥 𝐆𝐢𝐟𝐭", callback_data="cancel_gift")]
        ]
    )

    await message.reply_text(f"𝐝𝐨 𝐘𝐨𝐮 𝐑𝐞𝐚𝐥𝐥𝐲 𝐖𝐚𝐧𝐧𝐬 𝐓𝐨 𝐆𝐢𝐟𝐭 {message.reply_to_message.from_user.mention} ?", reply_markup=keyboard)

@shivuu.on_callback_query(filters.create(lambda _, __, query: query.data in ["confirm_gift", "cancel_gift"]))
async def on_callback_query(client, callback_query):
    sender_id = callback_query.from_user.id

    
    for (_sender_id, receiver_id), gift in pending_gifts.items():
        if _sender_id == sender_id:
            break
    else:
        await callback_query.answer("𝐓𝐡𝐢𝐬 𝐢𝐬 𝐧𝐨𝐭 𝐟𝐨𝐫 𝐲𝐨𝐮!", show_alert=True)
        return

    if callback_query.data == "confirm_gift":
        
        sender = await user_collection.find_one({'id': sender_id})
        receiver = await user_collection.find_one({'id': receiver_id})

        
        sender['characters'].remove(gift['character'])
        await user_collection.update_one({'id': sender_id}, {'$set': {'characters': sender['characters']}})

        
        if receiver:
            await user_collection.update_one({'id': receiver_id}, {'$push': {'characters': gift['character']}})
        else:
            
            await user_collection.insert_one({
                'id': receiver_id,
                'username': gift['receiver_username'],
                'first_name': gift['receiver_first_name'],
                'characters': [gift['character']],
            })

        
        del pending_gifts[(sender_id, receiver_id)]

        await callback_query.message.edit_text(f"𝐘𝐨𝐮 𝐡𝐚𝐯𝐞 𝐬𝐮𝐜𝐜𝐞𝐬𝐬𝐟𝐮𝐥𝐥𝐲 𝐠𝐢𝐟𝐭𝐞𝐝 𝐲𝐨𝐮𝐫 𝐜𝐚𝐫 𝐭𝐨 [{gift['receiver_first_name']}](tg://user?id={receiver_id})!")



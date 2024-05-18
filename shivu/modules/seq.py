import urllib.request
from pymongo import ReturnDocument

from telegram import Update
from telegram.ext import CommandHandler, CallbackContext

from shivu import application, collection, db, CHARA_CHANNEL_ID, sudo_users

owner_id = 6747352706


async def get_next_sequence_number(sequence_name):
    sequence_collection = db.sequences
    sequence_document = await sequence_collection.find_one_and_update(
        {'_id': sequence_name}, 
        {'$inc': {'sequence_value': 0}},  # Set increment to 0 to only retrieve the current value
        return_document=ReturnDocument.AFTER
    )
    if not sequence_document:
        await sequence_collection.insert_one({'_id': sequence_name, 'sequence_value': 0})
        return 0
    return sequence_document['sequence_value']

async def seq(update, context):
    user_id = int(update.effective_user.id)
    if user_id == owner_id:  # Replace owner_id with the actual owner's ID
        sequence_name = "character_id"  # Replace "your_sequence_name" with the actual sequence name
        current_sequence = await get_next_sequence_number(sequence_name)
        await update.message.reply_text(f"Current sequence: {current_sequence}")
    else:
        await update.message.reply_text("You are not authorized to use this command.")

async def cseq(update, context):
    user_id = int(update.effective_user.id)
    if user_id == owner_id:  # Replace owner_id with the actual owner's ID
        sequence_name = "character_id"  # Replace "character_id" with the actual sequence name
        # Parse the new sequence value from the command arguments
        try:
            new_sequence = int(context.args[0])
            sequence_collection = db.sequences
            await sequence_collection.update_one({'_id': sequence_name}, {'$set': {'sequence_value': new_sequence}})
            await update.message.reply_text(f"Sequence updated to: {new_sequence}")
        except (IndexError, ValueError):
            await update.message.reply_text("Invalid sequence value. Please provide a valid integer.")
    else:
        await update.message.reply_text("You are not authorized to use this command.")


import tempfile

async def cp(update, context):
    user_id = update.effective_user.id
    if user_id == owner_id:  # Replace owner_id with the actual owner's ID
        all_characters = await collection.distinct("_id")
        all_characters = [str(char_id) for char_id in all_characters]  # Convert ObjectId to string
        if all_characters:
            # Create a temporary text file
            with tempfile.NamedTemporaryFile(mode='w', delete=False) as file:
                file.write('\n'.join(all_characters))
                file_name = file.name
            # Send the text file as a document
            await update.message.reply_document(document=open(file_name, 'rb'), filename='character_ids.txt')
            # Remove the temporary text file
            os.remove(file_name)
        else:
            await update.message.reply_text("No cars found in the database.")
    else:
        await update.message.reply_text("You are not authorized to use this command.")

# Add the handler for the /cp command
application.add_handler(CommandHandler("cp", cp))


application.add_handler(CommandHandler("seq", seq, block=True))


application.add_handler(CommandHandler("cseq", cseq, block=True))

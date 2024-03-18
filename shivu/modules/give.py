from telegram import Update
from telegram.ext import CallbackContext, CommandHandler
from pymongo import MongoClient

from shivu import application, OWNER_ID, mongo_url

client = MongoClient(mongo_url)
db = client["characters"]
characters_collection = db["characters"]

async def give(update: Update, context: CallbackContext) -> None:
    if update.effective_user.id != OWNER_ID:
        await update.message.reply_text("You are not authorized to use this command.")
        return

    replied_user = update.message.reply_to_message.from_user
    if replied_user is None:
        await update.message.reply_text("Please reply to a user to give them a character.")
        return

    character_id = context.args[0] if len(context.args) > 0 else None
    
    if character_id is None:
        await update.message.reply_text("Please provide the ID number of the character to give.")
        return

    character = characters_collection.find_one({"id": character_id})
    if character:
        # Update the character's owner to the replied user's ID
        characters_collection.update_one({"id": character_id}, {"$set": {"owner_id": replied_user.id}})
        response = f"Character with ID '{character_id}' has been given to user '{replied_user.username}'."
    else:
        response = f"Character with ID '{character_id}' not found in the database."

    await update.message.reply_text(response)

application.add_handler(CommandHandler("give", give))

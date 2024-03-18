from telegram import Update
from telegram.ext import CallbackContext, CommandHandler
from pymongo import MongoClient
from shivu import db, collection, top_global_groups_collection, group_user_totals_collection, user_collection, user_totals_collection
from shivu import application, shivuu, LOGGER 
from shivu.modules import ALL_MODULES
client = MongoClient("mongo_url")
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

    id = context.args[0] if context.args else None

    if id is None:
        await update.message.reply_text("Please provide the ID number of the character to give.")
        return

    character = characters_collection.find_one({"id": collection})
    if character:
        # Update the character's owner to the replied user's ID
        characters_collection.update_one({"id": collection}, {"$set": {"owner_id": replied_user.id}})
        response = f"Character with ID '{id}' has been given to user '{replied_user.username}'."
    else:
        response = f"Character with ID '{id}' not found in the database."

    await update.message.reply_text(response)

application.add_handler(CommandHandler("give", give))

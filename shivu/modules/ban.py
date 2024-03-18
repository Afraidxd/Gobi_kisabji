
from telegram import Update
from telegram.ext import CallbackContext, CommandHandler, Updater

from pymongo import MongoClient

from shivu import OWNER_ID, mongo_url

# MongoDB connection
client = MongoClient(mongo_url)
db = client["bot_db"]
blocked_users_collection = db["blocked_users"]

def is_owner(update: Update) -> bool:
    return update.message.from_user.id == OWNER_ID

def block_user(update: Update, context: CallbackContext):
    if not is_owner(update):
        update.message.reply_text("You are not authorized to use this command.")
        return
    user_id = update.message.reply_to_message.from_user.id
    blocked_users_collection.insert_one({"user_id": user_id})
    update.message.reply_text("User blocked successfully.")

def unblock_user(update: Update, context: CallbackContext):
    if not is_owner(update):
        update.message.reply_text("You are not authorized to use this command.")
        return
    user_id = update.message.reply_to_message.from_user.id
    blocked_users_collection.delete_one({"user_id": user_id})
    update.message.reply_text("User unblocked successfully.")

def banlist(update: Update, context: CallbackContext):
    if not is_owner(update):
        update.message.reply_text("You are not authorized to use this command.")
        return
    banned_users = blocked_users_collection.find()
    banned_user_ids = [str(user["user_id"]) for user in banned_users]
    update.message.reply_text("Banned users:\n" + "\n".join(banned_user_ids))

def check(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    banned_user = blocked_users_collection.find_one({"user_id": user_id})
    if banned_user:
        update.message.reply_text("You are banned.")
    else:
        update.message.reply_text("You are not banned.")

# Add handlers for the commands
updater = Updater("YOUR_TOKEN", use_context=True)
dispatcher = updater.dispatcher

dispatcher.add_handler(CommandHandler("block", block_user))
dispatcher.add_handler(CommandHandler("unblock", unblock_user))
dispatcher.add_handler(CommandHandler("banlist", banlist))
dispatcher.add_handler(CommandHandler("check", check))

print ("no")

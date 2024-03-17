import sys
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext
import pymongo
from shivu import OWNER_ID, mongo_url

# Connect to MongoDB
client = pymongo.MongoClient(mongo_url)
db = client[config.MONGO_DB]

# Define the command handler functions
def is_owner(update: Update):
    return update.message.from_user.id == OWNER_ID

def block_user(update: Update, context: CallbackContext):
    if not is_owner(update):
        update.message.reply_text("You are not authorized to use this command.")
        return
    user_id = update.message.reply_to_message.from_user.id
    collection = db["blocked_users"]
    collection.insert_one({"user_id": user_id})
    update.message.reply_text("User blocked successfully.")

def unblock_user(update: Update, context: CallbackContext):
    if not is_owner(update):
        update.message.reply_text("You are not authorized to use this command.")
        return
    user_id = update.message.reply_to_message.from_user.id
    collection = db["blocked_users"]
    collection.delete_many({"user_id": user_id})
    update.message.reply_text("User unblocked successfully.")

def get_blocklist(update: Update, context: CallbackContext):
    if not is_owner(update):
        update.message.reply_text("You are not authorized to use this command.")
        return
    collection = db["blocked_users"]
    blocked_users = collection.find()
    blocklist = [str(user["user_id"]) for user in blocked_users]
    update.message.reply_text(f"Blocked Users: {', '.join(blocklist)}")

def check_block(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    collection = db["blocked_users"]
    blocked_user = collection.find_one({"user_id": user_id})
    if blocked_user:
        update.message.reply_text("You are blocked.")
    else:
        update.message.reply_text("You are not blocked.")

# Create an updater and dispatcher
updater = Updater(config.TOKEN)
dispatcher = updater.dispatcher

# Add the command handlers to the dispatcher
dispatcher.add_handler(CommandHandler("block", block_user))
dispatcher.add_handler(CommandHandler("unblock", unblock_user))
dispatcher.add_handler(CommandHandler("blocklist", get_blocklist))
dispatcher.add_handler(CommandHandler("check", check_block))

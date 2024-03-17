import sys
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext
import pymongo
from shivu import OWNER_ID, mongo_url

# Connect to MongoDB
client = pymongo.MongoClient(config.MONGO_URI)
db = client[config.MONGO_DB]

# Define the command handler functions
def is_owner(update: Update):
    return update.message.from_user.id == config.OWNER_ID

def ban_user(update: Update, context: CallbackContext):
if not is_owner(update):
 update.message.reply_text("You are not authorized to use this command.")
 return
user_id = update.message.reply_to_message.from_user.id
collection = db["banned_users"]
collection.insert_one({"user_id": user_id})
update.message.reply_text("User banned successfully.")

def unban_user(update: Update, context: CallbackContext):
if not is_owner(update):
 update.message.reply_text("You are not authorized to use this command.")
 return
user_id = update.message.reply_to_message.from_user.id
collection = db["banned_users"]
collection.delete_many({"user_id": user_id})
update.message.reply_text("User unbanned successfully.")

def get_banlist(update: Update, context: CallbackContext):
if not is_owner(update):
 update.message.reply_text("You are not authorized to use this command.")
 return
collection = db["banned_users"]
banned_users = collection.find()
banlist = [str(user["user_id"]) for user in banned_users]
update.message.reply_text(f"Banned Users: {', '.join(banlist)}")

def check_ban(update: Update, context: CallbackContext):
user_id = update.message.from_user.id
collection = db["banned_users"]
banned_user = collection.find_one({"user_id": user_id})
if banned_user:
 update.message.reply_text("You are banned.")
else:
 update.message.reply_text("You are not banned.")

# Create an updater and dispatcher
updater = Updater(config.BOT_TOKEN)
dispatcher = updater.dispatcher

# Add the command handlers to the dispatcher
dispatcher.add_handler(CommandHandler("ban", ban_user))
dispatcher.add_handler(CommandHandler("unban", unban_user))
dispatcher.add_handler(CommandHandler("banlist", get_banlist))
dispatcher.add_handler(CommandHandler("check", check_ban))

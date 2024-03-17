
from os import environ, execle
import sys
from telegram import Update
from telegram.ext import CallbackContext

# Assume the following functions are already defined:
# is_owner(update) -> checks if the user is the owner
# db -> MongoDB connection

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
    collection.delete_one({"user_id": user_id})
    update.message.reply_text("User unblocked successfully.")

def banlist(update: Update, context: CallbackContext):
    if not is_owner(update):
        update.message.reply_text("You are not authorized to use this command.")
        return
    collection = db["blocked_users"]
    banned_users = collection.find()
    banned_user_ids = [str(user["user_id"]) for user in banned_users]
    update.message.reply_text("Banned users:\n" + "\n".join(banned_user_ids))

def check(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    collection = db["blocked_users"]
    banned_user = collection.find_one({"user_id": user_id})
    if banned_user:
        update.message.reply_text("You are banned.")
    else:
        update.message.reply_text("You are not banned.")

# Add handlers for the commands
dispatcher.add_handler(CommandHandler("block", block_user))
dispatcher.add_handler(CommandHandler("unblock", unblock_user))
dispatcher.add_handler(CommandHandler("banlist", banlist))
dispatcher.add_handler(CommandHandler("checkban", check))

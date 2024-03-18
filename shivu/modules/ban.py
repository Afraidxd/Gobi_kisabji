from telegram import Update
from telegram.ext import CallbackContext, CommandHandler
from pymongo import MongoClient

from shivu import application, OWNER_ID, mongo_url 

client = MongoClient("mongo_url")
db = client["telegram_bot"]
ban_collection = db["ban_list"]

async def block(update: Update, context: CallbackContext) -> None:
    if update.effective_user.id != OWNER_ID:
        await update.message.reply_text("You are not authorized to use this command.")
        return

    user_id = update.message.reply_to_message.from_user.id
    if ban_collection.find_one({"user_id": user_id}):
        await update.message.reply_text(f"User {user_id} is already blocked.")
    else:
        ban_collection.insert_one({"user_id": user_id})
        await update.message.reply_text(f"User {user_id} has been blocked.")

async def unblock(update: Update, context: CallbackContext) -> None:
    if update.effective_user.id != OWNER_ID:
        await update.message.reply_text("You are not authorized to use this command.")
        return

    user_id = update.message.reply_to_message.from_user.id
    result = ban_collection.delete_one({"user_id": user_id})
    if result.deleted_count > 0:
        await update.message.reply_text(f"User {user_id} has been unblocked.")
    else:
        await update.message.reply_text(f"User {user_id} is not blocked.")

async def banlist(update: Update, context: CallbackContext) -> None:
    if update.effective_user.id != OWNER_ID:
        await update.message.reply_text("You are not authorized to use this command.")
        return

    banned_users = [doc["user_id"] for doc in ban_collection.find()]
    await update.message.reply_text(f"Banned Users: {', '.join(map(str, banned_users))}")

async def check(update: Update, context: CallbackContext) -> None:
    user_id = update.effective_user.id
    if ban_collection.find_one({"user_id": user_id}):
        await update.message.reply_text("You are blocked. Please ask the owner to unblock.")
    else:
        await update.message.reply_text("You are not blocked.")

application.add_handler(CommandHandler("block", block, block=False))
application.add_handler(CommandHandler("unblock", unblock, block=False))
application.add_handler(CommandHandler("banlist", banlist, block=False))
application.add_handler(CommandHandler("check", check, block=False))

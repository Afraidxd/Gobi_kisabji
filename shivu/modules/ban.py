from telegram import Update, Bot
from telegram.ext import CallbackContext
from pymongo import MongoClient
from shivu import OWNER_ID, mongo_url, TOKEN

# MongoDB connection
client = MongoClient(mongo_url)
db = client["bot_db"]
blocked_users_collection = db["blocked_users"]

def add_blacklist(user_id: int):
    blocked_users_collection.insert_one({"user_id": user_id})

def remove_blacklist(user_id: int):
    blocked_users_collection.delete_one({"user_id": user_id})

def get_blacklisted():
    banned_users = blocked_users_collection.find()
    return [user["user_id"] for user in banned_users]

def is_owner(update: Update) -> bool:
    return update.message.from_user.id == OWNER_ID

def blacklist_user(bot: Bot, update: Update):
    if not is_owner(update):
        update.message.reply_text("You are not authorized to use this command.")
        return
    try:
        user_id = int(update.message.text.split(" ", maxsplit=1)[1])
    except (IndexError, ValueError):
        update.message.reply_text("Please provide a valid user ID.")
        return
    add_blacklist(user_id)
    update.message.reply_text(f"User {user_id} blacklisted successfully.")

def unblacklist_user(bot: Bot, update: Update):
    if not is_owner(update):
        update.message.reply_text("You are not authorized to use this command.")
        return
    try:
        user_id = int(update.message.text.split(" ", maxsplit=1)[1])
    except (IndexError, ValueError):
        update.message.reply_text("Please provide a valid user ID.")
        return
    remove_blacklist(user_id)
    update.message.reply_text(f"User {user_id} unblacklisted successfully.")

def list_blacklisted_users(bot: Bot, update: Update):
    if not is_owner(update):
        update.message.reply_text("You are not authorized to use this command.")
        return
    banned_user_ids = get_blacklisted()
    update.message.reply_text("List of Blacklisted Users:\n" + "\n".join(map(str, banned_user_ids)))

# Create a Bot instance
bot = Bot(token=TOKEN)

# Start the Bot
updater.start_polling()

# Poll for updates and handle commands directly
while True:
    updates = bot.get_updates()
    for update in updates:
        if update.message.text.startswith('/blacklist'):
            blacklist_user(bot, update)
        elif update.message.text.startswith('/unblacklist'):
            unblacklist_user(bot, update)
        elif update.message.text.startswith('/listblacklisted'):
            list_blacklisted_users(bot, update)

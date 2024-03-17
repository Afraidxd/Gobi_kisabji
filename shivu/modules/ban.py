import pymongo
from pyrogram import Client, filters
from shivu import OWNER_ID, BOT_TOKEN, API_ID, API_HASH

# Connect to MongoDB
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["ban_db"]
ban_collection = db["bans"]

# Initialize the Bot
app = Client("my_bot", bot_token=BOT_TOKEN, api_id=API_ID, api_hash=API_HASH)

# Ban Command
@app.on_message(filters.user(OWNER_ID) & filters.command("ban"))
def ban_user(client, message):
    user_id = message.text.split(" ")[1]
    ban_collection.insert_one({"user_id": user_id})
    message.reply(f"User {user_id} has been banned.")

# Unban Command
@app.on_message(filters.user(OWNER_ID) & filters.command("unban"))
def unban_user(client, message):
    user_id = message.text.split(" ")[1]
    ban_collection.delete_one({"user_id": user_id})
    message.reply(f"User {user_id} has been unbanned.")

# Banlist Command
@app.on_message(filters.user(OWNER_ID) & filters.command("banlist"))
def ban_list(client, message):
    banned_users = [ban["user_id"] for ban in ban_collection.find()]
    message.reply(f"Banned Users: {', '.join(banned_users)}")

# Check Command
@app.on_message(filters.command("check"))
def check_ban(client, message):
    user_id = message.text.split(" ")[1]
    if ban_collection.find_one({"user_id": user_id}):
        message.reply(f"User {user_id} is banned.")
    else:
        message.reply(f"User {user_id} is not banned.")

app.run()

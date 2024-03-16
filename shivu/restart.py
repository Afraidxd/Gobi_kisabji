import os
import subprocess
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext

# Define the token for your Telegram bot
TOKEN = "7152549014:AAGQl39KqsCe7g8_oZO2tFa12tZOAIP75tY"
HEROKU_API_KEY = os.getenv("dd4d1c03-103c-457d-8905-72ad12656d7a")

# Define the command handler for the /restart command
def restart(update: Update, context: CallbackContext):
    chat_id = update.message.chat_id
    context.bot.send_message(chat_id=chat_id, text="Restarting dyno...")
    
    # Restart the Heroku dyno using the Heroku API key
    subprocess.run(["heroku", "restart", "--app=YOUR_HEROKU_APP_NAME", "--api-key=" + HEROKU_API_KEY])

# Create an instance of the Updater class with your bot's token
updater = Updater(token=TOKEN, use_context=True)

# Get the dispatcher to register handlers
dispatcher = updater.dispatcher

# Register the /restart command handler
dispatcher.add_handler(CommandHandler("restart", restart))

# Start the Bot
updater.start_polling()
updater.idle()

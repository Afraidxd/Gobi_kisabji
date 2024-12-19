import importlib
import re
from flask import Flask, request
from telegram import Update
from telegram.ext import Application
from shivu import LOGGER  # Custom logger
from shivu.modules import ALL_MODULES
from config import TOKEN  # Import bot token from your config file

# Initialize Flask app
app = Flask(__name__)

# Initialize Telegram bot application
application = Application.builder().token(TOKEN).build()

# Escape markdown function
def escape_markdown(text):
    escape_chars = r'\*_`\\~>#+-=|{}.!'
    return re.sub(r'([%s])' % re.escape(escape_chars), r'\\\1', text)

@app.route("/webhook", methods=["POST"])
def webhook():
    """Handle incoming Telegram updates via webhook."""
    update = Update.de_json(request.json, application.bot)
    application.process_update(update)
    return "OK", 200

@app.route("/", methods=["GET"])
def index():
    """Root endpoint for health checks."""
    return "Bot is running via webhook!", 200

def main():
    """Start the bot and set webhook."""
    # Import all modules dynamically
    for module_name in ALL_MODULES:
        importlib.import_module("shivu.modules." + module_name)

    LOGGER.info("Starting bot with webhook...")

    # Choreo will provide an HTTPS endpoint, set it as the webhook URL
    WEBHOOK_URL = "https://<your-choreo-generated-url>/webhook"

    # Set the webhook for Telegram bot
    application.bot.set_webhook(url=WEBHOOK_URL)
    LOGGER.info(f"Webhook set to: {WEBHOOK_URL}")

    # Run the Flask server
    app.run(host="0.0.0.0", port=5000)

if __name__ == "__main__":
    main()

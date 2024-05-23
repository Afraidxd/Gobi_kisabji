import importlib
import logging
from telegram.ext import Application
from shivu import application, LOGGER
from shivu.modules import ALL_MODULES
from bot_commands import add_handlers

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def main():
    logger.info("Starting bot")

    # Initialize the application with your token
    app = Application.builder().token("YOUR_TELEGRAM_BOT_TOKEN").build()

    # Dynamically import all modules
    for module_name in ALL_MODULES:
        importlib.import_module(f"shivu.modules.{module_name}")

    # Add handlers from bot_commands
    add_handlers(app)

    logger.info("Bot started")
    app.run_polling()

if __name__ == '__main__':
    main()
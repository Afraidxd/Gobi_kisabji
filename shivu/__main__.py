import logging
from telegram.ext import Application
from bot_commands import add_handlers
from shivu import application as app 
# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def main():
    logger.info("Starting bot")
    application = Application.builder().token("app").build()

    # Add handlers from bot_commands
    add_handlers(application)

    logger.info("Bot started")
    application.run_polling()

if __name__ == '__main__':
    main()
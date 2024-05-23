import importlib
import time
import random
import re
import asyncio
from html import escape

from typing import Optional
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram import Update
from telegram.ext import Updater, CallbackQueryHandler
from telegram.ext import CommandHandler, MessageHandler, filters

from telegram.ext import CommandHandler, CallbackContext, MessageHandler, CallbackQueryHandler, filters

from shivu import collection, top_global_groups_collection, group_user_totals_collection, user_collection, user_totals_collection, shivuu 
from shivu import application, LOGGER
from shivu.modules import ALL_MODULES

from telegram.ext import Application
for module_name in ALL_MODULES:
    importlib.import_module(f"shivu.modules.{module_name}")

from shivu import application as app 
# Enable logging


def main():
    
    application = Application.builder().token("app").build()

    # Add handlers from bot_commands
   application.add_handlers(application)

    logger.info("Bot started")
    application.run_polling()

if __name__ == '__main__':
    main()
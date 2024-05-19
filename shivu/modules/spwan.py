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

locks = {}
message_counters = {}
spam_counters = {}
last_characters = {}
sent_characters = {}
first_correct_guesses = {}
message_counts = {}

for module_name in ALL_MODULES:
    imported_module = importlib.import_module("shivu.modules." + module_name)

last_user = {}
warned_users = {}

def escape_markdown(text):
    escape_chars = r'\*_`\\~>#+-=|{}.!'
    return re.sub(r'([%s])' % re.escape(escape_chars), r'\\\1', text)

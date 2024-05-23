import importlib
import re

from telegram import Update
from telegram.ext import CommandHandler, CallbackContext

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

last_user = {}
warned_users = {}
started_users = set()  # Keep track of users who have started the bot in private

def escape_markdown(text):
    escape_chars = r'\*_`\\~>#+-=|{}.!'
    return re.sub(r'([%s])' % re.escape(escape_chars), r'\\\1', text)

def start(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    started_users.add(user_id)
    update.message.reply_text("Thank you for starting the bot in private. You can now use it in groups!")

def check_private_start(func):
    def wrapper(update: Update, context: CallbackContext, *args, **kwargs):
        user_id = update.effective_user.id
        if user_id not in started_users:
            update.message.reply_text("Please start the bot in private first.")
            return
        return func(update, context, *args, **kwargs)
    return wrapper

def decorate_all_handlers(module):
    for attr_name in dir(module):
        attr = getattr(module, attr_name)
        if isinstance(attr, CommandHandler):
            handler = attr
            handler.callback = check_private_start(handler.callback)

def main():
    application.add_handler(CommandHandler("start", start))

    for module_name in ALL_MODULES:
        imported_module = importlib.import_module("shivu.modules." + module_name)
        decorate_all_handlers(imported_module)
    
    LOGGER.info("Starting bot...")
    shivuu.start()  # Assuming shivuu.start() starts the bot using your framework

if __name__ == "__main__":
    main()
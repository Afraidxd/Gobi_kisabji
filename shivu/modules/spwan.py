import importlib
import re
from typing import Optional

from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackContext, MessageHandler, filters

from shivu import collection, user_collection, application, LOGGER
from shivu.modules import ALL_MODULES

# Initialize user interactions collection
user_interactions_collection = collection('user_interactions')

# Import all modules dynamically
for module_name in ALL_MODULES:
    importlib.import_module("shivu.modules." + module_name)

# Function to escape markdown characters
def escape_markdown(text):
    escape_chars = r'\*_`\\~>#+-=|{}.!'
    return re.sub(r'([%s])' % re.escape(escape_chars), r'\\\1', text)

# Command to be run when the user starts the bot in private
async def start_private(update: Update, context: CallbackContext) -> None:
    user_id = update.effective_user.id
    await user_interactions_collection.update_one(
        {'user_id': user_id},
        {'$set': {'started_private': True}},
        upsert=True
    )
    await update.message.reply_text('Bot started in private chat! You can now use commands in groups.')

# Command to handle the favorite car functionality
async def fav(update: Update, context: CallbackContext) -> None:
    user_id = update.effective_user.id

    # Check if the user has started the bot in private
    user_interaction = await user_interactions_collection.find_one({'user_id': user_id})
    if not user_interaction or not user_interaction.get('started_private'):
        await update.message.reply_text('Please start the bot in private chat first before using this command.')
        return

    if not context.args:
        await update.message.reply_text('Please provide Car ID...')
        return

    character_id = context.args[0]

    user = await user_collection.find_one({'id': user_id})
    if not user:
        await update.message.reply_text('You have not acquired any car yet...')
        return

    character = next((c for c in user['characters'] if c['id'] == character_id), None)
    if not character:
        await update.message.reply_text('This car is not in your collection')
        return

    user['favorites'] = [character_id]

    await user_collection.update_one({'id': user_id}, {'$set': {'favorites': user['favorites']}})

    await update.message.reply_text(f'Car {character["name"]} is your favorite now...')

def main() -> None:
    """Run bot."""
    application.add_handler(CommandHandler("start", start_private))
    application.add_handler(CommandHandler("favorite", fav))

    application.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()

import importlib
import random
from datetime import timedelta
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CommandHandler, CallbackContext, CallbackQueryHandler
from shivu import user_collection, shivuu, application
from shivu.modules import ALL_MODULES

locks = {}
message_counters = {}
spam_counters = {}
last_characters = {}
sent_characters = {}
first_correct_guesses = {}
message_counts = {}
user_tokens = {}
current_guess = {}

OWNER_ID = 6747352706

for module_name in ALL_MODULES:
    imported_module = importlib.import_module("shivu.modules." + module_name)

last_user = {}
warned_users = {}

# List of images and their correct answers
images = [
    ("https://telegra.ph/file/a6ef02040254d51d60360.jpg", "🐺"),
    ("https://telegra.ph/file/59c070e068e9d379a3270.jpg", "🦬"),
    ("https://telegra.ph/file/5185ad733940b4447031e.jpg", "🍞"),
    ("https://telegra.ph/file/2424eb24186f2378ef363.jpg", "🧄"),
    ("https://telegra.ph/file/d3864edbee52ac19bb6f2.jpg", "🦥"),
    ("https://telegra.ph/file/249af44d79d33c27ce622.jpg", "🫓"),
    ("https://telegra.ph/file/d4c03930563c9f9062868.jpg", "🦏"),
    ("https://telegra.ph/file/c3e8b7ea12c560e0dfcd6.jpg", "🗻"),
    ("path/to/image9.jpg", "Correct Answer 9"),
    ("path/to/image10.jpg", "Correct Answer 10")
]

def get_random_image():
    return random.choice(images)

async def send_image(update: Update, context: CallbackContext) -> None:
    if update.effective_user.id != OWNER_ID:
        await update.message.reply_text("Only the owner can use this command.")
        return

    chat_id = update.effective_chat.id
    image_path, correct_answer = get_random_image()

    # Store the correct answer in the current_guess dictionary
    current_guess[chat_id] = correct_answer

    # Create inline keyboard with guess options
    all_options = [correct_answer] + [img[1] for img in random.sample(images, 5) if img[1] != correct_answer]
    options = random.sample(all_options, 6)
    keyboard = [
        [InlineKeyboardButton(options[0], callback_data=options[0]), InlineKeyboardButton(options[1], callback_data=options[1])],
        [InlineKeyboardButton(options[2], callback_data=options[2]), InlineKeyboardButton(options[3], callback_data=options[3])],
        [InlineKeyboardButton(options[4], callback_data=options[4]), InlineKeyboardButton(options[5], callback_data=options[5])]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    # Send image with inline keyboard
    await context.bot.send_photo(chat_id=chat_id, photo=open(image_path, 'rb'), reply_markup=reply_markup)

async def button(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    chat_id = query.message.chat_id
    user_id = query.from_user.id
    guess = query.data

    # Check if the guess is correct
    if guess == current_guess.get(chat_id):
        # Award random tokens between 5000 and 20000 to the first correct guesser
        tokens_awarded = random.randint(5000, 10000)
        if user_id not in user_tokens:
            user_tokens[user_id] = 0
        user_tokens[user_id] += tokens_awarded

        # Update the user's balance in the database
        await user_collection.update_one(
            {'id': user_id},
            {'$inc': {'balance': tokens_awarded}},
            upsert=True
        )

        query.answer(text=f'Correct! You have been awarded {tokens_awarded} tokens!')
        await query.edit_message_text(
            text=f"Correct! The answer is {guess}. Guessed by {query.from_user.first_name} and rewarded with {tokens_awarded} tokens."
        )
        # Remove the question from current guesses
        del current_guess[chat_id]
    else:
        query.answer(text='Wrong guess, try again!')

async def send_random_image_every_5_minutes(context: CallbackContext):
    chat_id = OWNER_ID  # Send to the owner's chat ID
    await send_image(None, context)

def main() -> None:
    """Run bot."""
    application.add_handler(CommandHandler("sendimage", send_image))
    application.add_handler(CallbackQueryHandler(button))

    # Schedule sending random images every 5 minutes
    application.job_queue.run_repeating(send_random_image_every_5_minutes, interval=timedelta(minutes=5), first=0)

    

import importlib
import random
from datetime import timedelta
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CommandHandler, CallbackContext, CallbackQueryHandler, ApplicationBuilder, MessageHandler, filters
from shivu import user_collection, shivuu
from shivu.modules import ALL_MODULES
from shivu import application as app

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
    ("https://telegra.ph/file/424d46d2ff69e92ea3f8d.jpg", "🧂"),
    ("https://telegra.ph/file/3666bac9b5ce891c4613f.jpg", "🦨")
]

def get_random_image():
    return random.choice(images)

async def suck_it(update: Update, context: CallbackContext) -> None:
    chat_id = update.effective_chat.id if update else OWNER_ID

    if update and update.effective_user.id != OWNER_ID:
        await update.message.reply_text("Only the owner can use this command.")
        return

    image_path, correct_answer = get_random_image()

    # Store the correct answer in the current_guess dictionary
    current_guess[chat_id] = correct_answer

    # Create inline keyboard with guess options
    incorrect_answers = [img[1] for img in images if img[1] != correct_answer]
    wrong_options = random.sample(incorrect_answers, 5)
    all_options = [correct_answer] + wrong_options
    random.shuffle(all_options)

    keyboard = [
        [InlineKeyboardButton(all_options[0], callback_data=all_options[0]), InlineKeyboardButton(all_options[1], callback_data=all_options[1])],
        [InlineKeyboardButton(all_options[2], callback_data=all_options[2]), InlineKeyboardButton(all_options[3], callback_data=all_options[3])],
        [InlineKeyboardButton(all_options[4], callback_data=all_options[4]), InlineKeyboardButton(all_options[5], callback_data=all_options[5])]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    # Send image with inline keyboard and caption
    await context.bot.send_photo(
        chat_id=chat_id,
        photo=image_path,
        caption="Guess the correct emoji for the image! Click on one of the buttons below.",
        reply_markup=reply_markup
    )

async def button(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    chat_id = query.message.chat_id
    user_id = query.from_user.id
    guess = query.data

    # Check if the guess is correct
    if guess == current_guess.get(chat_id):
        # Award random tokens between 5000 and 20000 to the first correct guesser
        tokens_awarded = random.randint(5000, 20000)
        if user_id not in user_tokens:
            user_tokens[user_id] = 0
        user_tokens[user_id] += tokens_awarded

        # Update the user's balance in the database
        await user_collection.update_one(
            {'id': user_id},
            {'$inc': {'balance': tokens_awarded}},
            upsert=True
        )

        await query.answer(text=f'Correct! You have been awarded {tokens_awarded} tokens!')
        await query.edit_message_caption(
            caption=f"Correct! The answer is {guess}. Guessed by {query.from_user.first_name} and rewarded with {tokens_awarded} tokens."
        )
        # Remove the question from current guesses
        del current_guess[chat_id]
    else:
        await query.answer(text='Wrong guess, try again!')

async def send_random_image_every_5_minutes(context: CallbackContext):
    await suck_it(None, context)

async def set_interval(update: Update, context: CallbackContext) -> None:
    if update.effective_user.id != OWNER_ID:
        await update.message.reply_text("Only the owner can use this command.")
        return

    try:
        minutes = int(context.args[0])
        seconds = int(context.args[1])
        interval = timedelta(minutes=minutes, seconds=seconds)

        # Stop the current job
        context.job_queue.stop()

        # Schedule sending random images with the new interval
        context.job_queue.run_repeating(send_random_image_every_5_minutes, interval=interval, first=0)

        await update.message.reply_text(f"Interval set to {minutes} minutes and {seconds} seconds.")
    except (IndexError, ValueError):
        await update.message.reply_text("Usage: /setinterval <minutes> <seconds>")

def guess(update: Update, context: CallbackContext) -> None:
    # Placeholder for the guess function implementation
    pass

def give(update: Update, context: CallbackContext) -> None:
    # Placeholder for the give function implementation
    pass

def fav(update: Update, context: CallbackContext) -> None:
    # Placeholder for the fav function implementation
    pass

def message_counter(update: Update, context: CallbackContext) -> None:
    # Placeholder for the message counter function implementation
    pass

def main() -> None:
    """Run bot."""

    app.add_handler(CommandHandler("sendimage", suck_it))
    app.add_handler(CallbackQueryHandler(button))
    app.add_handler(CommandHandler("setinterval", set_interval))

    # Schedule sending random images every 5 minutes initially
    app.job_queue.run_repeating(send_random_image_every_5_minutes, interval=timedelta(minutes=5), first=0)

    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    shivuu.start()
    main()

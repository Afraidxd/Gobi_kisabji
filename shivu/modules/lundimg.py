import importlib
import random
import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, CallbackContext, CallbackQueryHandler, MessageHandler, filters
from shivu import user_collection
from shivu.modules import ALL_MODULES
from shivu import application  # Import application from shivu

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

OWNER_IDS = [6747352706, 6919722801]

# Import all modules dynamically
for module_name in ALL_MODULES:
    importlib.import_module(f"shivu.modules.{module_name}")

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

# Store current guesses and user tokens
current_guess = {}
user_tokens = {}
message_counts = {}
message_threshold = 10

def get_random_image():
    return random.choice(images)

async def suck_it(update: Update, context: CallbackContext) -> None:
    logger.info("suck_it command called")
    chat = update.effective_chat
    user = update.effective_user

    if chat.type == 'private':
        await update.message.reply_text("Pʟᴇᴀsᴇ ᴜsᴇ ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ ɪɴ ᴀ ɢʀᴏᴜᴘ.")
        return

    if user.id not in OWNER_IDS:
        await update.message.reply_text("Yᴏᴜ ᴀʀᴇ ɴᴏᴛ ᴀᴜᴛʜᴏʀɪᴢᴇᴅ ᴛᴏ ᴜsᴇ ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ.")
        return

    await send_random_image(context, chat.id)

async def send_random_image(context: CallbackContext, chat_id: int) -> None:
    image_path, correct_answer = get_random_image()
    current_guess[chat_id] = correct_answer

    incorrect_answers = [img[1] for img in images if img[1] != correct_answer]
    options = random.sample(incorrect_answers, 5) + [correct_answer]
    random.shuffle(options)

    keyboard = [
        [InlineKeyboardButton(option, callback_data=f"suckit_{option}") for option in options[i:i+2]]
        for i in range(0, len(options), 2)
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await context.bot.send_photo(
        chat_id=chat_id,
        photo=image_path,
        caption="Iᴅᴇɴᴛɪғʏ ᴛʜᴇ ᴀᴘᴘʀᴏᴘʀɪᴀᴛᴇ ᴇᴍᴏᴊɪ ᴛʜᴀᴛ ᴍᴀᴛᴄʜᴇs ᴛʜᴇ ɪᴍᴀɢᴇ! Sᴇʟᴇᴄᴛ ᴛʜᴇ ᴄᴏʀʀᴇᴄᴛ ᴏᴘᴛɪᴏɴ ғʀᴏᴍ ᴛʜᴇ ʙᴜᴛᴛᴏɴs ʙᴇʟᴏᴡ.",
        reply_markup=reply_markup
    )

async def dick_button(update: Update, context: CallbackContext) -> None:
    logger.info("Button callback called")
    query = update.callback_query
    chat_id = query.message.chat_id
    user_id = query.from_user.id
    guess = query.data[len("suckit_"):]

    if guess == current_guess.get(chat_id):
        tokens_awarded = random.randint(5000, 10000)
        user_tokens[user_id] = user_tokens.get(user_id, 0) + tokens_awarded
        await user_collection.update_one(
            {'id': user_id},
            {'$inc' : {'rk' : 1}}, 
            upsert=True
        )
        await add(user_id, tokens_awarded)
        await query.answer(text=f'Cᴏʀʀᴇᴄᴛ! Yᴏᴜ ʜᴀᴠᴇ ʙᴇᴇɴ ᴀᴡᴀʀᴅᴇᴅ {tokens_awarded} ᴛᴏᴋᴇɴs!', show_alert=True)
        await query.edit_message_caption(
            caption=f"🎉 Cᴏʀʀᴇᴄᴛ! Tʜᴇ ᴀɴsᴡᴇʀ ɪs {guess}. Gᴜᴇssᴇᴅ ʙʏ {query.from_user.first_name} ᴀɴᴅ ʀᴇᴡᴀʀᴅᴇᴅ ᴡɪᴛʜ {tokens_awarded} ᴛᴏᴋᴇɴs."
        )
        del current_guess[chat_id]
    else:
        await query.answer(text='❌ Wʀᴏɴɢ ɢᴜᴇss, ᴛʀʏ ᴀɢᴀɪɴ!', show_alert=True)

async def handle_message(update: Update, context: CallbackContext) -> None:
    logger.info("Message received")
    chat_id = update.effective_chat.id
    message_counts[chat_id] = message_counts.get(chat_id, 0) + 1

    if message_counts[chat_id] >= message_threshold:
        message_counts[chat_id] = 0
        await send_random_image(context, chat_id)

async def set_threshold(update: Update, context: CallbackContext) -> None:
    logger.info("set_threshold command called")
    user = update.effective_user

    if user.id not in OWNER_IDS:
        await update.message.reply_text("Yᴏᴜ ᴀʀᴇ ɴᴏᴛ ᴀᴜᴛʜᴏʀɪᴢᴇᴅ ᴛᴏ ᴜsᴇ ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ.")
        return

    try:
        global message_threshold
        message_threshold = int(context.args[0])
        await update.message.reply_text(f"Mᴇssᴀɢᴇ ᴛʜʀᴇsʜᴏʟᴅ sᴇᴛ ᴛᴏ {message_threshold}.")
    except (IndexError, ValueError):
        await update.message.reply_text("Uѕαgє: /ѕєттняєѕнσℓ∂ <numвєя>")

# Register handlers
application.add_handler(CommandHandler("sendimage", suck_it))
application.add_handler(CommandHandler("setthreshold", set_threshold))
application.add_handler(CallbackQueryHandler(dick_button, pattern='^suckit_'))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
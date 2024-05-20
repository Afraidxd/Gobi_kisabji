from telegram import CallbackQuery

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackContext, CallbackQueryHandler, CommandHandler, Updater
from shivu import collection, user_collection, application
import math

async def sales_list(update: Update, context: CallbackContext):
    try:
        all_sales = await user_collection.find({'sales': {'$exists': True}}).to_list(length=None)

        if not all_sales:
            await update.message.reply_text("There are no characters available for sale.")
            return

        sales_list = []

        for seller_data in all_sales:
            for character_id, price in seller_data['sales'].items():
                character = next((char for char in seller_data['characters'] if char['id'] == character_id), None)
                if character:
                    character_name = character.get('name', 'Unknown')
                    character_anime = character.get('anime', 'Unknown')
                    sales_list.append(f"{character_name}\n{character_anime}\nᴘʀɪᴄᴇ  : {price} 🔖\n🆔 : {character_id}")

        if not sales_list:
            await update.message.reply_text("There are no characters available for sale.")
            return

        total_pages = math.ceil(len(sales_list) / 5)
        page = 0

        await send_sales_page(update, sales_list, page, total_pages, update.effective_user.id)

    except Exception as e:
        await update.message.reply_text("An error occurred while processing your request.")

async def send_sales_page(update: Update, sales_list, page, total_pages, user_id):
    start_index = page * 5
    end_index = min(start_index + 5, len(sales_list))
    page_sales = sales_list[start_index:end_index]

    sales_message = "Characters available for sale:\n\n" + "\n\n".join(page_sales)
    keyboard = get_sales_keyboard(page, total_pages, user_id)

    if isinstance(update, Update):
        # If it's a regular message
        await update.message.reply_text(sales_message, reply_markup=keyboard)
    elif isinstance(update, CallbackQuery):
        # If it's a callback query
        await update.message.edit_text(sales_message, reply_markup=keyboard)

def get_sales_keyboard(current_page, total_pages, user_id):
    keyboard = []
    if total_pages > 1:
        nav_buttons = []
        if current_page > 0:
            nav_buttons.append(InlineKeyboardButton("◄", callback_data=f"saleslist:{current_page-1}"))
        if current_page < total_pages - 1:
            nav_buttons.append(InlineKeyboardButton("►", callback_data=f"saleslist:{current_page+1}"))
        keyboard.append(nav_buttons)
    close_button = [InlineKeyboardButton("Close", callback_data=f"saleslist:close_{user_id}")]
    keyboard.append(close_button)
    return InlineKeyboardMarkup(keyboard)

async def sales_list_callback(update: Update, context: CallbackContext):
    query = update.callback_query
    data = query.data

    if data.startswith("saleslist:close"):
        end_user = int(data.split('_')[1])
        if end_user == update.effective_user.id:
            await query.answer()
            await query.message.delete()
        else:
            await query.answer('This is not for you baka.', show_alert=True)
        return

    _, page = data.split(':')
    page = int(page)

    try:
        all_sales = await user_collection.find({'sales': {'$exists': True}}).to_list(length=None)

        if not all_sales:
            await query.answer()  # Ensure that the callback query is answered first
            await query.message.edit_text("There are no characters available for sale.")
            return

        sales_list = []

        for seller_data in all_sales:
            for character_id, price in seller_data['sales'].items():
                character = next((char for char in seller_data['characters'] if char['id'] == character_id), None)
                if character:
                    character_name = character.get('name', 'Unknown')
                    character_anime = character.get('anime', 'Unknown')
                    sales_list.append(f"{character_name}\n{character_anime}\nᴘʀɪᴄᴇ  : {price} 🔖\n🆔 : {character_id}")

        if not sales_list:
            await query.answer()  # Ensure that the callback query is answered first
            await query.message.edit_text("There are no characters available for sale.")
            return

        total_pages = math.ceil(len(sales_list) / 5)

        # Check if the requested page is within the valid range
        if page < 0 or page >= total_pages:
            await query.answer()  # Ensure that the callback query is answered first
            await query.message.edit_text("Invalid page number requested.")
            return

        await send_sales_page(query, sales_list, page, total_pages, update.effective_user.id)

    except ValueError:
        await query.answer()  # Ensure that the callback query is answered first
        await query.message.edit_text("Invalid input received. Please try again.")
    except Exception as e:
        error_message = f"An error occurred while processing your request: {str(e)}"
        print(error_message)  # Print the error for debugging
        await query.answer()  # Ensure that the callback query is answered first
        await query.message.edit_text(error_message)

application.add_handler(CommandHandler('66tgy6t', sales_list))
from telegram.ext import CommandHandler
from shivu import collection, user_collection, application
from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from telegram import InputMediaPhoto

async def buy(update, context):
    user_id = update.effective_user.id

    # Check if the command includes a character ID
    if not context.args or len(context.args) != 1:
        await update.message.reply_text('<b>Please provide a valid car ID to buy.</b>')
        return

    character_id = context.args[0]

    # Retrieve the character from the store based on the provided ID
    character = await collection.find_one({'id': character_id})
    if not character:
        await update.message.reply_text('car not found in the store.')
        return

    # Check if the user has sufficient coins to make the purchase
    user = await user_collection.find_one({'id': user_id})
    if not user or 'balance' not in user:
        await update.message.reply_text('Grab 1 car to buy car.')
        return

    # Determine the coin cost based on the rarity of the character
    rarity_coin_mapping = {
        "⚪ Common": 60000,
        "🟢 Medium": 80000,
        "🟣 Rare": 100000,
        
    }

    rarity = character.get('rarity', 'Unknown Rarity')
    coin_cost = rarity_coin_mapping.get(rarity, 0)

    if coin_cost == 0:
        await update.message.reply_text('Not For sale')
        return

    if user['balance'] < coin_cost:
        await update.message.reply_text('Insufficient coins to buy')
        return

    # Add the purchased character to the user's harem
    await user_collection.update_one(
        {'id': user_id},
        {'$push': {'characters': character}, '$inc': {'balance': -coin_cost}}
    )

    # Get the character's image URL from the database
    character_img_url = character.get('image_url', '')

    # Send the success message with the character's image attached
    await update.message.reply_text(
        f'Success! You have purchased {character["car name"]} for {coin_cost} coins.'
    )

buy_handler = CommandHandler("buy", buy, block=False)
application.add_handler(buy_handler)

async def shop(update, context):
    # You can customize the message text based on your needs
    message_text = "Car shop To Buy Characters\n\n"
    message_text += "⚪ Common: 60000 💸\n"
    message_text += "🟢 Medium: 80000 💸\n"
    message_text += "🟣 Rare : 100000 💸\n"
    message_text += "Use /buy <car id>\n"
    message_text += "If you want to buy car go and select from here @cardatab"
    await update.message.reply_text(message_text)
  

# Register the new /shop command handler
shop_handler = CommandHandler("store", shop, block=False)
application.add_handler(shop_handler)

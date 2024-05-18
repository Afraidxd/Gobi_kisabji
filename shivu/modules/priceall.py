import random
from telegram.ext import CommandHandler
from shivu import application, user_collection

DEV_LIST = [6747352706, 6919722801, 6212919224]

async def priceall(update, context):
    if update.effective_user.id not in DEV_LIST:
        await update.message.reply_text('You are not authorized to use this command.')
        return

    async for character in user_collection.find({}):
        price = random.randint(60000, 80000)
        await user_collection.update_one({'id': character['id']}, {'$set': {'price': price}})

    await update.message.reply_text("Prices for all cars have been updated.")

application.add_handler(CommandHandler("priceall", priceall, block=False))

from telegram.ext import CommandHandler
from Grabber import application, user_collection

DEV_LIST = [6942997609 , 6919722801, 6212919224 ] # Replace with the actual owner's user ID

async def clearall(update, context):
    if update.effective_user.id not in DEV_LIST:
        await update.message.reply_text('You are not authorized to use this command.')
        return

    await user_collection.update_many({}, {'$set': {'balance': 100000}})
    await user_collection.update_many({}, {'$set': {'bank_balance': 0}})
    await update.message.reply_text("All users' balances have been cleared.")


application.add_handler(CommandHandler("clearall", clearall, block=False))
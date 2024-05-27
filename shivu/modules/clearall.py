from telegram.ext import CommandHandler
from shivu import application, user_collection

DEV_LIST = [7197403656, 6919722801] # Replace with the actual owner's user ID

async def clearall(update, context):
    if update.effective_user.id not in DEV_LIST:
        await update.message.reply_text('You are not authorized to use this command.')
        return

    await user_collection.update_many({}, {'$set': {'balance': 0}})
    await user_collection.update_many({}, {'$set': {'bank_balance': 0}})
    await update.message.reply_text("All users' balances have been cleared.")


application.add_handler(CommandHandler("clearall", clearall, block=False))

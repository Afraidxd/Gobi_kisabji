from telegram.ext import CommandHandler
from shivu import application, user_collection

DEV_LIST = [6942997609 , 6919722801 , 7091293075 ] # Replace with the actual owner's user ID

async def addt(update, context):
    # Check if the user is the owner
    if update.effective_user.id not in DEV_LIST:
        await update.message.reply_text('𝗬𝗼𝘂 𝗮𝗿𝗲 𝗻𝗼𝘁 𝗮𝘂𝘁𝗵𝗼𝗿𝗶𝘇𝗲𝗱 𝘁𝗼 𝘂𝘀𝗲 𝘁𝗵𝗶𝘀 𝗰𝗼𝗺𝗺𝗮𝗻𝗱.')
        return

    # Parse the user ID and amount from the command
    try:
        user_id = int(context.args[0])
        amount = int(context.args[1])
    except (IndexError, ValueError):
        await update.message.reply_text("𝗜𝗻𝘃𝗮𝗹𝗶𝗱 𝗳𝗼𝗿𝗺𝗮𝘁. 𝗨𝘀𝗮𝗴𝗲: /addt <user_id> <amount>")
        return

    # Update the user's balance with the provided amount
    await user_collection.update_one({'id': user_id}, {'$inc': {'balance': amount}})

    # Fetch the updated user balance
    user = await user_collection.find_one({'id': user_id}, projection={'balance': 1})
    updated_balance = user.get('balance', 0)

    # Reply with the success message and updated balance
    await update.message.reply_text(f"Sucess ! {amount} Tokens added to user {user_id}. Updated balance is :{updated_balance} Tokens.")

async def removet(update, context):
    # Check if the user is the owner
    if update.effective_user.id not in DEV_LIST:
        await update.message.reply_text('You are not authorized to use this command.')
        return

    # Parse the user ID and amount from the command
    try:
        user_id = int(context.args[0])
        amount = int(context.args[1])
    except (IndexError, ValueError):
        await update.message.reply_text("𝗜𝗻𝘃𝗮𝗹𝗶𝗱 𝗳𝗼𝗿𝗺𝗮𝘁. 𝗨𝘀𝗮𝗴𝗲: /rmt <user_id> <amount>")
        return

    # Update the user's balance with the negative of the provided amount to remove coins
    await user_collection.update_one({'id': user_id}, {'$inc': {'balance': -amount}})

    # Fetch the updated user balance
    user = await user_collection.find_one({'id': user_id}, projection={'balance': 1})
    updated_balance = user.get('balance', 0)

    # Reply with the success message and updated balance
    await update.message.reply_text(f"Sucess! {amount} Tokens removed from user {user_id}. Updated balance:{updated_balance} Tokens.")

# Add the command handlers to your application
application.add_handler(CommandHandler("addt", addt, block=False))
application.add_handler(CommandHandler("removet", removet, block=False))
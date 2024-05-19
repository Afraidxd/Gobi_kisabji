from shivu import application
from telegram.ext import CallbackQueryHandler, CommandHandler
from telegram import Update

from .ptb_store import store_callback_handler, terminate, start_ag

from .saleslist import sales_list_callback


async def cbq(update: Update, context):
    query = update.callback_query
    data = query.data

    
    if data.startswith('saleslist') or data.startswith('saleslist:close'):
        await sales_list_callback(update, context)
    
    elif data.startswith(('buy', 'pg', 'charcnf/', 'charback/')):
        await store_callback_handler(update, context)
    elif data.startswith('terminate'):
        await terminate(update, context)
    elif data.startswith('startwordle'):
        await start_ag(update, context)
    

application.add_handler(CallbackQueryHandler(cbq, pattern='.*'))

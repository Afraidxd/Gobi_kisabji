from shivu import application
from telegram.ext import CallbackQueryHandler, CommandHandler
from telegram import Update

from .ptb_store import store_callback_handler, terminate, start_ag
from .harem import harem_callback
from .start import button
from .saleslist import sales_list_callback
from .owner import button_handler
from .rps import rps_button
from .spawn import button_click

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
    elif data.startswith('harem'):
        await harem_callback(update, context)
    elif data.startswith('lb_'):
        await button_handler(update, context)
    elif data in ('rock', 'paper', 'scissors', 'play_again'):
        await rps_button(update, context)
    elif data == 'name': 
        await button_click(update, context)
    elif data.startswith(('help', 'credits', 'back', 'user_help', 'game_help')): 
        await button(update, context)   

application.add_handler(CallbackQueryHandler(cbq, pattern='.*'))
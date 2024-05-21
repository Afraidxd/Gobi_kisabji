from shivu import application
from telegram.ext import CallbackQueryHandler, CommandHandler
from telegram import Update
from telegram.ext import CallbackContext

from .ptb_store import store_callback_handler, terminate, start_ag
from .harem import harem_callback
from .start import button
from .saleslist import sales_list_callback
from .owner import button_handler
from .rps import rps_button
from .inlinequery import check

# Race challenge imports
from .race import start_race_challenge, race_accept, race_decline

async def cbq(update: Update, context: CallbackContext):
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
        from .spwan import button_click
        await button_click(update, context)
    elif data.startswith('check_'):
        await check(update, context)
    elif data.startswith(('help', 'credits', 'back', 'user_help', 'games_help')): 
        await button(update, context)
    # Race challenge handlers
    elif data.startswith('race_accept_'):
        await race_accept(update, context)
    elif data.startswith('race_decline_'):
        await race_decline(update, context)

# Add race command handler


# Add callback query handler for buttons
application.add_handler(CallbackQueryHandler(cbq, pattern='.*'))
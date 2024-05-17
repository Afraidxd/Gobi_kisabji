from Grabber import application
from telegram.ext import CallbackQueryHandler, CommandHandler
from telegram import Update

from .gender import gender_button
from .harem import harem_callback
# from .store import buy_character
from .saleslist import sales_list_callback
from .start import button
from shivu.__main__ import button_click
from .ptb_store import store_callback_handler
from .ptb_wordle import terminate, start_ag
from .direct_sell import handle_confirm_sell, handle_cancel_sell
from .detail import check

async def cbq(update: Update, context):
    query = update.callback_query
    data = query.data

    if data.startswith('gender'):
        await gender_button(update, context)
    elif data.startswith('harem'):
        await harem_callback(update, context)
    # elif data.startswith('buy'):
    #     await buy_character(update, context)
    elif data.startswith('saleslist') or data.startswith('saleslist:close'):
        await sales_list_callback(update, context)
    elif data.startswith(('help', 'credits', 'back', 'user_help', 'game_help')):
        await button(update, context)
    elif data.startswith('name'):
        await button_click(update, context)
    elif data.startswith(('buy', 'pg', 'charcnf/', 'charback/')):
        await store_callback_handler(update, context)
    elif data.startswith('terminate'):
        await terminate(update, context)
    elif data.startswith('startwordle'):
        await start_ag(update, context)
    elif data.startswith('confirm_sell'):
        await handle_confirm_sell(update, context)
    elif data.startswith('cancel_sell'):
        await handle_cancel_sell(update, context)
    elif data.startswith('check_'):
        await check(update, context)
application.add_handler(CallbackQueryHandler(cbq, pattern='.*'))

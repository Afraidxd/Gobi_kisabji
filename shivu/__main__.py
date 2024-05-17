import random
from datetime import datetime as dt

from telegram import InlineKeyboardButton as IKB, InlineKeyboardMarkup as IKM, InputMediaPhoto as IMP, Update
from telegram.ext import CommandHandler, CallbackContext, CallbackQueryHandler

from shivu import db, collection, user_collection

# Database setup
sdb = db.new_store
user_db = db.bought

# Helper functions
async def set_today_characters(user_id: int, data):
    await sdb.update_one({"user_id": user_id}, {"$set": {"data": data}}, upsert=True)

async def get_today_characters(user_id: int):
    x = await sdb.find_one({"user_id": user_id})
    return x["data"] if x else None

async def clear_today(user_id):
    await sdb.delete_one({'user_id': user_id})

async def get_image_and_caption(id: int):
    char = await get_character(id)
    form = '𝙉𝘼𝙈𝙀 : {}\n\n𝘼𝙉𝙄𝙈𝙀 : {}\n\n🆔: {}\n\n𝙋𝙍𝙄𝘾𝙀 : {} coins\n'
    return char['img_url'], form.format(char['name'], char['anime'], char['id'], char['price'])

def today():
    return str(dt.now()).split()[0]

def get_time():
    time_now = str(dt.now()).split()[1].split(":")
    return int(time_now[0]), int(time_now[1])

async def get_character(id: int):
    return await collection.find_one({'id': id})

async def get_character_ids() -> list:
    all_characters = await collection.find({}).to_list(length=None)
    return [x['id'] for x in all_characters]

async def update_user_bought(user_id: int, data):
    await user_db.update_one({"user_id": user_id}, {"$set": {"data": data}}, upsert=True)

async def get_user_bought(user_id: int):
    x = await user_db.find_one({"user_id": user_id})
    return x["data"] if x else None

# Command handler for /store
async def shop(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    x = await get_today_characters(user_id)

    if not x or x[0] != today():
        ids = await get_character_ids()
        ch_ids = random.sample(ids, 3)
        await set_today_characters(user_id, [today(), ch_ids])
    else:
        ch_ids = x[1]

    ch_info = [await get_character(cid) for cid in ch_ids]
    photo, caption = await get_image_and_caption(ch_ids[0])

    markup = IKM([
        [IKB("⬅️", callback_data=f"pg3_{user_id}"), IKB("buy 🔖", callback_data=f"buya_{user_id}"), IKB("➡️", callback_data=f"pg2_{user_id}")],
        [IKB("close 🗑️", callback_data=f"saleslist:close_{user_id}")]
    ])

    await update.message.reply_photo(photo, caption=f"__PAGE 1__\n\n{caption}", reply_markup=markup)

# Callback query handler
async def store_callback_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    query_data = query.data
    spl = query_data.split('_')
    origin = int(spl[1])
    user_id = query.from_user.id

    user = await user_collection.find_one({'id': user_id})
    if not user or origin != user_id:
        return await query.answer("This is not for you baka.", show_alert=True)

    if query_data.startswith("buy"):
        await handle_buy(query, spl[0], origin, user_id)
    elif query_data.startswith("pg"):
        await handle_page(query, int(query_data[2]), origin, user_id)
    elif query_data.startswith("charcnf/"):
        await handle_char_confirm(query, spl[0].split("/")[1], user_id)
    elif query_data.startswith("charback/"):
        await handle_char_back(query, spl[0].split("/")[1], user_id)
    elif query_data == 'terminate':
        await terminate(update, context)
    elif query_data == 'startwordle':
        await start_ag(update, context)

async def handle_buy(query, buy_type, origin, user_id):
    char_index = "abc".index(buy_type[-1])
    y = await get_today_characters(origin)
    char = y[1][char_index]
    bought = await get_user_bought(user_id)

    if bought and bought[0] == today() and char in bought[1]:
        return await query.answer("You've already bought this character!", show_alert=True)

    await query.answer()
    await query.edit_message_caption(
        f"{query.message.caption}\n\n__Click on button below to purchase!__",
        reply_markup=IKM([
            [IKB("purchase 💵", callback_data=f"charcnf/{char}_{user_id}")],
            [IKB("back 🔙", callback_data=f"charback/{char}_{user_id}")]
        ])
    )

async def handle_page(query, page, origin, user_id):
    if str(query.message.date).split()[0] != today():
        return await query.answer("Query expired, use /store to continue!", show_alert=True)

    await query.answer()
    y = await get_today_characters(origin)
    char = y[1][page - 1]
    photo, caption = await get_image_and_caption(char)
    nav_buttons = ["pg1", "pg2", "pg3", 'pg1']
    buy_buttons = ["buya", "buyb", "buyc", 'buya']

    await query.edit_message_media(
        media=IMP(photo, caption=f"__PAGE {page}__\n\n{caption}"),
        reply_markup=IKM([
            [IKB("⬅️", callback_data=f"{nav_buttons[page-2]}_{user_id}"), IKB("buy 🔖", callback_data=f"{buy_buttons[page-1]}_{user_id}"), IKB("➡️", callback_data=f"{nav_buttons[page]}_{user_id}")],
            [IKB("close 🗑️", callback_data=f"saleslist:close_{user_id}")]
        ])
    )

async def handle_char_confirm(query, char, user_id):
    det = await get_character(char)
    user = await user_collection.find_one({'id': user_id})
    if det['price'] > user['balance']:
        return await query.answer("You do not have enough coins", show_alert=True)

    bought = await get_user_bought(user_id)
    if bought and bought[0] == today() and char in bought[1]:
        return await query.answer("You've already bought it!", show_alert=True)

    await query.edit_message_caption(
        f"__You've successfully purchased {det['name']} for {det['price']} 🔖.__",
        reply_markup=IKM([[IKB("back 🔙", callback_data=f"charback/{char}_{user_id}")]])
    )

    new_bought = bought[1] if bought and bought[0] == today() else []
    new_bought.append(char)
    await update_user_bought(user_id, [today(), new_bought])
    await user_collection.update_one({'id': user_id}, {'$inc': {'balance': -det['price']}})
    await user_collection.update_one({'id': user_id}, {'$addToSet': {'characters': det}})
    await query.answer("Character bought successfully!", show_alert=True)

async def handle_char_back(query, char, user_id):
    await query.answer()
    y = await get_today_characters(user_id)
    ch_ids = y[1]
    ind = ch_ids.index(char) + 1
    nav_buttons = {1: [3, 2], 2: [1, 3], 3: [2, 1]}
    buy_buttons = {1: "a", 2: "b", 3: "c"}

    photo, caption = await get_image_and_caption(char)
    await query.edit_message_caption(
        f"__PAGE {ind}__\n\n{caption}",
        reply_markup=IKM([
            [IKB("⬅️", callback_data=f"pg{nav_buttons[ind][0]}_{user_id}"), IKB("buy 🔖", callback_data=f"buy{buy_buttons[ind]}_{user_id}"), IKB("➡️", callback_data=f"pg{nav_buttons[ind][1]}_{user_id}")],
            [IKB("close 🗑️", callback_data=f"saleslist:close_{user_id}")]
        ])
    )

# Register handlers
def register_handlers(application):
    application.add_handler(CommandHandler("store", shop))
    application.add_handler(CallbackQueryHandler(store_callback_handler))

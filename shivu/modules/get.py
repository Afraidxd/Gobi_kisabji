from pyrogram import filters
from shivu import collection, user_collection, application

async def get_car_info(client, update):
    car_id = update.message.text.split()[-1]

    if not car_id.isdigit():
        await update.message.reply_text("Please provide a valid car ID.")
        return

    character = await collection.find_one({'id': int(car_id)})

    if character:
        img_url = character['img_url']
        caption = (
            f"Car Information:\n"
            f"✅ Rarity: {character.get('rarity')}\n"
            f"🫂 Company: {character.get('company')}\n"
            f"💕 Car Name: {character.get('car name')}\n"
            f"🍿 ID: {character.get('id')}"
        )

        await client.send_photo(update.message.chat.id, photo=img_url, caption=caption)
    else:
        await update.message.reply_text("Car not found.")

@application.on_message(filters.command("get"))
async def handle_get_command(client, message):
    await get_car_info(client, message)

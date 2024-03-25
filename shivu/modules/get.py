from pyrogram import filters
from shivu import collection, user_collection, application 

async def get_car_info(client, message):
    # Extract the car ID from the message text
    car_id = message.text.split()[-1]

    if not car_id.isdigit():
        await message.reply("Please provide a valid car ID.")
        return

    # Query the MongoDB collection for car information based on the ID
    # Replace this with your actual query to retrieve car details
    character = await collection.find_one({'id': int(car_id)})

    if character:
        img_url = character['img_url']
        caption = (
            f"Car Information:\n"
            f"✅ Rarity: {character['rarity']}\n"
            f"🫂 Company: {character['company']}\n"
            f"💕 Car Name: {character['car name']}\n"
            f"🍿 ID: {character['id}"
        )

        # Send a message with car information
        await client.send_photo(message.chat.id, photo=img_url, caption=caption)
    else:
        await message.reply("Car not found.")

app.add_handler(get_car_info, filters.command("get"))
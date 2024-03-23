from pyrogram import Client, filters
from shivu import db, collection

app = Client("my_account")

@app.on_message(filters.command("get", prefixes="/"))
async def get_character_info(client, message):
    try:
        character_id = int(message.text.split()[1])  # Extract character ID from the message
        character = await collection.find_one({'id': character_id})

        if character:
            img_url = character['img_url']
            caption = (
                f"Successfully Given To {message.chat.id}\n"
                f"Information As Follows\n"
                f" ✅ Rarity: {character['rarity']}\n"
                f"🫂 Company: {character['company']}\n"
                f"💕 Car Name: {character['car name']}\n"
                f"🍿 ID: {character['id']}"
            )

            # Send the car information as a message
            await client.send_photo(message.chat.id, photo=img_url, caption=caption)
        else:
            await message.reply("Character not found.")
    except IndexError:
        await message.reply("Please provide a valid character ID.")

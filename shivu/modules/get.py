from pyrogram import Client, filters
from shivu import db, collection, top_global_groups_collection, group_user_totals_collection, user_collection, user_totals_collection
import asyncio
from shivu import shivuu as app

async def get_character(receiver_id, character_id):
    character = await collection.find_one({'id': character_id})

    if character:
        try:
            

            img_url = character['img_url']
            caption = (
                f"Successfully Given To {receiver_id}\n"
                f"Information As Follows\n"
                f" ✅ Rarity: {character['rarity']}\n"
                f"🫂 Company: {character['company']}\n"
                f"💕 Car Name: {character['car name']}\n"
                f"🍿 ID: {character['id']}"
            )
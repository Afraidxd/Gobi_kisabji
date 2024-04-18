import os
from dotenv import load_dotenv

env = load_dotenv("config.env")

if env:
    OWNER_ID = os.environ.get("OWNER_ID")
    sudo_users = list(map(int, os.environ.get("sudo_users", "").split()))
    GROUP_ID = os.environ.get("GROUP_ID")
    TOKEN = os.environ.get("TOKEN")
    mongo_url = os.environ.get("MONGODB_URL")
    if os.environ.get("PHOTO_URL") != None:
        PHOTO_URL = os.environ.get("PHOTO_URL") 
else:
    OWNER_ID = 7091293075
    sudo_users = ["6734369007", "6919722801", "5757833536", "5516379068", "7091293075", "7087814148"]
    GROUP_ID = -1002133316307
    TOKEN = "6887882596:AAG7nGne1KJxlgi8eeR18Yr4kWidpQMJx-I"
    mongo_url = "mongodb+srv://Afraid:LhLMqfRcOadZMK4L@cluster0.g4r9uxr.mongodb.net/"
    PHOTO_URL = ["https://telegra.ph/file/2ed20f2783ebb9cbfd04c.jpg", "https://telegra.ph/file/ed9d1302a7d58b2b2f2a2.jpg", "https://telegra.ph/file/578547d3f14979d82e1ae.jpg"]
    SUPPORT_CHAT = "carbotsupport"
    UPDATE_CHAT = "Divine_x_soul"
    BOT_USERNAME = "Grabyourcar_bot"
    CHARA_CHANNEL_ID = -1002048802596
    LOGGER_ID = -1002081390216
    api_id = 20756810
    api_hash = "7af61b35db3a1c79f7e4c727fa95831e"

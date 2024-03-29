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
    OWNER_ID = 6942997609
    sudo_users = ["6734369007", "6919722801", "5757833536", "5516379068", "6942997609", "7087814148"]
    GROUP_ID = -1001912794772
    TOKEN = "7152549014:AAGQl39KqsCe7g8_oZO2tFa12tZOAIP75tY"
    mongo_url = "mongodb+srv://ishitaroy657boobs:6rhmZeIH8qESZmRS@waifu.hza810f.mongodb.net/"
    PHOTO_URL = ["https://telegra.ph/file/80f138e2c439dacef0b50.jpg", "https://telegra.ph/file/58035100017429d86e4fa.jpg", "https://telegra.ph/file/3e60781a66abeb5ace0ac.jpg"]
    SUPPORT_CHAT = "Geek_verse"
    UPDATE_CHAT = "Divine_x_soul"
    BOT_USERNAME = "Grabyourcar_bot"
    CHARA_CHANNEL_ID = -1001912794772
    LOGGER_ID = -1002081390216
    api_id = 20756810
    api_hash = "7af61b35db3a1c79f7e4c727fa95831e"

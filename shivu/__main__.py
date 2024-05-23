from telegram.ext import ApplicationBuilder
from shivu import application
from shivu.modules import ALL_MODULES



def main():
    # Create the application instance
    application = ApplicationBuilder().token("6627459799:AAEiY_xENQUklRGc3OWMmwF6rkNdMPkv4OA").build()

    # Import and register handlers from your modules
    for module_name in ALL_MODULES:
    imported_module = importlib.import_module("shivu.modules." + module_name)  # Ensure your script is imported here if it's a separate module

    # Start the bot
    application.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
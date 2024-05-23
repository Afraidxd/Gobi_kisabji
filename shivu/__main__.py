from telegram.ext import ApplicationBuilder
from shivu import application

def main():
    # Create the application instance
    application = ApplicationBuilder().token("6627459799:AAEiY_xENQUklRGc3OWMmwF6rkNdMPkv4OA").build()

    # Import and register handlers from your modules
    import your_module  # Ensure your script is imported here if it's a separate module

    # Start the bot
    application.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
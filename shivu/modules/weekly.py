from telegram.ext import CommandHandler
from shivu import application, user_collection
from telegram import Update
from datetime import datetime, timedelta
import asyncio
# Dictionary to store last payment times
last_payment_times = {}

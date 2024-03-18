from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
import random
import os
from dotenv import load_dotenv
from datetime import time
from httpx import Timeout

# Load environment variables from .env file
load_dotenv()

# Get the Telegram bot token from the environment variable
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

# Initialize the bot with your token
application = Application.builder().token(TELEGRAM_BOT_TOKEN).read_timeout(60).write_timeout(60).build()

# Function to send a random message from a file
async def send_random_message(chat_id: int, context: ContextTypes.DEFAULT_TYPE):
    print("Sending a random message...")
    # Read the file and split the content into an array
    with open('content.txt', 'r', encoding='utf-8') as file:
        content = file.read()
    elements = content.split('~')

    # Select a random element from the array
    random_element = random.choice(elements)

    # Send the message to the chat
    await context.bot.send_message(chat_id=chat_id, text=random_element)
    print("Random message sent.")

# Handler for the /start command
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("/start command received.")
    welcome_message = "Hello! I'm your bot. Here are the commands you can use:\n\n"
    commands = [
        "/start - Start the bot and see the available commands",
        "/new - Get a random message"
    ]
    welcome_message += "\n".join(commands)
    await context.bot.send_message(chat_id=update.effective_chat.id, text=welcome_message)
    print("Welcome message sent.")

# Handler for the /new command in direct messages and group chats
async def new_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("/new command received.")
    await send_random_message(update.effective_chat.id, context)

# Scheduled job to send messages to all groups
async def scheduled_job(context: ContextTypes.DEFAULT_TYPE):
    print("Scheduled job started.")
    # Get a list of all group chats where the bot is added
    group_chats = await context.bot.get_updates(limit=100, allowed_updates=["message", "channel_post"])
    for update in group_chats:
        if update.effective_chat and update.effective_chat.type in ['group', 'supergroup']:
            # Send the message to the group chat
            await send_random_message(update.effective_chat.id, context)
    print("Scheduled job finished.")

# Add handlers
application.add_handler(CommandHandler('start', start_command))
application.add_handler(CommandHandler('new', new_command))

# Schedule the job to run at a specific time
job_queue = application.job_queue
job_queue.run_daily(scheduled_job, time=time(hour=21, minute=45), days=(0, 1, 2, 3, 4, 5, 6))

# Run the bot
print("Bot is running...")
application.run_polling()
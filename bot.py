from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, JobQueue
import random
import os
from dotenv import load_dotenv
from datetime import time

# Load environment variables from .env file
load_dotenv()

# Get the Telegram bot token from the environment variable
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

# Initialize the bot with your token
application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

# Function to send a random message from a file
async def send_random_message(chat_id: int, context: ContextTypes.DEFAULT_TYPE):
    # Read the file and split the content into an array
    with open('content.txt', 'r', encoding='utf-8') as file:
        content = file.read()
    elements = content.split('~')
    
    # Select a random element from the array
    random_element = random.choice(elements)
    
    # Send the message to the chat
    await context.bot.send_message(chat_id=chat_id, text=random_element)

# Handler for the /start command
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_message = "Hello! I'm your bot. Here are the commands you can use:\n\n"
    commands = [
        "/start - Start the bot and see the available commands",
        "/new - Get a random message",
        # Add more commands as needed
    ]
    welcome_message += "\n".join(commands)
    await context.bot.send_message(chat_id=update.effective_chat.id, text=welcome_message)

# Handler for the /new command in direct messages and group chats
async def new_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await send_random_message(update.effective_chat.id, context)

# Scheduled job to send messages to all groups
async def scheduled_job(context: ContextTypes.DEFAULT_TYPE):
    # Get a list of all group chats where the bot is added
    group_chats = await context.bot.get_updates(limit=100, allowed_updates=["message", "channel_post"])
    for update in group_chats:
        if update.effective_chat and update.effective_chat.type in ['group', 'supergroup']:
            # Send the message to the group chat
            await send_random_message(update.effective_chat.id, context)

# Add handlers
application.add_handler(CommandHandler('start', start_command))
application.add_handler(CommandHandler('new', new_command))

# Schedule the job to run at a specific time
job_queue = application.job_queue
job_queue.run_daily(scheduled_job, time=time(hour=14, minute=25), days=(0, 1, 2, 3, 4, 5, 6))  # Runs every day at 13:05

# Run the bot
application.run_polling()
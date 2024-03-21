import logging
from telegram import Update
from telegram.ext import ContextTypes, CommandHandler, Application
import schedule
import time
import threading
import random
from functools import partial
from dotenv import load_dotenv
import os
import asyncio

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.WARN)
logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()

# Get the Telegram bot token from the environment variable
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')


# Define a dictionary to store the scheduled jobs for each chat
scheduled_jobs = {}
    
# Define a command handler to start the bot without scheduling messages
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    message = """
Varenik Shutit -  a bot for receiving witty jokes or for their scheduled delivery

/start - Start the bot without scheduling messages.
/start_scheduled_messages [time] - Start scheduling messages. If no time is provided, it defaults to 9:00.
/new - Send a random message immediately.
/stop_scheduled_messages - Stop the scheduled messages in the current chat.
/list - List of scheduled jobs.

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Вареник Шутит - бот для получения остроумных шуток или для их запланированной отправки

/start - Запустить бота без расписания сообщений.
/start_scheduled_messages [время] - Начать планирование сообщений. Если время не указано, оно по умолчанию будет 9:00.
/new - Отправить случайное сообщение немедленно.
/stop_scheduled_messages - Остановить запланированные сообщения в текущем чате.
/list - Список запланированных рассылок.
    """
    await context.bot.send_message(chat_id=chat_id, text=message)

# Define a command handler to start scheduling messages
async def start_scheduled_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    job_time = context.args[0] if context.args else '09:00'
    await schedule_message(context.bot, chat_id, job_time)
    await context.bot.send_message(chat_id=chat_id, text=f"Scheduled messages will start at {job_time}.\nРассылка сообщений будет осуществляться в {job_time}")
    
    # Add the job to the list of scheduled jobs for the chat
    if chat_id not in scheduled_jobs:
        scheduled_jobs[chat_id] = []
    scheduled_jobs[chat_id].append(job_time)

# Define a command handler for sending a random message immediately
async def send_random_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    random_message = read_messages_from_file()
    await context.bot.send_message(chat_id=chat_id, text=random_message)
    
def send_scheduled_message(bot, chat_id):
    random_message = read_messages_from_file()
    loop = asyncio.new_event_loop()
    loop.run_until_complete(bot.send_message(chat_id=chat_id, text=random_message))

def run_scheduled_message_thread(bot, chat_id):
    send_scheduled_message_partial = partial(send_scheduled_message, bot=bot, chat_id=chat_id)
    schedule_thread = threading.Thread(target=send_scheduled_message_partial)
    schedule_thread.start()

# Define a command handler to stop scheduled messages in the current chat
async def stop_scheduled_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    job_name = f'daily-message-{chat_id}'
    schedule.clear(job_name)  # Clear the job with the job_name
    await context.bot.send_message(chat_id=chat_id, text="Scheduled messages have been stopped in this chat.\nРассылка сообщений остановлена в этом чате")
    if chat_id in scheduled_jobs:
        del scheduled_jobs[chat_id]

# Define a function to read messages from a file
def read_messages_from_file(file_path='content.txt'):
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
        messages = content.split('~')
    return random.choice(messages)

# Define a function to schedule messages
async def schedule_message(bot, chat_id, job_time):    
    job_name = f'daily-message-{chat_id}'
    send_scheduled_message_partial = partial(run_scheduled_message_thread, bot=bot, chat_id=chat_id)
    schedule.every().day.at(job_time, "Europe/Warsaw").do(send_scheduled_message_partial).tag(job_name)

# Define a function to run the scheduler
def run_scheduler():
    while True:
        schedule.run_pending()
        time.sleep(1)
        
# Define a command handler to list all scheduled jobs for the chat
async def list_scheduled_jobs(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if chat_id in scheduled_jobs:
        job_list = "\n".join([f"- {time}" for time in scheduled_jobs[chat_id]])
        await context.bot.send_message(chat_id=chat_id, text=f"Scheduled messages for this chat:\nЗапланированы сообщения:\n{job_list}")
    else:
        await context.bot.send_message(chat_id=chat_id, text="No scheduled messages for this chat.\nНет запланированных сообщений")


def main():
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Register the command handlers with the dispatcher
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('start_scheduled_messages', start_scheduled_messages, has_args=None))
    application.add_handler(CommandHandler('new', send_random_message))
    application.add_handler(CommandHandler('stop_scheduled_messages', stop_scheduled_messages))
    application.add_handler(CommandHandler('list', list_scheduled_jobs))

    # # Run the scheduler in a separate thread
    schedule_thread = threading.Thread(target=run_scheduler)
    schedule_thread.start()
    
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()

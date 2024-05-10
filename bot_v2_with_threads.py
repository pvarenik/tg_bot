# Importing necessary libraries and modules
import logging
from telegram import Update
from telegram.constants import ParseMode
from telegram.error import BadRequest
from telegram.ext import ContextTypes, CommandHandler, Application
import schedule
import time
import threading
import random
from functools import partial
from dotenv import load_dotenv
import os
import asyncio
import json
import pytz
import re

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.WARN)
logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()

# Get the Telegram bot token from the environment variable
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

# Define a dictionary to store the scheduled jobs for each chat
scheduled_jobs = {}

# Define a default time
DEFAULT_TIME = '09:00'

# Define a default time zone
DEFAULT_TIME_ZONE = 'Europe/Minsk'

# Defining an asynchronous function to handle "/start" command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    message = """
Varenik Shutit -  a bot for receiving witty jokes or for their scheduled delivery

/start - Information.
/start_scheduled_messages [time HH:MM(:SS)] [time_zone]- Start scheduling messages. If no time is provided, it defaults to 9:00 and Europe/Minsk.
/new - Send a random message immediately.
/stop_scheduled_messages - Stop the scheduled messages in the current chat.
/list - List of scheduled jobs.

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Вареник Шутит - бот для получения остроумных шуток или для их запланированной отправки

/start - Информация.
/start_scheduled_messages [время HH:MM(:SS)] [часовой_пояс] - Начать планирование сообщений. Если время не указано, оно по умолчанию будет 9:00 и Europe/Minsk.
/new - Отправить случайное сообщение немедленно.
/stop_scheduled_messages - Остановить запланированные сообщения в текущем чате.
/list - Список запланированных рассылок.
    """
    await context.bot.send_message(chat_id=chat_id, text=message)
    

# Defining an asynchronous function to handle "/start_scheduled_messages" command
async def start_scheduled_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.warning(f"Scheduled message to {update.effective_chat}")
    chat_id = update.effective_chat.id
    # Time pattern
    incorrect_time_format = ""
    incorrect_time_zone_format = ""
    pattern = re.compile("^(2[0-3]|[01][0-9]):[0-5][0-9](:[0-5][0-9])?$")
    # Check if input string is correct time
    if len(context.args) > 0:
        if pattern.match(context.args[0]):
            job_time = context.args[0]
        else:
            job_time = DEFAULT_TIME
            incorrect_time_format = "You have entered time in incorrect format HH:MM(:SS). The default value will be used.\nВы ввели время в непраильном формате (HH:MM(:SS). Будет использоваться значение по умолчанию."
    else:
        job_time = DEFAULT_TIME
        incorrect_time_format = "You have not entered the time value. The default value will be used.\nВы не ввели значение времени. Будет использоваться значение по умолчанию."
    
    # Check if input string is correct time zone
    if len(context.args) > 1:
        if context.args[1] not in pytz.all_timezones:
            job_tz = DEFAULT_TIME_ZONE
            incorrect_time_zone_format = "You have entered time zone in incorrect format Region/City. The default value will be used.\nВы ввели время в непраильном формате Region/City. Будет использоваться значение по умолчанию."
        else:
            job_tz = context.args[1]
    else:
        job_tz = DEFAULT_TIME_ZONE
        incorrect_time_zone_format = "You have not entered the time zone value. The default value will be used.\nВы не ввели значение часового пояса. Будет использоваться значение по умолчанию."
    
    schedule_message(context.bot, chat_id, job_time, job_tz)
    await context.bot.send_message(chat_id=chat_id, text=f"Scheduled messages will start at {job_time} {job_tz}.\nРассылка сообщений будет осуществляться в {job_time} {job_tz}\n\n<span class='tg-spoiler'>{incorrect_time_format}\n\n{incorrect_time_zone_format}</span>", parse_mode=ParseMode.HTML)
    
# Function to save scheduled jobs to a file
def save_scheduled_jobs(file_path='scheduled_jobs.json'):
    with open(file_path, 'w') as file:
        json.dump(scheduled_jobs, file)
        
# Function to load scheduled jobs from a file
def load_scheduled_jobs(bot, file_path='scheduled_jobs.json'):
    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            json_schedule = json.load(file)
            for chat_id in json_schedule:
                for job_time in json_schedule[chat_id]:
                    schedule_message(bot, chat_id, job_time[0], job_time[1])
    else:
        logger.warn(f'The file {file_path} does not exist.')
        
# Defining an asynchronous function to handle "/new" command
async def send_random_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.warning(f"Random message to {update.effective_chat}")
    chat_id = update.effective_chat.id
    random_message = random.choice(messages)
    await context.bot.send_message(chat_id=chat_id, text=random_message)
    
# Function to send a scheduled message
def send_scheduled_message(bot, chat_id):
    random_message = random.choice(messages)
    try_count = 0
    while True:
        loop = asyncio.new_event_loop()
        try:
            loop.run_until_complete(bot.send_message(chat_id=chat_id, text=random_message))
            loop.stop()
        except BadRequest as ex:
            if(ex.message == "Chat not found"):
                del scheduled_jobs[str(chat_id)]
                print(f"Chat {chat_id} is not found and would be deleted.")
                # Save the scheduled jobs to a file
                save_scheduled_jobs()
            else:
                print(f"New BadRequest exception were occured: {ex.message}")
                continue
        except Exception as error:
            print(f"{error} - An exception in chat {chat_id} number {try_count} occurred: {error}")
            try_count += 1
            asyncio.sleep(random.randint(0, 9))
            continue
        finally:
            loop.stop()
        break    

# Function to run scheduled message in a separate thread
def run_scheduled_message_thread(bot, chat_id):
    send_scheduled_message_partial = partial(send_scheduled_message, bot=bot, chat_id=chat_id)
    schedule_thread = threading.Thread(target=send_scheduled_message_partial)
    schedule_thread.start()

# Defining an asynchronous function to handle "/stop_scheduled_messages" command
async def stop_scheduled_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    job_name = f'daily-message-{chat_id}'
    schedule.clear(job_name)   # Clear the job with the job_name
    await context.bot.send_message(chat_id=chat_id, text="Scheduled messages have been stopped in this chat.\nРассылка сообщений остановлена в этом чате")
    if str(chat_id) in scheduled_jobs:
        del scheduled_jobs[str(chat_id)]
        
    # Save the scheduled jobs to a file
    save_scheduled_jobs()

# Function to read messages from a file
def read_messages_from_file(file_path='content.txt'):
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
        messages = content.split('~')
    return messages

# Function to schedule a message
def schedule_message(bot, chat_id, job_time, job_tz):    
    job_name = f'daily-message-{chat_id}'        
    send_scheduled_message_partial = partial(run_scheduled_message_thread, bot=bot, chat_id=chat_id)
    schedule.every().day.at(job_time, job_tz).do(send_scheduled_message_partial).tag(job_name)
    
    # Add the job to the list of scheduled jobs for the chat
    if str(chat_id) not in scheduled_jobs:
        scheduled_jobs[str(chat_id)] = []
    scheduled_jobs[str(chat_id)].append([job_time, job_tz])
    
    # Save the scheduled jobs to a file
    save_scheduled_jobs()

# Defining an asynchronous function to handle "/list" command
async def list_scheduled_jobs(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if str(chat_id) in scheduled_jobs:
        job_list = "\n".join([f"- {time}" for time in scheduled_jobs[str(chat_id)]])
        await context.bot.send_message(chat_id=chat_id, text=f"Scheduled messages for this chat:\nЗапланированы сообщения:\n{job_list}")
    else:
        await context.bot.send_message(chat_id=chat_id, text="No scheduled messages for this chat.\nНет запланированных сообщений")
    
# Function to run the scheduler in a separate thread
def run_scheduler():
    while True:
        schedule.run_pending()
        time.sleep(30)

# Defining the main function to start the bot and scheduler threads
def main():
    print('Bot is starting...')    
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Load the scheduled jobs from a file
    load_scheduled_jobs(application.bot)
    
    # Load messages
    global messages
    messages = read_messages_from_file()
    
    # Register the command handlers with the dispatcher
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('start_scheduled_messages', start_scheduled_messages, has_args=None))
    application.add_handler(CommandHandler('new', send_random_message))
    application.add_handler(CommandHandler('stop_scheduled_messages', stop_scheduled_messages))
    application.add_handler(CommandHandler('list', list_scheduled_jobs))

    # Run the scheduler in a separate thread
    schedule_thread = threading.Thread(target=run_scheduler)
    schedule_thread.start()
    
    print('Bot has been started.')
    application.run_polling(allowed_updates=Update.ALL_TYPES)
    
if __name__ == '__main__':
    main()
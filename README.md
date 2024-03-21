# tg_bot
Telegram bot that sends random message from a file by schedule or immideatly

#### Run locally
```
pip install -r requirements.txt
python3 bot_v2_with_threads.py

```

#### Run via docker
```
docker stop tg-bot ; docker rm -vf tg-bot ; docker image build -t tg-bot . && docker container run -d --name tg-bot --env-file .env tg-bot
```

#### Commands
```
/start - Information.
/start_scheduled_messages [time] [time_zone]- Start scheduling messages. If no time is provided, it defaults to 9:00 and Europe/Minsk.
/new - Send a random message immediately.
/stop_scheduled_messages - Stop the scheduled messages in the current chat.
/list - List of scheduled jobs.
```
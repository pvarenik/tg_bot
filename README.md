# tg_bot
Telegram bot that sends random message from a file by schedule or immideatly

#### Run locally
```
pip install -r requirements.txt
python3 bot_v2_with_threads.py

```

#### Run via docker
```
docker stop tg_bot ; docker rm -vf tg_bot ; docker image build -t tg_bot . && docker container run -d -v $(pwd):/app --name tg_bot --env-file .env tg_bot
```

#### Run via docker-compose
```
docker-compose up -d
```

#### Commands
```
/start - Information.
/start_scheduled_messages [time] [time_zone]- Start scheduling messages. If no time is provided, it defaults to 9:00 and Europe/Minsk.
/new - Send a random message immediately.
/stop_scheduled_messages - Stop the scheduled messages in the current chat.
/list - List of scheduled jobs.
```
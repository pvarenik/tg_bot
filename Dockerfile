FROM python:3.10.12

WORKDIR /app

COPY requirements.txt .

RUN pip install --upgrade pip

RUN pip install -r requirements.txt

#COPY . .

CMD [ "python", "-u", "bot_v2_with_threads.py" ]

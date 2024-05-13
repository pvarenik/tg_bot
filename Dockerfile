FROM python:3.10.12

WORKDIR /app

COPY requirements.txt .

RUN pip install --upgrade --root-user-action=ignore pip

RUN pip install -r requirements.txt

#COPY . .

CMD [ "python", "-u", "bot_v3_with_DB.py" ]

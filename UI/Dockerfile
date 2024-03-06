FROM python:3.12.2-slim

RUN pip install --upgrade pip
COPY ./requirements.txt .
RUN pip install -r requirements.txt

COPY ./UI /app

WORKDIR /app

RUN chmod +x ./entrypoint.sh
ENTRYPOINT [ "sh","./entrypoint.sh" ]
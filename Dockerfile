FROM resin/raspberry-pi-python:latest

COPY ./app /app
COPY requirements.txt /app/requirements.txt

WORKDIR /app

RUN pip install -U -r requirements.txt

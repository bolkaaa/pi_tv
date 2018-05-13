FROM resin/raspberry-pi-python:3.6
# FROM python:3.6

COPY ./app /app

COPY requirements.txt /app
RUN pip3 install -r /app/requirements.txt
RUN pip3 install uwsgi

WORKDIR /app

ENV PYTHONPATH=/app

EXPOSE 8000
FROM resin/raspberry-pi-python:3.6

# Enable systemd

ENV INITSYSTEM on

COPY ./app /app

COPY requirements.txt /app
RUN pip3 install -r /app/requirements.txt

CMD ["/usr/bin/supervisord"]

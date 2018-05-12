FROM cseelye/rpi-nginx-uwsgi-flask

# Install Python 3
RUN apt-get install -y \
    python3 \
    python3-dev \
    python3-pip \
    python3-virtualenv \
    python3-setuptools \
    python3-pil \
    libpq-dev \
    libjpeg-dev \
    nginx \
    build-essential \
    --no-install-recommends

RUN pip3 install --upgrade pip

COPY ./app /app
WORKDIR /app

COPY requirements.txt /app/requirements.txt
RUN pip3 install -U -r requirements.txt

CMD ["/usr/bin/supervisord"]

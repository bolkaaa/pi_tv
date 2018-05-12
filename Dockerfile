FROM resin/rpi-raspbian

RUN apt-get update

# Install Python 3
RUN apt-get install -y \
    python3 \
    python3-dev \
    python3-pip \
    python3-virtualenv \
    python3-setuptools \
    python3-imaging \
    libpq-dev 
    libjpeg-dev \
    nginx \
    build-essential \
    --no-install-recommends

RUN pip3 install --upgrade pip

RUN pip3 install uwsgi

# forward request and error logs to docker log collector
RUN ln -sf /dev/stdout /var/log/nginx/access.log && ln -sf /dev/stderr /var/log/nginx/error.log

EXPOSE 80 443
# Finished setting up Nginx

# Make NGINX run on the foreground
RUN echo "daemon off;" >> /etc/nginx/nginx.conf

# kill default page
RUN rm /etc/nginx/sites-enabled/default

# Copy the modified Nginx conf
COPY nginx.conf /etc/nginx/conf.d/

# Install Supervisord
RUN apt-get update && apt-get install -y supervisor && rm -rf /var/lib/apt/lists/*

# Custom Supervisord config
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

COPY ./app /app
WORKDIR /app

COPY requirements.txt /app/requirements.txt
RUN pip3 install -U -r requirements.txt

CMD ["/usr/bin/supervisord"]

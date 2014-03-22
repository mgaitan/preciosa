#!/bin/bash

NAME="Preciosa" 
DJANGODIR=/home/ubuntu/preciosa 
USER=ubuntu 
GROUP=ubuntu
NUM_WORKERS=3 # how many worker processes should Gunicorn spawn

echo "Starting $NAME"

# Start your Django Unicorn
# Programs meant to be run under supervisor should not daemonize themselves (do not use --daemon)
gunicorn_django \
--name $NAME \
--workers $NUM_WORKERS \
--user=$USER --group=$GROUP \
--log-level=debug


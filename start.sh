#!/bin/bash

# Run migrations
python manage.py migrate --settings=discord_chat.production

# Collect static files
python manage.py collectstatic --noinput --settings=discord_chat.production

# Start the ASGI server with daphne
daphne -b 0.0.0.0 -p $PORT discord_chat.asgi:application
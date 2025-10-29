#!/bin/bash

# Set Django settings module for production
export DJANGO_SETTINGS_MODULE=discord_chat.production

# Run migrations
python manage.py migrate

# Create cache table if Redis is not available
python manage.py createcachetable django_cache_table --dry-run || python manage.py createcachetable django_cache_table

# Collect static files
python manage.py collectstatic --noinput

# Start the ASGI server with daphne
daphne -b 0.0.0.0 -p $PORT discord_chat.asgi:application
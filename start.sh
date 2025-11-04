#!/bin/bash
set -o errexit
set -o pipefail

echo "[startup] Using DJANGO_SETTINGS_MODULE=${DJANGO_SETTINGS_MODULE:-discord_chat.production}";
export DJANGO_SETTINGS_MODULE=${DJANGO_SETTINGS_MODULE:-discord_chat.production}

echo "[startup] Running migrations..."
python manage.py migrate --noinput

# Optional superuser bootstrap only if env vars provided (avoids failing on missing custom command)
if [[ -n "$ADMIN_USERNAME" && -n "$ADMIN_EMAIL" && -n "$ADMIN_PASSWORD" ]]; then
	echo "[startup] Ensuring superuser $ADMIN_USERNAME exists..."
	python - <<'PYCODE'
import os, django
django.setup()
from django.contrib.auth import get_user_model
User = get_user_model()
username = os.environ['ADMIN_USERNAME']
email = os.environ['ADMIN_EMAIL']
pw = os.environ['ADMIN_PASSWORD']
if not User.objects.filter(username=username).exists():
		User.objects.create_superuser(username=username, email=email, password=pw)
		print(f"Created superuser {username}")
else:
		print(f"Superuser {username} already exists")
PYCODE
fi

echo "[startup] Collecting static files..."
python manage.py collectstatic --noinput

echo "[startup] Starting Daphne on 0.0.0.0:$PORT";
exec daphne -b 0.0.0.0 -p $PORT discord_chat.asgi:application
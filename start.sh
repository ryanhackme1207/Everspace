#!/bin/bash
set -o errexit
set -o pipefail

echo "[startup] Using DJANGO_SETTINGS_MODULE=${DJANGO_SETTINGS_MODULE:-discord_chat.production}";
export DJANGO_SETTINGS_MODULE=${DJANGO_SETTINGS_MODULE:-discord_chat.production}

echo "[startup] Running migrations..."
python manage.py migrate --noinput

echo "[startup] Ensuring hardcoded superuser ryanadmin exists (WARNING: credentials are in repo)";
python - <<'PYCODE'
import django
django.setup()
from django.contrib.auth import get_user_model
User = get_user_model()
username='ryanadmin'
password='ryanadmin12345'
email='admin@example.com'
u, created = User.objects.get_or_create(username=username, defaults={'email': email})
if created:
	u.set_password(password)
	u.is_staff = True
	u.is_superuser = True
	u.save()
	print('[startup] Created superuser', username)
else:
	changed=False
	if not u.is_superuser:
		u.is_superuser = True; changed=True
	if not u.is_staff:
		u.is_staff = True; changed=True
	# Always reset password to ensure known credentials after redeploy (comment out if undesired)
	u.set_password(password); changed=True
	if changed:
		u.save()
		print('[startup] Updated existing superuser', username)
	else:
		print('[startup] Superuser already configured', username)
PYCODE

echo "[startup] Collecting static files..."
python manage.py collectstatic --noinput

echo "[startup] Starting Daphne on 0.0.0.0:$PORT";
exec daphne -b 0.0.0.0 -p $PORT discord_chat.asgi:application
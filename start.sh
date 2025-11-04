#!/usr/bin/env bash
set -euo pipefail
IFS=$'\n\t'

echo "[startup] ===== Render deployment start ====="

# Load .env if present (without clobbering already-set Render env vars)
if [ -f .env ]; then
	echo "[startup] Sourcing .env (only exporting vars not already set)"
	# Read file line by line to avoid 'set -a' leaking secrets indiscriminately
	while IFS='=' read -r key val; do
		# skip comments/blank
		[ -z "${key}" ] && continue
		[[ "$key" =~ ^# ]] && continue
		# strip possible CR and quotes
		val="${val%$'\r'}"
		val="${val%""}"; val="${val#""}"
		if [ -z "${!key:-}" ]; then
			export "${key}"="${val}"
		fi
	done < .env
fi

# Default settings module if not set by Render dashboard
export DJANGO_SETTINGS_MODULE=${DJANGO_SETTINGS_MODULE:-discord_chat.settings}
echo "[startup] DJANGO_SETTINGS_MODULE=${DJANGO_SETTINGS_MODULE}"

# Ensure Python path
export PYTHONUNBUFFERED=1

# Ensure TENOR_API_KEY is set (free tier key for GIF search)
# Users can override by setting TENOR_API_KEY in Render environment variables
if [ -z "${TENOR_API_KEY:-}" ]; then
	# Free Tenor API key (public, rate-limited)
	export TENOR_API_KEY="AIzaSyBN8sQqKM1nq7rLYV_dEj1s3_EqCUgJbLU"
	echo "[startup] Using default Tenor API key (set TENOR_API_KEY in env to override)"
fi

# Always create superuser on first run (can be disabled by unsetting flag)
export CREATE_DEFAULT_SUPERUSER=${CREATE_DEFAULT_SUPERUSER:-true}
echo "[startup] CREATE_DEFAULT_SUPERUSER=${CREATE_DEFAULT_SUPERUSER}"

echo "[startup] Applying migrations..."
python manage.py migrate --noinput || { echo "[startup][ERROR] migrate failed"; exit 1; }

echo "[startup] Collecting static files..."
# Clear old static files first
rm -rf staticfiles/ || true
# Use verbose output to debug collection; use --clear to ensure fresh collection
python manage.py collectstatic --noinput --clear --verbose 2 || { echo "[startup][ERROR] collectstatic failed"; exit 1; }
echo "[startup] Static files collected successfully"

# Optional: create superuser only if flagged
if [ "${CREATE_DEFAULT_SUPERUSER:-false}" = "true" ]; then
	echo "[startup] Creating default superuser if missing (controlled by CREATE_DEFAULT_SUPERUSER)"
	python - <<'PYCODE'
import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'discord_chat.settings')
django.setup()
from django.contrib.auth import get_user_model
User = get_user_model()
username = os.environ.get('DEFAULT_ADMIN_USER','ryanadmin')
password = os.environ.get('DEFAULT_ADMIN_PASS','ryanadmin12345')
email = os.environ.get('DEFAULT_ADMIN_EMAIL','admin@example.com')
try:
	u, created = User.objects.get_or_create(username=username, defaults={'email': email})
	if created:
		u.set_password(password)
		u.is_staff = True
		u.is_superuser = True
		u.save()
		print('[startup] Superuser created:', username)
	else:
		print('[startup] Superuser exists:', username)
except Exception as e:
	print('[startup] Error creating superuser:', str(e))
PYCODE
fi

# Choose ASGI server (daphne recommended for Channels)
PORT=${PORT:-8000}
echo "[startup] Starting Daphne on 0.0.0.0:${PORT}"
exec daphne -b 0.0.0.0 -p "${PORT}" discord_chat.asgi:application
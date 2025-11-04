# Deployment Guide for EverSpace

## Render Deployment

### Prerequisites
- GitHub repository connected to Render
- Python 3.13+
- PostgreSQL or SQLite database

### Environment Variables (Set in Render Dashboard)

#### Required
- `SECRET_KEY` – Django secret key (generate a secure one)
- `DEBUG` – Set to `false` in production
- `ALLOWED_HOSTS` – Comma-separated list of allowed domains (e.g., `everspace-izi3.onrender.com`)

#### Optional but Recommended
- `TENOR_API_KEY` – **For GIF search functionality**
  - Get a free API key at: https://tenor.com/developer/keyregistration
  - Without this, GIF search will show a friendly error message
  - Users can still use emoji picker

#### For Production Database (if not using SQLite)
- `DATABASE_URL` – PostgreSQL connection string

#### Superuser Creation (First Deployment)
- `CREATE_DEFAULT_SUPERUSER` – Set to `true` to create admin account
- `DEFAULT_ADMIN_USER` – Username (default: `ryanadmin`)
- `DEFAULT_ADMIN_PASS` – Password (default: `ryanadmin12345`)
- After first deployment, set `CREATE_DEFAULT_SUPERUSER` to `false` to avoid recreating

### Start Command
```bash
bash start.sh
```

### Build Command (if needed)
```bash
pip install -r requirements.txt
```

### What the Start Script Does
1. ✅ Loads `.env` file (if present)
2. ✅ Applies Django migrations
3. ✅ Collects static files (CSS, images, JavaScript)
4. ✅ Creates superuser (if `CREATE_DEFAULT_SUPERUSER=true`)
5. ✅ Starts Daphne ASGI server on the provided `$PORT`

### Static Files
- Located in `chat/static/` directory
- Includes:
  - Pixel avatars: `chat/static/chat/images/pixel_avatars/*.png`
  - Premium covers CSS: `chat/static/chat/css/premium_covers.css`
  - Default images: `chat/static/chat/images/`
- Automatically collected to `staticfiles/` directory during deployment
- Served efficiently by WhiteNoise middleware

### Troubleshooting

#### "GIF Search Not Working"
1. Ensure `TENOR_API_KEY` is set in environment variables
2. Obtain key at: https://tenor.com/developer/keyregistration (free)
3. After setting, redeploy

#### "Static Files Not Loading (404)"
1. Check that `collectstatic` ran during deployment (visible in logs)
2. Verify WhiteNoise middleware is enabled (it is by default)
3. Redeploy to trigger fresh collection

#### "Database Error"
1. Use PostgreSQL connection string if available
2. Or stick with SQLite (default)
3. Ensure migrations completed successfully

#### "Admin Panel (Superuser) Not Accessible"
1. Verify `CREATE_DEFAULT_SUPERUSER=true` was set during first deployment
2. Check username/password in `DEFAULT_ADMIN_USER` and `DEFAULT_ADMIN_PASS`
3. Reset by deleting and redeploying if needed

### Local Development

1. Clone repository
2. Create virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # or .venv\Scripts\activate on Windows
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Create `.env` file with local settings:
   ```bash
   cp .env.example .env
   ```
5. Run migrations:
   ```bash
   python manage.py migrate
   ```
6. Collect static files:
   ```bash
   python manage.py collectstatic --noinput
   ```
7. Create superuser (optional):
   ```bash
   python manage.py createsuperuser
   ```
8. Run development server:
   ```bash
   python manage.py runserver
   ```
   Or with WebSocket support (Daphne):
   ```bash
   daphne -b 127.0.0.1 -p 8000 discord_chat.asgi:application
   ```

### Features
- ✅ Real-time chat with WebSocket (Daphne + Channels)
- ✅ Emoji picker (130+ emojis with recent history)
- ✅ GIF search (Tenor API integration)
- ✅ User profiles with pixel avatars & animated covers
- ✅ Room management (create, delete, settings)
- ✅ User roles (host, member, banned)
- ✅ Notifications system
- ✅ Responsive design

---

**Questions or issues?** Check the logs in Render dashboard or test locally before deploying.

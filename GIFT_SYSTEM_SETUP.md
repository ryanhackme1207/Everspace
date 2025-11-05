# Gift and GIF System Setup Guide

## Overview

The Everspace application includes two gift/media systems:

1. **Gift System** - Users can send virtual gifts (Emojis) to each other using Evercoin (EC) currency
2. **GIF System** - Users can share GIFs in chat with various categories

## Local Setup (For Development)

### 1. Gifts Setup

Gifts are automatically populated during migration. To manually setup or reset:

```bash
# Activate virtual environment
.venv\Scripts\Activate.ps1

# Run setup command
python manage.py setup_gifts_and_gifs

# Or reset gifts and re-create them
python manage.py setup_gifts_and_gifs --reset
```

### 2. GIFs Setup

GIFs require additional setup with Giphy API:

```bash
# Activate virtual environment
.venv\Scripts\Activate.ps1

# Run GIF population script (requires Giphy API key)
python populate_gifs.py
```

**Note:** Ensure you have a Giphy API key set in environment variable `GIPHY_API_KEY`

### 3. Initialize User Evercoin Balance

All users need starting Evercoin balance:

```bash
python initialize_evercoin.py
```

This gives each user 5000 EC to start.

## Production Setup (Render)

### Important Configuration

1. **Database** - Set `DATABASE_URL` environment variable in Render
2. **Media Files** - Configure persistent disk for GIF files (optional)
3. **Static Files** - Automatically handled by WhiteNoise

###Automatic Setup on Deployment

The `Procfile` is configured to automatically:
1. Run migrations
2. Collect static files
3. Setup gifts and GIF packs

**This happens automatically during release phase. No manual action needed.**

If Giphy GIFs don't populate automatically, manually trigger with:

```bash
python populate_gifs.py  # Run locally and sync to Render
```

## Troubleshooting

### Issue: "No gifts available" in Gift Picker

**Symptoms:** Gift picker opens but shows empty list

**Solution:**

1. Check if gifts exist in database:
   ```bash
   python manage.py shell
   >>> from chat.models import Gift
   >>> Gift.objects.count()
   # Should show 11
   ```

2. If count is 0, run setup:
   ```bash
   python manage.py setup_gifts_and_gifs
   ```

3. Check debug endpoint (doesn't require authentication):
   - Local: `http://localhost:8000/debug/gifts-status/`
   - Render: `https://yourdomain.onrender.com/debug/gifts-status/`

### Issue: "No GIFs available" in GIF Picker

**Symptoms:** GIF picker opens but shows empty grid

**Solution:**

1. Check GIF pack existence:
   ```bash
   python manage.py shell
   >>> from chat.models import GifPack, GifFile
   >>> GifPack.objects.count()  # Should be > 0
   >>> GifFile.objects.count()  # Should be > 0
   ```

2. If no GIF files, run population:
   ```bash
   python populate_gifs.py
   ```

3. Check media files are served:
   - Verify `MEDIA_ROOT` and `MEDIA_URL` in settings
   - Check if GIF files exist in `/media/gifs/` folder

### Issue: Gifts/GIFs not showing after deploying to Render

**Solution:**

1. Trigger a new deploy (click "Deploy" button in Render)
2. Watch the build logs to verify setup commands ran
3. Check environment variables are set correctly
4. Manually run setup if needed:
   ```bash
   # Via Render Shell
   python manage.py setup_gifts_and_gifs --settings=discord_chat.production
   ```

### Issue: Evercoin balance showing 0

**Solution:**

1. Initialize evercoin for users:
   ```bash
   python initialize_evercoin.py
   ```

2. Check user profile exists:
   ```bash
   python manage.py shell
   >>> from chat.models import UserProfile
   >>> from django.contrib.auth.models import User
   >>> user = User.objects.first()
   >>> profile = user.profile
   >>> print(profile.evercoin)
   ```

## Debugging API Responses

### Check Gifts API Response

```bash
# Requires authentication
curl -b cookies.txt http://localhost:8000/chat/gifts/list/
```

Expected response:
```json
{
    "success": true,
    "gifts": {
        "common": [...],
        "rare": [...],
        "epic": [...],
        "legendary": [...]
    },
    "user_evercoin": 5000
}
```

### Check GIF Packs API Response

```bash
curl -b cookies.txt http://localhost:8000/chat/gifs/packs/
```

Expected response:
```json
{
    "success": true,
    "packs": [
        {"id": 1, "name": "Funny", "icon": "😂", "gif_count": 2},
        ...
    ]
}
```

### Check Debug Endpoint (No Auth Required)

```bash
curl http://localhost:8000/debug/gifts-status/
```

Expected response:
```json
{
    "success": true,
    "gifts_count": 11,
    "gif_files_count": 11,
    "gif_packs_count": 10,
    "message": "Debug info"
}
```

## Database Models

### Gift Model
- `name`: Gift name (e.g., "Rose")
- `emoji`: Unicode emoji
- `rarity`: common | rare | epic | legendary
- `cost`: Evercoin cost (50-1000)
- `animation`: Animation type to play when received
- `description`: Short description

### GifPack Model
- `name`: Pack category name
- `icon`: Category emoji
- `is_active`: Whether pack is visible
- `order`: Display order

### GifFile Model
- `title`: GIF title
- `pack`: Related GifPack
- `gif_file`: Uploaded or external GIF file
- `url`: External URL (for Giphy)
- `thumbnail`: Thumbnail image
- `tags`: Comma-separated tags
- `is_active`: Whether GIF is visible

### Intimacy Model (Tracks 亲密度)
- `user1`: First user
- `user2`: Second user  
- `points`: Intimacy score between users

## Gift Costs Reference

| Gift | Emoji | Cost (EC) | Rarity |
|------|-------|-----------|--------|
| Rose | 🌹 | 50 | Common |
| Heart | ❤️ | 75 | Common |
| Star | ⭐ | 100 | Common |
| Cake | 🎂 | 150 | Common |
| Diamond | 💎 | 300 | Rare |
| Trophy | 🏆 | 350 | Rare |
| Crown | 👑 | 400 | Rare |
| Fireworks | 🎆 | 500 | Epic |
| Rainbow | 🌈 | 600 | Epic |
| Unicorn | 🦄 | 700 | Epic |
| Dragon | 🐉 | 1000 | Legendary |

## Gift Animations

Each gift triggers a different animation when received:

- **hearts-rain**: Rose, Heart - hearts falling
- **sparkle-spin**: Star - spinning with sparkles
- **float**: Cake - floating upward
- **crystal-drop**: Diamond - crystal falling effect
- **trophy-rise**: Trophy, Crown - rising with glow
- **fireworks**: Fireworks - burst effect
- **rotate-rainbow**: Rainbow - rotating with rainbow glow
- **unicorn-gallop**: Unicorn - galloping motion
- **dragon-fly**: Dragon - flying motion

## Support

For issues, check:
1. Database queries in Django shell
2. Server logs in Render dashboard
3. Browser console (F12) for JavaScript errors
4. Network tab to see API response codes and payloads

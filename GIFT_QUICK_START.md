# Quick Start: Gift System in EverSpace Chat

## What Changed? 🔄

| Feature | Before | After |
|---------|--------|-------|
| **Button** | 🎥 GIF | 🎁 Gift |
| **Search** | Tenor API (external) | Database (local) |
| **Content** | Animated GIFs | Emoji Gifts |
| **API Key** | Required | Not needed |
| **Tracking** | None | Full transaction log |

## For Users

### Send a Gift
```
1. Click 🎁 Gift button in chat
2. Browse gifts by rarity tab
3. Click gift you like
4. (Optional) Type message (max 200 chars)
5. Click "Send Gift"
6. Enter recipient username
7. Done! 🎉
```

### Available Gifts
- **Common:** Rose 🌹, Heart ❤️, Star ⭐, Flower 🌸, Cake 🎂
- **Rare:** Diamond 💎, Crown 👑, Trophy 🏆, Gift Box 🎁
- **Epic:** Fireworks 🎆, Rainbow 🌈, Unicorn 🦄
- **Legendary:** Dragon 🐉, Phoenix 🔥, Meteor ☄️

## For Developers

### New API Endpoints

#### POST /chat/gifts/send/
Send a gift to a user in the same room.

**Request:**
```json
{
  "gift_id": 1,
  "recipient": "username",
  "room": "1234567",
  "message": "optional message"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Gift sent to username!",
  "transaction_id": 123
}
```

#### GET /chat/gifts/list/
Get all available gifts grouped by rarity.

**Response:**
```json
{
  "success": true,
  "gifts": {
    "common": [{id, name, emoji, rarity}, ...],
    "rare": [...],
    "epic": [...],
    "legendary": [...]
  }
}
```

### Database Models

```python
# Gift.objects.all()
Gift
  ├─ id: int
  ├─ name: str (unique)
  ├─ emoji: str (e.g., "🌹")
  ├─ rarity: str (common|rare|epic|legendary)
  └─ created_at: datetime

# GiftTransaction.objects.all()
GiftTransaction
  ├─ id: int
  ├─ gift: FK(Gift)
  ├─ sender: FK(User)
  ├─ receiver: FK(User)
  ├─ room: FK(Room)
  ├─ quantity: int
  ├─ message: str (optional, max 200)
  └─ sent_at: datetime
```

### Add New Gifts

**Option 1: Edit populate_gifts.py**
```python
DEFAULT_GIFTS = [
    # Add your gift here:
    {
        'name': 'Treasure Chest',
        'emoji': '💰',
        'rarity': 'legendary',
        'description': 'A treasure chest full of gold',
        'icon_url': '/static/chat/gifts/treasure.png'
    }
]
```

Then run:
```bash
python populate_gifts.py
```

**Option 2: Django Admin**
```
http://localhost:8000/admin/chat/gift/
```

### Add Gift Images (Future Enhancement)

```bash
# Create folder
mkdir -p chat/static/chat/gifts/

# Add PNG/SVG files
# Update Gift.icon_url in database
```

## Files Changed

### Removed
- Tenor API key from `start.sh`
- `TENOR_API_KEY` from `settings.py`
- `gif_search()` view and URL route
- GIF picker UI from `room.html`

### Created
- `Gift` model in `models.py`
- `GiftTransaction` model in `models.py`
- `send_gift()` view in `views.py`
- `get_gifts()` view in `views.py`
- `populate_gifts.py` script
- Migration `0009_gift_gifttransaction.py`

### Updated
- `room.html` - Replaced GIF picker with Gift picker
- `urls.py` - Added gift endpoints
- Database - 15 new gifts populated

## Testing

### Check Gift Count
```bash
python manage.py shell
>>> from chat.models import Gift
>>> Gift.objects.count()
15  # ✅ Should return 15
```

### Send Test Gift
```python
from django.contrib.auth.models import User
from chat.models import Room, Gift, GiftTransaction

user1 = User.objects.get(username='ryanadmin')
user2 = User.objects.get(username='other_user')
room = Room.objects.first()
gift = Gift.objects.get(name='Rose')

GiftTransaction.objects.create(
    gift=gift,
    sender=user1,
    receiver=user2,
    room=room,
    message="For you!"
)
```

### Check Transactions
```python
GiftTransaction.objects.all()
# Shows all gifts ever sent
```

## Deployment

```bash
# 1. Apply migrations
python manage.py migrate

# 2. Populate gifts
python populate_gifts.py

# 3. Test in browser
# http://localhost:8000/chat/

# 4. Try sending a gift!
```

## FAQ

**Q: Can I customize the gifts?**  
A: Yes! Edit `populate_gifts.py` and rerun it, or use Django admin.

**Q: What happens if I delete a gift?**  
A: Old transactions are preserved (FK relationship). New users can't send that gift.

**Q: Can users see gift history?**  
A: Currently no UI for this, but data is in `GiftTransaction` table. Can add later.

**Q: Why no images, just emojis?**  
A: Keeps system simple. Can add PNG/SVG later without breaking anything.

**Q: Is there a daily gift limit?**  
A: Not yet, but can be added in future versions.

**Q: Can I edit messages after sending?**  
A: No, gifts are immutable once sent. This is by design.

## Troubleshooting

### "Gift picker shows error loading gifts"
```
Check 1: Is /chat/gifts/list/ endpoint working?
  curl http://localhost:8000/chat/gifts/list/

Check 2: Are gifts in database?
  python manage.py shell
  from chat.models import Gift
  print(Gift.objects.count())  # Should be 15+

Fix: python populate_gifts.py
```

### "Recipient is not a member of this room"
```
Both sender and receiver must be in same room.
Ask user to join the room first.
```

### "Gift doesn't appear in chat"
```
Check 1: WebSocket connection active (console)
Check 2: Browser console for errors
Check 3: Check room consumers handling gift_received
```

## Performance

- ✅ **No external API calls** = Fast
- ✅ **Local database queries** = Low latency
- ✅ **No rate limits** = Unlimited gifts
- ✅ **Emoji-only display** = Minimal bandwidth

---

**Documentation:** See `GIFT_SYSTEM_GUIDE.md` for full details  
**Summary:** See `GIFT_MIGRATION_SUMMARY.md` for all changes  
**Ready to Deploy:** Yes ✅  

Need help? Check the documentation files!

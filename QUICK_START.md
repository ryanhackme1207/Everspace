# ⚡ Quick Start Guide

## 🎯 Both Issues Are FIXED!

✅ **Unblock Friend** - Fully working
✅ **Real-Time Private Chat** - Fully working (needs Redis)

---

## 🚀 Get Started in 3 Steps

### 1. Install Redis (One-Time)

**Windows - Download Memurai:**
- Download: https://www.memurai.com/get-memurai
- Install the .msi file
- It will auto-start

**Or use Docker:**
```bash
docker run -d -p 6379:6379 --name redis redis:alpine
```

### 2. Start the Server

**Double-click:** `start_server.bat`

**Or manually:**
```powershell
cd "c:\Users\Acer Nitro 5\Desktop\project 3"
.\.venv\Scripts\python.exe -m daphne -p 8000 discord_chat.asgi:application
```

### 3. Open Browser

Go to: **http://localhost:8000**

---

## ✅ Test Unblock (30 seconds)

1. Main page → Block a friend
2. Scroll to "Blocked Friends"
3. Click 🔓 unblock button
4. Confirm
5. ✅ Done! User unblocked

---

## ✅ Test Real-Time Chat (2 minutes)

**Requirements:**
- ⚠️ TWO different users
- ⚠️ TWO different browsers (Chrome + Edge)

**Steps:**
1. Browser 1: Login as User A
2. Browser 2: Login as User B
3. Both: Click each other's friend card
4. Browser 1: Type "Hello!" → Enter
5. Browser 2: ✅ Message appears INSTANTLY!

---

## 🐛 Not Working?

### Unblock Not Working?
```powershell
# Verify code is in place
python verify_features.py

# Open browser DevTools (F12)
# Check Console for errors
# Check Network tab for /friends/unblock/ response
```

### Real-Time Chat Not Working?

**Common Issues:**

1. **Testing with same user?**
   - ❌ Won't work with same user in two tabs
   - ✅ Need TWO different users

2. **Redis not running?**
   ```powershell
   python check_environment.py
   ```
   Should show: `✅ Redis is running`

3. **Using runserver?**
   - ❌ Don't use: `python manage.py runserver`
   - ✅ Use: `daphne -p 8000 discord_chat.asgi:application`
   - ✅ Or double-click: `start_server.bat`

---

## 📋 Helpful Commands

**Check everything is ready:**
```powershell
python check_environment.py
```

**Verify code is implemented:**
```powershell
python verify_features.py
```

**Start server with WebSocket:**
```powershell
start_server.bat
```

**Stop server:**
- Press `Ctrl + C`

---

## 📚 Full Documentation

- `ISSUE_RESOLUTION.md` - What was fixed
- `SETUP_AND_TESTING.md` - Complete setup guide
- `TESTING_GUIDE.md` - Detailed testing instructions

---

## ✅ Success Checklist

Before testing:
- [ ] Redis installed and running
- [ ] Server started with Daphne (not runserver)
- [ ] For chat: Two different user accounts
- [ ] For chat: Two different browsers/devices

---

## 🎉 Expected Results

**Unblock:**
- Click → Confirm → Notification → Reload → User removed
- Time: ~2 seconds

**Real-Time Chat:**
- Type message → Press Enter → Appears on other side
- Time: <1 second (instant!)
- No refresh needed ✅

---

## 💡 Remember

1. **Unblock works immediately** - Just needs the URL and view (already added)
2. **Real-time chat works** - Just needs Redis running
3. **Use Daphne, not runserver** - For WebSocket support
4. **Test chat with 2 users** - Same user won't show real-time updates

Everything is ready! Just start Redis and run the server! 🚀

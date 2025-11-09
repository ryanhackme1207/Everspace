# 🚀 Complete Setup and Testing Guide

## ✅ Current Status

### What's Already Done:
1. ✅ **Unblock Friend Feature** - Fully implemented
   - Backend URL: `/friends/unblock/`
   - View function: `unblock_friend()` in views.py
   - Frontend button and JavaScript ready
   
2. ✅ **Real-Time Private Chat** - Fully implemented
   - WebSocket consumer: `PrivateChatConsumer`
   - WebSocket client in private_chat.html
   - Real-time message delivery
   
3. ✅ **Required Packages Installed**
   - Django Channels 4.3.1 ✅
   - Daphne 4.2.1 ✅
   - channels-redis ✅
   - redis ✅

### What Needs to be Done:
- ⚠️ **Start Redis Server** (required for WebSocket to work)

---

## 📋 Step-by-Step Setup

### Step 1: Install Redis (If Not Already Installed)

**For Windows:**

Download and install Redis from one of these options:

**Option A: Memurai (Recommended for Windows)**
1. Download from: https://www.memurai.com/get-memurai
2. Install the .msi file
3. Start Memurai from Start Menu or run: `memurai`

**Option B: Redis for Windows (via WSL)**
```powershell
# Install WSL if you don't have it
wsl --install

# Inside WSL terminal:
sudo apt update
sudo apt install redis-server
sudo service redis-server start
```

**Option C: Docker (If you have Docker)**
```powershell
docker run -d -p 6379:6379 redis:alpine
```

### Step 2: Start Redis

**If using Memurai:**
- It should auto-start after installation
- Or run from Start Menu: "Memurai"

**If using WSL:**
```bash
sudo service redis-server start
```

**If using Docker:**
```bash
docker start <container-name>
```

### Step 3: Verify Redis is Running

Open PowerShell and run:
```powershell
cd "c:\Users\Acer Nitro 5\Desktop\project 3"
.\.venv\Scripts\python.exe check_environment.py
```

You should see: `✅ Redis is running and accessible`

### Step 4: Start the Application

**Open TWO PowerShell windows:**

**Terminal 1 - Start Redis (if needed):**
```powershell
# Skip if Redis auto-starts (Memurai)
# Or if using WSL: wsl sudo service redis-server start
```

**Terminal 2 - Start Django with WebSocket Support:**
```powershell
cd "c:\Users\Acer Nitro 5\Desktop\project 3"
.\.venv\Scripts\python.exe -m daphne -p 8000 discord_chat.asgi:application
```

You should see:
```
2025-XX-XX XX:XX:XX INFO     Starting server at tcp:port=8000:interface=127.0.0.1
2025-XX-XX XX:XX:XX INFO     HTTP/2 support not enabled (install the http2 package)
2025-XX-XX XX:XX:XX INFO     Configuring endpoint tcp:port=8000:interface=127.0.0.1
```

### Step 5: Open Browser

Navigate to: `http://localhost:8000`

---

## 🧪 Testing the Features

### Test 1: Unblock Friend Feature

1. **Login** to your account
2. **Block a friend** first (if you don't have any):
   - Go to main page
   - Find a friend
   - Click block button (🚫 icon)
   - Confirm
   
3. **Find Blocked Users Section**:
   - Scroll down on main page
   - Look for "Blocked Friends" section
   - You should see blocked user with grayscale avatar
   
4. **Unblock the User**:
   - Click the unblock button (🔓 icon)
   - Confirm in dialog box
   - You should see success notification
   - Page will reload after 1.5 seconds
   - User should be removed from blocked list
   
5. **Verify**:
   - User is no longer in blocked list
   - You can send friend request again

**Expected Result:** ✅ Unblock works instantly, user removed from blocked list

---

### Test 2: Real-Time Private Chat

⚠️ **CRITICAL: You MUST test with TWO different users!**

#### Setup (One-time):

1. **Create two test accounts**:
   - Account 1: "alice" (or use your existing account)
   - Account 2: "bob" (create a new test account)
   
2. **Make them friends**:
   - Send friend request from alice to bob
   - Accept it in bob's account

#### Testing Steps:

1. **Open TWO browsers** (or Incognito + Normal):
   - Browser 1: Google Chrome
   - Browser 2: Microsoft Edge (or Firefox)
   
2. **Login to different accounts**:
   - Browser 1: Login as "alice"
   - Browser 2: Login as "bob"
   
3. **Open DevTools in BOTH browsers**:
   - Press F12
   - Go to Console tab
   
4. **Open Private Chat on BOTH sides**:
   - Browser 1 (alice): Click on bob's friend card
   - Browser 2 (bob): Click on alice's friend card
   - Both should be in private chat view
   
5. **Check Console for WebSocket Connection**:
   - Look for: `[WebSocket] Connected to private chat`
   - ✅ If you see this, WebSocket is working!
   - ❌ If you don't see this, Redis may not be running
   
6. **Send Messages**:
   - Browser 1 (alice): Type "Hello from Alice!" and press Enter
   - **Immediately check Browser 2 (bob)**:
     - Message should appear **instantly** without refresh
     - You should see "Hello from Alice!" in bob's chat
   
   - Browser 2 (bob): Type "Hi Alice!" and press Enter
   - **Immediately check Browser 1 (alice)**:
     - Message should appear **instantly** without refresh
   
7. **Test Typing Indicator** (Bonus):
   - Start typing in one browser (don't send)
   - Other browser should show "... is typing" indicator

**Expected Result:** 
- ✅ Messages appear instantly without refresh
- ✅ Console shows "[WebSocket] Received" logs
- ✅ Typing indicators work
- ✅ Sound plays on message receive (unless muted)

---

## 🐛 Troubleshooting

### Issue: "Unblock doesn't work"

**Symptoms:**
- Button click does nothing
- No notification appears
- User still in blocked list

**Solutions:**

1. **Check Browser Console (F12)**:
   ```javascript
   // Should see:
   POST http://localhost:8000/friends/unblock/ 200 OK
   ```
   
2. **Check Network Tab**:
   - Go to Network tab in DevTools
   - Click unblock button
   - Look for request to `/friends/unblock/`
   - Check response: should be `{"success": true, ...}`
   
3. **Check CSRF Token**:
   - View page source
   - Search for: `csrfmiddlewaretoken`
   - Should exist in a hidden input field
   
4. **Verify URL exists**:
   ```powershell
   cd "c:\Users\Acer Nitro 5\Desktop\project 3"
   .\.venv\Scripts\python.exe verify_features.py
   ```
   Should show: `✅ Found: path('friends/unblock/'`

---

### Issue: "Real-time chat doesn't work / Messages need refresh"

**Symptoms:**
- Messages don't appear instantly
- Need to refresh page to see new messages
- Console shows errors

**Common Mistakes:**

1. ❌ **Testing with same user in two tabs**
   - This won't work! You need TWO different users
   - Solution: Use two different accounts in different browsers
   
2. ❌ **Redis not running**
   - WebSocket needs Redis
   - Check: Run `check_environment.py`
   - Solution: Start Redis (see Step 1 above)
   
3. ❌ **Using `runserver` instead of Daphne**
   - `python manage.py runserver` doesn't support WebSocket
   - Solution: Use `daphne -p 8000 discord_chat.asgi:application`
   
4. ❌ **Not checking both sides**
   - You need to be in the chat view on BOTH accounts
   - Solution: Open private chat on both browsers

**Diagnostic Steps:**

1. **Check Redis is running**:
   ```powershell
   .\.venv\Scripts\python.exe check_environment.py
   ```
   Should show: `✅ Redis is running and accessible`
   
2. **Check WebSocket connection**:
   - Open DevTools Console (F12)
   - Look for: `[WebSocket] Connected to private chat`
   - If missing, check server console for errors
   
3. **Check server is using Daphne**:
   - Server output should say "Starting server at tcp:port=8000"
   - If it says "Starting development server", you're using wrong command
   
4. **Check WebSocket URL**:
   - In Console, should see: `ws://localhost:8000/ws/private-chat/<username>/`
   - If shows `http://` instead of `ws://`, WebSocket not configured
   
5. **Test with curl (advanced)**:
   ```powershell
   curl -X POST http://localhost:8000/friends/send-message/ `
     -H "Content-Type: application/x-www-form-urlencoded" `
     -d "username=testuser&content=test"
   ```

---

### Issue: "Packages not found"

**Symptoms:**
- ImportError: No module named 'channels'
- ImportError: No module named 'redis'

**Solution:**
```powershell
cd "c:\Users\Acer Nitro 5\Desktop\project 3"
.\.venv\Scripts\python.exe -m pip install channels channels-redis daphne redis
```

---

### Issue: "Port 8000 already in use"

**Symptoms:**
- Error: [Errno 10048] error while attempting to bind
- Address already in use

**Solutions:**

1. **Find process using port 8000**:
   ```powershell
   netstat -ano | findstr :8000
   ```
   
2. **Kill the process**:
   ```powershell
   # Replace <PID> with the process ID from above
   taskkill /PID <PID> /F
   ```
   
3. **Or use different port**:
   ```powershell
   .\.venv\Scripts\python.exe -m daphne -p 8001 discord_chat.asgi:application
   ```
   Then open: `http://localhost:8001`

---

## 🎯 Quick Reference Commands

### Check if everything is ready:
```powershell
cd "c:\Users\Acer Nitro 5\Desktop\project 3"
.\.venv\Scripts\python.exe check_environment.py
```

### Verify features are implemented:
```powershell
.\.venv\Scripts\python.exe verify_features.py
```

### Start the application:
```powershell
# Make sure Redis is running first!
.\.venv\Scripts\python.exe -m daphne -p 8000 discord_chat.asgi:application
```

### Stop the application:
- Press `Ctrl + C` in the terminal

### View server logs:
- Check the terminal where Daphne is running
- Look for WebSocket connection messages
- Look for error messages

---

## ✅ Success Checklist

Before you start testing, verify:

- [ ] Redis is installed and running
- [ ] All packages installed (channels, daphne, etc.)
- [ ] Application started with Daphne (not runserver)
- [ ] Browser can access http://localhost:8000
- [ ] For unblock: Have at least one blocked user
- [ ] For chat: Have two different user accounts
- [ ] For chat: Using two different browsers/devices
- [ ] DevTools Console open (F12) to see logs

---

## 📞 Still Having Issues?

Run the diagnostic scripts and save the output:

```powershell
# Check environment
.\.venv\Scripts\python.exe check_environment.py > environment_report.txt

# Verify features
.\.venv\Scripts\python.exe verify_features.py > features_report.txt

# Check for errors
.\.venv\Scripts\python.exe manage.py check
```

Then review the output files for specific issues.

---

## 🎉 Expected Final Results

### When Working Correctly:

1. **Unblock Feature**:
   - Button click → Confirmation dialog → Success notification → Page reload → User removed
   - Total time: ~2 seconds
   
2. **Real-Time Chat**:
   - User A types message → Presses Enter → User B sees it immediately (<1 second)
   - No refresh needed
   - Typing indicators work
   - Sounds play
   - Console shows WebSocket activity

Both features are 100% implemented and ready to use!

Just need to start Redis and use Daphne instead of runserver.

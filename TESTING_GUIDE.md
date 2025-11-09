# Testing Guide for Recent Features

## 1. Unblock Friend Feature ✅

### Backend Implementation
- **URL**: `/friends/unblock/` (POST)
- **View**: `unblock_friend()` in `chat/views.py` (line 1312)
- **Function**: Deletes blocked Friendship record to allow interaction again

### Frontend Implementation
- **Button**: Located in Blocked Friends section on main page
- **JavaScript**: `unblockFriend()` function in `chat/templates/chat/index.html` (line 2151)

### How to Test
1. **Block a User First**:
   - Go to main page
   - Find a friend in your friends list
   - Click the block button (🚫 icon)
   - Confirm the action

2. **View Blocked Users**:
   - On main page, find the "Blocked Friends" section
   - You should see the blocked user with grayscale avatar
   - Status shows "Blocked" with ban icon

3. **Unblock the User**:
   - Click the unblock button (🔓 unlock icon)
   - Confirm the unblock action in the dialog
   - You should see a success notification
   - Page will reload after 1.5 seconds
   - User should disappear from blocked list

4. **Verify Unblock**:
   - You can now send friend request to this user again
   - No blocked relationship exists in database

### Troubleshooting
- **If unblock doesn't work**:
  - Open browser DevTools (F12)
  - Go to Console tab
  - Click unblock button
  - Check for JavaScript errors
  - Go to Network tab
  - Look for POST request to `/friends/unblock/`
  - Check response (should be `{"success": true, "message": "..."}`)

---

## 2. Real-Time Private Chat Messages ✅

### Backend Implementation
- **WebSocket**: `PrivateChatConsumer` in `chat/private_chat_consumer.py` (line 11)
- **URL Pattern**: `/ws/private-chat/<username>/`
- **Channels**: Uses Django Channels with Redis

### Frontend Implementation
- **WebSocket Client**: `connectWebSocket()` in `chat/templates/chat/private_chat.html` (line 1101)
- **Message Handler**: Listens for 'chat_message' type (line 1112)
- **Send Method**: Uses WebSocket if connected, fallback to HTTP (line 1254)

### How Messages Flow
1. **User A sends message**:
   - JavaScript calls `sendMessage()` function
   - Checks if WebSocket is connected (line 1260)
   - Sends via `privateSocket.send()` with type 'chat_message'
   - Message added to UI immediately (line 1267)

2. **Backend receives message**:
   - `PrivateChatConsumer.receive()` handles it (line 50)
   - Saves message to database
   - Broadcasts to channel group (both users) via `group_send()`

3. **User B receives message**:
   - WebSocket `onmessage` handler triggered (line 1112)
   - Checks `data.sender !== currentUsername` (line 1117)
   - Calls `addMessage()` to display (line 1118)
   - Plays notification sound
   - Marks message as read

### How to Test Properly

#### ⚠️ IMPORTANT: Testing Requirements
You **CANNOT** test real-time messaging with:
- Same browser, different tabs (same user)
- Same user logged in twice
- Same device/browser

You **MUST** test with:
- Two different browsers (Chrome + Firefox)
- Two different devices (PC + Phone)
- Two different user accounts
- Incognito/Private windows with different users

#### Testing Steps
1. **Setup**:
   - Create two test accounts (e.g., "alice" and "bob")
   - Make sure they are friends (accepted friendship)

2. **Open Two Sessions**:
   - Browser 1: Login as "alice"
   - Browser 2: Login as "bob"
   - Keep DevTools open in both (F12)

3. **Start Private Chat**:
   - In Browser 1 (alice): Click on bob's friend card
   - In Browser 2 (bob): Click on alice's friend card
   - Both should be in private chat view

4. **Test Real-Time Messaging**:
   - In Browser 1 (alice): Type "Hello from Alice" and press Enter
   - Check Browser 2 (bob): Message should appear **immediately** without refresh
   - In Browser 2 (bob): Type "Hi Alice!" and press Enter
   - Check Browser 1 (alice): Message should appear **immediately**

5. **Verify WebSocket Connection**:
   - In DevTools Console, look for:
     ```
     [WebSocket] Connected to private chat
     [WebSocket] Received: {type: 'chat_message', message: '...', sender: '...'}
     ```

6. **Test Typing Indicators** (Bonus):
   - Start typing in one browser
   - Other browser should show "... is typing" indicator

### Expected Behavior
- ✅ Messages appear instantly without page refresh
- ✅ Console shows WebSocket connection established
- ✅ Console logs received messages
- ✅ Sound plays when receiving message (unless muted)
- ✅ Typing indicators work
- ✅ Messages persist after page refresh

### Troubleshooting

#### Messages Require Refresh
**Possible Causes**:
1. **WebSocket not connected**:
   - Check console for "[WebSocket] Connected" message
   - If missing, check Redis is running: `redis-cli ping` should return "PONG"
   - Check Daphne/ASGI server is running

2. **Testing with same user**:
   - Must test with TWO different users in TWO different browsers
   - Logic filters out your own messages: `if (data.sender !== currentUsername)`

3. **JavaScript errors**:
   - Open DevTools Console (F12)
   - Look for red error messages
   - Check if `addMessage()` function is defined

4. **Backend issues**:
   - Check server console for errors
   - Verify Channels and Redis are configured
   - Test WebSocket URL manually: `ws://localhost:8000/ws/private-chat/username/`

#### WebSocket Won't Connect
1. **Check ASGI application**:
   ```bash
   # Make sure you're running with Daphne, not runserver
   daphne -p 8000 discord_chat.asgi:application
   ```

2. **Check Redis**:
   ```bash
   redis-cli ping
   # Should return: PONG
   ```

3. **Check routing**:
   - File: `chat/routing.py`
   - Should have: `path('ws/private-chat/<str:friend_username>/', PrivateChatConsumer.as_asgi())`

4. **Check settings**:
   - `CHANNEL_LAYERS` configured in settings
   - `ASGI_APPLICATION` set to `'discord_chat.asgi.application'`

---

## Quick Verification Checklist

### Unblock Feature
- [ ] URL `/friends/unblock/` exists in `chat/urls.py`
- [ ] `unblock_friend()` view exists in `chat/views.py`
- [ ] Unblock button appears in Blocked Friends section
- [ ] JavaScript function `unblockFriend()` exists
- [ ] CSRF token present on page
- [ ] Success notification appears
- [ ] Page reloads after unblock
- [ ] User removed from blocked list

### Real-Time Chat
- [ ] WebSocket connects (check console)
- [ ] Using two different users in different browsers
- [ ] Messages appear instantly without refresh
- [ ] Console shows "Received" messages
- [ ] Typing indicators work
- [ ] Sound plays on message receive
- [ ] Redis is running
- [ ] Using Daphne/ASGI server (not runserver)

---

## Common Mistakes

### "Unblock doesn't work"
- ❌ Not checking browser console for errors
- ❌ Not checking Network tab for HTTP response
- ❌ Expecting instant UI update (page needs reload)
- ✅ Check if URL exists in urls.py
- ✅ Check if view function has correct logic
- ✅ Verify CSRF token is being sent

### "Real-time chat doesn't work"
- ❌ Testing with same user in two tabs
- ❌ Using Django runserver instead of Daphne
- ❌ Redis not running
- ❌ Looking at wrong page (not both chat windows)
- ✅ Use two different users
- ✅ Use two different browsers/devices
- ✅ Check WebSocket connection in console
- ✅ Verify both users are in chat view

---

## Technical Details

### Unblock Flow
```
User clicks Unblock
    ↓
JavaScript: unblockFriend(username)
    ↓
Fetch POST: /friends/unblock/
    ↓
Backend: views.unblock_friend()
    ↓
Find Friendship with status='blocked'
    ↓
Delete Friendship record
    ↓
Return JSON: {success: true, message: '...'}
    ↓
Show notification
    ↓
Reload page after 1.5s
```

### Real-Time Message Flow
```
User A: Type message → Press Enter
    ↓
JavaScript: sendMessage()
    ↓
WebSocket: privateSocket.send({type: 'chat_message', message: '...'})
    ↓
Add to UI immediately (User A sees it)
    ↓
Backend: PrivateChatConsumer.receive()
    ↓
Save to database
    ↓
Broadcast: channel_layer.group_send()
    ↓
User A WebSocket: Receives message (filtered out: sender === currentUsername)
User B WebSocket: Receives message
    ↓
User B: addMessage(message, false, timestamp)
    ↓
Message appears in User B's chat (real-time!)
```

---

## Need Help?

If features still don't work after following this guide:

1. **Collect Debug Info**:
   - Browser console errors (screenshot)
   - Network tab showing failed requests
   - Server console output
   - Redis status: `redis-cli ping`
   - Python packages: `pip list | grep -i "django\|channels\|redis"`

2. **Check Prerequisites**:
   ```bash
   # Required packages
   pip install channels channels-redis daphne redis

   # Start Redis (if not running)
   redis-server

   # Run with Daphne (for WebSocket support)
   daphne -p 8000 discord_chat.asgi:application
   ```

3. **Verify Code**:
   - `chat/urls.py` - unblock URL present
   - `chat/views.py` - unblock_friend() function exists
   - `chat/private_chat_consumer.py` - WebSocket consumer complete
   - `chat/templates/chat/index.html` - unblockFriend() JavaScript
   - `chat/templates/chat/private_chat.html` - WebSocket connection code

All code is already implemented! Both features should work out of the box.

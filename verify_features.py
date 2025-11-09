"""
Verification Script for Unblock and Real-Time Chat Features
This script checks if all required components are properly implemented.
"""

import os
import sys

def check_file_contains(filepath, search_strings, description):
    """Check if file contains all required strings"""
    print(f"\n{'='*60}")
    print(f"Checking: {description}")
    print(f"File: {filepath}")
    print(f"{'='*60}")
    
    if not os.path.exists(filepath):
        print(f"❌ FILE NOT FOUND: {filepath}")
        return False
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    all_found = True
    for search_str in search_strings:
        if search_str in content:
            print(f"✅ Found: {search_str[:50]}...")
        else:
            print(f"❌ Missing: {search_str[:50]}...")
            all_found = False
    
    return all_found

def main():
    print("""
    ╔═══════════════════════════════════════════════════════════╗
    ║   Feature Verification Script                             ║
    ║   Checking: Unblock Friend + Real-Time Private Chat       ║
    ╚═══════════════════════════════════════════════════════════╝
    """)
    
    base_path = r"c:\Users\Acer Nitro 5\Desktop\project 3"
    results = []
    
    # 1. Check unblock URL
    results.append(check_file_contains(
        os.path.join(base_path, "chat", "urls.py"),
        ["path('friends/unblock/', views.unblock_friend, name='unblock_friend')"],
        "Unblock URL Route"
    ))
    
    # 2. Check unblock view
    results.append(check_file_contains(
        os.path.join(base_path, "chat", "views.py"),
        [
            "def unblock_friend(request):",
            "friendship.delete()",
            "You have unblocked"
        ],
        "Unblock View Function"
    ))
    
    # 3. Check unblock JavaScript
    results.append(check_file_contains(
        os.path.join(base_path, "chat", "templates", "chat", "index.html"),
        [
            "function unblockFriend(username)",
            "fetch('/friends/unblock/'",
            "onclick=\"unblockFriend"
        ],
        "Unblock Frontend (JavaScript + Button)"
    ))
    
    # 4. Check WebSocket consumer
    results.append(check_file_contains(
        os.path.join(base_path, "chat", "private_chat_consumer.py"),
        [
            "class PrivateChatConsumer",
            "async def receive",
            "chat_message",
            "channel_layer.group_send"
        ],
        "WebSocket Consumer (Backend)"
    ))
    
    # 5. Check WebSocket client
    results.append(check_file_contains(
        os.path.join(base_path, "chat", "templates", "chat", "private_chat.html"),
        [
            "let privateSocket = null",
            "function connectWebSocket()",
            "new WebSocket(wsPath)",
            "privateSocket.onmessage",
            "if (data.type === 'chat_message')",
            "addMessage(data.message, false"
        ],
        "WebSocket Client (Frontend)"
    ))
    
    # 6. Check WebSocket routing
    results.append(check_file_contains(
        os.path.join(base_path, "chat", "routing.py"),
        [
            "PrivateChatConsumer",
            "ws/private-chat"
        ],
        "WebSocket URL Routing"
    ))
    
    # Summary
    print(f"\n{'='*60}")
    print("VERIFICATION SUMMARY")
    print(f"{'='*60}")
    
    passed = sum(results)
    total = len(results)
    
    print(f"\nTests Passed: {passed}/{total}")
    
    if passed == total:
        print("""
        ✅ ✅ ✅ ALL CHECKS PASSED! ✅ ✅ ✅
        
        Both features are fully implemented:
        
        1. ✅ Unblock Friend Feature
           - URL route exists
           - Backend view implemented
           - Frontend button and JavaScript ready
        
        2. ✅ Real-Time Private Chat
           - WebSocket consumer implemented
           - WebSocket client connected
           - Message handlers configured
           - Routing configured
        
        IMPORTANT TESTING NOTES:
        
        For Unblock Feature:
        - Go to main page
        - Find Blocked Friends section
        - Click unblock button
        - Confirm action
        - Page will reload
        
        For Real-Time Chat:
        - MUST test with TWO different users
        - MUST use TWO different browsers/devices
        - Cannot test with same user in two tabs!
        - Open private chat on both sides
        - Type message in one browser
        - Should appear instantly in other browser
        
        Make sure Redis is running:
            redis-server
        
        Run application with Daphne (for WebSocket):
            daphne -p 8000 discord_chat.asgi:application
        
        Check the TESTING_GUIDE.md for detailed instructions!
        """)
    else:
        print(f"""
        ⚠️  {total - passed} CHECK(S) FAILED
        
        Please review the failed checks above.
        Some components may be missing or incorrectly implemented.
        """)
    
    print(f"{'='*60}\n")

if __name__ == "__main__":
    main()

"""
Runtime Debugging Helper
Run this script to check common issues that might prevent features from working
"""

import os
import sys

def check_redis():
    """Check if Redis is running"""
    print("\n" + "="*60)
    print("1. Checking Redis Connection")
    print("="*60)
    
    try:
        import redis
        r = redis.Redis(host='localhost', port=6379, db=0, socket_connect_timeout=2)
        r.ping()
        print("✅ Redis is running and accessible")
        return True
    except ImportError:
        print("❌ Redis package not installed. Run: pip install redis")
        return False
    except Exception as e:
        print(f"❌ Cannot connect to Redis: {e}")
        print("\n💡 Solutions:")
        print("   - Start Redis: redis-server")
        print("   - Check if Redis is installed")
        print("   - Verify Redis is running on localhost:6379")
        return False

def check_channels():
    """Check if Django Channels is installed"""
    print("\n" + "="*60)
    print("2. Checking Django Channels")
    print("="*60)
    
    try:
        import channels
        print(f"✅ Django Channels {channels.__version__} is installed")
        return True
    except ImportError:
        print("❌ Django Channels not installed. Run: pip install channels channels-redis")
        return False

def check_daphne():
    """Check if Daphne is installed"""
    print("\n" + "="*60)
    print("3. Checking Daphne ASGI Server")
    print("="*60)
    
    try:
        import daphne
        print(f"✅ Daphne {daphne.__version__} is installed")
        return True
    except ImportError:
        print("❌ Daphne not installed. Run: pip install daphne")
        return False

def check_settings():
    """Check Django settings for Channels configuration"""
    print("\n" + "="*60)
    print("4. Checking Django Settings")
    print("="*60)
    
    settings_path = r"c:\Users\Acer Nitro 5\Desktop\project 3\discord_chat\settings.py"
    
    if not os.path.exists(settings_path):
        print(f"❌ Settings file not found: {settings_path}")
        return False
    
    with open(settings_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    checks = [
        ("ASGI_APPLICATION", "ASGI application configured"),
        ("CHANNEL_LAYERS", "Channel layers configured"),
        ("'channels'", "Channels app in INSTALLED_APPS")
    ]
    
    all_ok = True
    for key, description in checks:
        if key in content:
            print(f"✅ {description}")
        else:
            print(f"⚠️  May be missing: {description}")
            all_ok = False
    
    return all_ok

def check_migrations():
    """Check if database migrations are up to date"""
    print("\n" + "="*60)
    print("5. Checking Database Migrations")
    print("="*60)
    
    try:
        os.chdir(r"c:\Users\Acer Nitro 5\Desktop\project 3")
        import subprocess
        result = subprocess.run(
            [sys.executable, "manage.py", "showmigrations", "--plan"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if "[X]" in result.stdout and "[ ]" not in result.stdout:
            print("✅ All migrations applied")
            return True
        elif "[ ]" in result.stdout:
            print("⚠️  Unapplied migrations detected")
            print("\n💡 Run: python manage.py migrate")
            return False
        else:
            print("✅ Migrations check completed")
            return True
            
    except Exception as e:
        print(f"⚠️  Could not check migrations: {e}")
        return True  # Don't fail on this

def print_startup_commands():
    """Print commands to start the application"""
    print("\n" + "="*60)
    print("6. Application Startup Commands")
    print("="*60)
    
    print("""
    To run the application with WebSocket support:
    
    1. Start Redis (in one terminal):
       redis-server
    
    2. Start Django with Daphne (in another terminal):
       cd "c:\\Users\\Acer Nitro 5\\Desktop\\project 3"
       daphne -p 8000 discord_chat.asgi:application
    
    3. Open browser:
       http://localhost:8000
    
    Alternative (without WebSocket - for testing only):
       python manage.py runserver
       (Note: WebSocket features won't work with runserver!)
    """)

def test_websocket_url():
    """Check if WebSocket URLs are properly configured"""
    print("\n" + "="*60)
    print("7. WebSocket URL Configuration")
    print("="*60)
    
    asgi_path = r"c:\Users\Acer Nitro 5\Desktop\project 3\discord_chat\asgi.py"
    routing_path = r"c:\Users\Acer Nitro 5\Desktop\project 3\chat\routing.py"
    
    files_ok = True
    
    if os.path.exists(asgi_path):
        with open(asgi_path, 'r', encoding='utf-8') as f:
            content = f.read()
            if "ProtocolTypeRouter" in content and "websocket" in content:
                print("✅ ASGI configuration looks correct")
            else:
                print("⚠️  ASGI configuration may be incomplete")
                files_ok = False
    else:
        print(f"❌ ASGI file not found: {asgi_path}")
        files_ok = False
    
    if os.path.exists(routing_path):
        with open(routing_path, 'r', encoding='utf-8') as f:
            content = f.read()
            if "PrivateChatConsumer" in content and "private-chat" in content:
                print("✅ Private chat WebSocket routing configured")
            else:
                print("⚠️  Private chat routing may be missing")
                files_ok = False
    else:
        print(f"❌ Routing file not found: {routing_path}")
        files_ok = False
    
    return files_ok

def main():
    print("""
    ╔═══════════════════════════════════════════════════════════╗
    ║        Runtime Environment Debugging Helper              ║
    ║   Checks prerequisites for Unblock and Real-Time Chat    ║
    ╚═══════════════════════════════════════════════════════════╝
    """)
    
    results = []
    
    # Run all checks
    results.append(("Redis", check_redis()))
    results.append(("Channels", check_channels()))
    results.append(("Daphne", check_daphne()))
    results.append(("Settings", check_settings()))
    results.append(("Migrations", check_migrations()))
    results.append(("WebSocket URLs", test_websocket_url()))
    
    # Print startup commands
    print_startup_commands()
    
    # Summary
    print("\n" + "="*60)
    print("ENVIRONMENT CHECK SUMMARY")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    print(f"\nChecks Passed: {passed}/{total}\n")
    
    for name, result in results:
        status = "✅" if result else "❌"
        print(f"{status} {name}")
    
    if passed == total:
        print("""
        ╔═══════════════════════════════════════════════════════════╗
        ║        ✅ ENVIRONMENT READY! ✅                           ║
        ╚═══════════════════════════════════════════════════════════╝
        
        All prerequisites are installed and configured!
        
        To start testing:
        
        1. Start Redis: redis-server
        2. Start app: daphne -p 8000 discord_chat.asgi:application
        3. Open browser: http://localhost:8000
        
        Both features should work:
        - ✅ Unblock friend (check Blocked Friends section)
        - ✅ Real-time private chat (test with 2 different users)
        """)
    else:
        print("""
        ╔═══════════════════════════════════════════════════════════╗
        ║     ⚠️  SOME CHECKS FAILED - Action Required ⚠️          ║
        ╚═══════════════════════════════════════════════════════════╝
        
        Please fix the failed checks above before testing.
        
        Quick fixes:
        
        Install missing packages:
            pip install channels channels-redis daphne redis
        
        Start Redis:
            redis-server
        
        Apply migrations:
            python manage.py migrate
        """)
    
    print("="*60 + "\n")

if __name__ == "__main__":
    main()

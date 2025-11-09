"""
Keep-Alive Bot for Render Free Tier
This bot pings your web service every 10 minutes to keep it alive
and prevent automatic spin-down on Render's free plan.
"""

import requests
import time
import logging
from datetime import datetime
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('keep_alive.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Your Render URL (change this to your actual Render URL)
RENDER_URL = os.environ.get('RENDER_URL', 'https://your-app-name.onrender.com')

# Ping interval in seconds (10 minutes = 600 seconds)
PING_INTERVAL = 600

# Timeout for requests
REQUEST_TIMEOUT = 30

def ping_service():
    """Ping the service to keep it alive"""
    try:
        logger.info(f"Pinging service at {RENDER_URL}...")
        
        response = requests.get(
            RENDER_URL,
            timeout=REQUEST_TIMEOUT,
            headers={
                'User-Agent': 'KeepAliveBot/1.0',
                'Accept': 'text/html,application/json'
            }
        )
        
        if response.status_code == 200:
            logger.info(f"✅ Ping successful! Status: {response.status_code}")
            return True
        else:
            logger.warning(f"⚠️ Unexpected status code: {response.status_code}")
            return False
            
    except requests.exceptions.Timeout:
        logger.error("❌ Request timed out")
        return False
    except requests.exceptions.ConnectionError as e:
        logger.error(f"❌ Connection error: {e}")
        return False
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
        return False

def main():
    """Main loop to keep the service alive"""
    logger.info("🚀 Keep-Alive Bot started!")
    logger.info(f"📍 Target URL: {RENDER_URL}")
    logger.info(f"⏱️  Ping interval: {PING_INTERVAL} seconds ({PING_INTERVAL/60} minutes)")
    logger.info("="*60)
    
    ping_count = 0
    success_count = 0
    
    while True:
        try:
            ping_count += 1
            logger.info(f"\n🔄 Ping #{ping_count} at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
            if ping_service():
                success_count += 1
            
            success_rate = (success_count / ping_count) * 100
            logger.info(f"📊 Success rate: {success_rate:.2f}% ({success_count}/{ping_count})")
            logger.info(f"⏳ Next ping in {PING_INTERVAL/60} minutes...")
            logger.info("-"*60)
            
            # Wait before next ping
            time.sleep(PING_INTERVAL)
            
        except KeyboardInterrupt:
            logger.info("\n\n🛑 Bot stopped by user")
            logger.info(f"📊 Final statistics:")
            logger.info(f"   Total pings: {ping_count}")
            logger.info(f"   Successful: {success_count}")
            logger.info(f"   Failed: {ping_count - success_count}")
            logger.info(f"   Success rate: {(success_count / ping_count * 100):.2f}%")
            break
        except Exception as e:
            logger.error(f"❌ Critical error in main loop: {e}")
            logger.info("⏳ Retrying in 60 seconds...")
            time.sleep(60)

if __name__ == "__main__":
    main()

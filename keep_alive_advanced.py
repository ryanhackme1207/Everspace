"""
Advanced Keep-Alive Service with Health Monitoring
Pings multiple endpoints and monitors service health
"""

import requests
import time
import logging
from datetime import datetime
import os
import json
from typing import List, Dict

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('keep_alive_advanced.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class KeepAliveService:
    def __init__(self, base_url: str, ping_interval: int = 600):
        self.base_url = base_url.rstrip('/')
        self.ping_interval = ping_interval
        self.stats = {
            'total_pings': 0,
            'successful_pings': 0,
            'failed_pings': 0,
            'start_time': datetime.now()
        }
        
        # Multiple endpoints to check
        self.endpoints = [
            '/',  # Home page
            '/chat/',  # Chat page
            '/authentication/login/',  # Login page
        ]
        
    def ping_endpoint(self, endpoint: str) -> bool:
        """Ping a specific endpoint"""
        url = f"{self.base_url}{endpoint}"
        try:
            response = requests.get(
                url,
                timeout=30,
                headers={
                    'User-Agent': 'Mozilla/5.0 (KeepAliveBot/2.0)',
                    'Accept': 'text/html,application/json'
                },
                allow_redirects=True
            )
            
            if response.status_code in [200, 301, 302]:
                logger.info(f"   ✅ {endpoint} - Status {response.status_code}")
                return True
            else:
                logger.warning(f"   ⚠️ {endpoint} - Status {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"   ❌ {endpoint} - Error: {str(e)[:50]}")
            return False
    
    def ping_all_endpoints(self) -> Dict:
        """Ping all configured endpoints"""
        results = {
            'timestamp': datetime.now().isoformat(),
            'endpoints': {},
            'overall_success': False
        }
        
        successful = 0
        for endpoint in self.endpoints:
            success = self.ping_endpoint(endpoint)
            results['endpoints'][endpoint] = success
            if success:
                successful += 1
        
        results['overall_success'] = successful > 0
        results['success_rate'] = (successful / len(self.endpoints)) * 100
        
        return results
    
    def save_stats(self):
        """Save statistics to file"""
        try:
            with open('keep_alive_stats.json', 'w') as f:
                stats_copy = self.stats.copy()
                stats_copy['start_time'] = stats_copy['start_time'].isoformat()
                stats_copy['last_update'] = datetime.now().isoformat()
                stats_copy['uptime_hours'] = (datetime.now() - self.stats['start_time']).total_seconds() / 3600
                json.dump(stats_copy, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save stats: {e}")
    
    def run(self):
        """Main loop"""
        logger.info("🚀 Advanced Keep-Alive Service Started!")
        logger.info(f"📍 Target: {self.base_url}")
        logger.info(f"⏱️  Interval: {self.ping_interval}s ({self.ping_interval/60}min)")
        logger.info(f"🎯 Monitoring {len(self.endpoints)} endpoints")
        logger.info("="*70)
        
        while True:
            try:
                self.stats['total_pings'] += 1
                logger.info(f"\n🔄 Ping #{self.stats['total_pings']} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                
                results = self.ping_all_endpoints()
                
                if results['overall_success']:
                    self.stats['successful_pings'] += 1
                    logger.info(f"✅ Overall Success! ({results['success_rate']:.0f}% endpoints responded)")
                else:
                    self.stats['failed_pings'] += 1
                    logger.error(f"❌ All endpoints failed!")
                
                # Calculate and display stats
                success_rate = (self.stats['successful_pings'] / self.stats['total_pings']) * 100
                uptime = datetime.now() - self.stats['start_time']
                
                logger.info(f"📊 Stats: {self.stats['successful_pings']}/{self.stats['total_pings']} " +
                           f"({success_rate:.1f}% success rate)")
                logger.info(f"⏱️  Uptime: {uptime.days}d {uptime.seconds//3600}h {(uptime.seconds//60)%60}m")
                logger.info(f"⏳ Next ping in {self.ping_interval/60} minutes...")
                logger.info("-"*70)
                
                # Save stats every 10 pings
                if self.stats['total_pings'] % 10 == 0:
                    self.save_stats()
                
                time.sleep(self.ping_interval)
                
            except KeyboardInterrupt:
                logger.info("\n\n🛑 Service stopped by user")
                self.print_final_stats()
                self.save_stats()
                break
            except Exception as e:
                logger.error(f"❌ Critical error: {e}")
                logger.info("⏳ Retrying in 60 seconds...")
                time.sleep(60)
    
    def print_final_stats(self):
        """Print final statistics"""
        uptime = datetime.now() - self.stats['start_time']
        logger.info(f"\n{'='*70}")
        logger.info("📊 FINAL STATISTICS")
        logger.info(f"{'='*70}")
        logger.info(f"⏱️  Total Runtime: {uptime.days}d {uptime.seconds//3600}h {(uptime.seconds//60)%60}m")
        logger.info(f"📈 Total Pings: {self.stats['total_pings']}")
        logger.info(f"✅ Successful: {self.stats['successful_pings']}")
        logger.info(f"❌ Failed: {self.stats['failed_pings']}")
        if self.stats['total_pings'] > 0:
            success_rate = (self.stats['successful_pings'] / self.stats['total_pings']) * 100
            logger.info(f"📊 Success Rate: {success_rate:.2f}%")
        logger.info(f"{'='*70}\n")

def main():
    # Get URL from environment variable or use default
    render_url = os.environ.get('RENDER_URL', 'https://your-app-name.onrender.com')
    
    # Get ping interval from environment (default 10 minutes)
    ping_interval = int(os.environ.get('PING_INTERVAL', '600'))
    
    service = KeepAliveService(render_url, ping_interval)
    service.run()

if __name__ == "__main__":
    main()

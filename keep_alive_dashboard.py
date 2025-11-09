"""
Keep-Alive Bot with Web Dashboard
Run this on a free service like PythonAnywhere, Heroku, or Replit
"""

from flask import Flask, render_template_string, jsonify
import requests
import threading
import time
from datetime import datetime
import os

app = Flask(__name__)

# Configuration
RENDER_URL = os.environ.get('RENDER_URL', 'https://your-app-name.onrender.com')
PING_INTERVAL = int(os.environ.get('PING_INTERVAL', '600'))

# Stats
stats = {
    'total_pings': 0,
    'successful_pings': 0,
    'failed_pings': 0,
    'last_ping_time': None,
    'last_ping_status': None,
    'start_time': datetime.now(),
    'is_running': False
}

def ping_service():
    """Ping the target service"""
    try:
        response = requests.get(
            RENDER_URL,
            timeout=30,
            headers={'User-Agent': 'KeepAliveBot/1.0'}
        )
        return response.status_code == 200
    except:
        return False

def keep_alive_loop():
    """Background loop to keep service alive"""
    stats['is_running'] = True
    while stats['is_running']:
        try:
            stats['total_pings'] += 1
            success = ping_service()
            
            if success:
                stats['successful_pings'] += 1
                stats['last_ping_status'] = 'success'
            else:
                stats['failed_pings'] += 1
                stats['last_ping_status'] = 'failed'
            
            stats['last_ping_time'] = datetime.now()
            
            time.sleep(PING_INTERVAL)
        except Exception as e:
            print(f"Error in keep-alive loop: {e}")
            time.sleep(60)

# Dashboard HTML
DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Keep-Alive Bot Dashboard</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container {
            max-width: 800px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            padding: 30px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        }
        h1 {
            text-align: center;
            color: #667eea;
            margin-bottom: 30px;
            font-size: 2.5rem;
        }
        .status-card {
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            padding: 20px;
            border-radius: 15px;
            margin-bottom: 20px;
            text-align: center;
        }
        .status-card.success { background: linear-gradient(135deg, #11998e, #38ef7d); }
        .status-card.failed { background: linear-gradient(135deg, #eb3349, #f45c43); }
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-top: 20px;
        }
        .stat-box {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 12px;
            text-align: center;
            border: 2px solid #e9ecef;
        }
        .stat-value {
            font-size: 2rem;
            font-weight: bold;
            color: #667eea;
            margin: 10px 0;
        }
        .stat-label {
            color: #6c757d;
            font-size: 0.9rem;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        .info-box {
            background: #e7f3ff;
            border-left: 4px solid #667eea;
            padding: 15px;
            border-radius: 8px;
            margin-top: 20px;
        }
        .info-box p { margin: 5px 0; color: #333; }
        .refresh-btn {
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            border: none;
            padding: 12px 30px;
            border-radius: 8px;
            cursor: pointer;
            font-size: 1rem;
            margin: 20px auto;
            display: block;
            transition: transform 0.2s;
        }
        .refresh-btn:hover { transform: translateY(-2px); }
        .pulse {
            display: inline-block;
            width: 12px;
            height: 12px;
            border-radius: 50%;
            background: #38ef7d;
            animation: pulse 2s infinite;
            margin-right: 8px;
        }
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.3; }
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🚀 Keep-Alive Bot Dashboard</h1>
        
        <div class="status-card {{ status_class }}">
            <h2><span class="pulse"></span>Bot Status: {{ 'ACTIVE' if is_running else 'STOPPED' }}</h2>
            <p>Last Ping: {{ last_ping_time }}</p>
            <p>Status: {{ last_ping_status }}</p>
        </div>

        <div class="stats-grid">
            <div class="stat-box">
                <div class="stat-label">Total Pings</div>
                <div class="stat-value">{{ total_pings }}</div>
            </div>
            <div class="stat-box">
                <div class="stat-label">Successful</div>
                <div class="stat-value" style="color: #38ef7d;">{{ successful_pings }}</div>
            </div>
            <div class="stat-box">
                <div class="stat-label">Failed</div>
                <div class="stat-value" style="color: #f45c43;">{{ failed_pings }}</div>
            </div>
            <div class="stat-box">
                <div class="stat-label">Success Rate</div>
                <div class="stat-value">{{ success_rate }}%</div>
            </div>
        </div>

        <div class="info-box">
            <p><strong>🎯 Target URL:</strong> {{ target_url }}</p>
            <p><strong>⏱️ Ping Interval:</strong> {{ ping_interval }} seconds ({{ ping_minutes }} minutes)</p>
            <p><strong>🕐 Uptime:</strong> {{ uptime }}</p>
        </div>

        <button class="refresh-btn" onclick="location.reload()">🔄 Refresh Dashboard</button>
    </div>

    <script>
        // Auto-refresh every 30 seconds
        setTimeout(() => location.reload(), 30000);
    </script>
</body>
</html>
"""

@app.route('/')
def dashboard():
    """Display dashboard"""
    uptime = datetime.now() - stats['start_time']
    uptime_str = f"{uptime.days}d {uptime.seconds//3600}h {(uptime.seconds//60)%60}m"
    
    success_rate = 0
    if stats['total_pings'] > 0:
        success_rate = round((stats['successful_pings'] / stats['total_pings']) * 100, 1)
    
    last_ping_time = 'Never'
    if stats['last_ping_time']:
        last_ping_time = stats['last_ping_time'].strftime('%Y-%m-%d %H:%M:%S')
    
    status_class = 'success' if stats['last_ping_status'] == 'success' else 'failed'
    
    return render_template_string(
        DASHBOARD_HTML,
        is_running=stats['is_running'],
        total_pings=stats['total_pings'],
        successful_pings=stats['successful_pings'],
        failed_pings=stats['failed_pings'],
        success_rate=success_rate,
        last_ping_time=last_ping_time,
        last_ping_status=stats['last_ping_status'] or 'N/A',
        target_url=RENDER_URL,
        ping_interval=PING_INTERVAL,
        ping_minutes=PING_INTERVAL/60,
        uptime=uptime_str,
        status_class=status_class
    )

@app.route('/api/stats')
def api_stats():
    """API endpoint for stats"""
    return jsonify(stats)

@app.route('/api/ping-now')
def api_ping_now():
    """Manual ping trigger"""
    success = ping_service()
    return jsonify({'success': success})

if __name__ == '__main__':
    # Start keep-alive thread
    thread = threading.Thread(target=keep_alive_loop, daemon=True)
    thread.start()
    
    # Start Flask app
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)

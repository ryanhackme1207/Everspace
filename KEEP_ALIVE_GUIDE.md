# 🚀 Keep-Alive Bot Setup Guide

## 🎯 Problem
Render.com's free tier spins down your service after 15 minutes of inactivity, which can cause:
- Service downtime
- Slow response times (cold starts)
- Database connection issues

## ✅ Solution
Use a keep-alive bot to ping your service every 10 minutes to keep it active.

---

## 📦 What's Included

### 1. **Simple Keep-Alive Bot** (`keep_alive_bot.py`)
- Basic ping functionality
- Logs to console and file
- Perfect for running on your local machine

### 2. **Advanced Keep-Alive Bot** (`keep_alive_advanced.py`)
- Monitors multiple endpoints
- Detailed statistics
- JSON stats export
- Health monitoring

### 3. **Dashboard Keep-Alive Bot** (`keep_alive_dashboard.py`)
- Web-based dashboard
- Real-time statistics
- Can be deployed to another free service
- Auto-refresh every 30 seconds

---

## 🚀 Quick Start

### Option 1: Run Locally (Easiest)

1. **Edit the URL in `.env.keepalive`:**
   ```
   RENDER_URL=https://your-actual-app.onrender.com
   ```

2. **Run the launcher:**
   ```bash
   # Windows
   run_keep_alive.bat

   # Linux/Mac
   python keep_alive_bot.py
   ```

3. **Keep the window open** - The bot will ping every 10 minutes

---

### Option 2: Deploy to Another Free Service (Recommended)

Deploy the dashboard bot to a free service that doesn't spin down:

#### **A. PythonAnywhere (FREE, Always On)**

1. Sign up at [pythonanywhere.com](https://www.pythonanywhere.com) (free tier)

2. Upload `keep_alive_dashboard.py`

3. Create a new Flask web app:
   ```bash
   pip install flask requests
   ```

4. Set environment variables:
   ```python
   RENDER_URL = 'https://your-app.onrender.com'
   PING_INTERVAL = 600
   ```

5. The bot runs 24/7 and has a dashboard!

#### **B. Replit (FREE)**

1. Create account at [replit.com](https://replit.com)

2. Create new Python Repl

3. Upload `keep_alive_dashboard.py`

4. Add to `.replit`:
   ```toml
   run = "python keep_alive_dashboard.py"
   ```

5. Set secrets (environment variables):
   - `RENDER_URL`: Your Render app URL
   - `PING_INTERVAL`: 600

6. Click "Run" - Replit keeps it alive automatically!

#### **C. Koyeb (FREE)**

1. Sign up at [koyeb.com](https://www.koyeb.com)

2. Deploy from GitHub:
   - Push `keep_alive_dashboard.py` to GitHub
   - Connect to Koyeb
   - Set environment variables

3. Free tier includes always-on service!

---

### Option 3: Use a Cron Job Service (FREE)

#### **Cron-Job.org**

1. Sign up at [cron-job.org](https://cron-job.org) (free)

2. Create new cron job:
   - URL: `https://your-app.onrender.com`
   - Schedule: Every 10 minutes
   - Title: Keep Alive

3. Done! No code needed.

#### **UptimeRobot**

1. Sign up at [uptimerobot.com](https://uptimerobot.com) (free)

2. Add new monitor:
   - Type: HTTP(s)
   - URL: `https://your-app.onrender.com`
   - Interval: 5 minutes (minimum)

3. You get uptime monitoring + keep-alive!

---

## ⚙️ Configuration

Edit `.env.keepalive` or set environment variables:

```bash
# Your Render URL
RENDER_URL=https://your-app-name.onrender.com

# Ping interval (seconds)
# 600 = 10 minutes (recommended)
# 420 = 7 minutes (more frequent)
PING_INTERVAL=600

# Request timeout
REQUEST_TIMEOUT=30
```

---

## 📊 Features Comparison

| Feature | Simple Bot | Advanced Bot | Dashboard Bot |
|---------|-----------|--------------|---------------|
| Keep service alive | ✅ | ✅ | ✅ |
| Console logging | ✅ | ✅ | ✅ |
| File logging | ✅ | ✅ | ❌ |
| Multiple endpoints | ❌ | ✅ | ❌ |
| Statistics | Basic | Detailed | Detailed |
| Web dashboard | ❌ | ❌ | ✅ |
| JSON export | ❌ | ✅ | ✅ (API) |
| Easy deployment | ❌ | ❌ | ✅ |

---

## 🎨 Dashboard Preview

When running `keep_alive_dashboard.py`, you'll see:

- 🟢 Live bot status
- 📊 Real-time statistics
- ✅ Success rate
- ⏱️ Uptime counter
- 🎯 Target URL info
- 🔄 Auto-refresh

Access at: `http://localhost:5000` (local) or your deployment URL

---

## 🐛 Troubleshooting

### Bot stops after closing terminal
**Solution:** Deploy to a free service (PythonAnywhere, Replit, Koyeb)

### "Connection refused" error
**Solution:** Check your Render URL is correct and accessible

### Bot uses too much bandwidth
**Solution:** Increase `PING_INTERVAL` to 900 (15 minutes) or use cron-job.org

### Want email alerts when service is down
**Solution:** Use UptimeRobot - it includes email notifications

---

## 💡 Best Practices

1. **Use multiple endpoints** - Ping `/`, `/chat/`, etc. to test different parts
2. **Set reasonable interval** - 10 minutes is optimal (not too frequent)
3. **Monitor logs** - Check `keep_alive.log` regularly
4. **Use external service** - Don't run on your local machine 24/7
5. **Combine with UptimeRobot** - Get monitoring + keep-alive

---

## 🆓 100% Free Solutions (Recommended Order)

1. **UptimeRobot** (Easiest, No coding)
   - 5-minute monitoring interval
   - Email alerts included
   - 50 monitors free

2. **Cron-Job.org** (Simple, No coding)
   - Custom intervals
   - Email notifications
   - Multiple URLs

3. **PythonAnywhere + Dashboard** (Best features)
   - Beautiful dashboard
   - Always-on free tier
   - Full control

4. **Replit** (Quick setup)
   - One-click deployment
   - Auto-keeps itself alive
   - Built-in secrets manager

---

## 📝 Notes

- **Render free tier limitation**: Services sleep after 15 minutes
- **Database persistence**: Using PostgreSQL? Enable persistent disk in Render
- **Alternative**: Consider upgrading to Render's $7/month plan for always-on

---

## 🚨 Important: Database Persistence

**Your database WON'T be cleared when service spins down!**

Render's free tier:
- ✅ Keeps PostgreSQL database data
- ✅ Keeps SQLite file (if using persistent disk)
- ❌ Service container restarts (but data persists)

To ensure database persistence:
1. Use Render's PostgreSQL (recommended)
2. Or enable "Persistent Disk" in Render dashboard
3. Or use external database (Railway, Supabase, etc.)

---

## 🎯 Recommended Setup

**For maximum uptime + monitoring:**

1. Deploy your app to Render
2. Use UptimeRobot for keep-alive + monitoring
3. Optionally: Deploy dashboard bot to PythonAnywhere for statistics

This gives you:
- ✅ Service stays awake
- ✅ Email alerts if down
- ✅ Uptime statistics
- ✅ 100% FREE

---

## 📞 Need Help?

Check the logs:
- `keep_alive.log` - Main log file
- `keep_alive_stats.json` - Statistics
- Console output - Real-time status

Happy hosting! 🚀

# 🚀 Quick Start Guide - Elia Parking Bot V4

## ⚡ 5-Minute Setup

### Step 1: Install (2 minutes)
```bash
# Double-click install.bat
# OR manually:
pip install -r requirements.txt
playwright install chromium
```

### Step 2: Configure (2 minutes)
```bash
python main.py --setup
```

Answer the prompts:
- Organization name (e.g., "acme-corp")
- Your email
- MFA method (choose authenticator if you have TOTP secret)
- Notification webhooks (optional)

### Step 3: Add Password (30 seconds)
Edit `.env` file:
```env
ELIA_PASSWORD=YourActualPassword123!
```

### Step 4: Test (30 seconds)
```bash
python main.py --test-auth
```

### Step 5: Deploy (30 seconds)
```bash
# Option A: Windows Task Scheduler (recommended)
python main.py --setup-tasks

# Option B: Run continuously
python main.py --daemon
```

## ✅ Done!

Your bot will now:
- 🌙 Reserve executive spots at midnight (weekdays)
- 🌅 Reserve regular spots at 6am (weekdays)
- 📱 Notify you of success/failure
- 🔄 Handle auth refreshes automatically

## 📋 Quick Commands

```bash
# Manual reservation
python main.py --reserve executive
python main.py --reserve regular

# Testing
python main.py --test-spots executive
python main.py --test-spots regular

# Debug mode
python main.py --reserve executive --visible --log-level DEBUG
```

## 🆘 Troubleshooting

### Can't authenticate?
```bash
python main.py --test-auth --visible --log-level DEBUG
```
Watch the browser to see where it fails.

### No spots detected?
```bash
python main.py --test-spots regular --visible
```
Check `screenshots/` folder for debug images.

### Windows task not running?
1. Open Task Scheduler
2. Find `EliaBot` tasks
3. Right-click → Run manually
4. Check "History" tab for errors

## 🎯 Next Steps

1. ✅ Test manual reservation once: `python main.py --reserve regular`
2. ✅ Verify notifications are working
3. ✅ Let it run for a week
4. ✅ Check logs periodically: `logs/elia_bot_*.log`

## 💡 Pro Tips

- **TOTP Automation**: Get your authenticator secret for fully automated MFA
- **Notifications**: Set up Discord/Telegram to monitor remotely
- **Testing**: Run `--test-spots` during business hours to see current availability
- **Debugging**: Always use `--visible` flag when troubleshooting

---

**Need help?** Check `README.md` for detailed documentation.

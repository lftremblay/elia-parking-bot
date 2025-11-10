# 🤖 Elia Parking Bot V4

**Enterprise-grade automated parking reservation system for app.elia.io**

## 🌟 Features

- ✅ **Aggressive Authentication Handling** - Multiple fallback strategies for Microsoft SSO & MFA
- 🔄 **Advanced Token Refresh** - Aggressive token refresh with session persistence
- 🤖 **AI-Powered Spot Detection** - Computer vision + DOM parsing for reliable spot finding
- ⏰ **Dual Scheduling** - Midnight executive spots + 6am regular spots
- 📱 **Multi-Channel Notifications** - Discord, Telegram, Email, Windows toasts
- 🔐 **Secure Credential Storage** - Encrypted session data with Windows DPAPI
- 🪟 **Windows Task Scheduler Integration** - Run automatically even when locked
- 🎯 **Retry Logic** - Exponential backoff with multiple strategies
- 📸 **Debug Screenshots** - Automatic capture on errors
- 🔍 **Headless Operation** - Fully autonomous, no GUI required

## 🏗️ Architecture

```
V4_EliaBot/
├── main.py                    # Main entry point & CLI
├── bot_orchestrator.py        # Core bot logic coordinator
├── auth_manager.py            # Authentication & token management
├── browser_automation.py      # Playwright-based browser control
├── spot_detector.py           # AI-powered spot detection
├── scheduler.py               # Dual-time scheduling system
├── notifier.py                # Multi-channel notifications
├── config.json                # User configuration
├── .env                       # Credentials (gitignored)
├── requirements.txt           # Python dependencies
├── logs/                      # Execution logs
├── screenshots/               # Debug screenshots
├── browser_data/              # Persistent browser profile
└── session_data/              # Encrypted session storage
```

## 🚀 Quick Start

### 1. Install Dependencies

```bash
# Install Python packages
pip install -r requirements.txt

# Install Playwright browsers
playwright install chromium
```

### 2. Initial Setup

```bash
python main.py --setup
```

This will:
- Ask for your Elia organization name
- Configure your email and MFA method
- Set up notification channels
- Create config.json and .env files

**⚠️ IMPORTANT:** After setup, edit `.env` and add your password:
```env
ELIA_PASSWORD=your_actual_password
```

### 3. Test Authentication

```bash
python main.py --test-auth
```

This opens a browser (visible) to test the full authentication flow including MFA.

### 4. Deploy

Choose your deployment method:

#### Option A: Windows Task Scheduler (Recommended)
```bash
python main.py --setup-tasks
```

This creates two scheduled tasks:
- **EliaBot_Executive**: Runs at midnight on weekdays
- **EliaBot_Regular**: Runs at 6am on weekdays

#### Option B: Run as Daemon
```bash
python main.py --daemon
```

Runs continuously with built-in scheduler. Requires keeping terminal open or running as a Windows service.

## 📋 Usage

### Manual Reservation
```bash
# Reserve executive spot now
python main.py --reserve executive

# Reserve regular spot now
python main.py --reserve regular
```

### Testing & Debugging
```bash
# Test spot detection (visible browser)
python main.py --test-spots executive
python main.py --test-spots regular

# Run with visible browser (for debugging)
python main.py --reserve executive --visible

# Enable debug logging
python main.py --reserve executive --log-level DEBUG
```

### Configuration Management
```bash
# Use custom config file
python main.py --config my_config.json --reserve regular

# Re-run setup wizard
python main.py --setup
```

## ⚙️ Configuration

### config.json

```json
{
  "elia": {
    "organization": "your-org-name",
    "credentials": {
      "email": "your.email@company.com",
      "mfa_method": "authenticator"  // or "email", "push"
    }
  },
  "schedules": {
    "executive_spots": {
      "enabled": true,
      "time": "00:00:00",  // Midnight
      "weekdays_only": true
    },
    "regular_spots": {
      "enabled": true,
      "time": "06:00:00",  // 6am
      "weekdays_only": true
    }
  },
  "retry": {
    "max_attempts": 5,
    "aggressive_refresh": true
  },
  "notifications": {
    "discord_webhook": "https://discord.com/api/webhooks/...",
    "telegram_bot_token": "123456:ABC-DEF...",
    "telegram_chat_id": "123456789"
  }
}
```

### .env (Credentials)

```env
ELIA_ORG=your-org
ELIA_EMAIL=your.email@company.com
ELIA_PASSWORD=your_password_here
TOTP_SECRET=YOUR_BASE32_SECRET  # For authenticator automation
DISCORD_WEBHOOK_URL=https://...
TELEGRAM_BOT_TOKEN=...
TELEGRAM_CHAT_ID=...
```

## 🔐 MFA Automation Options

### Option 1: TOTP (Recommended)
Most reliable. Get your TOTP secret when setting up Microsoft Authenticator:
1. When adding account, click "Can't scan QR code?"
2. Copy the secret key (base32 string)
3. Add to `.env`: `TOTP_SECRET=ABCD1234...`

### Option 2: Email Codes
Requires email access automation (IMAP). Less reliable due to delivery delays.

### Option 3: Push Notifications
Manual approval required. Bot will wait 30 seconds for you to approve.

## 📱 Notification Setup

### Discord
1. Create webhook in your Discord server settings
2. Add URL to config or `.env`

### Telegram
1. Create bot with [@BotFather](https://t.me/botfather)
2. Get bot token
3. Get your chat ID (send message to bot, then visit `https://api.telegram.org/bot<TOKEN>/getUpdates`)

### Email
Configure SMTP settings in `config.json`:
```json
"email": {
  "enabled": true,
  "smtp_server": "smtp.gmail.com",
  "smtp_port": 587,
  "from_email": "your@email.com",
  "to_email": "notify@email.com",
  "password": "app_password"
}
```

## 🐛 Troubleshooting

### Authentication Fails
```bash
# Test with visible browser to see what's happening
python main.py --test-auth --visible --log-level DEBUG

# Check logs
tail -f logs/elia_bot_*.log
```

### MFA Not Working
- Verify TOTP secret is correct
- Check time sync on your machine
- Try manual MFA approval first

### No Spots Detected
```bash
# Test spot detection with visible browser
python main.py --test-spots regular --visible

# Check debug screenshots
ls screenshots/debug_*.png
```

### Windows Task Not Running
1. Open Task Scheduler
2. Find `EliaBot` folder
3. Right-click task → Run
4. Check "Last Run Result" and "History" tab

### Session Expires Too Quickly
- Enable aggressive token refresh in `config.json`
- Increase browser profile persistence
- Check if org has session timeout policies

## 🔧 Advanced Usage

### Custom Spot Detection
Edit `spot_detector.py` to customize color ranges or patterns for your specific Elia UI.

### API-Based Reservation
If you reverse-engineer Elia's API, update `browser_automation.py` to use direct API calls instead of browser automation.

### Run as Windows Service
Use NSSM or create a proper Windows service wrapper around the daemon mode.

### Cloud Deployment
Deploy to a cloud VM (AWS EC2, Azure VM) and run the daemon mode 24/7.

## 📊 Monitoring

### Check Logs
```bash
# View today's log
cat logs/elia_bot_2025-10-28.log

# Watch live
Get-Content logs/elia_bot_*.log -Wait
```

### Success Notifications
You'll receive notifications on:
- ✅ Successful reservations
- ❌ Failed attempts
- ⚠️ No spots available
- 🔐 Authentication required

## 🔒 Security Notes

- **Credentials**: Stored in `.env` (gitignored). Use file permissions to restrict access.
- **Session Data**: Encrypted with Fernet using machine-specific key.
- **Browser Profile**: Contains session cookies. Protect `browser_data/` folder.
- **Logs**: May contain sensitive info. Rotate and secure log files.

## 📝 Maintenance

### Update Dependencies
```bash
pip install --upgrade -r requirements.txt
playwright install chromium
```

### Clear Session (Force Re-auth)
```bash
rm -rf session_data/
rm -rf browser_data/
python main.py --test-auth
```

### Backup Configuration
```bash
# Backup your config and credentials
cp config.json config.backup.json
cp .env .env.backup
```

## 🆘 Support

### Common Issues
1. **Import errors**: Run `pip install -r requirements.txt`
2. **Playwright errors**: Run `playwright install chromium`
3. **Permission denied**: Run CMD/PowerShell as Administrator
4. **Task doesn't wake PC**: Enable "Wake to run" in Task Scheduler + BIOS

### Debugging Steps
1. Run with `--visible --log-level DEBUG`
2. Check screenshots in `screenshots/` folder
3. Review logs in `logs/` folder
4. Verify credentials in `.env`
5. Test individual components (auth, spots, etc.)

## 📄 License

Personal use only. Respect Elia's terms of service.

## 🎯 Roadmap

- [ ] API reverse engineering for faster operations
- [ ] Machine learning for optimal reservation timing
- [ ] Multi-user support
- [ ] Web dashboard for monitoring
- [ ] Mobile app notifications
- [ ] Preferred spot selection logic
- [ ] Historical analytics

---

**Built with ❤️ for reliable parking reservations**

*Architecture enhancement documentation in progress for GitHub integration*

## 📋 Architecture Analysis

**Comprehensive brownfield architecture analysis completed** - Key findings:

- **GitHub Actions**: Current MFA handling needs cloud-compatible session management
- **Scheduling**: Dual system (Windows + GitHub) needs UTC coordination
- **Authentication**: Local encryption won't work in CI/CD environment
- **Technical Debt**: 5 critical areas identified for enhancement

**Next Step**: Creating Product Requirements Document (PRD) for enhancements

*Full analysis available in project documentation*

## 📋 Product Requirements Document - COMPLETE

**Comprehensive Cloud-First Enhancement PRD has been created** - Key deliverables:

- **9 Detailed User Stories** covering authentication, workflows, configuration, notifications, and migration
- **23 Functional Requirements** with comprehensive edge case handling
- **15 Non-Functional Requirements** for performance, security, and reliability
- **4-Phase Implementation Roadmap** with 8-week timeline and success metrics
- **Cloud-First Architecture** designed to solve Windows Task Scheduler limitations

**Document Status**: ✅ Complete - Ready for development execution
**Next Step**: Begin Phase 1 development with Cloud Authentication Foundation

*PRD contains detailed technical specifications, story sequencing, and risk mitigation strategies*

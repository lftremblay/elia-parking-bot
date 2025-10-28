# 🚀 Deployment Checklist - Elia Parking Bot V4

## ✅ Pre-Deployment

### 1. System Requirements
- [ ] Windows 10/11 (or Windows Server)
- [ ] Python 3.8 or higher installed
- [ ] Administrator access (for Windows Task Scheduler)
- [ ] Stable internet connection
- [ ] Chrome/Chromium browser compatible

### 2. Elia Account Requirements
- [ ] Active Elia organization account
- [ ] Know your organization name (e.g., "acme-corp")
- [ ] Valid email/password credentials
- [ ] MFA method configured (Authenticator app recommended)
- [ ] Access to parking reservation feature

### 3. Optional (Recommended)
- [ ] TOTP secret key (for automated MFA)
- [ ] Discord webhook URL (for notifications)
- [ ] Telegram bot token & chat ID (for notifications)

---

## 🔧 Installation Steps

### Step 1: Copy Files
- [ ] Copy entire V4_EliaBot folder to permanent location
  - Recommended: `C:\EliaBot\` or `C:\Users\YourName\EliaBot\`
  - **DO NOT** run from Temp folder - files may be deleted

### Step 2: Install Dependencies
```bash
cd C:\EliaBot
.\install.bat
```
- [ ] Verify Python packages installed
- [ ] Verify Playwright Chromium installed
- [ ] Check for any error messages

### Step 3: Run Diagnostics
```bash
python diagnostics.py
```
- [ ] All checks should pass (green checkmarks)
- [ ] Fix any red X errors before continuing

### Step 4: Initial Configuration
```bash
python main.py --setup
```
Provide:
- [ ] Organization name
- [ ] Email address
- [ ] MFA method selection
- [ ] TOTP secret (if available)
- [ ] Notification webhooks (optional)

### Step 5: Edit Credentials
- [ ] Open `.env` file in text editor
- [ ] Replace `YOUR_PASSWORD_HERE` with actual password
- [ ] Verify TOTP_SECRET if using authenticator
- [ ] **IMPORTANT**: Keep this file secure!

---

## 🧪 Testing Phase

### Test 1: Authentication
```bash
python main.py --test-auth --visible
```
- [ ] Browser opens successfully
- [ ] Organization page appears
- [ ] Microsoft login works
- [ ] MFA completes (manually or automatically)
- [ ] Dashboard loads
- [ ] No errors in console

**If fails**: Check logs in `logs/` folder

### Test 2: Spot Detection (During Business Hours)
```bash
python main.py --test-spots regular --visible
```
- [ ] Browser navigates to parking page
- [ ] Available spots are detected
- [ ] Screenshot saved in `screenshots/` folder
- [ ] Spot list displayed in console

**If no spots found**: 
- Check if parking page loaded correctly
- Verify spots are actually available
- Review debug screenshots

### Test 3: Manual Reservation (OPTIONAL - USE CAREFULLY)
```bash
python main.py --reserve regular --visible --log-level DEBUG
```
⚠️ **WARNING**: This will attempt a real reservation!
- [ ] Only run if you actually want to reserve a spot
- [ ] Watch the entire process
- [ ] Verify reservation succeeded in Elia
- [ ] Check notification received

---

## 📅 Deployment Options

### Option A: Windows Task Scheduler (Recommended)

#### Setup Tasks
```bash
python main.py --setup-tasks
```
- [ ] Tasks created successfully
- [ ] Open Task Scheduler (`taskschd.msc`)
- [ ] Navigate to Task Scheduler Library → EliaBot
- [ ] Verify two tasks exist:
  - [ ] `EliaBot_Executive` (midnight, weekdays)
  - [ ] `EliaBot_Regular` (6am, weekdays)

#### Configure Tasks
For each task:
- [ ] Right-click → Properties
- [ ] General tab:
  - [ ] "Run whether user is logged on or not" - Checked
  - [ ] "Run with highest privileges" - Checked
  - [ ] "Configure for: Windows 10" - Selected
- [ ] Conditions tab:
  - [ ] "Wake the computer to run this task" - Checked
  - [ ] "Start only if the following network connection is available" - Checked → Any connection
- [ ] Settings tab:
  - [ ] "Allow task to be run on demand" - Checked
  - [ ] "If the task fails, restart every: 5 minutes" - Set
  - [ ] "Attempt to restart up to: 3 times" - Set

#### Test Tasks
- [ ] Right-click `EliaBot_Regular` → Run
- [ ] Check Last Run Result (should be 0x0)
- [ ] Verify in Elia that reservation was made
- [ ] Check notification received
- [ ] Review logs: `logs/elia_bot_*.log`

### Option B: Daemon Mode

#### Run as Background Process
```bash
start /min python main.py --daemon
```
- [ ] Process starts successfully
- [ ] Console shows scheduled times
- [ ] Leave running 24/7

**Limitations**:
- Requires computer to stay on
- Process may stop if user logs out
- Not recommended for production

#### Convert to Windows Service (Advanced)
Use NSSM (Non-Sucking Service Manager):
```bash
nssm install EliaParkingBot "C:\Path\To\python.exe" "C:\EliaBot\main.py --daemon"
nssm set EliaParkingBot AppDirectory C:\EliaBot
nssm start EliaParkingBot
```
- [ ] Service installed
- [ ] Service starts automatically
- [ ] Service survives reboots

---

## 🔐 Security Hardening

### File Permissions
- [ ] Restrict `.env` file access (Right-click → Properties → Security)
- [ ] Only your user account should have read access
- [ ] Remove access for other users

### Browser Profile
- [ ] Restrict `browser_data/` folder access
- [ ] Contains session cookies - protect like passwords

### Session Data
- [ ] `session_data/` is encrypted by default
- [ ] Backup `.key` file securely
- [ ] Never share session files

### Credentials Backup
- [ ] Backup `.env` to secure location (encrypted USB, password manager)
- [ ] Backup `config.json`
- [ ] **DO NOT** commit to git

---

## 📊 Monitoring Setup

### Notifications
- [ ] Test Discord webhook (if configured)
- [ ] Test Telegram bot (if configured)
- [ ] Verify emails deliver (if configured)
- [ ] Add bot to monitoring channel

### Logging
- [ ] Review log rotation (30 days retention)
- [ ] Set up log monitoring (optional)
- [ ] Create alerts for failures (optional)

### Health Checks
Create a simple monitoring script:
```bash
# Check if reservation ran today
findstr /C:"Successfully reserved" logs\elia_bot_*.log
```

---

## 🔄 Ongoing Maintenance

### Daily
- [ ] Check notification for reservation status
- [ ] Verify spot was actually reserved in Elia

### Weekly
- [ ] Review logs for errors: `logs/elia_bot_*.log`
- [ ] Check Task Scheduler history
- [ ] Verify tasks are running on schedule

### Monthly
- [ ] Update dependencies: `pip install --upgrade -r requirements.txt`
- [ ] Update Playwright: `playwright install chromium`
- [ ] Clear old screenshots: `del screenshots\* /Q`
- [ ] Archive old logs

### When Elia UI Changes
- [ ] Run `--test-spots` to verify detection still works
- [ ] Check debug screenshots
- [ ] May need to update selectors in `browser_automation.py`

---

## 🆘 Troubleshooting Guide

### Issue: Authentication Fails

**Symptoms**: Can't get past login screen

**Solutions**:
1. [ ] Run `python main.py --test-auth --visible --log-level DEBUG`
2. [ ] Verify credentials in `.env`
3. [ ] Check if MFA is blocking
4. [ ] Try manual login first to verify account works
5. [ ] Clear session: `del session_data\* /Q` and try again

### Issue: No Spots Detected

**Symptoms**: Bot runs but finds no available spots

**Solutions**:
1. [ ] Verify spots are actually available (check Elia manually)
2. [ ] Run during business hours when spots are typically available
3. [ ] Check debug screenshots in `screenshots/`
4. [ ] Update color detection in `spot_detector.py` if UI changed

### Issue: Reservation Fails

**Symptoms**: Spots detected but reservation doesn't complete

**Solutions**:
1. [ ] Run `--visible` mode to watch what happens
2. [ ] Check if you have reservation limit reached
3. [ ] Verify button selectors in `browser_automation.py`
4. [ ] Try manual reservation to rule out account issues

### Issue: Windows Task Doesn't Run

**Symptoms**: Task shows in scheduler but never executes

**Solutions**:
1. [ ] Right-click task → Run (test manually)
2. [ ] Check "History" tab for error details
3. [ ] Verify "Wake to run" is enabled
4. [ ] Check power settings (prevent sleep)
5. [ ] Verify Python path in task is correct
6. [ ] Run as administrator: `schtasks /Run /TN "EliaBot\EliaBot_Regular"`

### Issue: Session Expires Too Quickly

**Symptoms**: Bot needs to re-authenticate frequently

**Solutions**:
1. [ ] Enable aggressive refresh in `config.json`
2. [ ] Verify browser profile persists: check `browser_data/`
3. [ ] Check if organization has strict session policies
4. [ ] Use TOTP automation to handle re-auth automatically

---

## ✅ Final Verification

Before considering deployment complete:

- [ ] Bot successfully authenticated at least once
- [ ] Test reservation completed successfully (optional but recommended)
- [ ] Notifications working
- [ ] Windows tasks configured and tested
- [ ] All logs reviewing cleanly
- [ ] Credentials secured
- [ ] Backup of configuration made
- [ ] Monitoring set up

---

## 📞 Support Resources

- **Logs**: `logs/elia_bot_YYYY-MM-DD.log`
- **Screenshots**: `screenshots/`
- **Configuration**: `config.json`, `.env`
- **Documentation**: `README.md`, `QUICKSTART.md`
- **Diagnostics**: `python diagnostics.py`

---

## 🎉 Deployment Complete!

Your Elia Parking Bot V4 is now:
- ✅ Installed and configured
- ✅ Tested and verified
- ✅ Scheduled to run automatically
- ✅ Monitored with notifications
- ✅ Secured and backed up

**What happens next:**
1. Bot will run at midnight (executive) and 6am (regular) on weekdays
2. You'll receive notifications of success/failure
3. Review logs weekly for any issues
4. Enjoy your automated parking reservations! 🎊

---

**Last Updated**: 2025-10-28
**Bot Version**: V4.0

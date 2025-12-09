# 📧 Email Notifications Setup Guide

## ✅ **Email Notifications Added!**

Your parking bot now sends you email updates after every run!

---

## 🎯 **What You'll Get Emails About**

### **✅ Success Emails:**
- **Subject:** `✅ Parking Booked Successfully (2 spots)`
- **When:** Bot successfully books parking
- **Contains:** Executive + regular spot results

### **❌ Failure Emails:**
- **Subject:** `❌ Parking Booking Failed`
- **When:** Token expired or no spots available
- **Contains:** Error details and troubleshooting

### **🏖️ Vacation Emails:**
- **Shows:** Which dates were skipped for vacation
- **Contains:** Full booking summary with vacation info

---

## 📋 **Quick Setup (5 Minutes)**

### **Step 1: Create Gmail App Password**

1. **Go to:** https://myaccount.google.com/apppasswords
2. **Sign in** to your Google account
3. **Select app:** "Mail"
4. **Select device:** "Other (Custom name)"
5. **Name it:** "Parking Bot"
6. **Click "Generate"**
7. **Copy the 16-character password** (e.g., `abcd efgh ijkl mnop`)

### **Step 2: Update .env File**

Edit your `.env` file with your email details:

```bash
# Replace with your actual email
EMAIL_ADDRESS=your_email@gmail.com

# Paste the 16-character app password (no spaces)
SMTP_PASSWORD=abcdefghijklmnop

# Gmail settings (keep these)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
```

**Example:**
```bash
EMAIL_ADDRESS=louis-felix.tremblay@gmail.com
SMTP_PASSWORD=abcd efgh ijkl mnop
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
```

### **Step 3: Test Email Notifications**

```bash
# Test the bot with email notifications
python production_api_bot.py --smart
```

**You should receive an email within 30 seconds!**

---

## 📧 **What the Emails Look Like**

### **Success Email Example:**
```
Subject: ✅ Parking Booked Successfully (2 spots)

🤖 Elia Parking Bot - Smart Booking Results
==================================================
📅 Run Date: December 9, 2025 at 12:30 PM

🎯 Executive Spot (Tomorrow):
   ✅ SUCCESS - 2025-12-10

📅 Regular Spots (14-15 Days Ahead):
   ✅ SUCCESS - 2025-12-23 (14 days ahead)
   ✅ SUCCESS - 2025-12-24 (15 days ahead)

📊 SUMMARY:
   Executive booked: ✅ Yes
   Regular spots booked: 2/2
   Total skipped: 0

🔗 View detailed logs: https://github.com/lftremblay/elia-parking-bot/actions
```

### **Vacation Skip Example:**
```
Subject: ✅ Parking Booked Successfully (1 spot)

🏖️ Skipped Dates (2 total):
   🏖️ 2025-12-24 (vacation)
   🏖️ 2025-12-25 (vacation)

📊 SUMMARY:
   Executive booked: ✅ Yes
   Regular spots booked: 1/2
   Total skipped: 2
```

---

## ⚙️ **Email Configuration Options**

### **For Gmail Users (Recommended):**
```bash
EMAIL_ADDRESS=your_email@gmail.com
SMTP_PASSWORD=your_16_char_app_password
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
```

### **For Outlook Users:**
```bash
EMAIL_ADDRESS=your_email@outlook.com
SMTP_PASSWORD=your_app_password
SMTP_HOST=smtp-mail.outlook.com
SMTP_PORT=587
```

### **For Work Email:**
Ask your IT department for:
- SMTP server address
- SMTP port (usually 587 or 25)
- App password or login credentials

---

## 🔧 **Troubleshooting**

### **"Email notifications disabled - missing configuration"**
**Solution:** Fill in `EMAIL_ADDRESS` and `SMTP_PASSWORD` in `.env`

### **"Failed to send email"**
**Common causes:**
1. **Wrong password** → Use App Password, not regular password
2. **Firewall blocking** → Try different network
3. **SMTP settings wrong** → Check with your email provider

### **"Not receiving emails"**
**Check:**
1. **Spam folder** → Mark as "Not Spam"
2. **Email address** → Verify it's correct
3. **App password** → Regenerate if needed

---

## 🎯 **Email Features**

### **Smart Subject Lines:**
- ✅ `Parking Booked Successfully (2 spots)`
- ❌ `Parking Booking Failed`
- 🏖️ `Parking Booked Successfully (1 spot, 2 skipped)`

### **Beautiful HTML Emails:**
- 🎨 **Color-coded** success/failure
- 📊 **Clear summary** of results
- 🔗 **Direct link** to GitHub logs
- 📱 **Mobile-friendly** design

### **Comprehensive Information:**
- 🕐 **Run time** and date
- 🎯 **Executive spot** results
- 📅 **Regular spot** results
- ⏭️ **Skipped dates** (including vacation)
- 📊 **Success summary**

---

## 📊 **Email Timing**

### **When You'll Get Emails:**
- **Every weekday** at midnight (when bot runs)
- **Manual runs** when you test locally
- **Failures** when something goes wrong

### **No Emails On:**
- **Weekends** (bot doesn't run)
- **Successful silent runs** (if you disable)

---

## 🎉 **Benefits**

### **✅ Peace of Mind:**
- **Know immediately** if parking was booked
- **Get alerts** on vacation skips
- **Quick troubleshooting** for failures

### **✅ Convenience:**
- **No need to check GitHub** for basic status
- **Email archive** of all booking results
- **Mobile notifications** on your phone

### **✅ Professional:**
- **Beautiful HTML emails** with clear formatting
- **Detailed information** for debugging
- **Direct links** to detailed logs

---

## 🚀 **Ready to Use!**

### **What to Do:**
1. **Generate App Password** (2 minutes)
2. **Update .env file** (1 minute)
3. **Test with `--smart`** (1 minute)
4. **Check your email** (30 seconds)

### **Total Setup Time:** **5 minutes!**

---

## 📧 **Example Email Preview**

```
┌─────────────────────────────────────┐
│ ✅ Parking Booked Successfully (2)  │
├─────────────────────────────────────┤
│ 🤖 Elia Parking Bot Results         │
│ 📅 December 9, 2025 at 12:30 AM    │
│                                     │
│ 🎯 Executive: ✅ SUCCESS - Dec 10   │
│ 📅 Regular: ✅ SUCCESS - Dec 23     │
│ 📅 Regular: ✅ SUCCESS - Dec 24     │
│                                     │
│ 📊 Executive booked: ✅ Yes         │
│ 📊 Regular booked: 2/2              │
│ 📊 Total skipped: 0                 │
│                                     │
│ 🔗 View Logs: GitHub Actions        │
└─────────────────────────────────────┘
```

---

## 🎯 **You're All Set!**

**Email notifications are now fully integrated!**

**Just complete the 5-minute setup and you'll start getting booking updates!** 📧✨

**No more wondering if the bot worked - you'll know immediately!** 🎉

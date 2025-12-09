# 🎯 Smart Weekday Booking Guide

## ✅ **What's New**

Your parking bot now has **intelligent booking logic** that:
- ✅ **Books executive spots for tomorrow** (6-hour policy)
- ✅ **Books regular spots 14-15 days ahead** (advance booking)
- ✅ **Skips weekends automatically**
- ✅ **Prevents double-booking**
- ✅ **Runs Monday-Friday only**

---

## 🎯 **Smart Booking Strategy**

### **How It Works:**

```
Every weekday at midnight (Montreal time):

STEP 1: Executive Spot for Tomorrow
├── Check if tomorrow is a weekday
├── Check if already booked
└── Book executive spot (6h policy compliant)

STEP 2: Regular Spots 14-15 Days Ahead
├── Check 14 days ahead (if weekday)
│   ├── Check if already booked
│   └── Book regular spot
├── Check 15 days ahead (if weekday)
│   ├── Check if already booked
│   └── Book regular spot
└── Skip weekends automatically

RESULT: Always have parking booked!
```

---

## 📊 **Booking Logic Explained**

### **Executive Spots (Tomorrow)**
- **Policy**: Can only book 6 hours ahead
- **Workflow runs**: Midnight (6 hours before 6 AM)
- **Target**: Executive spots (preferred)
- **Fallback**: Regular spots if no executive available

### **Regular Spots (14-15 Days Ahead)**
- **Policy**: Can book 14-15 days in advance
- **Workflow runs**: Same midnight run
- **Target**: Regular spots
- **Purpose**: Ensure parking 2 weeks out

### **Weekend Handling**
- **Automatic skip**: No bookings for Saturday/Sunday
- **Smart detection**: Checks day of week before booking
- **Efficient**: Doesn't waste API calls on weekends

### **Double-Booking Prevention**
- **Check first**: Queries existing bookings before attempting
- **Skip if booked**: Won't try to book if spot already reserved
- **Logged**: Shows which dates were skipped

---

## 🚀 **Usage**

### **Automated (Recommended)**
The GitHub workflow runs automatically:
```yaml
Schedule: Monday-Friday at midnight Montreal time
Command: python production_api_bot.py --smart
```

**You don't need to do anything!** ✅

### **Manual Testing**
Test the smart booking locally:
```bash
python production_api_bot.py --smart
```

### **Check Existing Bookings**
See what you already have booked:
```bash
python production_api_bot.py --check-bookings
```

### **Check Availability**
See what spots are available:
```bash
python production_api_bot.py --status
```

---

## 📋 **Command Reference**

### **Smart Booking (New!)**
```bash
python production_api_bot.py --smart
```
**Does:**
- Books executive for tomorrow
- Books regular 14-15 days ahead
- Skips weekends
- Prevents double-booking

### **Check Bookings (New!)**
```bash
python production_api_bot.py --check-bookings
```
**Shows:** All your bookings for next 30 days

### **Single Reservation**
```bash
python production_api_bot.py --reserve --hours 12
```
**Does:** Books one spot for tomorrow

### **Check Status**
```bash
python production_api_bot.py --status
```
**Shows:** Available spots for tomorrow

---

## 🗓️ **Example Workflow**

### **Monday Midnight Run:**
```
📅 STEP 1: Executive spot for Tuesday
  ✅ Checking 2025-12-10 (Tuesday)
  ✅ No existing booking found
  ✅ Successfully reserved P-Exc. - 6

📅 STEP 2: Regular spots 14-15 days ahead
  ✅ Checking 2025-12-23 (Monday) - 14 days ahead
  ✅ No existing booking found
  ✅ Successfully reserved P-Reg. - 12
  
  ✅ Checking 2025-12-24 (Tuesday) - 15 days ahead
  ✅ No existing booking found
  ✅ Successfully reserved P-Reg. - 8

📊 SMART BOOKING SUMMARY
Executive (tomorrow): ✅ SUCCESS - 2025-12-10
Regular spots (14-15 days ahead):
  ✅ SUCCESS - 2025-12-23 (14 days ahead)
  ✅ SUCCESS - 2025-12-24 (15 days ahead)
```

### **Friday Midnight Run:**
```
📅 STEP 1: Executive spot for Saturday
  ⏭️ Tomorrow is Saturday - skipping

📅 STEP 2: Regular spots 14-15 days ahead
  ✅ Checking 2025-12-27 (Friday) - 14 days ahead
  ⏭️ Skipping 2025-12-27 - already booked
  
  ⏭️ 2025-12-28 is Saturday - skipping

📊 SMART BOOKING SUMMARY
Executive (tomorrow): ⏭️ SKIPPED (weekend)
Skipped (already booked): 1 date
  ⏭️ 2025-12-27
```

---

## ✅ **Benefits**

### **Always Have Parking**
- Executive spot ready for next day
- Regular spots booked 2 weeks ahead
- Never worry about availability

### **Optimal Timing**
- Executive: Books at earliest possible time (6h policy)
- Regular: Books as far ahead as allowed (14-15 days)
- Maximizes your chances of getting preferred spots

### **Efficient**
- No wasted API calls on weekends
- No duplicate bookings
- Smart retry logic

### **Transparent**
- Detailed logs show what was booked
- Shows what was skipped and why
- Easy to debug if issues occur

---

## 🎯 **Workflow Schedule**

### **GitHub Actions:**
```yaml
Schedule: Monday-Friday at 5:00 AM UTC (Midnight Montreal)
Runs on: Weekdays only (1-5 = Mon-Fri)
Command: python production_api_bot.py --smart
```

### **What Gets Booked:**

| Day Workflow Runs | Executive Booked For | Regular Booked For |
|-------------------|---------------------|-------------------|
| Monday midnight | Tuesday | 2 weeks ahead (Mon/Tue) |
| Tuesday midnight | Wednesday | 2 weeks ahead (Tue/Wed) |
| Wednesday midnight | Thursday | 2 weeks ahead (Wed/Thu) |
| Thursday midnight | Friday | 2 weeks ahead (Thu/Fri) |
| Friday midnight | ⏭️ Skip (weekend) | 2 weeks ahead (Fri/Mon) |
| Saturday | ⏭️ No run | ⏭️ No run |
| Sunday | ⏭️ No run | ⏭️ No run |

---

## 🔧 **Configuration**

### **Current Settings:**
- **Executive booking window**: 12 hours (6 AM - 6 PM)
- **Regular booking window**: 12 hours (6 AM - 6 PM)
- **Days ahead for regular**: 14-15 days
- **Weekdays only**: Monday-Friday
- **Floor ID**: `sp_Mkddt7JNKkLPhqTc`

### **To Modify:**
Edit `production_api_bot.py`:
```python
# Change booking window hours
booking_window_hours=12  # Change to 8, 10, etc.

# Change days ahead for regular spots
for days_ahead in [14, 15]:  # Change to [13, 14] or [15, 16]
```

---

## 📊 **Monitoring**

### **Check Workflow Runs:**
1. Go to: `https://github.com/lftremblay/elia-parking-bot/actions`
2. Click on latest "Smart Weekday Parking Bot" run
3. View logs to see what was booked

### **Check Your Bookings:**
```bash
python production_api_bot.py --check-bookings
```

### **View Logs:**
- GitHub Actions uploads logs as artifacts
- Retention: 7 days
- Download from workflow run page

---

## ⚠️ **Important Notes**

### **Token Refresh:**
- Token expires every ~14 days
- Extension shows expiry date
- Update both local `.env` AND GitHub secret
- See: `COPY_TOKEN_FEATURE.md`

### **6-Hour Policy:**
- Executive spots: Must book within 6 hours
- Workflow runs at midnight (6h before 6 AM)
- **Cannot test during day** (too far ahead)
- Use `--status` to check without booking

### **Regular Spot Policy:**
- Can book 14-15 days ahead
- Policy may vary by organization
- Adjust days_ahead if needed

---

## 🎉 **Summary**

### **What You Get:**
✅ **Automated weekday parking**
✅ **Executive spots for tomorrow**
✅ **Regular spots 2 weeks ahead**
✅ **No weekend bookings**
✅ **No double-booking**
✅ **Smart, efficient, reliable**

### **What You Do:**
1. ✅ Update GitHub secret when token expires (~14 days)
2. ✅ Check workflow runs occasionally
3. ✅ Enjoy automated parking! 🎉

**That's it! Your parking is now fully automated!** 🚀

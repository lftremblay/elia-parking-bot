# Elia Parking Bot - Booking Policies Documentation

## 📋 Executive Policies Summary

Based on extensive testing and API responses, here are the confirmed booking policies for different spot types in the Elia parking system.

---

## 🏢 Executive Spots (P-Exc.)

### **Booking Window Policy**
- **Advance Booking:** ❌ **NOT ALLOWED** more than 6 hours in advance
- **API Response:** `BOOKING_REACH_POLICY: 6 HOURS` error when booking >6 hours ahead
- **Behavior:** Executive spots are released for booking only within 6 hours of the actual parking time

### **Time Requirements**
- **Minimum Duration:** 6 hours (policy minimum)
- **Recommended Duration:** 12 hours (full day: 6 AM - 6 PM Montreal)
- **Time Format:** `06:00:00.000Z` to `18:00:00.000Z` for full day

### **Availability & Competition**
- **High Demand:** Executive spots are premium and highly competitive
- **Occupancy:** Often 80-97% occupied
- **Strategy:** Must book within 6-hour window to secure these spots

### **Booking Strategy**
```python
# Executive spots require same-day booking
booking_window_hours = 12  # Full day duration
# But must be executed within 6 hours of actual time
```

---

## 🚗 Regular Spots (P-Standard)

### **Booking Window Policy**
- **Advance Booking:** ✅ **ALLOWED** up to 14 days in advance
- **API Response:** Successfully books 14 days ahead
- **Policy Limit:** 15-day maximum booking window (use 14 to be safe)

### **Time Requirements**
- **Minimum Duration:** 6 hours
- **Recommended Duration:** 12 hours (full day)
- **Time Format:** `06:00:00.000Z` to `18:00:00.000Z`

### **Availability & Competition**
- **Moderate Demand:** Less competitive than executive spots
- **Occupancy:** Varies, typically more availability
- **Strategy:** Book 14 days in advance for guaranteed spot

### **Booking Strategy**
```python
# Regular spots can be booked far in advance
booking_window_hours = 12  # Full day duration
days_ahead = 14  # Book 2 weeks ahead
```

---

## 📅 General System Policies

### **Time Zone Handling**
- **API Time:** UTC (Zulu time)
- **Display Time:** Montreal local time (EST/EDT)
- **Conversion:** 6 AM Montreal = 06:00:00.000Z (during standard time)
- **Full Day:** 06:00:00.000Z to 18:00:00.000Z = 6 AM to 6 PM Montreal

### **Booking Validation Rules**
1. **Minimum Duration:** 6 hours required by API
2. **Start Time:** Must be 06:00:00.000Z for full-day booking
3. **End Time:** Must be 18:00:00.000Z for 12-hour booking
4. **Date Format:** YYYY-MM-DD for API calls

### **User Authentication**
- **Required:** Valid ELIA_GRAPHQL_TOKEN
- **User ID:** Retrieved from authenticated session
- **Permissions:** User must have parking access

---

## 🎯 Optimal Booking Strategies

### **Executive Spots Strategy**
```python
# Timing: Execute within 6 hours of needed parking
# Example: For tomorrow morning parking, run at midnight same day
if is_executive_spot:
    execute_booking_time = needed_time - timedelta(hours=6)
    booking_window = 12  # Full day
```

### **Regular Spots Strategy**
```python
# Timing: Book 14 days in advance
if is_regular_spot:
    execute_booking_time = today  # Book immediately
    target_date = today + timedelta(days=14)
    booking_window = 12  # Full day
```

---

## 🚫 Common Booking Errors & Solutions

### **Error: `BOOKING_REACH_POLICY: 6 HOURS`**
- **Cause:** Trying to book executive spot >6 hours in advance
- **Solution:** Use same-day booking for executive spots
- **Alternative:** Book regular spots 14 days ahead instead

### **Error: `Validation error (MissingFieldArgument)`**
- **Cause:** Incorrect GraphQL query format
- **Solution:** Use proper `input` parameter structure
- **Fixed:** Updated to correct API schema

### **Error: `FieldUndefined`**
- **Cause:** Using deprecated field names
- **Solution:** Use `bookingsBySpace` structure
- **Fixed:** Updated response parsing logic

---

## 📊 System Behavior Analysis

### **Vacation Date Handling**
- **Format:** Line-separated dates in `vacation_dates.txt`
- **Parsing:** Splits on newlines (not commas)
- **Behavior:** Bot skips booking on vacation dates
- **Example:** `2025-12-24\n2025-12-25\n2025-12-26`

### **Occupancy Checks**
- **Previous:** Had high occupancy restrictions (>90%)
- **Current:** ✅ **REMOVED** - bot books regardless of occupancy
- **Rationale:** High occupancy shouldn't prevent booking available spots

### **Module Caching Issues**
- **Problem:** Python caches modules, changes not reflected
- **Solution:** Use `fresh_run.py` to bypass caching
- **GitHub Actions:** Automatically uses fresh instance

---

## 🔄 GitHub Actions Configuration

### **Cron Schedule**
```yaml
# Run at midnight Eastern Time (UTC-5 in winter, UTC-4 in summer)
- cron: '0 5 * * 1-5'  # 5:00 UTC = midnight EST (Monday-Friday)
```

### **Required Secrets**
```
ELIA_GRAPHQL_TOKEN      # API authentication
EMAIL_ADDRESS           # Email notifications
SMTP_PASSWORD           # Email password
SMTP_HOST               # SMTP server
SMTP_PORT               # SMTP port
ELIA_EMAIL              # User email
TOTP_SECRET             # 2FA secret
MICROSOFT_USERNAME      # Microsoft account
```

---

## 🎯 Final Recommendations

### **For Executive Spots:**
1. **Timing is critical** - book within 6 hours of need
2. **Use 12-hour duration** for full day coverage
3. **Monitor availability** - spots fill up quickly
4. **Consider regular spots** if advance booking needed

### **For Regular Spots:**
1. **Book 14 days ahead** for guaranteed availability
2. **Use 12-hour duration** for full day coverage
3. **Skip vacation dates** automatically
4. **Monitor occupancy** but don't restrict booking

### **System Configuration:**
1. **Use fresh_run.py** to avoid caching issues
2. **Configure all 8 GitHub secrets** for Actions
3. **Monitor logs** for booking success/failure
4. **Test regularly** to ensure API compatibility

---

## 📈 Success Metrics

### **Working Features:**
- ✅ Vacation date parsing (line-separated)
- ✅ Executive spot detection and booking attempts
- ✅ Regular spot 14-day advance booking
- ✅ Time calculation (6 AM - 6 PM Montreal)
- ✅ Email notifications (when configured)
- ✅ GitHub Actions automation
- ✅ Module caching bypass

### **Expected Results:**
- **Executive spots:** Booked when available within 6-hour window
- **Regular spots:** Booked 14 days in advance
- **Vacation dates:** Automatically skipped
- **Notifications:** Email sent on booking completion

---

*Last Updated: December 11, 2025*
*Based on extensive API testing and real-world usage*

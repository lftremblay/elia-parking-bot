# 📁 Elia Parking Bot - Clean Project Structure

## 🎯 Core Production Files

### Main Bot Logic
- **`production_api_bot.py`** - Main bot with smart booking strategy
  - Books executive spots for tomorrow
  - Books regular spots 14 days ahead
  - Handles vacation dates
  - Prevents double-booking

### API & Detection
- **`fixed_graphql_client.py`** - GraphQL API client for Elia system
- **`correct_booking_detector.py`** - Detects existing bookings to prevent conflicts

### Runners
- **`fresh_run.py`** - Production runner (bypasses Python cache)
- **`final_booking_test.py`** - Test mode runner for manual workflow

## 📋 Configuration Files

- **`.env`** - Environment variables (gitignored)
  - `ELIA_GRAPHQL_TOKEN` - Auth token from Chrome extension
  - `ELIA_EMAIL` - Your Elia email
  - `TOTP_SECRET` - 2FA secret
  
- **`requirements.txt`** - Python dependencies
- **`vacation_dates.txt`** - Vacation dates to skip (YYYY-MM-DD format)
- **`.gitignore`** - Git ignore patterns
- **`.gitattributes`** - Git line ending configuration

## 📚 Documentation

- **`README.md`** - Main project documentation
- **`ELIA_POLICIES.md`** - Booking policies and rules
- **`SMART_BOOKING_GUIDE.md`** - How the smart booking works
- **`VACATION_DEMO.md`** - Vacation feature guide

## 🤖 GitHub Actions Workflows

Located in `.github/workflows/`:

- **`midnight-bot.yml`** - Automated midnight runs (4-5 AM UTC)
- **`manual-parking-bot.yml`** - Manual trigger workflow
- **`daily-parking-bot.yml`** - Legacy daily workflow (not used)

## 🔧 Tools & Extensions

- **`elia-token-extension/`** - Chrome extension to extract auth token
- **`.windsurf/`** - Windsurf IDE configuration

## 📊 File Count Summary

**Total Files:** 8 core Python files + 4 config files + 4 docs = **16 essential files**

**Removed:** 24 old test/debug files and outdated documentation

## 🚀 How It Works

1. **Midnight Run** (Automated)
   - GitHub Actions triggers at midnight EST
   - Runs `fresh_run.py` → `production_api_bot.py`
   - Books spots automatically

2. **Manual Run** (On-Demand)
   - Trigger from GitHub Actions UI
   - Choose test mode or production mode
   - View results in Actions logs

3. **Booking Strategy**
   - ✅ Executive spot for tomorrow (if weekday)
   - ✅ Regular spots 14 days ahead (weekdays only)
   - ✅ Skips existing bookings (no double-booking)
   - ✅ Skips vacation dates from `vacation_dates.txt`
   - ✅ Fallback to regular if executive unavailable

## 🎨 Clean & Minimal

This project now contains **only essential files** - no clutter, no old code, just what's needed for production! 🚗✨

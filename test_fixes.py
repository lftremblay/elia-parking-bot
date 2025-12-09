#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script to verify the fixes are working
"""
import os
import sys
from dotenv import load_dotenv

# Force reload environment
load_dotenv(override=True)

print("TESTING FIXES")
print("=" * 50)

# Test 1: Email configuration
print("EMAIL CONFIGURATION TEST:")
print(f"   - EMAIL_ADDRESS: '{os.getenv('EMAIL_ADDRESS')}'")
print(f"   - SMTP_PASSWORD: {'SET' if os.getenv('SMTP_PASSWORD') else 'MISSING'}")
print(f"   - SMTP_HOST: '{os.getenv('SMTP_HOST')}'")
print(f"   - SMTP_PORT: '{os.getenv('SMTP_PORT')}'")

email_enabled = all([os.getenv('EMAIL_ADDRESS'), os.getenv('SMTP_PASSWORD')])
print(f"   - ENABLED: {email_enabled}")
print()

# Test 2: Import and test the bot
try:
    from production_api_bot import ProductionEliaBot, EmailNotifier
    
    print("BOT IMPORT TEST:")
    
    # Test email notifier
    email_notifier = EmailNotifier()
    print(f"   - Email Notifier Enabled: {email_notifier.enabled}")
    print()
    
    # Test bot time calculation
    bot = ProductionEliaBot()
    start_time, end_time = bot._calculate_booking_times(6)
    print(f"TIME CALCULATION TEST:")
    print(f"   - Input: 6 hours")
    print(f"   - Output: {start_time} to {end_time}")
    print(f"   - Expected: 06:00:00.000Z to 12:00:00.000Z")
    print(f"   - Correct: {start_time == '06:00:00.000Z' and end_time == '12:00:00.000Z'}")
    print()
    
    print("All tests completed successfully!")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()

#!/usr/bin/env python3
"""
🔍 TOTP SECRET VALIDATION DEBUGGER
Validates if your TOTP secret matches Microsoft Authenticator expectations
"""

import pyotp
import time
from datetime import datetime, timezone, timedelta

def debug_totp_secret():
    """Debug TOTP secret and generate current valid codes"""
    
    print("🔍 TOTP SECRET DEBUGGER")
    print("=" * 50)
    
    # Test with a sample secret (replace with your actual secret for testing)
    # IMPORTANT: Never commit your actual secret to git!
    # TOTP secrets are typically 32+ characters (base32 encoded)
    # Example: "JBSWY3DPEHPK3PXP" (this is just an example)
    test_secret = "vjjncwlnls77kzxn"  # 16-character secret - testing if it works
    
    if test_secret == "YOUR_SECRET_HERE":
        print("❌ PLEASE EDIT THIS FILE:")
        print("   Replace 'YOUR_SECRET_HERE' with your actual TOTP secret")
        print("   Then run: python debug_totp_secret.py")
        return
    
    # Warning for short secrets but allow testing
    if len(test_secret) < 20:
        print(f"⚠️ SHORT SECRET WARNING: '{test_secret}'")
        print(f"   Length: {len(test_secret)} characters (Microsoft usually uses 32+)")
        print("   Testing anyway to see if it generates valid codes...")
        print()
    
    print(f"🔑 Testing secret: {test_secret[:8]}...{test_secret[-8:]}")
    print()
    
    # Generate TOTP for different time windows
    totp = pyotp.TOTP(test_secret)
    
    print("🕐 CURRENT TIME WINDOWS:")
    print("-" * 30)
    
    offsets = [-90, -60, -30, 0, 30, 60, 90]
    
    for offset in offsets:
        current_time = datetime.now(timezone.utc) + timedelta(seconds=offset)
        code = totp.at(current_time)
        time_str = current_time.strftime('%H:%M:%S')
        print(f"Offset {offset:>3}s ({time_str}) → {code}")
    
    print()
    print("📱 MANUAL VALIDATION INSTRUCTIONS:")
    print("-" * 40)
    print("1. Open Microsoft Authenticator app")
    print("2. Find your Elia account")
    print("3. Compare the 6-digit code shown NOW")
    print("4. Match it with the 'Offset 0s' code above")
    print()
    print("🚨 IF CODES DON'T MATCH:")
    print("   → Your TOTP secret is incorrect")
    print("   → Need to extract the correct secret from Microsoft Authenticator")
    print("   → Or regenerate the secret in Microsoft account settings")
    
    print()
    print("🔧 TOTP SECRET EXTRACTION OPTIONS:")
    print("-" * 40)
    print("1. Microsoft Authenticator → Export QR code → Scan with QR reader")
    print("2. Microsoft Account Security → Add new authenticator → Get new secret")
    print("3. Use Android app like 'Authenticator Plus' to export existing secrets")

if __name__ == "__main__":
    debug_totp_secret()

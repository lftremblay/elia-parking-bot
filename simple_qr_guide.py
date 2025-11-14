#!/usr/bin/env python3
"""
📱 SIMPLE QR CODE SECRET EXTRACTION GUIDE
Helps you extract TOTP secret from QR code without complex dependencies
"""

def print_qr_extraction_guide():
    """Print step-by-step guide for extracting TOTP secret"""
    
    print("📱 QR CODE SECRET EXTRACTION GUIDE")
    print("=" * 50)
    print()
    print("🔍 METHOD 1: Online QR Decoder (EASIEST)")
    print("-" * 40)
    print("1. Save your QR code image as PNG/JPG")
    print("2. Go to: https://qrdecoder.com/ or https://zxing.org/w/decode.jspx")
    print("3. Upload your QR code image")
    print("4. Look for text like: otpauth://totp/Elia:your-email@domain.com?secret=XXXXXXXXXX&issuer=Elia")
    print("5. Copy the secret part (after secret= and before &)")
    print()
    print("🔍 METHOD 2: Phone QR Scanner")
    print("-" * 40)
    print("1. Use any QR scanner app on your phone")
    print("2. Scan the QR code from your screen")
    print("3. Copy the resulting URL/text")
    print("4. Extract the secret from the URL")
    print()
    print("🔍 METHOD 3: Microsoft Account (RECOMMENDED)")
    print("-" * 40)
    print("1. Go to: https://account.microsoft.com/security")
    print("2. Advanced security options → Two-step verification")
    print("3. Authenticator app → Set up a different Authenticator app")
    print("4. Choose Phone → Show QR code → Can't scan?")
    print("5. 'Show secret' → Copy the 32+ character secret")
    print()
    print("📝 WHAT TO LOOK FOR:")
    print("-" * 40)
    print("✅ VALID SECRET: JBSWY3DPEHPK3PXPJBSWY3DPEHPK3PXP (32+ chars, base32)")
    print("✅ VALID SECRET: MFRGG3DFMZTWQ3DKNRQXIZLTMFZGG33F (32+ chars, base32)")
    print("❌ INVALID: vjjncwlnls77kzxn (too short, not base32)")
    print("❌ INVALID: 123456 (numbers only)")
    print()
    print("🎯 ONCE YOU HAVE THE SECRET:")
    print("-" * 40)
    print("1. Edit debug_totp_secret.py")
    print("2. Replace the test_secret with your real secret")
    print("3. Run: python debug_totp_secret.py")
    print("4. Validate it matches Microsoft Authenticator")
    print()
    print("🔧 TOTP SECRET FORMAT:")
    print("-" * 40)
    print("• Length: 16-64 characters (usually 32)")
    print("• Characters: A-Z, 2-7 (base32 encoding)")
    print("• Example: JBSWY3DPEHPK3PXPJBSWY3DPEHPK3PXP")
    print("• No spaces or special characters")

def validate_secret_format(secret):
    """Validate if secret looks like a proper TOTP secret"""
    
    if not secret or len(secret) < 16:
        return False, "Too short (minimum 16 characters)"
    
    # Check if it's base32 encoded
    base32_chars = set("ABCDEFGHIJKLMNOPQRSTUVWXYZ234567")
    if not all(c.upper() in base32_chars for c in secret):
        return False, "Contains invalid characters (must be base32: A-Z, 2-7)"
    
    if len(secret) < 20:
        return True, "Valid but short (should be 32+ characters for Microsoft)"
    
    return True, "Valid TOTP secret format"

if __name__ == "__main__":
    print_qr_extraction_guide()
    
    print("\n🔍 SECRET VALIDATOR")
    print("-" * 30)
    
    # Test some examples
    test_secrets = [
        "JBSWY3DPEHPK3PXPJBSWY3DPEHPK3PXP",
        "vjjncwlnls77kzxn",
        "MFRGG3DFMZTWQ3DKNRQXIZLTMFZGG33F",
        "123456"
    ]
    
    for secret in test_secrets:
        is_valid, message = validate_secret_format(secret)
        status = "✅" if is_valid else "❌"
        print(f"{status} {secret[:20]}... - {message}")

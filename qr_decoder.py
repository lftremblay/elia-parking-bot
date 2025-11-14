#!/usr/bin/env python3
"""
🔍 QR CODE SECRET EXTRACTOR
Extracts TOTP secret from QR code images
"""

import cv2
import numpy as np
from pyzbar import pyzbar
import re

def decode_qr_from_image(image_path):
    """Decode QR code and extract TOTP secret"""
    
    print("🔍 QR CODE SECRET EXTRACTOR")
    print("=" * 40)
    
    try:
        # Read the image
        image = cv2.imread(image_path)
        if image is None:
            print(f"❌ Could not read image: {image_path}")
            return None
        
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Decode QR codes
        qr_codes = pyzbar.decode(gray)
        
        if not qr_codes:
            print("❌ No QR codes found in image")
            return None
        
        # Extract data from first QR code
        qr_data = qr_codes[0].data.decode('utf-8')
        print(f"📱 QR Code Data: {qr_data}")
        print()
        
        # Extract TOTP secret from QR data
        # TOTP QR codes typically follow format: otpauth://totp/Service:User?secret=SECRET&issuer=Service
        secret_match = re.search(r'secret=([^&]+)', qr_data)
        
        if secret_match:
            secret = secret_match.group(1)
            print(f"🔑 EXTRACTED TOTP SECRET: {secret}")
            print(f"📏 Secret length: {len(secret)} characters")
            
            # Validate it's a proper base32 secret
            if len(secret) >= 16 and all(c in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ234567' for c in secret.upper()):
                print("✅ Valid TOTP secret detected!")
                return secret
            else:
                print("⚠️ Secret may not be valid TOTP format")
                return secret
        else:
            print("❌ No secret found in QR code data")
            print("🔍 Raw QR data:", qr_data)
            return None
            
    except Exception as e:
        print(f"❌ Error decoding QR code: {e}")
        return None

def main():
    """Main function"""
    import sys
    
    if len(sys.argv) != 2:
        print("Usage: python qr_decoder.py <path_to_qr_image>")
        print("Example: python qr_decoder.py qr_code.png")
        return
    
    image_path = sys.argv[1]
    secret = decode_qr_from_image(image_path)
    
    if secret:
        print()
        print("🎯 NEXT STEPS:")
        print("1. Update debug_totp_secret.py with this secret")
        print("2. Run: python debug_totp_secret.py")
        print("3. Validate against Microsoft Authenticator")
        print("4. Update your configuration with the correct secret")

if __name__ == "__main__":
    main()

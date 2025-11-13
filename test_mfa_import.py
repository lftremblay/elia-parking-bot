#!/usr/bin/env python3
"""
Quick test to verify pyotp import and MFA functionality
"""

import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_pyotp_import():
    """Test that pyotp can be imported and used"""
    try:
        import pyotp
        print("✅ pyotp import successful")
        
        # Test TOTP generation
        test_secret = "JBSWY3DPEHPK3PXP"  # Test secret
        totp = pyotp.TOTP(test_secret)
        code = totp.now()
        print(f"✅ TOTP code generation successful: {code}")
        
        return True
    except Exception as e:
        print(f"❌ pyotp test failed: {e}")
        return False

def test_browser_automation_import():
    """Test that browser_automation can import pyotp"""
    try:
        from browser_automation import BrowserAutomation
        print("✅ BrowserAutomation import successful")
        return True
    except Exception as e:
        print(f"❌ BrowserAutomation import failed: {e}")
        return False

def test_bot_orchestrator_import():
    """Test that bot_orchestrator has the new method"""
    try:
        from bot_orchestrator import EliaParkingBot
        print("✅ EliaParkingBot import successful")
        
        # Check if the new method exists
        if hasattr(EliaParkingBot, '_authenticate_with_cloud_manager'):
            print("✅ _authenticate_with_cloud_manager method exists")
        else:
            print("❌ _authenticate_with_cloud_manager method missing")
            return False
        
        return True
    except Exception as e:
        print(f"❌ EliaParkingBot import failed: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing MFA Import Fixes")
    print("=" * 40)
    
    tests = [
        test_pyotp_import,
        test_browser_automation_import,
        test_bot_orchestrator_import
    ]
    
    results = []
    for test in tests:
        print(f"\n🔍 Running {test.__name__}...")
        results.append(test())
    
    print("\n" + "=" * 40)
    print(f"📊 Test Results: {sum(results)}/{len(results)} passed")
    
    if all(results):
        print("🎉 ALL TESTS PASSED! Fixes are working correctly!")
        sys.exit(0)
    else:
        print("❌ Some tests failed. Please check the issues above.")
        sys.exit(1)

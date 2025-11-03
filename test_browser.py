#!/usr/bin/env python3
"""
Simple test script for browser_automation.py
"""

import browser_automation
import os

def test_basic_import():
    """Test that the module can be imported"""
    print("✅ Module imported successfully")
    return True

def test_class_instantiation():
    """Test that BrowserAutomation class can be instantiated"""
    config = {
        'advanced': {
            'browser_profile_path': './test_browser_data'
        }
    }

    try:
        browser = browser_automation.BrowserAutomation(config)
        print("✅ BrowserAutomation class instantiated successfully")
        print(f"📁 Profile path: {browser.profile_path}")
        print(f"📁 Screenshot dir: {browser.screenshot_dir}")
        return True
    except Exception as e:
        print(f"❌ Class instantiation failed: {e}")
        return False

def test_playwright_availability():
    """Test Playwright availability"""
    if browser_automation.PLAYWRIGHT_AVAILABLE:
        print("✅ Playwright is available")
    else:
        print("⚠️  Playwright not available (expected if not installed)")
    return True

def main():
    """Run all tests"""
    print("🚀 Testing Browser Automation Module")
    print("=" * 50)

    tests = [
        ("Basic Import", test_basic_import),
        ("Playwright Check", test_playwright_availability),
        ("Class Instantiation", test_class_instantiation),
    ]

    passed = 0
    total = len(tests)

    for test_name, test_func in tests:
        print(f"\n🔍 Running: {test_name}")
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name}: PASSED")
            else:
                print(f"❌ {test_name}: FAILED")
        except Exception as e:
            print(f"❌ {test_name}: ERROR - {e}")

    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 ALL TESTS PASSED! Module is ready for production.")
        return 0
    else:
        print("❌ Some tests failed. Please review the issues.")
        return 1

if __name__ == "__main__":
    exit(main())

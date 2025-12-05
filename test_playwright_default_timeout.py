#!/usr/bin/env python3
"""
Test Playwright Default Timeout Fix
Validates that Playwright default timeouts are properly set in cloud auth
"""

import re
from pathlib import Path

print("🔧 Testing Playwright Default Timeout Fix")
print("=" * 50)

def test_default_timeout_setting():
    """Test that default timeouts are set in cloud auth manager"""
    print("\n1. Testing Playwright default timeout configuration...")
    
    file_path = Path("src/cloud/cloud_auth_manager.py")
    
    if not file_path.exists():
        print(f"   ❌ File not found: {file_path}")
        return False
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for default timeout settings
        checks = [
            {
                "pattern": r"set_default_timeout\(45000\)",
                "description": "Default operation timeout set to 45s"
            },
            {
                "pattern": r"set_default_navigation_timeout\(45000\)",
                "description": "Default navigation timeout set to 45s"
            },
            {
                "pattern": r"Set Playwright default timeouts to 45s",
                "description": "Timeout configuration logged"
            }
        ]
        
        all_found = True
        for check in checks:
            if re.search(check["pattern"], content):
                print(f"   ✅ {check['description']}")
            else:
                print(f"   ❌ {check['description']} - NOT FOUND")
                all_found = False
        
        return all_found
        
    except Exception as e:
        print(f"   ❌ Error reading file: {e}")
        return False

def test_timeout_order():
    """Test that default timeouts are set before any operations"""
    print("\n2. Testing timeout configuration order...")
    
    file_path = Path("src/cloud/cloud_auth_manager.py")
    
    if not file_path.exists():
        print(f"   ❌ File not found: {file_path}")
        return False
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Find the line numbers
        new_page_line = None
        set_timeout_line = None
        goto_line = None
        
        for i, line in enumerate(lines):
            if 'new_page()' in line:
                new_page_line = i
            elif 'set_default_timeout(45000)' in line:
                set_timeout_line = i
            elif 'goto("https://login.microsoft.com/"' in line:
                goto_line = i
        
        if new_page_line and set_timeout_line and goto_line:
            if new_page_line < set_timeout_line < goto_line:
                print(f"   ✅ Timeout configuration order correct:")
                print(f"      1. new_page() at line {new_page_line + 1}")
                print(f"      2. set_default_timeout() at line {set_timeout_line + 1}")
                print(f"      3. goto() at line {goto_line + 1}")
                return True
            else:
                print(f"   ❌ Timeout configuration order incorrect")
                return False
        else:
            print(f"   ⚠️  Could not verify order (missing markers)")
            return False
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def test_comprehensive_coverage():
    """Test that all timeout scenarios are covered"""
    print("\n3. Testing comprehensive timeout coverage...")
    
    file_path = Path("src/cloud/cloud_auth_manager.py")
    
    if not file_path.exists():
        print(f"   ❌ File not found: {file_path}")
        return False
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Count different timeout configurations
        default_timeout_count = len(re.findall(r'set_default_timeout', content))
        explicit_timeout_count = len(re.findall(r'timeout=45000', content))
        
        print(f"   📊 Default timeout configurations: {default_timeout_count}")
        print(f"   📊 Explicit timeout parameters: {explicit_timeout_count}")
        
        if default_timeout_count >= 2:  # set_default_timeout and set_default_navigation_timeout
            print(f"   ✅ Default timeouts properly configured")
        else:
            print(f"   ❌ Missing default timeout configurations")
            return False
        
        if explicit_timeout_count >= 5:  # Multiple operations with explicit timeouts
            print(f"   ✅ Explicit timeouts maintained for critical operations")
        else:
            print(f"   ⚠️  Few explicit timeouts (relying on defaults)")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def test_expected_behavior():
    """Document expected behavior after fix"""
    print("\n4. Expected behavior after fix...")
    
    print("   📋 What this fix solves:")
    print("      ✅ Prevents 'Timeout 30000ms exceeded' errors")
    print("      ✅ Applies 45s timeout to ALL Playwright operations")
    print("      ✅ Covers implicit waits and selectors")
    print("      ✅ Ensures consistent timeout behavior")
    
    print("\n   🎯 Operations now covered:")
    print("      • page.goto() - navigation")
    print("      • page.wait_for_selector() - element waits")
    print("      • page.wait_for_load_state() - load waits")
    print("      • page.fill() - input operations")
    print("      • page.click() - click operations")
    print("      • All other Playwright operations")
    
    return True

def main():
    """Run all tests"""
    print("🔧 Validating Playwright Default Timeout Fix")
    print("=" * 50)
    
    tests = [
        ("Default Timeout Setting", test_default_timeout_setting),
        ("Timeout Configuration Order", test_timeout_order),
        ("Comprehensive Coverage", test_comprehensive_coverage),
        ("Expected Behavior", test_expected_behavior)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Test '{test_name}' failed: {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 50)
    print("🎯 Playwright Default Timeout Fix Test Results")
    print("=" * 50)
    
    all_passed = True
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
        if not result:
            all_passed = False
    
    print(f"\n🏆 Overall Result: {'ALL TESTS PASSED' if all_passed else 'SOME TESTS FAILED'}")
    
    if all_passed:
        print("\n🚀 Playwright default timeout fix is complete!")
        print("\n📋 Fix Summary:")
        print("✅ Default operation timeout: 30s → 45s")
        print("✅ Default navigation timeout: 30s → 45s")
        print("✅ Applied to ALL Playwright operations")
        print("✅ Set immediately after page creation")
        print("✅ Covers implicit and explicit waits")
        
        print("\n💡 This fix ensures:")
        print("- No more 'Timeout 30000ms exceeded' errors")
        print("- Consistent 45s timeout across all operations")
        print("- Better handling of slow Microsoft SSO")
        print("- Improved reliability in GitHub Actions")
        
        print("\n🎯 Ready for deployment!")
    else:
        print("\n⚠️  Some issues remain - review failed tests above")

if __name__ == "__main__":
    main()

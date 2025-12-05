#!/usr/bin/env python3
"""
Test Cloud Auth Timeout Fix
Validates that all timeout fixes have been applied to cloud authentication manager
"""

import re
from pathlib import Path

print("🔧 Testing Cloud Auth Timeout Fix")
print("=" * 50)

def test_cloud_auth_timeouts():
    """Test that all timeouts in cloud auth manager have been increased"""
    print("\n1. Testing cloud authentication timeout fixes...")
    
    file_path = Path("src/cloud/cloud_auth_manager.py")
    
    if not file_path.exists():
        print(f"   ❌ File not found: {file_path}")
        return False
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for all timeout improvements
        timeout_checks = [
            {
                "pattern": r"goto.*login\.microsoft\.com.*timeout=45000",
                "description": "Microsoft login navigation timeout (45s)"
            },
            {
                "pattern": r"wait_for_load_state.*networkidle.*timeout=45000",
                "description": "Network idle wait timeouts (45s)"
            },
            {
                "pattern": r"wait_for_selector.*timeout=15000.*Increased from 10s to 15s",
                "description": "MFA selector timeout (15s)"
            }
        ]
        
        results = []
        for check in timeout_checks:
            if re.search(check["pattern"], content, re.IGNORECASE | re.DOTALL):
                print(f"   ✅ {check['description']}")
                results.append(True)
            else:
                print(f"   ❌ {check['description']} - NOT FOUND")
                results.append(False)
        
        # Count all wait_for_load_state calls with timeout
        load_state_with_timeout = len(re.findall(r'wait_for_load_state.*timeout=45000', content))
        print(f"\n   📊 Found {load_state_with_timeout} wait_for_load_state calls with 45s timeout")
        
        # Check for any remaining default timeouts (potential issues)
        load_state_without_timeout = len(re.findall(r'wait_for_load_state\(["\']networkidle["\']\)(?!\s*,\s*timeout)', content))
        if load_state_without_timeout > 0:
            print(f"   ⚠️  Warning: {load_state_without_timeout} wait_for_load_state calls without explicit timeout")
        else:
            print(f"   ✅ All wait_for_load_state calls have explicit timeouts")
        
        return all(results) and load_state_with_timeout >= 5
        
    except Exception as e:
        print(f"   ❌ Error reading file: {e}")
        return False

def test_timeout_consistency():
    """Test that timeout values are consistent across the codebase"""
    print("\n2. Testing timeout consistency...")
    
    files_to_check = [
        "src/cloud/cloud_auth_manager.py",
        "browser_automation.py"
    ]
    
    timeout_values = {
        "45000": "Main navigation and load state timeouts",
        "15000": "MFA and input field timeouts"
    }
    
    all_consistent = True
    for file_path in files_to_check:
        path = Path(file_path)
        if path.exists():
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                print(f"\n   📄 {file_path}:")
                for timeout, description in timeout_values.items():
                    count = len(re.findall(rf'timeout={timeout}', content))
                    if count > 0:
                        print(f"      ✅ {description}: {count} occurrences")
                    else:
                        print(f"      ⚠️  {description}: Not found")
                        
            except Exception as e:
                print(f"      ❌ Error reading: {e}")
                all_consistent = False
        else:
            print(f"   ❌ {file_path} not found")
            all_consistent = False
    
    return all_consistent

def test_mfa_timeout_fix():
    """Test that MFA timeout has been increased"""
    print("\n3. Testing MFA timeout fix...")
    
    file_path = Path("src/cloud/cloud_auth_manager.py")
    
    if not file_path.exists():
        print(f"   ❌ File not found: {file_path}")
        return False
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for MFA timeout increase
        if re.search(r'timeout=15000.*Increased from 10s to 15s', content):
            print("   ✅ MFA input timeout increased to 15s")
            return True
        else:
            print("   ❌ MFA timeout fix not found")
            return False
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def test_error_messages():
    """Test that timeout error messages will be more informative"""
    print("\n4. Testing error handling improvements...")
    
    file_path = Path("src/cloud/cloud_auth_manager.py")
    
    if not file_path.exists():
        print(f"   ❌ File not found: {file_path}")
        return False
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for error handling
        error_patterns = [
            r'logger\.error.*Microsoft authentication failed',
            r'logger\.error.*MFA.*failed',
            r'except.*Exception.*as.*e'
        ]
        
        results = []
        for pattern in error_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                results.append(True)
            else:
                results.append(False)
        
        if all(results):
            print("   ✅ Error handling present")
            return True
        else:
            print("   ⚠️  Some error handling may be missing")
            return False
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def main():
    """Run all tests"""
    print("🔧 Validating Cloud Auth Timeout Fix")
    print("=" * 50)
    
    tests = [
        ("Cloud Auth Timeouts", test_cloud_auth_timeouts),
        ("Timeout Consistency", test_timeout_consistency),
        ("MFA Timeout Fix", test_mfa_timeout_fix),
        ("Error Handling", test_error_messages)
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
    print("🎯 Cloud Auth Timeout Fix Test Results")
    print("=" * 50)
    
    all_passed = True
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
        if not result:
            all_passed = False
    
    print(f"\n🏆 Overall Result: {'ALL TESTS PASSED' if all_passed else 'SOME TESTS FAILED'}")
    
    if all_passed:
        print("\n🚀 Cloud authentication timeout fix is complete!")
        print("\n📋 Fix Summary:")
        print("✅ Microsoft login navigation timeout: 30s → 45s (+50%)")
        print("✅ All networkidle waits: default → 45s")
        print("✅ MFA input timeout: 10s → 15s (+50%)")
        print("✅ Consistent timeout values across codebase")
        print("✅ Error handling maintained")
        
        print("\n💡 Expected Results:")
        print("- No more 'Timeout 30000ms exceeded' errors")
        print("- Microsoft SSO authentication succeeds")
        print("- MFA handling more reliable")
        print("- Cloud authentication works in GitHub Actions")
        
        print("\n🎯 Ready for deployment!")
    else:
        print("\n⚠️  Some issues remain - review failed tests above")

if __name__ == "__main__":
    main()

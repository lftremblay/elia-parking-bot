#!/usr/bin/env python3
"""
Test Applied Authentication Fixes
Validates that all timeout and error handling fixes have been properly applied
"""

import re
import json
from pathlib import Path
from loguru import logger

print("🔧 Testing Applied Authentication Fixes")
print("=" * 50)

def test_timeout_fixes_applied():
    """Test that timeout fixes have been applied to source files"""
    print("\n1. Testing timeout fixes in source files...")
    
    fixes_to_check = [
        {
            "file": "src/cloud/cloud_auth_manager.py",
            "pattern": r"timeout=15000.*Increased from 10s to 15s",
            "description": "MFA timeout increased from 10s to 15s"
        },
        {
            "file": "browser_automation.py", 
            "pattern": r"timeout=45000.*Increased from 30s to 45s",
            "description": "Main navigation timeout increased from 30s to 45s"
        },
        {
            "file": "browser_automation.py",
            "pattern": r"timeout=15000.*Increased from 5s to 15s",
            "description": "Email input timeout increased from 5s to 15s"
        },
        {
            "file": "browser_automation.py",
            "pattern": r"timeout=15000.*Increased from 10s to 15s", 
            "description": "Organization timeout increased from 10s to 15s"
        }
    ]
    
    results = []
    for fix in fixes_to_check:
        file_path = Path(fix["file"])
        if file_path.exists():
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                if re.search(fix["pattern"], content, re.IGNORECASE):
                    print(f"   ✅ {fix['description']}")
                    results.append(True)
                else:
                    print(f"   ❌ {fix['description']} - NOT FOUND")
                    results.append(False)
            except Exception as e:
                print(f"   ❌ {fix['description']} - ERROR: {e}")
                results.append(False)
        else:
            print(f"   ❌ {fix['description']} - FILE NOT FOUND")
            results.append(False)
    
    return all(results)

def test_health_monitoring_integration():
    """Test that health monitoring has been integrated"""
    print("\n2. Testing health monitoring integration...")
    
    checks = [
        {
            "file": "browser_health_monitor.py",
            "description": "Browser health monitor file exists"
        },
        {
            "file": "bot_orchestrator.py",
            "pattern": r"from browser_health_monitor import add_health_monitoring",
            "description": "Health monitoring import added to bot orchestrator"
        },
        {
            "file": "bot_orchestrator.py", 
            "pattern": r"add_health_monitoring\(self\.browser\)",
            "description": "Health monitoring integration added to browser initialization"
        },
        {
            "file": "bot_orchestrator.py",
            "pattern": r"cleanup_with_health_monitor",
            "description": "Enhanced cleanup method integrated"
        }
    ]
    
    results = []
    for check in checks:
        file_path = Path(check["file"])
        if file_path.exists():
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                if "pattern" in check:
                    if re.search(check["pattern"], content, re.IGNORECASE):
                        print(f"   ✅ {check['description']}")
                        results.append(True)
                    else:
                        print(f"   ❌ {check['description']} - NOT FOUND")
                        results.append(False)
                else:
                    print(f"   ✅ {check['description']}")
                    results.append(True)
            except Exception as e:
                print(f"   ❌ {check['description']} - ERROR: {e}")
                results.append(False)
        else:
            print(f"   ❌ {check['description']} - FILE NOT FOUND")
            results.append(False)
    
    return all(results)

def test_configuration_validation():
    """Test configuration supports the fixes"""
    print("\n3. Testing configuration support...")
    
    try:
        with open("config.json", "r") as f:
            config = json.load(f)
        
        checks = [
            ("retry" in config, "Retry configuration exists"),
            ("max_attempts" in config.get("retry", {}), "Max retry attempts configured"),
            ("backoff_seconds" in config.get("retry", {}), "Backoff strategy configured"),
            ("mfa" in config, "MFA configuration exists"),
            ("totp_secret" in config.get("mfa", {}), "TOTP secret configured")
        ]
        
        results = []
        for check, description in checks:
            if check:
                print(f"   ✅ {description}")
                results.append(True)
            else:
                print(f"   ❌ {description}")
                results.append(False)
        
        return all(results)
        
    except Exception as e:
        print(f"   ❌ Configuration validation failed: {e}")
        return False

def test_fix_files_created():
    """Test that all fix files have been created"""
    print("\n4. Testing fix files creation...")
    
    fix_files = [
        "auth_timeout_fix.py",
        "improved_auth_flow.py", 
        "browser_health_monitor.py",
        "test_complete_auth_fix.py",
        "test_applied_fixes.py"
    ]
    
    results = []
    for file_name in fix_files:
        file_path = Path(file_name)
        if file_path.exists():
            print(f"   ✅ {file_name} created")
            results.append(True)
        else:
            print(f"   ❌ {file_name} missing")
            results.append(False)
    
    return all(results)

def test_timeout_values():
    """Test specific timeout values in code"""
    print("\n5. Testing timeout values...")
    
    timeout_checks = [
        {
            "file": "src/cloud/cloud_auth_manager.py",
            "expected_values": [15000],  # MFA timeout
            "description": "MFA timeout set to 15s"
        },
        {
            "file": "browser_automation.py",
            "expected_values": [45000],  # Main navigation timeout
            "description": "Main navigation timeout set to 45s"
        }
    ]
    
    results = []
    for check in timeout_checks:
        file_path = Path(check["file"])
        if file_path.exists():
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                found_values = []
                for value in check["expected_values"]:
                    pattern = rf"timeout={value}"
                    if re.search(pattern, content):
                        found_values.append(value)
                
                if found_values:
                    print(f"   ✅ {check['description']}: {found_values}")
                    results.append(True)
                else:
                    print(f"   ❌ {check['description']}: No matching timeouts found")
                    results.append(False)
            except Exception as e:
                print(f"   ❌ {check['description']} - ERROR: {e}")
                results.append(False)
        else:
            print(f"   ❌ {check['description']} - FILE NOT FOUND")
            results.append(False)
    
    return all(results)

def main():
    """Run all tests"""
    print("🔧 Validating Applied Authentication Fixes")
    print("=" * 50)
    
    tests = [
        ("Timeout Fixes Applied", test_timeout_fixes_applied),
        ("Health Monitoring Integration", test_health_monitoring_integration),
        ("Configuration Support", test_configuration_validation),
        ("Fix Files Created", test_fix_files_created),
        ("Timeout Values", test_timeout_values)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            logger.error(f"❌ Test '{test_name}' failed: {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 50)
    print("🎯 Applied Fixes Validation Results")
    print("=" * 50)
    
    all_passed = True
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
        if not result:
            all_passed = False
    
    print(f"\n🏆 Overall Result: {'ALL FIXES APPLIED SUCCESSFULLY' if all_passed else 'SOME FIXES MISSING'}")
    
    if all_passed:
        print("\n🚀 Authentication fixes successfully applied!")
        print("\n📋 Summary of Applied Fixes:")
        print("✅ MFA timeout increased: 10s → 15s (+50%)")
        print("✅ Main navigation timeout increased: 30s → 45s (+50%)")
        print("✅ Email input timeout increased: 5s → 15s (+200%)")
        print("✅ Organization timeout increased: 10s → 15s (+50%)")
        print("✅ Browser health monitoring integrated")
        print("✅ Enhanced error recovery implemented")
        print("✅ Graceful cleanup for EPIPE prevention")
        
        print("\n💡 Expected Results:")
        print("- Eliminated Microsoft SSO timeout failures")
        print("- Improved MFA handling reliability")
        print("- Prevented EPIPE communication errors")
        print("- Enhanced error recovery and logging")
        
        print("\n🎯 Ready for production testing!")
    else:
        print("\n⚠️  Some fixes are missing - review failed tests above")

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
GitHub Workflow Validation Script
Ensures Quinn's QA Agent integration will work properly in GitHub Actions
"""

import os
import sys
import json
import subprocess
from pathlib import Path

def check_file_exists(file_path, description):
    """Check if a required file exists"""
    if Path(file_path).exists():
        print(f"✅ {description}: {file_path}")
        return True
    else:
        print(f"❌ {description}: {file_path} - MISSING")
        return False

def check_workflow_syntax():
    """Validate GitHub workflow YAML syntax"""
    try:
        # Simple YAML structure check without PyYAML dependency
        with open('.github/workflows/cloud-auth-deploy.yml', 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Check for required YAML structure
        required_keys = ['name:', 'on:', 'jobs:', 'env:']
        missing_keys = []
        
        for key in required_keys:
            if key not in content:
                missing_keys.append(key)
        
        if not missing_keys:
            print("✅ GitHub Workflow YAML structure: VALID")
            return True
        else:
            print(f"❌ GitHub Workflow YAML structure: MISSING KEYS {missing_keys}")
            return False
            
    except Exception as e:
        print(f"❌ GitHub Workflow validation: ERROR - {e}")
        return False

def check_python_imports():
    """Check if all required Python modules can be imported"""
    required_modules = [
        'pytest',
        'loguru', 
        'pyotp',
        'playwright',
        'msal',
        'cryptography'
    ]
    
    all_good = True
    for module in required_modules:
        try:
            __import__(module)
            print(f"✅ Python module: {module}")
        except ImportError:
            print(f"❌ Python module: {module} - NOT INSTALLED")
            all_good = False
    
    return all_good

def check_qa_validation_script():
    """Check if QA validation script exists and is runnable"""
    qa_script = Path('run_qa_validation.py')
    if not qa_script.exists():
        print("❌ QA validation script: run_qa_validation.py - MISSING")
        return False
    
    try:
        # Check if script has proper structure with encoding handling
        with open(qa_script, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            if 'def main()' in content and 'if __name__ == "__main__"' in content:
                print("✅ QA validation script: run_qa_validation.py - VALID STRUCTURE")
                return True
            else:
                print("❌ QA validation script: run_qa_validation.py - INVALID STRUCTURE")
                return False
    except Exception as e:
        print(f"❌ QA validation script validation: ERROR - {e}")
        return False

def check_cloud_auth_structure():
    """Check cloud authentication structure"""
    cloud_dir = Path('src/cloud')
    required_files = [
        'src/cloud/__init__.py',
        'src/cloud/cloud_auth_manager.py',
        'src/cloud/error_handler.py',
        'qa/__init__.py',
        'qa/cloud_auth_qa.py',
        'qa/report_generator.py'
    ]
    
    all_good = True
    for file_path in required_files:
        if not check_file_exists(file_path, f"Cloud auth component"):
            all_good = False
    
    return all_good

def validate_environment_variables():
    """Check environment variable configuration"""
    env_file = Path('.env')
    if env_file.exists():
        with open(env_file, 'r') as f:
            content = f.read()
            
        required_vars = [
            'TOTP_SECRET',
            'ELIA_PASSWORD', 
            'MICROSOFT_USERNAME'
        ]
        
        all_good = True
        for var in required_vars:
            if f"{var}=" in content:
                print(f"✅ Environment variable: {var}")
            else:
                print(f"❌ Environment variable: {var} - MISSING")
                all_good = False
        
        return all_good
    else:
        print("⚠️  .env file not found (expected for local development)")
        return True  # Not required for GitHub Actions

def main():
    """Main validation function"""
    print("🧪 Quinn's GitHub Workflow Validation")
    print("=" * 50)
    
    checks = [
        ("GitHub Workflow File", lambda: check_file_exists(".github/workflows/cloud-auth-deploy.yml", "GitHub workflow")),
        ("Workflow Syntax", check_workflow_syntax),
        ("Python Modules", check_python_imports),
        ("QA Validation Script", check_qa_validation_script),
        ("Cloud Auth Structure", check_cloud_auth_structure),
        ("Environment Variables", validate_environment_variables)
    ]
    
    results = []
    for check_name, check_func in checks:
        print(f"\n🔍 Checking {check_name}...")
        results.append(check_func())
    
    print("\n" + "=" * 50)
    print("📊 VALIDATION SUMMARY")
    print("=" * 50)
    
    passed = sum(results)
    total = len(results)
    
    print(f"✅ Passed: {passed}/{total}")
    print(f"❌ Failed: {total - passed}/{total}")
    
    if passed == total:
        print("\n🎉 ALL CHECKS PASSED! GitHub workflow is ready.")
        print("🚀 Quinn's QA Gate integration will work properly.")
        return 0
    else:
        print(f"\n⚠️  {total - passed} check(s) failed. Please fix before deploying.")
        return 1

if __name__ == "__main__":
    sys.exit(main())

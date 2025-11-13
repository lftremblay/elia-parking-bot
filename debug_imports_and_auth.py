#!/usr/bin/env python3
"""
Comprehensive Debug Script for MFA Authentication and Reservation Flows
Fixes import issues and validates both authentication and reservation systems
"""

import sys
import asyncio
import json
from pathlib import Path
from datetime import datetime
from loguru import logger

def test_imports():
    """Test all critical imports to ensure no import errors"""
    print("🔍 Testing Critical Imports...")
    
    import_results = {}
    
    # Test 1: Basic Python imports
    try:
        import json
        import asyncio
        import time
        import os
        import_results['basic_python'] = True
        print("✅ Basic Python imports: OK")
    except Exception as e:
        import_results['basic_python'] = False
        print(f"❌ Basic Python imports: FAILED - {e}")
    
    # Test 2: Core dependencies
    try:
        import pyotp
        import cryptography
        from loguru import logger
        import_results['core_dependencies'] = True
        print("✅ Core dependencies: OK")
    except Exception as e:
        import_results['core_dependencies'] = False
        print(f"❌ Core dependencies: FAILED - {e}")
    
    # Test 3: Playwright imports
    try:
        from playwright.async_api import Page, Browser, BrowserContext, async_playwright
        import_results['playwright'] = True
        print("✅ Playwright imports: OK")
    except Exception as e:
        import_results['playwright'] = False
        print(f"❌ Playwright imports: FAILED - {e}")
    
    # Test 4: Auth Manager import
    try:
        from auth_manager import AuthenticationManager
        import_results['auth_manager'] = True
        print("✅ Auth Manager import: OK")
    except Exception as e:
        import_results['auth_manager'] = False
        print(f"❌ Auth Manager import: FAILED - {e}")
        print(f"   Error details: {str(e)}")
    
    # Test 5: Bot Orchestrator import
    try:
        from bot_orchestrator import EliaParkingBot
        import_results['bot_orchestrator'] = True
        print("✅ Bot Orchestrator import: OK")
    except Exception as e:
        import_results['bot_orchestrator'] = False
        print(f"❌ Bot Orchestrator import: FAILED - {e}")
        print(f"   Error details: {str(e)}")
    
    # Test 6: Browser Automation import
    try:
        from browser_automation import BrowserAutomation
        import_results['browser_automation'] = True
        print("✅ Browser Automation import: OK")
    except Exception as e:
        import_results['browser_automation'] = False
        print(f"❌ Browser Automation import: FAILED - {e}")
    
    # Test 7: Scheduler import
    try:
        from scheduler import ReservationScheduler
        import_results['scheduler'] = True
        print("✅ Scheduler import: OK")
    except Exception as e:
        import_results['scheduler'] = False
        print(f"❌ Scheduler import: FAILED - {e}")
    
    return import_results

def test_configuration():
    """Test configuration files and settings"""
    print("\n🔧 Testing Configuration...")
    
    config_results = {}
    
    # Test config.json exists and is valid
    try:
        if Path("config.json").exists():
            with open("config.json", 'r') as f:
                config = json.load(f)
            
            required_sections = ["elia", "schedules", "retry"]
            for section in required_sections:
                if section in config:
                    config_results[f'config_{section}'] = True
                    print(f"✅ Config section '{section}': OK")
                else:
                    config_results[f'config_{section}'] = False
                    print(f"❌ Config section '{section}': MISSING")
            
            config_results['config_file'] = True
            print("✅ Config file: OK")
        else:
            config_results['config_file'] = False
            print("❌ Config file: MISSING")
    except Exception as e:
        config_results['config_file'] = False
        print(f"❌ Config file: FAILED - {e}")
    
    # Test environment files
    env_files = [".env", "local_env_template.env"]
    for env_file in env_files:
        try:
            if Path(env_file).exists():
                config_results[f'env_{env_file}'] = True
                print(f"✅ Environment file '{env_file}': OK")
            else:
                config_results[f'env_{env_file}'] = False
                print(f"⚠️ Environment file '{env_file}': NOT FOUND (optional)")
        except Exception as e:
            config_results[f'env_{env_file}'] = False
            print(f"❌ Environment file '{env_file}': FAILED - {e}")
    
    return config_results

async def test_authentication_manager():
    """Test Authentication Manager initialization and basic functionality"""
    print("\n🔐 Testing Authentication Manager...")
    
    auth_results = {}
    
    try:
        # Import and initialize
        from auth_manager import AuthenticationManager
        
        # Test initialization
        auth_manager = AuthenticationManager()
        auth_results['initialization'] = True
        print("✅ Auth Manager initialization: OK")
        
        # Test cloud environment detection
        is_cloud = auth_manager.is_cloud
        auth_results['cloud_detection'] = True
        print(f"✅ Cloud environment detection: {is_cloud}")
        
        # Test TOTP initialization
        if auth_manager.totp:
            auth_results['totp_init'] = True
            print("✅ TOTP initialization: OK")
        else:
            auth_results['totp_init'] = False
            print("⚠️ TOTP initialization: NOT CONFIGURED")
        
        # Test authentication status
        status = auth_manager.get_authentication_status()
        auth_results['status_check'] = True
        print("✅ Authentication status check: OK")
        print(f"   Status: {status}")
        
        # Test Playwright availability
        if hasattr(auth_manager, 'PLAYWRIGHT_AVAILABLE'):
            auth_results['playwright_available'] = auth_manager.PLAYWRIGHT_AVAILABLE
            print(f"✅ Playwright availability: {auth_manager.PLAYWRIGHT_AVAILABLE}")
        else:
            auth_results['playwright_available'] = False
            print("⚠️ Playwright availability: UNKNOWN")
        
    except Exception as e:
        auth_results['initialization'] = False
        print(f"❌ Auth Manager test: FAILED - {e}")
        print(f"   Error details: {str(e)}")
    
    return auth_results

async def test_bot_orchestrator():
    """Test Bot Orchestrator initialization and basic functionality"""
    print("\n🤖 Testing Bot Orchestrator...")
    
    bot_results = {}
    
    try:
        # Import and initialize
        from bot_orchestrator import EliaParkingBot
        
        # Test initialization
        bot = EliaParkingBot()
        bot_results['initialization'] = True
        print("✅ Bot Orchestrator initialization: OK")
        
        # Test auth manager integration
        if hasattr(bot, 'auth_manager') and bot.auth_manager:
            bot_results['auth_manager_integration'] = True
            print("✅ Auth Manager integration: OK")
        else:
            bot_results['auth_manager_integration'] = False
            print("❌ Auth Manager integration: FAILED")
        
        # Test cloud auth manager integration
        if hasattr(bot, 'cloud_auth_manager'):
            bot_results['cloud_auth_integration'] = True
            print("✅ Cloud Auth Manager integration: OK")
        else:
            bot_results['cloud_auth_integration'] = False
            print("⚠️ Cloud Auth Manager integration: NOT AVAILABLE")
        
        # Test browser automation integration
        if hasattr(bot, 'browser_automation') and bot.browser_automation:
            bot_results['browser_automation_integration'] = True
            print("✅ Browser Automation integration: OK")
        else:
            bot_results['browser_automation_integration'] = False
            print("❌ Browser Automation integration: FAILED")
        
        # Test spot detector integration
        if hasattr(bot, 'spot_detector') and bot.spot_detector:
            bot_results['spot_detector_integration'] = True
            print("✅ Spot Detector integration: OK")
        else:
            bot_results['spot_detector_integration'] = False
            print("❌ Spot Detector integration: FAILED")
        
    except Exception as e:
        bot_results['initialization'] = False
        print(f"❌ Bot Orchestrator test: FAILED - {e}")
        print(f"   Error details: {str(e)}")
    
    return bot_results

async def test_scheduler():
    """Test Scheduler initialization and basic functionality"""
    print("\n⏰ Testing Scheduler...")
    
    scheduler_results = {}
    
    try:
        # Import and initialize
        from scheduler import ReservationScheduler
        
        # Test initialization
        scheduler = ReservationScheduler({})
        scheduler_results['initialization'] = True
        print("✅ Scheduler initialization: OK")
        
        # Test cloud auth integration
        if hasattr(scheduler, 'cloud_auth_available'):
            scheduler_results['cloud_auth_integration'] = True
            print(f"✅ Cloud auth integration: {scheduler.cloud_auth_available}")
        else:
            scheduler_results['cloud_auth_integration'] = False
            print("❌ Cloud auth integration: FAILED")
        
    except Exception as e:
        scheduler_results['initialization'] = False
        print(f"❌ Scheduler test: FAILED - {e}")
        print(f"   Error details: {str(e)}")
    
    return scheduler_results

def generate_debug_report(results):
    """Generate comprehensive debug report"""
    print("\n📊 Generating Debug Report...")
    
    report = {
        "debug_session": "MFA Authentication and Reservation Flow Debug",
        "timestamp": datetime.now().isoformat(),
        "results": results,
        "overall_status": "PASS" if all(all(test_results.values()) for test_results in results.values()) else "FAIL",
        "summary": {
            "total_categories": len(results),
            "passed_categories": sum(1 for test_results in results.values() if all(test_results.values())),
            "failed_categories": sum(1 for test_results in results.values() if not all(test_results.values()))
        }
    }
    
    # Save report
    with open("debug_report.json", 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"📋 Debug report saved to: debug_report.json")
    
    # Print summary
    if report["overall_status"] == "PASS":
        print("🎉 Overall Debug Status: PASSED")
        print("✅ All systems ready for MFA and reservation testing")
    else:
        print("❌ Overall Debug Status: FAILED")
        print("⚠️ Some issues need to be resolved before testing")
    
    return report

async def main():
    """Main debug function"""
    print("🚀 Starting Comprehensive Debug Session...")
    print("=" * 60)
    
    results = {}
    
    # Run all tests
    results["imports"] = test_imports()
    results["configuration"] = test_configuration()
    results["authentication_manager"] = await test_authentication_manager()
    results["bot_orchestrator"] = await test_bot_orchestrator()
    results["scheduler"] = await test_scheduler()
    
    # Generate report
    report = generate_debug_report(results)
    
    # Provide next steps
    print("\n🎯 Next Steps:")
    if report["overall_status"] == "PASS":
        print("1. ✅ Import issues resolved - Ready for GitHub push")
        print("2. 🧪 Run MFA authentication test: python test_cloud_auth_integration.py")
        print("3. 🎯 Run reservation flow test: python test_end_to_end_reservation.py")
        print("4. 🚀 Deploy to GitHub Actions for cloud testing")
    else:
        print("1. 🔧 Fix remaining import/configuration issues")
        print("2. 🧪 Re-run this debug script to validate fixes")
        print("3. 🚀 Proceed with testing once all issues resolved")
    
    return 0 if report["overall_status"] == "PASS" else 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)

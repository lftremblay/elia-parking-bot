#!/usr/bin/env python3
"""
Quick validation script to test the import fix
"""

def test_auth_manager_import():
    """Test that auth_manager can be imported without errors"""
    try:
        from auth_manager import AuthenticationManager
        print("✅ SUCCESS: auth_manager.AuthenticationManager imported without errors")
        
        # Test instantiation
        auth_mgr = AuthenticationManager()
        print("✅ SUCCESS: AuthenticationManager instantiated without errors")
        
        # Test that Page type is available
        if hasattr(auth_mgr, 'PLAYWRIGHT_AVAILABLE'):
            print(f"✅ SUCCESS: Playwright availability check: {auth_mgr.PLAYWRIGHT_AVAILABLE}")
        
        return True
    except Exception as e:
        print(f"❌ FAILED: {e}")
        return False

def test_bot_orchestrator_import():
    """Test that bot_orchestrator can be imported without errors"""
    try:
        from bot_orchestrator import EliaParkingBot
        print("✅ SUCCESS: bot_orchestrator.EliaParkingBot imported without errors")
        return True
    except Exception as e:
        print(f"❌ FAILED: {e}")
        return False

if __name__ == "__main__":
    print("🔍 Validating Import Fix...")
    print("=" * 50)
    
    auth_success = test_auth_manager_import()
    bot_success = test_bot_orchestrator_import()
    
    if auth_success and bot_success:
        print("\n🎉 ALL IMPORTS FIXED SUCCESSFULLY!")
        print("✅ Ready for GitHub push and cloud testing")
    else:
        print("\n❌ IMPORT ISSUES STILL EXIST")
        print("🔧 Further debugging needed")

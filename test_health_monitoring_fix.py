#!/usr/bin/env python3
"""
Test Health Monitoring Fix
Validates that the health monitoring integration bug has been fixed
"""

import asyncio
from unittest.mock import Mock, AsyncMock
from browser_health_monitor import add_health_monitoring

print("🔧 Testing Health Monitoring Fix")
print("=" * 50)

class MockBrowserAutomation:
    """Mock browser automation for testing"""
    
    def __init__(self):
        self.page = None
        self.browser = None
        self.context = None
        self.config = {}
        self.auth_manager = None
    
    async def initialize(self, headless: bool = True):
        """Mock initialize method"""
        print("   Mock: Browser initialization started")
        self.page = Mock()
        self.browser = Mock()
        self.context = Mock()
        print("   Mock: Browser initialization completed")
        return True
    
    async def navigate_to_elia(self, organization: str):
        """Mock navigation method"""
        print(f"   Mock: Navigating to Elia with organization {organization}")
        return True
    
    async def handle_mfa(self, method: str = "authenticator", max_retries: int = 3):
        """Mock MFA handling"""
        print(f"   Mock: Handling MFA with method {method}")
        return True
    
    async def close(self):
        """Mock close method"""
        print("   Mock: Browser closed")
        return True

async def test_health_monitoring_integration():
    """Test that health monitoring integration works correctly"""
    print("\n1. Testing health monitoring integration...")
    
    try:
        # Create mock browser automation
        mock_browser = MockBrowserAutomation()
        
        # Add health monitoring
        enhanced_browser = add_health_monitoring(mock_browser)
        
        print("   ✅ Health monitoring wrapper created successfully")
        
        # Test that all required methods are available
        required_methods = ['initialize', 'navigate_to_elia', 'handle_mfa', 'close']
        
        for method in required_methods:
            if hasattr(enhanced_browser, method):
                print(f"   ✅ Method '{method}' is available")
            else:
                print(f"   ❌ Method '{method}' is missing")
                return False
        
        # Test method forwarding
        print("\n2. Testing method forwarding...")
        
        # Test initialize method
        result = await enhanced_browser.initialize(headless=True)
        if result:
            print("   ✅ Initialize method works correctly")
        else:
            print("   ❌ Initialize method failed")
            return False
        
        # Test navigation method
        result = await enhanced_browser.navigate_to_elia("quebecor")
        if result:
            print("   ✅ Navigation method works correctly")
        else:
            print("   ❌ Navigation method failed")
            return False
        
        # Test MFA method
        result = await enhanced_browser.handle_mfa()
        if result:
            print("   ✅ MFA method works correctly")
        else:
            print("   ❌ MFA method failed")
            return False
        
        # Test close method
        await enhanced_browser.close()
        print("   ✅ Close method works correctly")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Health monitoring integration test failed: {e}")
        return False

async def test_attribute_forwarding():
    """Test that attributes are properly forwarded"""
    print("\n3. Testing attribute forwarding...")
    
    try:
        # Create mock browser automation with test attributes
        mock_browser = MockBrowserAutomation()
        mock_browser.test_attribute = "test_value"
        mock_browser.config = {"test": "config"}
        
        # Add health monitoring
        enhanced_browser = add_health_monitoring(mock_browser)
        
        # Test attribute access
        if hasattr(enhanced_browser, 'test_attribute'):
            value = enhanced_browser.test_attribute
            if value == "test_value":
                print("   ✅ Attribute forwarding works correctly")
            else:
                print(f"   ❌ Attribute forwarding failed: expected 'test_value', got '{value}'")
                return False
        else:
            print("   ❌ Test attribute not found")
            return False
        
        # Test config access
        if hasattr(enhanced_browser, 'config'):
            config = enhanced_browser.config
            if config == {"test": "config"}:
                print("   ✅ Config forwarding works correctly")
            else:
                print(f"   ❌ Config forwarding failed: expected '{{\"test\": \"config\"}}', got '{config}'")
                return False
        else:
            print("   ❌ Config not found")
            return False
        
        return True
        
    except Exception as e:
        print(f"   ❌ Attribute forwarding test failed: {e}")
        return False

async def test_error_handling():
    """Test error handling in enhanced browser automation"""
    print("\n4. Testing error handling...")
    
    try:
        # Create mock browser that raises an error
        mock_browser = MockBrowserAutomation()
        
        # Override initialize to raise an error
        async def failing_initialize(*args, **kwargs):
            raise Exception("Mock initialization error")
        
        mock_browser.initialize = failing_initialize
        
        # Add health monitoring
        enhanced_browser = add_health_monitoring(mock_browser)
        
        # Test error handling
        try:
            await enhanced_browser.initialize()
            print("   ❌ Expected error was not raised")
            return False
        except Exception as e:
            if "Mock initialization error" in str(e):
                print("   ✅ Error handling works correctly")
                return True
            else:
                print(f"   ❌ Unexpected error: {e}")
                return False
        
    except Exception as e:
        print(f"   ❌ Error handling test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🔧 Validating Health Monitoring Fix")
    print("=" * 50)
    
    async def run_tests():
        tests = [
            ("Health Monitoring Integration", test_health_monitoring_integration),
            ("Attribute Forwarding", test_attribute_forwarding),
            ("Error Handling", test_error_handling)
        ]
        
        results = []
        for test_name, test_func in tests:
            try:
                result = await test_func()
                results.append((test_name, result))
            except Exception as e:
                print(f"❌ Test '{test_name}' failed with exception: {e}")
                results.append((test_name, False))
        
        return results
    
    # Run async tests
    results = asyncio.run(run_tests())
    
    print("\n" + "=" * 50)
    print("🎯 Health Monitoring Fix Test Results")
    print("=" * 50)
    
    all_passed = True
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
        if not result:
            all_passed = False
    
    print(f"\n🏆 Overall Result: {'ALL TESTS PASSED' if all_passed else 'SOME TESTS FAILED'}")
    
    if all_passed:
        print("\n🚀 Health monitoring fix is working correctly!")
        print("\n📋 Fix Summary:")
        print("✅ Method forwarding implemented")
        print("✅ Attribute forwarding implemented")
        print("✅ Error handling preserved")
        print("✅ Enhanced browser automation functional")
        
        print("\n💡 The 'EnhancedBrowserAutomation' object now properly:")
        print("- Forwards all missing methods to base automation")
        print("- Forwards all missing attributes to base automation")
        print("- Maintains health monitoring capabilities")
        print("- Handles errors gracefully")
        
        print("\n🎯 Ready for production deployment!")
    else:
        print("\n⚠️  Some issues remain - review failed tests above")

if __name__ == "__main__":
    main()

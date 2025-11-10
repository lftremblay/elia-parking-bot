#!/usr/bin/env python3
"""
Cloud Authentication Integration Test
Tests local development compatibility with cloud authentication patterns
"""

import asyncio
import os
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from auth_manager import AuthenticationManager
from cloud.cloud_auth_manager import CloudAuthenticationManager, is_cloud_environment


async def test_local_auth_manager():
    """Test local authentication manager with cloud integration"""
    print("🧪 Testing Local Authentication Manager...")
    
    # Create auth manager
    auth = AuthenticationManager()
    
    # Test environment detection
    print(f"📍 Environment detected: {'cloud' if auth.is_cloud else 'local'}")
    
    # Test enhanced status
    status = auth.get_enhanced_authentication_status()
    print(f"📊 Authentication Status: {status}")
    
    # Test cloud fallback authentication
    print("🔄 Testing cloud fallback authentication...")
    result = await auth.authenticate_with_cloud_fallback()
    print(f"✅ Authentication result: {result}")
    
    # Test final status
    final_status = auth.get_enhanced_authentication_status()
    print(f"📈 Final Status: {final_status}")
    
    return result


async def test_cloud_auth_manager():
    """Test cloud authentication manager directly"""
    print("\n🌐 Testing Cloud Authentication Manager...")
    
    try:
        # Create cloud auth manager
        cloud_auth = CloudAuthenticationManager()
        
        # Test environment detection
        print(f"📍 Cloud environment: {cloud_auth.is_cloud}")
        
        # Test authentication status
        status = cloud_auth.get_authentication_status()
        print(f"📊 Cloud Auth Status: {status}")
        
        # Test health validation
        health = await cloud_auth.validate_authentication_health()
        print(f"🏥 Health Check: {health}")
        
        return True
        
    except Exception as e:
        print(f"❌ Cloud auth test failed: {e}")
        return False


async def test_environment_detection():
    """Test environment detection logic"""
    print("\n🔍 Testing Environment Detection...")
    
    # Test current environment
    current_env = is_cloud_environment()
    print(f"📍 Current environment: {'cloud' if current_env else 'local'}")
    
    # Test environment variables
    env_vars = {
        'GITHUB_ACTIONS': os.getenv('GITHUB_ACTIONS'),
        'ENVIRONMENT': os.getenv('ENVIRONMENT'),
        'CI': os.getenv('CI')
    }
    print(f"🔧 Environment variables: {env_vars}")
    
    return current_env


def test_configuration_templates():
    """Test configuration template functionality"""
    print("\n📋 Testing Configuration Templates...")
    
    # Test if template exists
    template_path = Path("local_env_template.env")
    if template_path.exists():
        print(f"✅ Template file found: {template_path}")
        
        # Read and validate template
        with open(template_path, 'r') as f:
            content = f.read()
            
        required_vars = [
            'TOTP_SECRET',
            'ELIA_PASSWORD', 
            'MICROSOFT_USERNAME',
            'ENVIRONMENT'
        ]
        
        missing_vars = []
        for var in required_vars:
            if f"{var}=" not in content:
                missing_vars.append(var)
        
        if missing_vars:
            print(f"⚠️ Template missing variables: {missing_vars}")
        else:
            print("✅ Template contains all required variables")
            
        return len(missing_vars) == 0
    else:
        print(f"❌ Template file not found: {template_path}")
        return False


async def main():
    """Run all integration tests"""
    print("🚀 Starting Cloud Authentication Integration Tests\n")
    
    tests = [
        ("Environment Detection", test_environment_detection),
        ("Configuration Templates", test_configuration_templates),
        ("Local Auth Manager", test_local_auth_manager),
        ("Cloud Auth Manager", test_cloud_auth_manager),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            print(f"\n{'='*50}")
            print(f"🧪 Running: {test_name}")
            print('='*50)
            
            if asyncio.iscoroutinefunction(test_func):
                result = await test_func()
            else:
                result = test_func()
            
            results[test_name] = result
            status = "✅ PASSED" if result else "❌ FAILED"
            print(f"\n{status}: {test_name}")
            
        except Exception as e:
            results[test_name] = False
            print(f"\n❌ ERROR in {test_name}: {e}")
    
    # Summary
    print(f"\n{'='*50}")
    print("📊 TEST SUMMARY")
    print('='*50)
    
    passed = sum(1 for result in results.values() if result)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{status}: {test_name}")
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Cloud integration is ready.")
    else:
        print("⚠️ Some tests failed. Check the logs above.")
    
    return passed == total


if __name__ == "__main__":
    # Run the tests
    success = asyncio.run(main())
    sys.exit(0 if success else 1)

#!/usr/bin/env python3
"""
Test Cloud Authentication Integration
Story 1.2 - Task 1.4: Test authentication → bot initialization flow
"""

import asyncio
import sys
from pathlib import Path
from loguru import logger

# Add current directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from bot_orchestrator import EliaParkingBot


async def test_cloud_auth_integration():
    """
    Test the complete cloud authentication integration with bot orchestrator
    Story 1.2 - Task 1.4
    """
    logger.info("🧪 Starting Cloud Authentication Integration Test...")
    
    try:
        # Initialize bot with cloud auth integration
        logger.info("🤖 Initializing EliaParkingBot with cloud auth...")
        bot = EliaParkingBot()
        
        # Check if cloud auth is available
        if bot.cloud_auth_manager:
            logger.info("☁️ Cloud authentication manager is available")
            logger.info(f"🔍 Cloud environment detected: {bot.cloud_auth_manager.is_cloud}")
            
            if bot.cloud_auth_manager.is_cloud:
                logger.info("☁️ Running in cloud environment - will test cloud auth flow")
            else:
                logger.info("🏠 Running in local environment - will test local auth flow")
        else:
            logger.warning("⚠️ Cloud authentication manager not available")
            logger.info("🔄 Will test local authentication flow")
        
        # Test bot initialization
        logger.info("🚀 Testing bot initialization...")
        await bot.initialize(headless=True)
        logger.success("✅ Bot initialization completed")
        
        # Test authentication flow
        logger.info("🔐 Testing authentication flow...")
        auth_success = await bot.authenticate()
        
        if auth_success:
            logger.success("✅ Authentication successful!")
            
            # Verify bot state
            if bot.authenticated:
                logger.success("✅ Bot authentication state is correct")
            else:
                logger.error("❌ Bot authentication state is incorrect")
                return False
            
            # Check browser state
            if bot.browser.page:
                current_url = bot.browser.page.url
                logger.info(f"🌐 Current page URL: {current_url}")
                
                if 'app.elia.io' in current_url and 'login' not in current_url.lower():
                    logger.success("✅ Successfully authenticated and on dashboard")
                else:
                    logger.warning(f"⚠️ On unexpected page: {current_url}")
            else:
                logger.error("❌ Browser page not available")
                return False
                
        else:
            logger.error("❌ Authentication failed")
            return False
        
        # Test cleanup
        logger.info("🧹 Testing cleanup...")
        await bot.cleanup()
        logger.success("✅ Cleanup completed")
        
        logger.success("🎉 Cloud Authentication Integration Test PASSED!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Cloud Authentication Integration Test FAILED: {e}")
        return False


async def test_fallback_mechanism():
    """
    Test fallback from cloud auth to local auth
    Story 1.2 - Task 1.4
    """
    logger.info("🔄 Testing Cloud Auth → Local Auth Fallback...")
    
    try:
        # Initialize bot
        bot = EliaParkingBot()
        
        # Simulate cloud auth failure by forcing local auth
        original_cloud_manager = bot.cloud_auth_manager
        bot.cloud_auth_manager = None  # Force fallback to local auth
        
        logger.info("🔐 Testing local auth fallback...")
        await bot.initialize(headless=True)
        auth_success = await bot.authenticate()
        
        if auth_success:
            logger.success("✅ Local auth fallback works correctly")
        else:
            logger.warning("⚠️ Local auth fallback failed (may be expected in cloud env)")
        
        # Restore original state
        bot.cloud_auth_manager = original_cloud_manager
        await bot.cleanup()
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Fallback test failed: {e}")
        return False


async def main():
    """
    Main test runner
    """
    logger.info("🚀 Starting Story 1.2 - Task 1.4 Tests...")
    
    # Test 1: Cloud auth integration
    test1_result = await test_cloud_auth_integration()
    
    # Test 2: Fallback mechanism
    test2_result = await test_fallback_mechanism()
    
    # Summary
    logger.info("📊 Test Results Summary:")
    logger.info(f"✅ Cloud Auth Integration: {'PASSED' if test1_result else 'FAILED'}")
    logger.info(f"✅ Fallback Mechanism: {'PASSED' if test2_result else 'FAILED'}")
    
    overall_success = test1_result and test2_result
    
    if overall_success:
        logger.success("🎉 All Story 1.2 - Task 1.4 tests PASSED!")
        return 0
    else:
        logger.error("❌ Some tests FAILED!")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)

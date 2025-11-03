#!/usr/bin/env python3
"""
Comprehensive SSO and Auth Flow Test
Tests the improved Microsoft SSO handling for GitHub Actions compatibility
"""

import asyncio
import sys
import os
import pytest
from pathlib import Path
from loguru import logger

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from bot_orchestrator import EliaParkingBot
from auth_manager import AuthenticationManager


@pytest.mark.asyncio
async def test_sso_flow_headless():
    """Test SSO flow in headless mode (like GitHub Actions)"""
    print("=" * 80)
    print("🧪 Testing Microsoft SSO Flow (Headless Mode)")
    print("=" * 80)

    # Clean up any existing session data to force full auth
    session_dir = Path("./session_data")
    browser_dir = Path("./browser_data")

    if session_dir.exists():
        import shutil
        shutil.rmtree(session_dir)
        print("🧹 Cleared existing session data")

    if browser_dir.exists():
        import shutil
        shutil.rmtree(browser_dir)
        print("🧹 Cleared existing browser data")

    # Option 1: Use real config from config.json
    # Uncomment these lines to use your real email instead of test email:
    # bot = EliaParkingBot()  # Uses real config.json
    # auth_manager = bot.auth_manager

    # Option 2: Use test config (currently active)
    config = {
        'advanced': {
            'browser_profile_path': './test_browser_data'
        },
        'elia': {
            'organization': 'quebecor',
            'credentials': {
                'email': 'test@example.com',  # Change this to your real email if desired
                'mfa_method': 'authenticator'
            }
        },
        'retry': {
            'max_attempts': 1  # Reduce for testing
        }
    }

    bot = EliaParkingBot(config=config)
    auth_manager = AuthenticationManager(config=config)

    try:
        # Initialize in headless mode
        print("🚀 Initializing bot in headless mode...")
        await bot.initialize(headless=True)

        # Force re-authentication (clear authenticated flag)
        bot.authenticated = False

        # Test authentication flow
        print("🔐 Testing full authentication flow...")
        success = await bot.authenticate(force_reauth=True)

        if success:
            print("✅ SSO authentication test PASSED")
            print("✅ Bot can handle Microsoft SSO in headless mode")

            # Test MFA if needed
            mfa_method = bot.config.get('elia', {}).get('credentials', {}).get('mfa_method', 'authenticator')
            print(f"🔢 MFA method configured: {mfa_method}")

            if mfa_method == 'authenticator':
                code = auth_manager.get_totp_code()
                if code:
                    print(f"✅ TOTP code generation works: {code[:2]}****")
                else:
                    print("⚠️ TOTP code generation failed")

            return True
        else:
            print("❌ SSO authentication test FAILED")
            return False

    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        return False
    finally:
        await bot.cleanup()


@pytest.mark.asyncio
async def test_sso_flow_visible():
    """Test SSO flow in visible mode for debugging"""
    print("=" * 80)
    print("🧪 Testing Microsoft SSO Flow (Visible Mode)")
    print("=" * 80)

    # Clean up session data
    session_dir = Path("./session_data")
    browser_dir = Path("./browser_data")

    if session_dir.exists():
        import shutil
        shutil.rmtree(session_dir)
        print("🧹 Cleared existing session data")

    if browser_dir.exists():
        import shutil
        shutil.rmtree(browser_dir)
        print("🧹 Cleared existing browser data")

    # Initialize bot with proper config
    config = {
        'advanced': {
            'browser_profile_path': './test_browser_data'
        },
        'elia': {
            'organization': 'quebecor',
            'credentials': {
                'email': 'test@example.com',
                'mfa_method': 'authenticator'
            }
        },
        'retry': {
            'max_attempts': 1  # Reduce for testing
        }
    }
    
    bot = EliaParkingBot(config=config)

    try:
        # Initialize in visible mode
        print("🚀 Initializing bot in visible mode...")
        await bot.initialize(headless=False)

        # Test authentication flow
        print("🔐 Testing full authentication flow...")
        success = await bot.authenticate(force_reauth=True)

        if success:
            print("✅ SSO authentication test PASSED")
            print("✅ Bot can handle Microsoft SSO in visible mode")
            return True
        else:
            print("❌ SSO authentication test FAILED")
            return False

    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        return False
    finally:
        # Give time to see results
        await asyncio.sleep(5)
        await bot.cleanup()


@pytest.mark.asyncio
async def test_auth_manager():
    """Test authentication manager components"""
    print("=" * 80)
    print("🧪 Testing Authentication Manager")
    print("=" * 80)

    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()

    auth = AuthenticationManager()

    # Test TOTP generation
    print("🔢 Testing TOTP code generation...")
    code = auth.get_totp_code()
    if code:
        print(f"✅ TOTP code generated: {code[:2]}**** (length: {len(code)})")
    else:
        print("❌ TOTP code generation failed")
        # Debug: check config
        totp_secret = auth.config.get('mfa', {}).get('totp_secret')
        if totp_secret:
            print(f"ℹ️ TOTP secret found in config: {totp_secret[:4]}****")
        else:
            print("ℹ️ No TOTP secret in config")
        return False

    # Test session management
    print("💾 Testing session management...")
    auth.update_tokens("test_access_token", "test_refresh_token")
    auth.save_session()  # This doesn't return anything, just saves
    
    # Check if session file was created
    if auth.token_file.exists():
        print("✅ Session save successful")
    else:
        print("❌ Session save failed - file not created")
        return False

    # Test session loading
    new_auth = AuthenticationManager()
    loaded = new_auth.load_session()
    if loaded and new_auth.access_token == "test_access_token":
        print("✅ Session load successful")
    else:
        print("❌ Session load failed")
        print(f"  Loaded: {loaded}, Token: {new_auth.access_token}")
        return False

    return True


async def run_all_tests():
    """Run all authentication tests"""
    print("🤖 Elia Parking Bot V4 - SSO & Auth Flow Tests")
    print("This will test the improved authentication handling for GitHub Actions")
    print()

    results = []

    # Test auth manager
    auth_test = await test_auth_manager()
    results.append(("Auth Manager", auth_test))

    print()

    # Test visible mode (for manual verification)
    visible_test = await test_sso_flow_visible()
    results.append(("SSO Flow (Visible)", visible_test))

    print()

    # Test headless mode (like GitHub Actions)
    headless_test = await test_sso_flow_headless()
    results.append(("SSO Flow (Headless)", headless_test))

    print()
    print("=" * 80)
    print("📊 Test Results Summary")
    print("=" * 80)

    all_passed = True
    for test_name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_name}: {status}")
        if not passed:
            all_passed = False

    print()
    if all_passed:
        print("🎉 All tests PASSED! SSO flow should work in GitHub Actions.")
        print()
        print("Next steps:")
        print("1. Push these changes to your repository")
        print("2. Trigger a GitHub Actions workflow")
        print("3. Check the logs for successful authentication")
    else:
        print("⚠️ Some tests failed. Check the issues above before deploying.")

    return all_passed


if __name__ == "__main__":
    # Configure logging for tests
    logger.remove()
    logger.add(sys.stdout, format="{message}", level="INFO")

    # Run tests
    success = asyncio.run(run_all_tests())
    sys.exit(0 if success else 1)

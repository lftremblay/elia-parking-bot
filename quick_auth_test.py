#!/usr/bin/env python3
"""
Quick authentication test with real credentials
"""
import asyncio
import sys
import pytest
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from bot_orchestrator import EliaParkingBot

@pytest.mark.asyncio
async def test_real_auth():
    """Test authentication with real credentials"""
    print("🧪 Testing authentication with real credentials...")
    print("Email: louis-felix.tremblay@videotron.com")

    # Use test config instead of requiring config.json file
    config = {
        'elia': {
            'organization': 'quebecor',
            'credentials': {
                'email': 'test@example.com',  # Test email
                'mfa_method': 'authenticator'
            }
        },
        'advanced': {
            'browser_profile_path': './test_browser_data'
        },
        'retry': {
            'max_attempts': 1  # Reduce for testing
        }
    }

    # Initialize bot with test config
    bot = EliaParkingBot(config=config)

    try:
        # Initialize browser
        await bot.initialize(headless=False)  # Visible for debugging

        # Try authentication
        print("🔐 Attempting authentication...")
        success = await bot.authenticate(force_reauth=True)

        if success:
            print("✅ Authentication successful!")
            await asyncio.sleep(5)  # Let user see the result
        else:
            print("❌ Authentication failed")

    except Exception as e:
        print(f"❌ Test failed: {e}")
    finally:
        await bot.cleanup()

if __name__ == "__main__":
    asyncio.run(test_real_auth())

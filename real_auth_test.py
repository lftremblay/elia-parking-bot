#!/usr/bin/env python3
"""
Test authentication with REAL credentials from config.json
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
    """Test authentication with real credentials from config.json"""
    print("🔐 Testing authentication with REAL credentials from config.json")
    print("This will use your actual email: louis-felix.tremblay@videotron.com")

    # Initialize bot with real config
    bot = EliaParkingBot()  # Uses config.json by default

    try:
        # Initialize browser in visible mode for debugging
        print("🚀 Initializing browser (visible mode)...")
        await bot.initialize(headless=False)

        # Force fresh authentication
        print("🔄 Forcing fresh authentication...")
        success = await bot.authenticate(force_reauth=True)

        if success:
            print("✅ Authentication successful!")
            print("🎉 Your real credentials work with the improved SAML handling!")
            await asyncio.sleep(5)  # Let user see the dashboard
        else:
            print("❌ Authentication failed")
            print("Check the browser for any error messages")

    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

    finally:
        print("🧹 Cleaning up...")
        await bot.cleanup()

if __name__ == "__main__":
    asyncio.run(test_real_auth())

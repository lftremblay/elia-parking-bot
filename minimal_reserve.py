#!/usr/bin/env python3
"""
Minimal reservation script - bypasses dependency issues
"""
import asyncio
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def minimal_reservation():
    """Run minimal reservation with basic logging"""
    print("🚀 Starting minimal parking reservation...")

    try:
        # Import what we can
        from bot_orchestrator import EliaParkingBot

        # Create bot with default config
        bot = EliaParkingBot()

        print("🔐 Initializing bot...")
        await bot.initialize(headless=True)  # Run headless for automation

        print("🎯 Attempting to reserve regular spot...")
        success = await bot.reserve_spot("regular")

        if success:
            print("✅ Reservation successful!")
            return True
        else:
            print("❌ Reservation failed")
            return False

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        try:
            await bot.cleanup()
            print("🧹 Cleanup complete")
        except:
            pass

if __name__ == "__main__":
    result = asyncio.run(minimal_reservation())
    sys.exit(0 if result else 1)

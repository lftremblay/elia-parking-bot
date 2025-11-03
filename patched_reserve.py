#!/usr/bin/env python3
"""
Minimal reservation script with logging patch
"""
import asyncio
import sys
import os
import logging

# Setup basic logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s'
)
logger = logging.getLogger(__name__)

# Monkey patch loguru imports
import sys
from types import ModuleType

class FakeLoguru:
    def __init__(self):
        self.logger = logging.getLogger('elia_bot')

    def info(self, msg, *args, **kwargs):
        self.logger.info(msg, *args, **kwargs)

    def error(self, msg, *args, **kwargs):
        self.logger.error(msg, *args, **kwargs)

    def warning(self, msg, *args, **kwargs):
        self.logger.warning(msg, *args, **kwargs)

    def success(self, msg, *args, **kwargs):
        self.logger.info(f"✅ {msg}", *args, **kwargs)

    def debug(self, msg, *args, **kwargs):
        self.logger.debug(msg, *args, **kwargs)

    def remove(self):
        pass

    def add(self, *args, **kwargs):
        pass

# Create fake loguru module
fake_loguru = ModuleType('loguru')
fake_loguru.logger = FakeLoguru()
sys.modules['loguru'] = fake_loguru

# Also patch other missing imports
class FakeDotenv:
    def load_dotenv(self):
        pass

fake_dotenv = ModuleType('dotenv')
fake_dotenv.load_dotenv = lambda: None
sys.modules['dotenv'] = fake_dotenv

class FakePyOTP:
    class TOTP:
        def __init__(self, secret):
            self.secret = secret

        def now(self):
            # Return a dummy 6-digit code for testing
            return "123456"

fake_pyotp = ModuleType('pyotp')
fake_pyotp.TOTP = FakePyOTP.TOTP
sys.modules['pyotp'] = fake_pyotp

class FakeCryptography:
    class Fernet:
        def __init__(self, key):
            pass
        def encrypt(self, data):
            return data
        def decrypt(self, data):
            return data
        @staticmethod
        def generate_key():
            return b'dummy_key_for_testing'

fake_crypto = ModuleType('cryptography.fernet')
fake_crypto.Fernet = FakeCryptography.Fernet
sys.modules['cryptography.fernet'] = fake_crypto
sys.modules['cryptography'] = ModuleType('cryptography')

# Patch opencv
fake_cv2 = ModuleType('cv2')
sys.modules['cv2'] = fake_cv2

# Patch other potential missing modules
fake_pil = ModuleType('PIL')
fake_pil.Image = type('Image', (), {})  # Dummy class
sys.modules['PIL'] = fake_pil

for mod in ['pytesseract', 'discord_webhook', 'apscheduler', 'tenacity']:
    sys.modules[mod] = ModuleType(mod)

# Comprehensive numpy patch
fake_numpy = ModuleType('numpy')
fake_numpy.ndarray = type('ndarray', (), {})  # Dummy class
fake_numpy.uint8 = type('uint8', (), {})
fake_numpy.zeros = lambda *args, **kwargs: None
fake_numpy.array = lambda *args, **kwargs: None
fake_numpy.where = lambda *args, **kwargs: ([],)
sys.modules['numpy'] = fake_numpy

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def run_reservation():
    """Run reservation with patched imports"""
    print("🚀 Starting parking reservation with dependency patches...")

    try:
        # Import the bot
        from bot_orchestrator import EliaParkingBot

        # Create bot
        bot = EliaParkingBot()

        print("🔐 Initializing bot...")
        await bot.initialize(headless=True)

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
        except Exception as e:
            print(f"⚠️ Cleanup error: {e}")

if __name__ == "__main__":
    result = asyncio.run(run_reservation())
    sys.exit(0 if result else 1)

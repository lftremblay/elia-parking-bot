"""
Elia Parking Bot V4 - Main Entry Point
Enterprise-grade automated parking reservation system
"""

import asyncio
import sys
import argparse
from pathlib import Path
from loguru import logger
from dotenv import load_dotenv

from bot_orchestrator import EliaParkingBot
from scheduler import ReservationScheduler
from auth_manager import AuthenticationManager


def setup_logging(log_level: str = "INFO"):
    """Configure logging with rotation and formatting"""
    logger.remove()  # Remove default handler
    
    # Console output with colors
    logger.add(
        sys.stderr,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>",
        level=log_level,
        colorize=True
    )
    
    # File output with rotation
    log_dir = Path("./logs")
    log_dir.mkdir(exist_ok=True)
    
    logger.add(
        log_dir / "elia_bot_{time:YYYY-MM-DD}.log",
        rotation="00:00",
        retention="30 days",
        compression="zip",
        level="DEBUG",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} | {message}"
    )
    
    logger.info("📝 Logging configured")


async def run_reservation(spot_type: str, config_path: str = "config.json"):
    """Run a single reservation attempt"""
    logger.info(f"🚀 Starting {spot_type} spot reservation...")
    
    bot = EliaParkingBot(config_path)
    
    try:
        await bot.initialize(headless=True)
        success = await bot.reserve_spot(spot_type)
        
        if success:
            logger.success(f"✅ {spot_type.title()} spot reservation successful!")
            return 0
        else:
            logger.error(f"❌ {spot_type.title()} spot reservation failed")
            return 1
            
    except Exception as e:
        logger.error(f"❌ Critical error during reservation: {e}")
        return 1
    finally:
        await bot.cleanup()


async def run_daemon_mode(config_path: str = "config.json"):
    """Run bot in daemon mode with scheduler"""
    logger.info("🤖 Starting Elia Parking Bot in daemon mode...")
    
    import json
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    # Initialize scheduler
    scheduler = ReservationScheduler(config)
    
    # Create reservation callback
    async def reservation_callback(spot_type: str):
        logger.info(f"⏰ Scheduled reservation triggered: {spot_type}")
        await run_reservation(spot_type, config_path)
    
    # Setup schedules
    scheduler.setup_schedules(reservation_callback)
    
    # Show next runs
    next_runs = scheduler.get_next_runs()
    logger.info("📅 Scheduled runs:")
    for spot_type, next_run in next_runs.items():
        logger.info(f"   {spot_type.title()}: {next_run.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Run forever
    try:
        scheduler.run_forever()
    except KeyboardInterrupt:
        logger.info("⚠️ Daemon stopped by user")
        scheduler.stop()


async def test_authentication(config_path: str = "config.json"):
    """Test authentication flow"""
    logger.info("🧪 Testing authentication...")
    
    bot = EliaParkingBot(config_path)
    await bot.test_authentication()


async def test_spot_detection(config_path: str = "config.json", spot_type: str = "regular"):
    """Test spot detection without reservation"""
    logger.info(f"🧪 Testing {spot_type} spot detection...")
    
    bot = EliaParkingBot(config_path)
    
    try:
        await bot.initialize(headless=False)
        
        if not bot.authenticated:
            await bot.authenticate()
        
        # Navigate and find spots
        logger.info("🔍 Searching for spots...")
        available_spots = await bot.browser.find_available_spots(spot_type)
        
        logger.info(f"✅ Found {len(available_spots)} spots:")
        for i, spot in enumerate(available_spots, 1):
            logger.info(f"   {i}. {spot}")
        
        await asyncio.sleep(10)
        
    finally:
        await bot.cleanup()


def setup_initial_config():
    """Interactive setup for first-time configuration"""
    print("🔧 Elia Parking Bot V4 - Initial Setup")
    print("=" * 60)
    
    # Load environment
    load_dotenv()
    
    import json
    import os
    
    config_path = Path("config.json")
    
    # Get organization name
    org = input("\n🏢 Enter your Elia organization name: ").strip()
    
    # Get email
    email = input("📧 Enter your email address: ").strip()
    
    # MFA method
    print("\n🔐 MFA Method:")
    print("  1. Microsoft Authenticator (TOTP)")
    print("  2. Email code")
    print("  3. Push notification (manual approval)")
    mfa_choice = input("Select MFA method (1-3): ").strip()
    
    mfa_map = {
        '1': 'authenticator',
        '2': 'email',
        '3': 'push'
    }
    mfa_method = mfa_map.get(mfa_choice, 'authenticator')
    
    # TOTP secret if using authenticator
    totp_secret = ""
    if mfa_method == 'authenticator':
        print("\nℹ️  To use TOTP automation, you need your authenticator secret key.")
        print("   This is the base32 string shown when setting up the authenticator.")
        totp_secret = input("🔑 Enter TOTP secret (or press Enter to skip): ").strip()
    
    # Notification preferences
    print("\n📢 Notification Setup (optional):")
    discord_webhook = input("Discord webhook URL (or press Enter to skip): ").strip()
    telegram_token = input("Telegram bot token (or press Enter to skip): ").strip()
    telegram_chat = ""
    if telegram_token:
        telegram_chat = input("Telegram chat ID: ").strip()
    
    # Create config
    config = {
        "elia": {
            "organization": org,
            "url": "https://app.elia.io/",
            "credentials": {
                "email": email,
                "use_sso": True,
                "mfa_method": mfa_method
            }
        },
        "schedules": {
            "executive_spots": {
                "enabled": True,
                "time": "00:00:00",
                "days_advance": 14,
                "spot_type": "executive",
                "weekdays_only": True
            },
            "regular_spots": {
                "enabled": True,
                "time": "06:00:00",
                "days_advance": 14,
                "spot_type": "regular",
                "weekdays_only": True
            }
        },
        "retry": {
            "max_attempts": 5,
            "backoff_seconds": [5, 10, 30, 60, 120],
            "aggressive_refresh": True
        },
        "notifications": {
            "discord_webhook": discord_webhook,
            "telegram_bot_token": telegram_token,
            "telegram_chat_id": telegram_chat,
            "email": {
                "enabled": False
            }
        },
        "advanced": {
            "headless": True,
            "browser_profile_path": "./browser_data",
            "session_persistence": True,
            "screenshot_on_error": True,
            "ai_spot_detection": True,
            "use_api_when_possible": True
        }
    }
    
    # Save config
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)
    
    print(f"\n✅ Configuration saved to {config_path}")
    
    # Create .env file
    env_path = Path(".env")
    with open(env_path, 'w') as f:
        f.write(f"# Elia Parking Bot Configuration\n")
        f.write(f"ELIA_ORG={org}\n")
        f.write(f"ELIA_EMAIL={email}\n")
        f.write(f"ELIA_PASSWORD=YOUR_PASSWORD_HERE\n")
        if totp_secret:
            f.write(f"TOTP_SECRET={totp_secret}\n")
        if discord_webhook:
            f.write(f"DISCORD_WEBHOOK_URL={discord_webhook}\n")
        if telegram_token:
            f.write(f"TELEGRAM_BOT_TOKEN={telegram_token}\n")
            f.write(f"TELEGRAM_CHAT_ID={telegram_chat}\n")
    
    print(f"✅ Environment file created at {env_path}")
    print("\n⚠️  IMPORTANT: Edit .env and add your password!")
    print("\n🎉 Setup complete! Next steps:")
    print("  1. Edit .env and add your ELIA_PASSWORD")
    print("  2. Run: python main.py --test-auth")
    print("  3. If successful, run: python main.py --daemon")
    print("  4. Or setup Windows tasks: python main.py --setup-tasks")


def setup_windows_tasks(config_path: str = "config.json"):
    """Setup Windows Task Scheduler tasks"""
    print("🪟 Setting up Windows Task Scheduler tasks...")
    
    import json
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    scheduler = ReservationScheduler(config)
    script_path = Path(__file__).absolute()
    
    scheduler.setup_windows_tasks(script_path)
    
    print("\n✅ Windows tasks created!")
    print("\nℹ️  Tasks created:")
    print("  - EliaBot_Executive (midnight, weekdays)")
    print("  - EliaBot_Regular (6am, weekdays)")
    print("\n📋 To manage tasks, open Task Scheduler and look under 'EliaBot' folder")


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Elia Parking Bot V4 - Enterprise Automated Parking Reservation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py --setup                    # First-time setup
  python main.py --test-auth                # Test authentication
  python main.py --test-spots executive     # Test spot detection
  python main.py --reserve executive        # Reserve executive spot now
  python main.py --reserve regular          # Reserve regular spot now
  python main.py --daemon                   # Run in daemon mode (24/7)
  python main.py --setup-tasks              # Setup Windows scheduled tasks
  python main.py --spot-type executive      # Used by Windows Task Scheduler
        """
    )
    
    parser.add_argument('--reserve-all', action='store_true', help='Reserve all weekdays in next 14 days')
    parser.add_argument('--setup', action='store_true', help='Run initial setup wizard')
    parser.add_argument('--test-auth', action='store_true', help='Test authentication flow')
    parser.add_argument('--test-spots', choices=['executive', 'regular'], help='Test spot detection')
    parser.add_argument('--reserve', choices=['executive', 'regular'], help='Reserve a spot now')
    parser.add_argument('--daemon', action='store_true', help='Run in daemon mode with scheduler')
    parser.add_argument('--setup-tasks', action='store_true', help='Setup Windows Task Scheduler')
    parser.add_argument('--spot-type', choices=['executive', 'regular'], help='Spot type (for scheduled tasks)')
    parser.add_argument('--config', default='config.json', help='Config file path')
    parser.add_argument('--log-level', default='INFO', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'], help='Logging level')
    parser.add_argument('--headless', action='store_true', help='Force headless mode')
    parser.add_argument('--visible', action='store_true', help='Force visible browser (for debugging)')
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(args.log_level)
    
    # Load environment variables
    load_dotenv()
    
    try:
        # Run appropriate command
        if args.setup:
            setup_initial_config()
        
        elif args.test_auth:
            asyncio.run(test_authentication(args.config))
        
        elif args.test_spots:
            asyncio.run(test_spot_detection(args.config, args.test_spots))
        
        elif args.reserve_all:
            async def run_multi_day():
                bot = EliaParkingBot(args.config)
                await bot.initialize(headless=not args.visible)
                success = await bot.reserve_spot("regular", multi_day=True)
                await bot.cleanup()
                return 0 if success else 1
            
            exit_code = asyncio.run(run_multi_day())
            sys.exit(exit_code) 
        
        elif args.reserve:
            exit_code = asyncio.run(run_reservation(args.reserve, args.config))
            sys.exit(exit_code)
        
        elif args.daemon:
            asyncio.run(run_daemon_mode(args.config))
        
        elif args.setup_tasks:
            setup_windows_tasks(args.config)
        
        elif args.spot_type:
            # Called by Windows Task Scheduler
            exit_code = asyncio.run(run_reservation(args.spot_type, args.config))
            sys.exit(exit_code)
        
        else:
            parser.print_help()
            print("\n💡 Start with: python main.py --setup")
    
    except KeyboardInterrupt:
        logger.info("⚠️ Interrupted by user")
        sys.exit(130)
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

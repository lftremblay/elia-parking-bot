"""
Main Bot Orchestrator
Coordinates authentication, spot detection, and reservation
"""

import asyncio
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, List, Dict
from loguru import logger

from auth_manager import AuthenticationManager
from browser_automation import BrowserAutomation
from spot_detector import SpotDetector
from notifier import Notifier


class EliaParkingBot:
    """Main orchestrator for Elia parking reservation bot"""
    
    def __init__(self, config_path: str = "config.json", config: dict = None):
        # Load configuration
        if config is not None:
            self.config = config
        else:
            with open(config_path, 'r') as f:
                self.config = json.load(f)
        
        # Initialize components
        self.auth_manager = AuthenticationManager(config=self.config)
        self.browser = BrowserAutomation(self.config, self.auth_manager)
        self.spot_detector = SpotDetector(self.config)
        self.notifier = Notifier(self.config)
        
        # State
        self.authenticated = False
        self.retry_config = self.config.get('retry', {})
        
        logger.info("🤖 EliaParkingBot initialized")
    
    async def initialize(self, headless: bool = True):
        """Initialize the bot and browser"""
        logger.info("🚀 Initializing bot...")
        
        # Try to load existing session
        session_loaded = self.auth_manager.load_session()
        
        if session_loaded and self.auth_manager.is_session_valid():
            logger.success("✅ Valid session loaded from storage")
            self.authenticated = True
        else:
            logger.info("🔐 Authentication required")
        
        # Initialize browser
        await self.browser.initialize(headless=headless)
        
        logger.success("✅ Bot initialized")
    
    async def authenticate(self, force_reauth: bool = False) -> bool:
        """
        Authenticate with Elia system
        Uses aggressive retry and multiple strategies
        """
        if not force_reauth and self.authenticated:
            logger.info("✅ Already authenticated")
            return True
        
        logger.info("🔐 Starting authentication process...")
        
        # Get credentials from config
        elia_config = self.config.get('elia', {})
        organization = elia_config.get('organization')
        email = elia_config.get('credentials', {}).get('email')
        
        # Try authentication with retries
        max_attempts = self.retry_config.get('max_attempts', 3)
        
        for attempt in range(1, max_attempts + 1):
            try:
                logger.info(f"🎯 Authentication attempt {attempt}/{max_attempts}")
                
                # Navigate to Elia (this will detect if already logged in)
                success = await self.browser.navigate_to_elia(organization)
                if not success:
                    raise Exception("Failed to navigate to Elia")
                
                # Check current URL after navigation
                await asyncio.sleep(2)
                current_url = self.browser.page.url
                
                # If we're on the dashboard, we're already authenticated
                if 'app.elia.io' in current_url and 'login' not in current_url.lower():
                    logger.success("✅ Already logged in! Session persisted.")
                    self.authenticated = True
                    self.auth_manager.save_session()
                    return True
                
                # If we're on Microsoft login page, handle SSO
                if 'microsoft' in current_url.lower() or 'login' in current_url.lower():
                    logger.info("🔐 Authentication required...")
                    
                    # Handle Microsoft SSO
                    password = self._get_password()
                    sso_success = await self.browser.handle_microsoft_sso(email, password, max_retries=3)
                    if not sso_success:
                        raise Exception("Microsoft SSO failed")
                    
                    # CHECK IF SSO TOOK US DIRECTLY TO DASHBOARD (skip MFA)
                    current_url = self.browser.page.url
                    if ('app.elia.io' in current_url and 
                        'login' not in current_url.lower() and
                        'auth' not in current_url.lower()):
                        logger.success("✅ SSO completed and reached dashboard directly!")
                        self.authenticated = True
                        self.auth_manager.save_session()
                        return True
                    
                    # Handle MFA if needed
                    mfa_method = self.config.get('elia', {}).get('credentials', {}).get('mfa_method', 'authenticator')
                    if mfa_method != 'none':
                        logger.info(f"🔢 Handling MFA ({mfa_method})...")
                        mfa_success = await self.browser.handle_mfa(mfa_method, max_retries=3)
                        if not mfa_success:
                            raise Exception("MFA failed")
                        
                        # Brief wait for any final redirects
                        logger.info("⏳ Allowing time for final redirects...")
                        await asyncio.sleep(2)
                    
                    # Wait for dashboard with increased timeout
                    logger.info("🏠 Waiting for dashboard after authentication...")
                    dashboard_success = await self.browser.wait_for_dashboard(timeout=90000)  # 90 seconds
                    if not dashboard_success:
                        raise Exception("Failed to reach dashboard after authentication")
                    
                    logger.success("✅ Authentication successful!")
                    self.authenticated = True
                    
                    # Extract and save tokens
                    tokens = await self.browser.extract_tokens_from_browser()
                    if tokens:
                        # Save any extracted tokens
                        pass
                    
                    return True
                
                else:
                    logger.warning(f"⚠️ Unexpected URL after navigation: {current_url}")
                    raise Exception(f"Unexpected navigation result: {current_url}")
                
            except Exception as e:
                logger.error(f"❌ Authentication attempt {attempt} failed: {e}")
                
                if attempt < max_attempts:
                    backoff = self.retry_config.get('backoff_seconds', [5, 10, 30])[min(attempt-1, 2)]
                    logger.info(f"⏳ Retrying in {backoff} seconds...")
                    await asyncio.sleep(backoff)
                else:
                    logger.error("❌ All authentication attempts failed")
                    self.notifier.notify_auth_required()
                    return False
        
        return False
    
    def _get_password(self) -> str:
        """Get password from environment or secure storage"""
        import os
        from dotenv import load_dotenv
        
        load_dotenv()
        password = os.getenv('ELIA_PASSWORD')
        
        if not password:
            logger.warning("⚠️ No password found in environment")
            # Could implement keyring retrieval here
        
        return password
    
    async def reserve_spot(self, spot_type: str = "regular", multi_day: bool = False) -> bool:
        """
        Main reservation workflow using Elia-specific flow
        
        Args:
            spot_type: Type of spot to reserve ('executive' or 'regular')
            multi_day: If True, try to reserve all weekdays in next 14 days
        
        Returns:
            True if reservation successful
        """
        logger.info(f"🎯 Starting reservation workflow for {spot_type} spots...")
        
        try:
            # Ensure authenticated
            if not self.authenticated:
                logger.info("🔐 Not authenticated, attempting login...")
                auth_success = await self.authenticate()
                if not auth_success:
                    self.notifier.notify_failure(spot_type, "Authentication failed")
                    return False
            
# Use the Elia-specific reservation flow
            from elia_reservation_flow import full_reservation_flow, reserve_all_weekdays
            
            if multi_day and spot_type == "regular":
                logger.info(f"🚀 Using multi-day Elia reservation flow...")
                success = await reserve_all_weekdays(self.browser.page, spot_type)
            else:
                logger.info(f"🚀 Using single-day Elia reservation flow...")
                success = await full_reservation_flow(self.browser.page, spot_type)
            
            if success:
                logger.success(f"✅ Successfully reserved {spot_type} spot(s)!")
                self.notifier.notify_success(spot_type, "Reserved", "Check Elia app for details")
                return True
            else:
                logger.error(f"❌ Failed to reserve {spot_type} spot")
                self.notifier.notify_failure(spot_type, "No spots available or reservation failed")
                return False
            
        except Exception as e:
            logger.error(f"❌ Reservation workflow failed: {e}")
            self.notifier.notify_failure(spot_type, str(e))
            return False
    
    async def test_authentication(self):
        """Test authentication flow without reservation"""
        logger.info("🧪 Testing authentication...")
        
        await self.initialize(headless=False)
        success = await self.authenticate()
        
        if success:
            logger.success("✅ Authentication test passed!")
            await asyncio.sleep(5)
        else:
            logger.error("❌ Authentication test failed!")
        
        await self.cleanup()
    
    async def manual_reservation_test(self, spot_type: str = "regular"):
        """Manual test of reservation flow"""
        logger.info(f"🧪 Testing {spot_type} reservation flow...")
        
        await self.initialize(headless=False)
        success = await self.reserve_spot(spot_type)
        
        if success:
            logger.success("✅ Reservation test passed!")
        else:
            logger.error("❌ Reservation test failed!")
        
        await asyncio.sleep(10)
        await self.cleanup()
    
    async def cleanup(self):
        """Cleanup resources"""
        logger.info("🧹 Cleaning up...")
        await self.browser.close()
        logger.info("✅ Cleanup complete")


async def main():
    """Main entry point for testing"""
    bot = EliaParkingBot()
    
    # Test authentication
    await bot.test_authentication()


if __name__ == "__main__":
    asyncio.run(main())

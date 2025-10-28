"""
Browser Automation Handler using Playwright
Handles navigation, authentication, and spot reservation
"""

import asyncio
import json
import time
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Tuple
from loguru import logger

try:
    from playwright.async_api import async_playwright, Page, Browser, BrowserContext
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    logger.warning("⚠️ Playwright not installed. Install with: pip install playwright && playwright install chromium")


class BrowserAutomation:
    """Handles browser automation for Elia parking reservation"""
    
    def __init__(self, config: dict, auth_manager=None):
        if not PLAYWRIGHT_AVAILABLE:
            raise ImportError("Playwright is required. Install with: pip install playwright && playwright install chromium")
        self.config = config
        self.auth_manager = auth_manager
        self.playwright = None  # Add this line
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        
        # Paths
        self.profile_path = Path(config.get('advanced', {}).get('browser_profile_path', './browser_data'))
        self.screenshot_dir = Path('./screenshots')
        self.screenshot_dir.mkdir(exist_ok=True)
        
        logger.info("🌐 BrowserAutomation initialized")
    
    async def initialize(self, headless: bool = True):
        """Initialize browser with persistent profile"""
        logger.info(f"🚀 Launching browser (headless={headless})...")
    
        self.playwright = await async_playwright().start()
            
        # Launch browser with persistent context for session persistence
        self.context = await self.playwright.chromium.launch_persistent_context(
                user_data_dir=str(self.profile_path),
                headless=headless,
                channel='chrome',  # Use installed Chrome
                args=[
                    '--disable-blink-features=AutomationControlled',
                    '--disable-dev-shm-usage',
                    '--no-sandbox',
                    '--disable-setuid-sandbox',
                    '--disable-web-security',
                    '--disable-features=IsolateOrigins,site-per-process',
                ],
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                locale='en-US',
                timezone_id='America/New_York',
                permissions=['geolocation', 'notifications'],
                ignore_https_errors=True,
            )
            
        self.page = await self.context.new_page()
        
        # Set extra headers
        await self.page.set_extra_http_headers({
            'Accept-Language': 'en-US,en;q=0.9,fr;q=0.8',
        })
        
        logger.success("✅ Browser initialized with persistent profile")
        return self.page
    
    async def navigate_to_elia(self, organization: str) -> bool:
        """Navigate to Elia and handle organization input"""
        try:
            logger.info("📍 Navigating to Elia...")
            await self.page.goto('https://app.elia.io/', wait_until='networkidle', timeout=30000)
            
            # Wait for organization input
            await self.page.wait_for_selector('input[type="text"]', timeout=10000)
            
               # Enter organization name
            logger.info(f"🏢 Entering organization: {organization}")
            await self.page.fill('input[type="text"]', organization)
            
            # Click continue button
            await self.page.click('button')
            logger.info("✅ Organization submitted")
            
            # Wait for email input page
            await asyncio.sleep(2)
            
            # Check if email input is required (before Microsoft SSO)
            try:
                email_input = await self.page.wait_for_selector('input[type="email"], input[type="text"]', timeout=5000)
                if email_input:
                    # Get email from config
                    email = self.config.get('elia', {}).get('credentials', {}).get('email', '')
                    if email:
                        logger.info(f"📧 Entering email: {email}")
                        await self.page.fill('input[type="email"], input[type="text"]', email)
                        
                        # Click continue
                        await self.page.click('button')
                        logger.info("✅ Email submitted")
                        await asyncio.sleep(2)
            except Exception as e:
                logger.debug(f"No email input required or already at Microsoft login: {e}")
            
            logger.success("✅ Navigation to Elia complete")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to navigate to Elia: {e}")
            await self.take_screenshot("error_navigate")
            return False
    
    async def handle_microsoft_sso(self, email: str, password: str) -> bool:
        """Handle Microsoft SSO authentication"""
        try:
            logger.info("🔐 Handling Microsoft SSO...")
            
            # Wait for Microsoft login page
            await self.page.wait_for_url('**/login.microsoftonline.com/**', timeout=15000)
            logger.info("📧 Microsoft login page detected")
            
            # Enter email
            email_selector = 'input[type="email"], input[name="loginfmt"]'
            await self.page.wait_for_selector(email_selector, timeout=10000)
            await self.page.fill(email_selector, email)
            await self.page.click('input[type="submit"], button[type="submit"]')
            
            logger.info("✅ Email submitted")
            await asyncio.sleep(2)
            
            # Enter password
            password_selector = 'input[type="password"], input[name="passwd"]'
            await self.page.wait_for_selector(password_selector, timeout=10000)
            await self.page.fill(password_selector, password)
            await self.page.click('input[type="submit"], button[type="submit"]')
            
            logger.info("✅ Password submitted")
            return True
            
        except Exception as e:
            logger.error(f"❌ Microsoft SSO failed: {e}")
            await self.take_screenshot("error_sso")
            return False
    
    async def handle_mfa(self, method: str = "authenticator") -> bool:
        """Handle MFA challenge"""
        try:
            logger.info(f"🔢 Handling MFA ({method})...")
            
            # Wait for MFA prompt
            await asyncio.sleep(3)
            
            if method == "authenticator" or method == "totp":
                # Check if we need to enter TOTP code
                if await self.page.is_visible('input[name="otc"]', timeout=5000):
                    # Get TOTP code from auth manager
                    if self.auth_manager:
                        code = self.auth_manager.get_totp_code()
                        if code:
                            await self.page.fill('input[name="otc"]', code)
                            await self.page.click('input[type="submit"]')
                            logger.success("✅ TOTP code submitted")
                        else:
                            logger.error("❌ Failed to generate TOTP code")
                            return False
                else:
                    # Might be push notification - wait for approval
                    logger.info("📱 Waiting for MFA approval (push notification)...")
                    await asyncio.sleep(30)
            
            elif method == "email":
                logger.info("📧 Email MFA detected - check your email for code")
                # TODO: Implement email code retrieval from IMAP
                await asyncio.sleep(60)  # Wait for manual entry
            
            # Check if "Stay signed in?" prompt appears
            if await self.page.is_visible('text="Stay signed in?"', timeout=5000):
                logger.info("💾 Handling 'Stay signed in' prompt...")
                await self.page.click('input[type="submit"][value="Yes"]')
            
            return True
            
        except Exception as e:
            logger.error(f"❌ MFA handling failed: {e}")
            await self.take_screenshot("error_mfa")
            return False
    
    async def wait_for_dashboard(self) -> bool:
        """Wait for successful login and dashboard load"""
        try:
            logger.info("⏳ Waiting for dashboard to load...")
            
            # Wait for Elia app to load (check for app-specific elements)
            await self.page.wait_for_url('**/app.elia.io/**', timeout=60000)
            
            # Additional wait for app to fully initialize
            await asyncio.sleep(5)
            
            # Take screenshot of dashboard
            await self.take_screenshot("dashboard_loaded")
            
            logger.success("✅ Dashboard loaded successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to reach dashboard: {e}")
            await self.take_screenshot("error_dashboard")
            return False
    
    async def find_available_spots(self, spot_type: str = "any") -> List[Dict]:
        """Find available parking spots using AI vision and DOM parsing"""
        logger.info(f"🔍 Searching for available {spot_type} spots...")
        
        available_spots = []
        
        try:
            # Take screenshot for AI analysis
            screenshot_path = await self.take_screenshot(f"spot_search_{spot_type}")
            
            # Strategy 1: Parse DOM for spot availability
            spots_from_dom = await self._parse_spots_from_dom(spot_type)
            available_spots.extend(spots_from_dom)
            
            # Strategy 2: If no spots found, use image recognition
            if not available_spots:
                logger.info("🖼️  Attempting AI image recognition...")
                spots_from_image = await self._detect_spots_from_image(screenshot_path)
                available_spots.extend(spots_from_image)
            
            logger.info(f"✅ Found {len(available_spots)} available spots")
            return available_spots
            
        except Exception as e:
            logger.error(f"❌ Spot detection failed: {e}")
            return []
    
    async def _parse_spots_from_dom(self, spot_type: str) -> List[Dict]:
        """Parse available spots from page DOM"""
        spots = []
        
        try:
            # Execute JavaScript to find available spots
            # This will depend on the actual Elia app structure
            js_code = """
            () => {
                // Look for elements indicating available spots
                // This is a placeholder - actual selectors need to be determined
                const spotElements = document.querySelectorAll('[data-available="true"], .spot-available, .parking-spot.available');
                
                return Array.from(spotElements).map(el => ({
                    id: el.dataset.spotId || el.id,
                    name: el.textContent.trim(),
                    type: el.dataset.type || 'unknown',
                    available: true
                }));
            }
            """
            
            spots = await self.page.evaluate(js_code)
            logger.info(f"📋 Found {len(spots)} spots from DOM")
            
        except Exception as e:
            logger.warning(f"⚠️ DOM parsing failed: {e}")
        
        return spots
    
    async def _detect_spots_from_image(self, screenshot_path: Path) -> List[Dict]:
        """Detect available spots using image recognition"""
        # TODO: Implement CV-based spot detection
        # Look for green indicators, available badges, etc.
        logger.info("🤖 Image-based detection not yet implemented")
        return []
    
    async def reserve_spot(self, spot_id: str) -> bool:
        """Attempt to reserve a specific parking spot"""
        try:
            logger.info(f"🎯 Attempting to reserve spot: {spot_id}")
            
            # Click on the spot
            # This will depend on the actual UI structure
            spot_selector = f'[data-spot-id="{spot_id}"]'
            
            if await self.page.is_visible(spot_selector, timeout=5000):
                await self.page.click(spot_selector)
                await asyncio.sleep(1)
                
                # Look for confirmation button
                confirm_selectors = [
                    'button:has-text("Réserver")',
                    'button:has-text("Reserve")',
                    'button:has-text("Confirm")',
                    'button.reserve-btn',
                    'button[type="submit"]'
                ]
                
                for selector in confirm_selectors:
                    if await self.page.is_visible(selector, timeout=2000):
                        await self.page.click(selector)
                        logger.success(f"✅ Reservation confirmed for spot {spot_id}")
                        await self.take_screenshot("reservation_success")
                        return True
            
            logger.warning(f"⚠️ Could not find reservation button for spot {spot_id}")
            return False
            
        except Exception as e:
            logger.error(f"❌ Reservation failed: {e}")
            await self.take_screenshot("error_reservation")
            return False
    
    async def take_screenshot(self, name: str) -> Path:
        """Take a screenshot with timestamp"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{name}_{timestamp}.png"
        filepath = self.screenshot_dir / filename
        
        try:
            await self.page.screenshot(path=str(filepath), full_page=True)
            logger.debug(f"📸 Screenshot saved: {filepath}")
            return filepath
        except Exception as e:
            logger.error(f"❌ Screenshot failed: {e}")
            return None
    
    async def extract_tokens_from_browser(self) -> Dict[str, str]:
        """Extract authentication tokens from browser storage"""
        try:
            # Get localStorage
            local_storage = await self.page.evaluate('() => JSON.stringify(localStorage)')
            storage_data = json.loads(local_storage)
            
            # Get cookies
            cookies = await self.context.cookies()
            
            # Look for tokens
            tokens = {}
            for key, value in storage_data.items():
                if 'token' in key.lower() or 'auth' in key.lower():
                    tokens[key] = value
            
            logger.info(f"🔑 Extracted {len(tokens)} potential tokens from browser")
            return tokens
            
        except Exception as e:
            logger.error(f"❌ Token extraction failed: {e}")
            return {}
    
    async def close(self):
        """Close browser and cleanup"""
        if self.context:
            await self.context.close()
        if self.playwright:
            await self.playwright.stop()
        logger.info("🔚 Browser closed")


async def test_browser():
    """Test browser automation"""
    config = {
        'advanced': {
            'browser_profile_path': './test_browser_data'
        }
    }
    
    browser = BrowserAutomation(config)
    await browser.initialize(headless=False)
    
    # Test navigation
    await browser.navigate_to_elia("test-org")
    
    await asyncio.sleep(10)
    await browser.close()


if __name__ == "__main__":
    if PLAYWRIGHT_AVAILABLE:
        asyncio.run(test_browser())
    else:
        print("Please install Playwright: pip install playwright && playwright install chromium")

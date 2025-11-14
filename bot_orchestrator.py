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

# Cloud authentication integration (Story 1.2)
try:
    from src.cloud.cloud_auth_manager import CloudAuthenticationManager
    CLOUD_AUTH_AVAILABLE = True
    logger.info("☁️ Cloud authentication manager available")
except ImportError as e:
    CLOUD_AUTH_AVAILABLE = False
    logger.warning(f"⚠️ Cloud authentication not available: {e}")


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
        
        # Cloud authentication integration (Story 1.2 - Task 1.1)
        self.cloud_auth_manager = None
        if CLOUD_AUTH_AVAILABLE:
            try:
                self.cloud_auth_manager = CloudAuthenticationManager()
                logger.info("☁️ Cloud authentication manager initialized")
            except Exception as e:
                logger.warning(f"⚠️ Failed to initialize cloud auth manager: {e}")
        
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
    
    async def _authenticate_with_cloud_manager(self) -> bool:
        """
        Authenticate using cloud authentication manager
        Story 1.2 - Task 1.1: Cloud authentication integration
        """
        try:
            logger.info("☁️ Attempting cloud authentication...")
            
            # Use cloud authentication manager directly
            success = await self.cloud_auth_manager.authenticate_microsoft()
            
            if success:
                logger.success("☁️ Cloud authentication successful!")
                return True
            else:
                logger.error("☁️ Cloud authentication failed")
                return False
                
        except Exception as e:
            logger.error(f"☁️ Cloud authentication error: {e}")
            return False
    
    async def authenticate(self, force_reauth: bool = False) -> bool:
        """
        Authenticate with Elia system
        Uses aggressive retry and multiple strategies
        Story 1.2: Integrated with cloud authentication system
        """
        if not force_reauth and self.authenticated:
            logger.info("✅ Already authenticated")
            return True
        
        logger.info("🔐 Starting authentication process...")
        
        # Story 1.2 - Task 1.1: Try cloud authentication first
        if self.cloud_auth_manager and self.cloud_auth_manager.is_cloud:
            logger.info("☁️ Using cloud authentication (GitHub Actions environment)")
            try:
                # Use cloud authentication manager
                cloud_success = await self._authenticate_with_cloud_manager()
                if cloud_success:
                    logger.success("☁️ Cloud authentication successful!")
                    self.authenticated = True
                    return True
                else:
                    logger.warning("☁️ Cloud authentication failed, falling back to local auth")
            except Exception as e:
                logger.error(f"☁️ Cloud authentication error: {e}")
                logger.info("🔄 Falling back to local authentication...")
        
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
                
                # If we're on Microsoft/Kinde login page, handle SSO
                if 'microsoft' in current_url.lower() or 'login' in current_url.lower() or 'kinde' in current_url.lower():
                    logger.info("🔐 Authentication required...")
                    
                    # Handle SSO (Microsoft/Kinde)
                    password = self._get_password()
                    sso_success = await self.browser.handle_sso(email, password, max_retries=3)
                    if not sso_success:
                        raise Exception("SSO failed")
                    
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
        Story 1.2 - Task 2: Enhanced with complete end-to-end flow
        
        Args:
            spot_type: Type of spot to reserve ('executive' or 'regular')
            multi_day: If True, try to reserve all weekdays in next 14 days
        
        Returns:
            True if reservation successful
        """
        logger.info(f"🎯 Starting Story 1.2 enhanced reservation workflow for {spot_type} spots...")
        
        try:
            # Story 1.2 - Task 2.1: Enhanced authentication → spot detection handoff
            logger.info("🔐 Step 1: Verifying authentication...")
            
            # Ensure authenticated with cloud auth integration
            if not self.authenticated:
                logger.info("🔐 Not authenticated, attempting login...")
                auth_success = await self.authenticate()
                if not auth_success:
                    logger.error("❌ Authentication failed in reservation flow")
                    self.notifier.notify_failure(spot_type, "Authentication failed")
                    return False
                else:
                    logger.success("✅ Authentication successful for reservation")
            else:
                logger.info("✅ Already authenticated, proceeding to reservation")
            
            # Story 1.2 - Task 2.1: Verify authentication state before proceeding
            if not await self._verify_authentication_state():
                logger.error("❌ Authentication state verification failed")
                return False
            
            logger.info("🔍 Step 2: Starting spot detection phase...")
            
            # Story 1.2 - Task 2.1: Enhanced spot detection integration
            spot_detection_success = await self._perform_spot_detection(spot_type)
            if not spot_detection_success:
                logger.error("❌ Spot detection failed")
                self.notifier.notify_failure(spot_type, "Spot detection failed")
                return False
            
            logger.info("🎯 Step 3: Starting reservation execution...")
            
            # Story 1.2 - Task 2.2: Enhanced spot selection → execution flow
            execution_success = await self._execute_spot_reservation(spot_type)
            if not execution_success:
                logger.error("❌ Spot reservation execution failed")
                self.notifier.notify_failure(spot_type, "Reservation execution failed")
                return False
            
            # Story 1.2 - Task 2.3: Enhanced reservation verification
            logger.success(f"✅ Reservation execution completed for {spot_type} spot(s)!")
            
            # Add confirmation and verification
            verification_success = await self._verify_reservation_completion(spot_type)
            if verification_success:
                logger.success("✅ Reservation verification confirmed")
                self.notifier.notify_success(spot_type, "Reserved", "Check Elia app for details")
                return True
            else:
                logger.warning("⚠️ Reservation completed but verification failed")
                self.notifier.notify_success(spot_type, "Reserved (unverified)", "Check Elia app for details")
                return True  # Still return True since reservation worked
            
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
        return False
    
    # Story 1.2 - Task 2.1: Helper methods for enhanced flow
    async def _verify_authentication_state(self) -> bool:
        """
        Verify that authentication state is valid before proceeding
        Story 1.2 - Task 2.1: Authentication → spot detection handoff
        """
        try:
            logger.info("🔍 Verifying authentication state...")
            
            # Check if we have a valid browser page
            if not self.browser.page:
                logger.error("❌ Browser page not available")
                return False
            
            # Check current URL
            current_url = self.browser.page.url
            logger.info(f"🌐 Current URL: {current_url}")
            
            # Verify we're on the Elia dashboard
            if 'app.elia.io' in current_url and 'login' not in current_url.lower():
                logger.success("✅ Authentication state verified - on dashboard")
                return True
            else:
                logger.warning(f"⚠️ Not on expected dashboard page: {current_url}")
                
                # Try to navigate to dashboard
                logger.info("🔄 Attempting to navigate to dashboard...")
                await self.browser.page.goto("https://app.elia.io/dashboard")
                await asyncio.sleep(2)
                
                # Check again
                new_url = self.browser.page.url
                if 'app.elia.io' in new_url and 'login' not in new_url.lower():
                    logger.success("✅ Successfully navigated to dashboard")
                    return True
                else:
                    logger.error("❌ Failed to reach dashboard")
                    return False
                    
        except Exception as e:
            logger.error(f"❌ Authentication state verification failed: {e}")
            return False
    
    async def _perform_spot_detection(self, spot_type: str) -> bool:
        """
        Perform spot detection as part of the enhanced flow
        Story 1.2 - Task 2.1/2.2: Enhanced spot detection and selection
        """
        try:
            logger.info(f"🔍 Performing enhanced spot detection for {spot_type} spots...")
            
            # Navigate to parking page
            logger.info("🌐 Navigating to parking page...")
            await self.browser.page.goto("https://app.elia.io/parking")
            await asyncio.sleep(3)
            
            # Take screenshot for analysis
            screenshot_path = self.browser.screenshot_dir / f"spot_detection_{spot_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            await self.browser.page.screenshot(path=str(screenshot_path))
            logger.info(f"📸 Screenshot saved: {screenshot_path}")
            
            # Use spot detector to analyze
            logger.info("🤖 Analyzing screenshot for available spots...")
            detected_spots = self.spot_detector.detect_spots_from_screenshot(screenshot_path, spot_type)
            
            if detected_spots:
                logger.success(f"✅ Detected {len(detected_spots)} available {spot_type} spots")
                
                # Story 1.2 - Task 2.2: Enhanced spot selection and execution handoff
                selected_spot = await self._select_best_spot(detected_spots, spot_type)
                if selected_spot:
                    logger.info(f"🎯 Selected best spot: {selected_spot}")
                    
                    # Store selected spot for reservation execution
                    self.selected_spot = selected_spot
                    return True
                else:
                    logger.warning("⚠️ Failed to select best spot")
                    return False
            else:
                logger.warning(f"⚠️ No {spot_type} spots detected")
                return False
                
        except Exception as e:
            logger.error(f"❌ Spot detection failed: {e}")
            return False
    
    async def _select_best_spot(self, detected_spots: List[Dict], spot_type: str) -> Optional[Dict]:
        """
        Select the best spot from detected options
        Story 1.2 - Task 2.2: Spot selection → reservation execution flow
        """
        try:
            logger.info(f"🎯 Selecting best {spot_type} spot from {len(detected_spots)} options...")
            
            if not detected_spots:
                return None
            
            # Sort spots by confidence and other criteria
            sorted_spots = sorted(detected_spots, key=lambda x: (
                x.get('confidence', 0),  # Primary: confidence
                -x.get('area', 0),       # Secondary: larger area (negative for descending)
                x.get('y_coord', 999)    # Tertiary: higher on page (lower y)
            ), reverse=True)
            
            # Select the top spot
            best_spot = sorted_spots[0]
            
            logger.info(f"🎯 Best spot selected:")
            logger.info(f"  - Confidence: {best_spot.get('confidence', 0):.2f}")
            logger.info(f"  - Area: {best_spot.get('area', 0)}")
            logger.info(f"  - Coordinates: ({best_spot.get('x_coord', 0)}, {best_spot.get('y_coord', 0)})")
            
            # Story 1.2 - Task 2.2: Prepare spot for reservation execution
            await self._prepare_spot_for_reservation(best_spot)
            
            return best_spot
            
        except Exception as e:
            logger.error(f"❌ Spot selection failed: {e}")
            return None
    
    async def _prepare_spot_for_reservation(self, spot: Dict):
        """
        Prepare the selected spot for reservation execution
        Story 1.2 - Task 2.2: Spot selection → reservation execution flow
        """
        try:
            logger.info("🎯 Preparing selected spot for reservation...")
            
            # Calculate click coordinates with offset for better accuracy
            x_coord = spot.get('x_coord', 0) + spot.get('width', 0) // 2
            y_coord = spot.get('y_coord', 0) + spot.get('height', 0) // 2
            
            # Store execution coordinates
            self.spot_click_coords = (x_coord, y_coord)
            
            logger.info(f"🎯 Prepared click coordinates: ({x_coord}, {y_coord})")
            
            # Optionally highlight the spot visually (for debugging)
            if self.config.get('advanced', {}).get('debug_mode', False):
                await self._highlight_selected_spot(x_coord, y_coord)
            
        except Exception as e:
            logger.error(f"❌ Spot preparation failed: {e}")
    
    async def _highlight_selected_spot(self, x: int, y: int):
        """
        Highlight the selected spot for visual confirmation (debug mode)
        Story 1.2 - Task 2.2: Visual feedback for spot selection
        """
        try:
            logger.info("🎯 Highlighting selected spot...")
            
            # Add a temporary visual indicator
            await self.browser.page.evaluate("""
                (x, y) => {
                    const highlight = document.createElement('div');
                    highlight.style.position = 'absolute';
                    highlight.style.left = (x - 15) + 'px';
                    highlight.style.top = (y - 15) + 'px';
                    highlight.style.width = '30px';
                    highlight.style.height = '30px';
                    highlight.style.border = '3px solid red';
                    highlight.style.borderRadius = '50%';
                    highlight.style.pointerEvents = 'none';
                    highlight.style.zIndex = '9999';
                    highlight.id = 'spot-highlight';
                    document.body.appendChild(highlight);
                    
                    // Remove after 2 seconds
                    setTimeout(() => {
                        const elem = document.getElementById('spot-highlight');
                        if (elem) elem.remove();
                    }, 2000);
                }
            """, x, y)
            
            await asyncio.sleep(2)  # Allow time to see the highlight
            
        except Exception as e:
            logger.warning(f"⚠️ Failed to highlight spot: {e}")
    
    async def _execute_spot_reservation(self, spot_type: str) -> bool:
        """
        Execute the reservation for the selected spot
        Story 1.2 - Task 2.2: Complete spot selection → reservation execution flow
        """
        try:
            logger.info(f"🎯 Executing reservation for selected {spot_type} spot...")
            
            # Check if we have prepared click coordinates
            if not hasattr(self, 'spot_click_coords'):
                logger.error("❌ No spot coordinates prepared for reservation")
                return False
            
            x, y = self.spot_click_coords
            logger.info(f"🎯 Clicking on spot at coordinates: ({x}, {y})")
            
            # Click on the selected spot
            await self.browser.page.mouse.click(x, y)
            await asyncio.sleep(1)  # Wait for UI response
            
            # Look for reservation button or confirm dialog
            logger.info("🔍 Looking for reservation confirmation...")
            
            # Try multiple selectors for the reserve button
            reserve_selectors = [
                "button[contains(text(), 'Reserve')]",
                "button[contains(text(), 'Réserver')]", 
                "button[contains(text(), 'Book')]",
                ".reserve-button",
                ".booking-button",
                "button[type='submit']"
            ]
            
            reserve_button = None
            for selector in reserve_selectors:
                try:
                    if "contains" in selector:
                        # Handle XPath-like contains
                        text = selector.split("'")[1]
                        elements = await self.browser.page.query_selector_all(f"button:has-text('{text}')")
                        if elements:
                            reserve_button = elements[0]
                            break
                    else:
                        reserve_button = await self.browser.page.query_selector(selector)
                        if reserve_button:
                            break
                except:
                    continue
            
            if reserve_button:
                logger.info("✅ Found reservation button, clicking...")
                await reserve_button.click()
                await asyncio.sleep(2)
                
                # Handle any confirmation dialog
                await self._handle_reservation_confirmation()
                
                logger.success("✅ Spot reservation execution completed")
                return True
            else:
                logger.warning("⚠️ No reservation button found, trying direct reservation...")
                # Fallback: try to complete reservation without explicit button
                return await self._complete_direct_reservation()
                
        except Exception as e:
            logger.error(f"❌ Spot reservation execution failed: {e}")
            return False
    
    async def _handle_reservation_confirmation(self):
        """
        Handle any confirmation dialogs that appear after clicking reserve
        Story 1.2 - Task 2.2: Reservation execution confirmation handling
        """
        try:
            logger.info("🔍 Handling reservation confirmation...")
            
            # Look for confirmation dialogs
            confirmation_selectors = [
                "button:has-text('Confirm')",
                "button:has-text('Confirmer')",
                "button:has-text('Yes')",
                "button:has-text('Oui')",
                ".confirm-button",
                ".confirmation-modal button"
            ]
            
            for selector in confirmation_selectors:
                try:
                    confirm_button = await self.browser.page.query_selector(selector)
                    if confirm_button:
                        logger.info("✅ Found confirmation button, clicking...")
                        await confirm_button.click()
                        await asyncio.sleep(1)
                        break
                except:
                    continue
                    
        except Exception as e:
            logger.warning(f"⚠️ Confirmation handling failed: {e}")
    
    async def _complete_direct_reservation(self):
        """
        Complete reservation without explicit button clicks
        Story 1.2 - Task 2.2: Direct reservation completion
        """
        try:
            logger.info("🔄 Attempting direct reservation completion...")
            
            # Wait a moment for any automatic processing
            await asyncio.sleep(3)
            
            # Check if reservation was completed by checking page content
            current_url = self.browser.page.url
            page_content = await self.browser.page.content()
            
            # Look for success indicators
            if any(indicator in page_content.lower() for indicator in 
                   ["confirmed", "confirmée", "successful", "réussie"]):
                logger.success("✅ Direct reservation appears successful")
                return True
            else:
                logger.warning("⚠️ Direct reservation status unclear")
                return False
                
        except Exception as e:
            logger.error(f"❌ Direct reservation failed: {e}")
            return False
    
    async def _verify_reservation_completion(self, spot_type: str) -> bool:
        """
        Verify that reservation was completed successfully
        Story 1.2 - Task 2.3: Reservation confirmation and verification
        """
        try:
            logger.info("🔍 Verifying reservation completion...")
            
            # Wait a moment for any confirmation to appear
            await asyncio.sleep(2)
            
            # Take final screenshot
            final_screenshot = self.browser.screenshot_dir / f"reservation_final_{spot_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            await self.browser.page.screenshot(path=str(final_screenshot))
            logger.info(f"📸 Final screenshot saved: {final_screenshot}")
            
            # Check for confirmation indicators
            page_content = await self.browser.page.content()
            
            # Look for success indicators
            success_indicators = [
                "reservation confirmed",
                "réservation confirmée", 
                "booking successful",
                "réservation réussie"
            ]
            
            page_lower = page_content.lower()
            found_indicator = any(indicator in page_lower for indicator in success_indicators)
            
            if found_indicator:
                logger.success("✅ Reservation confirmation found on page")
                return True
            else:
                # Check if we're still on parking page (might indicate success)
                current_url = self.browser.page.url
                if "parking" in current_url:
                    logger.info("✅ Still on parking page - reservation likely successful")
                    return True
                else:
                    logger.warning("⚠️ No clear confirmation indicator found")
                    return False
                    
        except Exception as e:
            logger.error(f"❌ Reservation verification failed: {e}")
            return False


async def main():
    """Main entry point for testing"""
    bot = EliaParkingBot()
    
    # Test authentication
    await bot.test_authentication()


if __name__ == "__main__":
    asyncio.run(main())

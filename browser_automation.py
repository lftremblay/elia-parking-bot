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
import pyotp

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
        
        # Paths - ensure absolute paths
        profile_path = config.get('advanced', {}).get('browser_profile_path', './browser_data')
        self.profile_path = Path(profile_path).resolve()
        self.screenshot_dir = Path('./screenshots').resolve()
        self.screenshot_dir.mkdir(exist_ok=True)
        
        logger.info(f"🌐 BrowserAutomation initialized with profile: {self.profile_path}")
    
    async def initialize(self, headless: bool = True):
        """Initialize browser with persistent profile and anti-detection measures"""
        logger.info(f"🚀 Launching browser (headless={headless})...")
    
        self.playwright = await async_playwright().start()
        
        # Enhanced browser arguments for anti-detection
        browser_args = [
            '--disable-blink-features=AutomationControlled',
            '--disable-dev-shm-usage',
            '--no-sandbox',
            '--disable-setuid-sandbox',
            '--disable-web-security',
            '--disable-features=IsolateOrigins,site-per-process',
            '--disable-extensions',
            '--disable-plugins',
            '--disable-default-apps',
            '--disable-background-timer-throttling',
            '--disable-backgrounding-occluded-windows',
            '--disable-renderer-backgrounding',
            '--disable-field-trial-config',
            '--disable-back-forward-cache',
            '--disable-hang-monitor',
            '--disable-ipc-flooding-protection',
            '--disable-popup-blocking',
            '--disable-prompt-on-repost',
            '--force-color-profile=srgb',
            '--metrics-recording-only',
            '--no-first-run',
            '--enable-automation=false',
            '--password-store=basic',
            '--use-mock-keychain',
            '--no-service-autorun',
            '--export-tagged-pdf',
            '--disable-component-update',
            '--disable-domain-reliability',
            '--disable-client-side-phishing-detection',
            '--disable-background-networking',
            '--disable-breakpad',
            '--disable-component-extensions-with-background-pages',
            '--disable-ipc-flooding-protection',
            '--disable-print-preview',
            '--disable-component-cloud-policy',
            '--disable-background-timer-throttling',
            '--disable-backgrounding-occluded-windows',
        ]
        
        # Add headless-specific args only when headless
        if headless:
            browser_args.extend([
                '--headless=new',  # Use new headless mode
                '--disable-gpu',
                '--disable-software-rasterizer',
                '--disable-background-media-download',
                '--disable-features=VizDisplayCompositor',
            ])
        
        # Launch browser with persistent context for session persistence
        # Cross-platform browser executable detection
        executable_path = None
        
        # Environment debugging
        import platform
        import os
        
        logger.info(f"🔍 Environment: {platform.system()}")
        logger.info(f"🔍 Platform: {platform.platform()}")
        logger.info(f"🔍 Architecture: {platform.architecture()}")
        
        if platform.system() == "Windows":
            custom_path = "./browser_data/chrome-win/chrome.exe"
            if os.path.exists(custom_path):
                executable_path = custom_path
                logger.info(f"🌐 Using custom Windows browser: {custom_path}")
            else:
                logger.warning(f"⚠️ Custom Windows browser not found at: {custom_path}")
                logger.info("🌐 Falling back to system Playwright browser")
        elif platform.system() == "Linux":
            # In GitHub Actions, use system Playwright installation
            logger.info("🌐 Using system Playwright browser installation")
            # Verify Playwright browser is available
            try:
                import subprocess
                result = subprocess.run(['which', 'chromium-browser'], capture_output=True, text=True)
                if result.returncode == 0:
                    logger.info(f"🌐 Found system Chromium at: {result.stdout.strip()}")
                else:
                    logger.info("🌐 Using Playwright's built-in Chromium")
            except Exception as e:
                logger.debug(f"Could not verify system browser: {e}")
        elif platform.system() == "Darwin":  # macOS
            custom_path = "./browser_data/chrome-mac/Chromium.app/Contents/MacOS/Chromium"
            if os.path.exists(custom_path):
                executable_path = custom_path
                logger.info(f"🌐 Using custom macOS browser: {custom_path}")
            else:
                logger.warning(f"⚠️ Custom macOS browser not found at: {custom_path}")
                logger.info("🌐 Falling back to system Playwright browser")
        
        self.context = await self.playwright.chromium.launch_persistent_context(
                user_data_dir=str(self.profile_path),
                headless=headless,
                executable_path=executable_path,  # Use detected browser path
                args=browser_args,
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                locale='en-US',
                timezone_id='America/New_York',
                permissions=['geolocation', 'notifications'],
                ignore_https_errors=True,
                # Additional anti-detection measures
                bypass_csp=True,
                ignore_default_args=['--enable-automation'],
            )
            
        self.page = await self.context.new_page()
        
        # Set extra headers to mimic real browser
        await self.page.set_extra_http_headers({
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'en-US,en;q=0.9,fr;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0',
        })
        
        # Inject anti-detection scripts
        await self.page.add_init_script("""
            // Remove webdriver property
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined,
            });
            
            // Mock languages and plugins
            Object.defineProperty(navigator, 'languages', {
                get: () => ['en-US', 'en'],
            });
            
            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3, 4, 5],
            });
            
            // Mock permissions
            const originalQuery = window.navigator.permissions.query;
            window.navigator.permissions.query = (parameters) => (
                parameters.name === 'notifications' ?
                    Promise.resolve({ state: Notification.permission }) :
                    originalQuery(parameters)
            );
            
            // Mock screen properties for headless detection
            Object.defineProperty(screen, 'availHeight', {
                get: () => screen.height - 40,
            });
            
            // Override chrome runtime detection
            window.chrome = {
                runtime: {},
                csi: () => ({}),
                loadTimes: () => ({}),
            };
        """)
        
        logger.success("✅ Browser initialized with persistent profile and anti-detection measures")
        return self.page
    
    async def _wait_for_first_selector(self, selectors, timeout: int = 3000, state: str = 'visible') -> Optional[str]:
        """Return the first selector that becomes available within the timeout"""
        for selector in selectors:
            try:
                await self.page.wait_for_selector(selector, timeout=timeout, state=state)
                return selector
            except Exception:
                continue
        return None

    async def _is_selector_present(self, selectors) -> Optional[str]:
        """Check if any selector is currently present on the page"""
        for selector in selectors:
            try:
                element = await self.page.query_selector(selector)
                if element:
                    return selector
            except Exception:
                continue
        return None

    async def navigate_to_elia(self, organization: str) -> bool:
        """Navigate to Elia and handle organization input only if needed"""
        try:
            logger.info("📍 Navigating to Elia...")
            await self.page.goto('https://app.elia.io/', wait_until='networkidle', timeout=30000)
            
            # Wait a bit for the page to stabilize
            await asyncio.sleep(2)
            
            # Check if we're already on the dashboard (session persisted)
            current_url = self.page.url
            if 'app.elia.io' in current_url and 'login' not in current_url.lower():
                # Try to detect dashboard elements
                dashboard_indicators = [
                    'text="Parking"',  # Common dashboard text
                    'text="Réservation"',
                    'text="Reservation"',
                    '[data-testid*="parking"]',
                    '.parking-grid',
                    '.dashboard',
                    'h1',  # Usually has a header on dashboard
                    'nav',  # Navigation elements
                ]
                
                dashboard_detected = False
                for indicator in dashboard_indicators:
                    try:
                        if indicator.startswith('text='):
                            await self.page.wait_for_selector(f'*{indicator}', timeout=3000)
                        else:
                            await self.page.wait_for_selector(indicator, timeout=3000, state='visible')
                        logger.info(f"✅ Dashboard detected: {indicator}")
                        dashboard_detected = True
                        break
                    except:
                        continue
                
                if dashboard_detected:
                    logger.success("✅ Already on Elia dashboard - session persisted!")
                    return True
            
            # If not on dashboard, we need to enter organization
            logger.info("🏢 Need to enter organization - not logged in")
            
            # Wait for organization input (should be visible now)
            await self.page.wait_for_selector('input[type="text"]', timeout=10000)
            
            # Enter organization name
            logger.info(f"🏢 Entering organization: {organization}")
            await self.page.fill('input[type="text"]', organization)
            
            # Click continue button
            await self.page.click('button')
            logger.info("✅ Organization submitted")
            
            # Wait for email input page or redirect
            await asyncio.sleep(2)
            
            # Check if we got redirected to Microsoft SSO
            current_url = self.page.url
            if 'microsoft' in current_url.lower() or 'login' in current_url.lower():
                logger.info("🔐 Redirected to Microsoft SSO")
                return True  # Let the auth flow handle SSO
            
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
                logger.debug(f"No email input required: {e}")
            
            logger.success("✅ Navigation to Elia complete")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to navigate to Elia: {e}")
            await self.take_screenshot("error_navigate")
            return False
    
    async def handle_microsoft_sso(self, email: str, password: str, max_retries: int = 3) -> bool:
        """Handle Microsoft SSO authentication with robust retry logic"""
        for attempt in range(1, max_retries + 1):
            try:
                logger.info(f"🔐 Handling Microsoft SSO (attempt {attempt}/{max_retries})...")

                # Check for initial SSO choice page (Auth0)
                org_continue_selectors = [
                    'button:has-text("Continue with Quebecor")',
                    'button:has-text("Continue")',
                    'a:has-text("Continue with Quebecor")',
                    '[data-action="continue-with-org"]',
                    'button[id*="continue"]',
                    'a[id*="continue"]'
                ]

                # Look for "Continue with Quebecor" button first
                org_button_found = await self._is_selector_present(org_continue_selectors)
                if org_button_found:
                    logger.info(f"🏢 Found organization continue button: {org_button_found}")
                    await self.page.click(org_button_found)
                    logger.info("✅ Clicked 'Continue with Quebecor'")
                    await asyncio.sleep(2)

                    # Wait for redirect to Microsoft
                    await self.page.wait_for_load_state('networkidle', timeout=10000)
                    logger.info("🔄 Redirected after organization selection")

                login_hosts = [
                    '**/login.microsoftonline.com/**',
                    '**/login.microsoft.com/**',
                    '**/login.live.com/**',
                    '**/account.microsoft.com/**',
                    '**/.auth0.com/**',
                    '**/login.microsoftonline.com/**'  # SAML endpoint
                ]

                login_page_found = False
                for url_pattern in login_hosts:
                    try:
                        await self.page.wait_for_url(url_pattern, timeout=5000)
                        logger.info(f"📧 Login page detected: {url_pattern}")
                        login_page_found = True
                        break
                    except Exception:
                        continue

                if not login_page_found:
                    logger.warning("⚠️ Login page pattern not matched, inspecting current URL...")
                    current_url = self.page.url
                    if any(token in current_url.lower() for token in ['microsoft', 'login', 'auth0', 'saml']):
                        logger.info(f"📧 On login flow page: {current_url}")
                        # Wait for page to stabilize after potential SAML redirect
                        await asyncio.sleep(2)
                        await self.page.wait_for_load_state('networkidle', timeout=10000)
                        await asyncio.sleep(1)
                    else:
                        raise Exception(f"Not on expected login page: {current_url}")

                await asyncio.sleep(0.75 + (attempt * 0.25))

                email_selectors = [
                    'input[type="email"]',
                    'input[name="loginfmt"]',
                    'input[name="username"]',
                    'input[id*="email"]',
                    'input[id*="user"]',
                    '#i0116',
                    '#email',
                    'input[placeholder*="email"]',
                    'input[placeholder*="user"]'
                ]

                submit_selectors = [
                    'input[type="submit"]',
                    'button[type="submit"]',
                    '#idSIButton9',
                    'input[value="Next"]',
                    'input[value="Sign in"]',
                    'button:has-text("Next")',
                    'button:has-text("Sign in")',
                    'button:has-text("Continue")'
                ]

                error_selectors = [
                    '#usernameError',
                    'div[role="alert"] span',
                    '.error',
                    '[data-test="error"]',
                    '.message_error',
                    '.field-validation-error'
                ]

                password_selectors = [
                    'input[type="password"]',
                    'input[name="passwd"]',
                    '#i0118',
                    '#password',
                    'input[placeholder*="password"]'
                ]

                email_attempts = 0
                max_email_attempts = 5

                while email_attempts < max_email_attempts:
                    logger.info(f"🔍 Looking for email input (attempt {email_attempts + 1}/{max_email_attempts})...")
                    
                    email_selector = await self._wait_for_first_selector(email_selectors, timeout=5000)  # Increased timeout
                    if email_selector:
                        logger.info(f"✅ Found email input: {email_selector}")
                        await self.page.click(email_selector)
                        await self.page.fill(email_selector, "")
                        await self.page.type(email_selector, email, delay=75)  # Slightly slower typing
                        logger.info(f"✅ Email entered using selector: {email_selector}")

                        submit_selector = await self._wait_for_first_selector(submit_selectors, timeout=3000, state='visible')
                        if submit_selector:
                            await self.page.click(submit_selector)
                            logger.info(f"✅ Submit clicked using selector: {submit_selector}")
                        else:
                            await self.page.keyboard.press('Enter')
                            logger.info("✅ Submit via Enter key")

                        # Wait longer for redirect after email submission
                        logger.info("⏳ Waiting for redirect after email submission...")
                        await asyncio.sleep(3)

                        # CHECK IF WE'RE ALREADY ON DASHBOARD after email submission
                        current_url = self.page.url
                        if ('app.elia.io' in current_url and 
                            'login' not in current_url.lower() and
                            'auth' not in current_url.lower()):
                            logger.success("✅ Reached dashboard directly after email submission!")
                            return True

                        # Check for password field appearing
                        if await self._is_selector_present(password_selectors):
                            logger.info("📫 Password prompt detected after email submission")
                            break

                        # Check for email validation errors
                        error_selector = await self._is_selector_present(error_selectors)
                        if error_selector:
                            try:
                                error_text = await self.page.text_content(error_selector)
                                error_text = error_text.strip() if error_text else error_selector
                            except Exception:
                                error_text = error_selector
                            logger.warning(f"⚠️ Email validation message: {error_text}")
                            email_attempts += 1
                            continue

                        # Some flows redisplay another email prompt (e.g., Microsoft after SAML)
                        if await self._is_selector_present(email_selectors):
                            logger.info("🔁 Additional email prompt detected, re-entering email")
                            email_attempts += 1
                            await asyncio.sleep(2)
                            continue

                        # If neither password nor email prompt nor error, break to continue
                        logger.debug("ℹ️ No password prompt yet, waiting briefly")
                        await asyncio.sleep(2)
                        if await self._is_selector_present(password_selectors):
                            break
                    else:
                        # Check if password is already available (skip email step)
                        if await self._is_selector_present(password_selectors):
                            logger.info("ℹ️ Password prompt already available, skipping email step")
                            break
                        
                        email_attempts += 1
                        logger.debug(f"No email input found on attempt {email_attempts}, waiting...")
                        await asyncio.sleep(2)

                if email_attempts >= max_email_attempts and not await self._is_selector_present(password_selectors):
                    raise Exception("Email prompt persisted after multiple attempts")

                password_entered = False
                for selector in password_selectors:
                    try:
                        await self.page.wait_for_selector(selector, timeout=5000, state='visible')
                        await self.page.fill(selector, password)
                        logger.info(f"✅ Password entered using selector: {selector}")
                        password_entered = True
                        break
                    except Exception:
                        continue

                if not password_entered:
                    try:
                        await self.page.evaluate(f"""
                            const inputs = document.querySelectorAll('input[type="password"], input[name="passwd"]');
                            inputs.forEach(input => input.value = '{password}');
                        """)
                        logger.info("✅ Password entered via JavaScript")
                        password_entered = True
                    except Exception:
                        pass

                if not password_entered:
                    raise Exception("Could not enter password")

                submit_selector = await self._wait_for_first_selector(submit_selectors, timeout=2000, state='visible')
                if submit_selector:
                    await self.page.click(submit_selector)
                    logger.info(f"✅ Password submit clicked using selector: {submit_selector}")
                else:
                    await self.page.keyboard.press('Enter')
                    logger.info("✅ Password submit via Enter key")

                logger.info("✅ Microsoft SSO basic auth completed")
                return True

            except Exception as e:
                logger.warning(f"⚠️ SSO attempt {attempt} failed: {e}")
                await self.take_screenshot(f"error_sso_attempt_{attempt}")

                if attempt < max_retries:
                    backoff = 2 ** attempt
                    logger.info(f"⏳ Retrying SSO in {backoff} seconds...")
                    await asyncio.sleep(backoff)
                    try:
                        await self.page.goto('https://app.elia.io/', wait_until='networkidle', timeout=10000)
                    except Exception:
                        pass
                else:
                    logger.error(f"❌ All {max_retries} SSO attempts failed")

        return False
    
    async def handle_mfa(self, method: str = "authenticator", max_retries: int = 3) -> bool:
        """Handle MFA challenge with robust retry logic and improved Microsoft SSO integration"""
        for attempt in range(1, max_retries + 1):
            try:
                logger.info(f"🔢 Handling MFA ({method}) - attempt {attempt}/{max_retries}...")
                
                # Wait for MFA prompt with multiple possible indicators
                mfa_indicators = [
                    'input[name="otc"]',  # TOTP input
                    'input[name="code"]',  # Generic code input
                    'input[placeholder*="code"]',
                    'input[placeholder*="verification"]',
                    '#idTxtBx_SAOTCC_OTC',  # Microsoft specific
                    'text="Enter code"',
                    'text="Verification code"',
                    'text="Authenticator"',
                    'div[role="heading"]:has-text("Approve a sign in request")',
                    'div[role="heading"]:has-text("Approve a request")',
                    'div[role="heading"]:has-text("Enter code")',
                    'div[role="heading"]',  # More generic heading match
                    'h1, h2, h3, h4, h5, h6'  # Any heading that might contain MFA text
                ]

                # Enhanced fallback options for Microsoft SSO
                fallback_links = [
                    'text="Use a different verification option"',
                    'text="I can\'t use my Microsoft Authenticator app right now"',
                    'text="Use verification code"',
                    'text="Approve a request"',
                    'text="Sign in another way"',
                    'button:has-text("Approve")',
                    'button:has-text("Verify")',
                    'button:has-text("Send code")',
                    'button:has-text("Use another method")',
                    'button:has-text("Try another way")',
                    'button:has-text("Next")',
                    'button:has-text("Continue")',
                    'a:has-text("Use a different verification option")',
                    'a:has-text("Sign in another way")'
                ]


                # Check for and handle any MFA approval buttons first
                try:
                    for link in fallback_links:
                        try:
                            if await self.page.is_visible(f'*{link}', timeout=1000):
                                await self.page.click(f'*{link}')
                                logger.info(f"🔁 Selected MFA option: {link}")
                                await asyncio.sleep(2)  # Wait for UI to update
                                break
                        except Exception as e:
                            logger.debug(f"MFA fallback option {link} not found: {str(e)}")
                            continue
                except Exception as e:
                    logger.warning(f"Error handling MFA fallback options: {str(e)}")
                
                # Wait for MFA input field with retry logic
                mfa_prompt_found = False
                for retry in range(3):
                    for indicator in mfa_indicators:
                        try:
                            if indicator.startswith('text='):
                                await self.page.wait_for_selector(f'*{indicator}', timeout=5000)
                            else:
                                await self.page.wait_for_selector(indicator, timeout=5000, state='visible')
                            logger.info(f"🔢 MFA prompt detected: {indicator}")
                            mfa_prompt_found = True
                            break
                        except Exception as e:
                            logger.debug(f"MFA prompt not found with {indicator}: {str(e)}")
                            continue
                    
                    if mfa_prompt_found:
                        break
                    
                    # If we didn't find the prompt, wait and retry
                    if retry < 2:  # Don't wait on the last attempt
                        logger.info(f"No MFA prompt found, retrying in 2 seconds... (attempt {retry + 1}/3)")
                        await asyncio.sleep(2)

                # If we still don't have an MFA prompt, try to proceed anyway
                if not mfa_prompt_found:
                    logger.warning("⚠️  Could not detect MFA prompt, attempting to proceed...")
                
                # Generate and enter TOTP code
                totp = pyotp.TOTP(self.auth_manager.totp_secret)
                totp_code = totp.now()
                logger.info(f"🔢 Generated TOTP code: {totp_code[0:2]}****")
                
                # Try multiple input field selectors
                code_input_selectors = [
                    'input[name="otc"]',
                    'input[name="code"]',
                    'input[type="text"]',
                    'input[type="tel"]',
                    'input[autocomplete*="one"]',
                    'input[inputmode*="numeric"]',
                    'input[inputmode*="tel"]'
                ]
                
                code_entered = False
                for selector in code_input_selectors:
                    try:
                        input_field = await self.page.query_selector(selector)
                        if input_field:
                            await input_field.fill(totp_code)
                            logger.info(f"✅ TOTP code entered using selector: {selector}")
                            code_entered = True
                            break
                    except Exception as e:
                        logger.debug(f"Could not enter code using {selector}: {str(e)}")
                
                if not code_entered:
                    # Last resort: Try to focus and type the code
                    try:
                        await self.page.keyboard.type(totp_code)
                        logger.info("✅ TOTP code entered via keyboard typing")
                    except Exception as e:
                        logger.error(f"❌ Failed to enter TOTP code: {str(e)}")
                        continue
                
                # Try to submit the form
                try:
                    # Try pressing Enter first (works for most forms)
                    await self.page.keyboard.press('Enter')
                    logger.info("✅ Submitted MFA form via Enter key")
                except Exception as e:
                    logger.warning(f"⚠️  Could not submit with Enter: {str(e)}")
                    # Try to find and click a submit button
                    submit_buttons = await self.page.query_selector_all('button[type="submit"], input[type="submit"], button:has-text("Verify"), button:has-text("Submit"), button:has-text("Continue")')
                    if submit_buttons:
                        try:
                            await submit_buttons[0].click()
                            logger.info("✅ Submitted MFA form via button click")
                        except Exception as e:
                            logger.warning(f"⚠️  Could not click submit button: {str(e)}")
                
                # After MFA submission, wait for navigation and handle potential redirects
                logger.info("⏳ Waiting for MFA verification and potential redirects...")
                
                # Wait for navigation with a longer timeout
                try:
                    await asyncio.wait_for(self.page.wait_for_load_state('networkidle'), timeout=20.0)
                    await asyncio.sleep(2)  # Additional wait for any client-side redirects
                except Exception as e:
                    logger.warning(f"⚠️  Navigation wait timed out: {str(e)}")
                
                # Take a screenshot for debugging
                await self.take_screenshot("post_mfa_submission")
                
                # Check if we're back at the login page after MFA (failed MFA or redirect loop)
                current_url = self.page.url.lower()
                login_domains = ['login.microsoftonline.com', 'login.live.com', 'account.live.com']
                
                if any(domain in current_url for domain in login_domains):
                    # Enhanced error detection
                    try:
                        error_messages = [
                            'error', 'incorrect', 'invalid', 'try again', 'something went wrong',
                            'unable to sign in', 'sign-in was blocked', 'account is locked',
                            'temporarily disabled', 'suspicious activity', 'unusual sign-in',
                            'verify your identity', 'additional verification', 'security info',
                            'we couldn\'t sign you in', 'your account has been locked',
                            'this account has been locked', 'too many attempts'
                        ]
                        
                        # Check for error messages in the page content
                        page_content = (await self.page.content()).lower()
                        found_errors = [msg for msg in error_messages if msg in page_content]
                        
                        if found_errors:
                            self.logger.warning(f"⚠️  MFA failed - detected error messages: {', '.join(found_errors)[:100]}...")
                            return False
                            
                        # Check for specific error elements
                        error_selectors = [
                            'div#error', 'div.error', 'div.alert-error', 'div.message-error',
                            'div.error-message', 'span.error', 'p.error', 'div[role="alert"]',
                            'div[class*="error"]', 'div[class*="alert"]', 'div[class*="message"]'
                        ]
                        
                        for selector in error_selectors:
                            error_element = await self.page.query_selector(selector)
                            if error_element:
                                error_text = (await error_element.inner_text()).strip()
                                if error_text and len(error_text) < 500:  # Sanity check for error text length
                                    self.logger.warning(f"⚠️  MFA failed - error: {error_text}")
                                    return False
                    except Exception as e:
                        logger.warning(f"⚠️  Error checking MFA failure: {str(e)}")
                
                # Check for MFA retry prompt or other indicators
                retry_indicators = [
                    'try another way', 'i can\'t use my authenticator app',
                    'sign in another way', 'try a different verification method',
                    'i don\'t have access to this', 'having trouble?', 'trouble signing in?'
                ]
                
                # Look for retry indicators in buttons and links
                all_elements = await self.page.query_selector_all('a, button, input[type="button"], input[type="submit"]')
                for element in all_elements:
                    try:
                        element_text = (await element.inner_text()).lower()
                        if any(indicator in element_text for indicator in retry_indicators):
                            self.logger.warning(f"⚠️  MFA failed - retry prompt detected: {element_text}")
                            return False
                    except:
                        continue
                
                # If we're back at the email entry page, MFA failed
                email_input = await self.page.query_selector('input[type="email"]')
                if email_input:
                    self.logger.warning("⚠️  Redirected back to email entry - MFA likely failed")
                    return False
                
                # Last resort: Check for any interactive elements that might help us proceed
                self.logger.warning("⚠️  Possible redirect loop after MFA - attempting to find a way forward...")
                
                # Try to find and click a "Continue" or "Next" button if present
                possible_actions = [
                    ('continue', ['continue', 'next', 'proceed', 'ok', 'yes', 'verify', 'submit']),
                ('skip', ['skip', 'maybe later', 'do this later', 'not now']),
                ('use another method', ['use another method', 'try another way', 'other options'])
            ]
            
                clicked = False
                for action_name, keywords in possible_actions:
                    if clicked:
                        break
                        
                    for element in all_elements:
                        try:
                            element_text = (await element.inner_text()).lower()
                            if any(keyword in element_text for keyword in keywords):
                                await element.click()
                                self.logger.info(f"✅ Clicked '{element_text.strip()}' button to {action_name}")
                                await asyncio.sleep(3)  # Wait for navigation
                                clicked = True
                                break
                        except:
                            continue
            
            # If we're still on a login page after attempting to proceed, log detailed info
                current_url = self.page.url.lower()
                if any(domain in current_url for domain in login_domains):
                    # Take another screenshot for debugging
                    await self.take_screenshot("post_mfa_redirect_attempt")
                    
                    # Log page title and URL for debugging
                    page_title = await self.page.title()
                    self.logger.warning(f"⚠️  Still on login page after MFA - Title: {page_title}")
                    self.logger.warning(f"⚠️  Current URL: {current_url}")
                
                # Log visible text (first 500 chars) for context
                try:
                    visible_text = await self.page.evaluate('''() => {
                        return document.body.innerText;
                    }''')
                    self.logger.warning(f"⚠️  Page content preview: {visible_text[:500]}...")
                except:
                    self.logger.warning("⚠️  Could not retrieve page content")
                
                return False
                
                # After MFA success checks
                logger.info("✅ MFA verification appears successful")
                return True
                
            except Exception as e:
                logger.warning(f"⚠️ MFA attempt {attempt} failed: {e}")
                await self.take_screenshot(f"error_mfa_attempt_{attempt}")

    async def _detect_login_loop(self, current_url: str) -> bool:
        """Detect if we're stuck in a login redirect loop."""
        login_indicators = ['login', 'auth', 'signin', 'microsoftonline']
        
        # If we're on a login page but have already authenticated, this might be a redirect loop
        if any(indicator in current_url.lower() for indicator in login_indicators):
            logger.warning("⚠️ Detected potential redirect loop back to login page")
            
            # Try to detect if we're in a login form
            has_login_form = await self.page.evaluate("""
                () => {
                    const formElements = [
                                        document.querySelector('input[type="password"]'),
                                        document.querySelector('input[name*="pass"]'),
                                        document.querySelector('button[type="submit"]'),
                                        document.querySelector('input[type="submit"]')
                                    ].filter(el => el !== null);
                                    
                                    return {
                                        hasLoginForm: formElements.length > 0,
                                        formElementCount: formElements.length,
                                        pageTitle: document.title,
                                        formAction: document.querySelector('form')?.action || 'none',
                                        hasEmailField: document.querySelector('input[type="email"], input[name*="email"]') !== null,
                                        hasPasswordField: document.querySelector('input[type="password"], input[name*="pass"]') !== null
                                    };
                                }
                            """)
                            
            logger.info(f"🔍 Login page analysis: {has_login_form}")
            
            # If we see a login form with email/password after MFA, we're likely in a loop
            if has_login_form.get('hasLoginForm') and has_login_form.get('hasEmailField'):
                logger.error("❌ Detected login form after MFA - likely a redirect loop")
                
                # Try to get any error messages
                try:
                    error_messages = await self.page.evaluate("""
                                        () => {
                                            const errorSelectors = [
                                                '.error', '.alert', '.message', '.validation',
                                                '[role="alert"]', '[aria-live="assertive"]',
                                                '.error-message', '.alert-message', '.message-error'
                                            ];
                                            
                                            const errors = [];
                                            errorSelectors.forEach(selector => {
                                                document.querySelectorAll(selector).forEach(el => {
                                                    const text = el.textContent.trim();
                                                    if (text && !errors.includes(text)) {
                                                        errors.push(text);
                                                    }
                                                });
                                            });
                                            
                                            return errors;
                                        }
                                    """)
                    
                    if error_messages:
                        logger.error(f"❌ Error messages on login page: {error_messages}")
                    
                except Exception as e:
                    logger.debug(f"Could not extract error messages: {e}")
                
                return False
            
            # Check for MFA input elements
            mfa_still_present = await self._is_selector_present([
                'input[name="otc"]',
                'input[name="code"]',
                '#idTxtBx_SAOTCC_OTC',
                'button:has-text("Verify")',
                'button:has-text("Submit")',
                'button:has-text("Continue")',
                'button:has-text("Next")',
                'button:has-text("Sign in")',
                'button:has-text("Approve")',
                'button:has-text("Allow")',
                'button:has-text("Confirm")',
                'button:has-text("Done")',
                'button:has-text("Finish")',
                'button:has-text("Close")',
                'button:has-text("OK")',
                'button:has-text("Got it")',
                'button:has-text("I understand")',
                'button:has-text("I agree")',
                'button:has-text("I accept")',
                'button:has-text("I confirm")',
                'button:has-text("I acknowledge")'
            ])
            
            # If MFA input is gone and we've been redirected
            if not mfa_still_present and elapsed > 5:
                current_url = self.page.url.lower()
                login_indicators = ['login', 'auth', 'signin', 'microsoftonline']
                
                if not any(indicator in current_url for indicator in login_indicators):
                    logger.info(f"✅ MFA input cleared and not on login page, assuming success. Current URL: {self.page.url}")
                    await asyncio.sleep(2)  # Wait for any final redirects
                    return True
                else:
                    logger.info(f"⚠️ MFA input cleared but still on login page. Current URL: {self.page.url}")
                
                # Try to find and click any continue/next buttons
                continue_buttons = [
                    'button:has-text("Continue")',
                    'button:has-text("Next")',
                    'button:has-text("Sign in")',
                    'button:has-text("Approve")',
                    'button:has-text("Allow")',
                    'button:has-text("Confirm")',
                    'button:has-text("Done")',
                    'button:has-text("Finish")',
                    'button:has-text("Close")',
                    'button:has-text("OK")',
                    'button:has-text("Got it")',
                    'button:has-text("I understand")',
                    'button:has-text("I agree")',
                    'button:has-text("I accept")',
                    'button:has-text("I confirm")',
                    'button:has-text("I acknowledge")',
                    'input[type="submit"]',
                    'button[type="submit"]',
                    'button:has-text("Submit")',
                    'button:has-text("Continue")',
                    'button:has-text("Next")',
                    'button:has-text("Sign in")',
                    'button:has-text("Approve")',
                    'button:has-text("Allow")',
                    'button:has-text("Confirm")',
                    'button:has-text("Done")',
                    'button:has-text("Finish")',
                    'button:has-text("Close")',
                    'button:has-text("OK")',
                    'button:has-text("Got it")',
                    'button:has-text("I understand")',
                    'button:has-text("I agree")',
                    'button:has-text("I accept")',
                    'button:has-text("I confirm")',
                    'button:has-text("I acknowledge")'
                ]
                
                for button_sel in continue_buttons:
                    try:
                        if await self.page.is_visible(button_sel, timeout=1000):
                            await self.page.click(button_sel)
                            logger.info(f"✅ Clicked button: {button_sel}")
                            await asyncio.sleep(2)  # Wait for any redirects
                            return True
                    except Exception as e:
                        continue
                
                # Take periodic screenshots for debugging
                if elapsed % 10 == 0:  # Every 10 seconds
                    await self.take_screenshot(f"mfa_wait_{elapsed}s")
                
                # Try to get page title and URL for debugging
                try:
                    page_title = await self.page.title()
                    page_url = self.page.url
                    logger.info(f"🔄 Waiting for MFA... Title: {page_title}, URL: {page_url}")
                    
                    # Check for any visible text that might indicate the current state
                    try:
                        visible_text = await self.page.evaluate("""
                                        () => {
                                            const allText = [];
                                            const walker = document.createTreeWalker(
                                                document.body,
                                                NodeFilter.SHOW_TEXT,
                                                null,
                                                false
                                            );
                                            
                                            let node;
                                            while (node = walker.nextNode()) {
                                                const text = node.textContent.trim();
                                                if (text.length > 10 && text.length < 100) {
                                                    allText.push(text);
                                                }
                                                if (allText.length > 10) break; // Limit to first 10 visible texts
                                            }
                                            return allText.join(' | ');
                                        }
                                    """)
                        
                        if visible_text:
                            logger.info(f"📄 Page content: {visible_text[:200]}...")
                    except Exception as e:
                        logger.debug(f"Could not get page text: {e}")
                    
                except Exception as e:
                    logger.debug(f"Could not get page title/URL: {e}")
                
                await asyncio.sleep(check_interval)
                elapsed += check_interval
        
        # Timeout - log detailed information before failing
        logger.warning("⚠️ MFA verification timeout - gathering diagnostic information...")
        
        try:
            # Get final page state
            final_url = self.page.url
            final_title = await self.page.title()
            logger.warning(f"🔍 Final URL: {final_url}")
            logger.warning(f"🔍 Page title: {final_title}")
            
            # Take a screenshot
            screenshot_path = await self.take_screenshot("mfa_timeout_final")
            logger.warning(f"📸 Screenshot saved to: {screenshot_path}")
            
            # Log page content for debugging
            try:
                page_content = await self.page.content()
                logger.debug(f"📄 Page content (first 1000 chars): {page_content[:1000]}...")
            except Exception as e:
                logger.debug(f"Could not get page content: {e}")
            
        except Exception as e:
            logger.error(f"❌ Error gathering diagnostic information: {e}")
        
        return False
    async def wait_for_dashboard(self, timeout: int = 60000) -> bool:
        """Wait for successful login and dashboard load with flexible detection"""
        try:
            logger.info("⏳ Waiting for dashboard to load...")
            
            # IMMEDIATE CHECK: See if we're already on a non-auth page
            current_url = self.page.url
            logger.info(f"🔗 Current URL at start: {current_url}")
            
            if ('login' not in current_url.lower() and 
                'auth' not in current_url.lower() and
                'signin' not in current_url.lower() and
                'error' not in current_url.lower()):
                logger.info("✅ Already on non-auth page - checking for dashboard")
                
                # Quick check for interactive elements
                try:
                    interactive_count = await self.page.evaluate("""
                        () => document.querySelectorAll('button, a, input, select').length
                    """)
                    logger.info(f"📊 Found {interactive_count} interactive elements")
                    if interactive_count > 3:
                        await self.take_screenshot("dashboard_immediate")
                        logger.success("✅ Dashboard detected immediately")
                        return True
                except Exception as e:
                    logger.debug(f"Interactive element check failed: {e}")
            
            # More flexible URL patterns for different auth flows
            dashboard_url_patterns = [
                '**/app.elia.io/**',
                '**/elia.io/**',
                '**/parking/**',  # Sometimes redirects to parking subdomain
                '**/*parking*',   # Contains parking in URL
                '**/dashboard/**',
                '**/home/**',
                '**/reservation/**',
                '**/book/**',
                '**/map/**',
                '**/calendar/**',
                '**/profile/**',
                '**/settings/**',
                '**/account/**',
                '**/user/**',
                '**/my/**',
                '**/secure/**',
                '**/app/**',
                '**/web/**',
                '**/portal/**',
                '**/main/**',
                '**/index.html',
                '**/index.aspx',
                '**/default.aspx',
                '**/main.aspx'
            ]
            
            # Wait for any of the dashboard URL patterns
            url_detected = False
            for pattern in dashboard_url_patterns:
                try:
                    await self.page.wait_for_url(pattern, timeout=15000)  # 15 seconds per pattern
                    logger.info(f"✅ Dashboard URL detected: {pattern}")
                    url_detected = True
                    break
                except:
                    continue
            
            if not url_detected:
                # If no specific URL pattern matches, wait for page to stabilize
                logger.info("⏳ Waiting for page to stabilize...")
                await asyncio.sleep(5)  # Increased wait time
                
                # Check current URL
                current_url = self.page.url
                logger.info(f"📍 Current URL after wait: {current_url}")
                
                # Accept any URL that doesn't contain login/auth terms
                if ('login' not in current_url.lower() and 
                    'auth' not in current_url.lower() and
                    'signin' not in current_url.lower()):
                    logger.info("✅ On non-auth page after stabilization")
                    url_detected = True
            
            if not url_detected:
                logger.warning(f"⚠️ No dashboard URL pattern matched, current URL: {self.page.url}")
                # Continue anyway - might still be on dashboard
            
            # Wait for page to be interactive and check for dashboard elements
            await asyncio.sleep(2)
            
            # Debug: Log current page content
            try:
                page_title = await self.page.title()
                logger.info(f"📄 Page title: {page_title}")
            except:
                logger.debug("Could not get page title")
            
            # Debug: Check for any visible text on page
            try:
                visible_text = await self.page.evaluate("""
                    () => {
                        const elements = document.querySelectorAll('*');
                        const texts = [];
                        for (let el of elements) {
                            const text = el.textContent?.trim();
                            if (text && text.length > 3 && el.offsetParent !== null) {
                                texts.push(text.substring(0, 50));
                                if (texts.length >= 5) break; // Limit to first 5 visible texts
                            }
                        }
                        return texts;
                    }
                """)
                if visible_text:
                    logger.info(f"📝 Visible text: {visible_text[:2]}")  # Show first 2
            except Exception as e:
                logger.debug(f"Could not extract visible text: {e}")
            
            # Debug: Check current URL again
            current_url = self.page.url
            logger.info(f"🔗 Final URL: {current_url}")
            
            # AGGRESSIVE SUCCESS CHECK: If we're not on auth pages and have some content, assume success
            if ('login' not in current_url.lower() and 
                'auth' not in current_url.lower() and
                'signin' not in current_url.lower() and
                'error' not in current_url.lower()):
                
                # Check if page has loaded any content
                try:
                    body_text = await self.page.evaluate("() => document.body ? document.body.textContent.length : 0")
                    if body_text > 100:  # If page has substantial content
                        logger.info(f"📄 Page has {body_text} characters of content")
                        await self.take_screenshot("dashboard_success")
                        logger.success("✅ Dashboard loaded successfully (content check)")
                        return True
                except:
                    pass
            
            # Try to detect dashboard elements with more comprehensive checks
            dashboard_indicators = [
                # Text-based indicators
                'text="Parking"',
                'text="Réservation"',
                'text="Reservation"',
                'text="Dashboard"',
                'text="Welcome"',
                'text="Bonjour"',
                'text="Spot"',
                'text="Place"',
                
                # Element-based indicators
                '[data-testid*="parking"]',
                '[data-testid*="dashboard"]',
                '.parking-grid',
                '.dashboard',
                '.parking-spots',
                '.spots-container',
                '.reservation-form',
                'nav',
                'header',
                '.main-content',
                '#app',  # Common SPA root
                '.app-container',
                
                # Button/link indicators
                'button:has-text("Reserve")',
                'button:has-text("Réserver")',
                'a:has-text("Parking")',
                'a:has-text("Dashboard")',
                
                # Generic page structure
                'h1',
                'h2',
                '.card',
                '.panel'
            ]
            
            dashboard_detected = False
            for indicator in dashboard_indicators:
                try:
                    if indicator.startswith('text='):
                        await self.page.wait_for_selector(f'*{indicator}', timeout=5000)  # Reduced timeout
                    else:
                        await self.page.wait_for_selector(indicator, timeout=5000, state='visible')
                    logger.info(f"✅ Dashboard element detected: {indicator}")
                    dashboard_detected = True
                    break
                except:
                    continue
            
            if dashboard_detected:
                # Additional wait for dashboard to fully load
                await asyncio.sleep(2)
                
                # Take screenshot of successful dashboard load
                await self.take_screenshot("dashboard_loaded")
                
                logger.success("✅ Dashboard loaded successfully")
                return True
            else:
                # FINAL FALLBACK: If we're not on auth pages, assume success
                current_url = self.page.url
                if ('login' not in current_url.lower() and 
                    'auth' not in current_url.lower() and
                    'signin' not in current_url.lower() and
                    'error' not in current_url.lower()):
                    
                    logger.info("⚠️ No specific dashboard indicators found, but not on auth page - proceeding")
                    await self.take_screenshot("dashboard_fallback")
                    
                    # Check for basic page loaded indicators
                    try:
                        has_body = await self.page.evaluate("() => !!document.body")
                        has_title = await self.page.evaluate("() => !!document.title")
                        
                        if has_body and has_title:
                            logger.info("✅ Basic page structure detected - assuming dashboard")
                            return True
                    except:
                        pass
                    
                    return True
                else:
                    logger.warning(f"⚠️ Still on auth-related page: {current_url}")
                    await self.take_screenshot("error_dashboard")
                    return False
            
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

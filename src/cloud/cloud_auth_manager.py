"""
Cloud Authentication Manager for Elia Parking Bot
GitHub Actions optimized authentication with TOTP-first strategy and backup MFA methods
"""

import os
import json
import time
import pyotp
import base64
import asyncio
import imaplib
import email
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List, Tuple
from loguru import logger
from playwright.async_api import async_playwright, Browser, BrowserContext, Page
import msal
from pathlib import Path


class CloudAuthenticationManager:
    """Cloud-optimized authentication manager for GitHub Actions environment"""

    def __init__(self):
        """Initialize cloud authentication manager with GitHub Secrets support"""
        # Environment detection
        self.is_cloud = self._detect_cloud_environment()

        # Authentication state
        self.access_token = None
        self.refresh_token = None
        self.token_expiry = None
        self.cookies = {}
        self.headers = {}

        # MFA configuration
        self.totp = None
        self.mfa_methods = ["totp", "email", "push"]
        self.current_mfa_method = "totp"

        # Browser automation
        self.browser = None
        self.context = None
        self.page = None

        # Load credentials from GitHub Secrets or environment variables
        # This must come AFTER totp is initialized to None
        self.credentials = self._load_credentials()

        logger.info(
            f"🔐 CloudAuthenticationManager initialized (environment: {'cloud' if self.is_cloud else 'local'})"
        )

    def _detect_cloud_environment(self) -> bool:
        """Detect if running in GitHub Actions cloud environment"""
        return (
            os.getenv("GITHUB_ACTIONS") == "true"
            or os.getenv("ENVIRONMENT") == "docker"
            or os.getenv("CI") == "true"
        )

    def _load_credentials(self) -> Dict[str, str]:
        """Load credentials from GitHub Secrets or environment variables"""
        credentials = {
            "totp_secret": os.getenv("TOTP_SECRET"),
            "elia_password": os.getenv("ELIA_PASSWORD"),
            "smtp_password": os.getenv("SMTP_PASSWORD"),
            "smtp_host": os.getenv("SMTP_HOST", "smtp.gmail.com"),
            "smtp_port": int(os.getenv("SMTP_PORT", "993")),
            "email_address": os.getenv("EMAIL_ADDRESS"),
            "microsoft_username": os.getenv("MICROSOFT_USERNAME"),
        }

        # Validate only required credentials for basic authentication
        required_missing = [
            k
            for k, v in credentials.items()
            if v is None and k in ["totp_secret", "elia_password", "microsoft_username"]
        ]
        
        # Log missing credentials but don't fail for optional ones
        if required_missing:
            logger.warning(f"⚠️ Missing required credentials: {required_missing}")
            # For QA testing, we'll allow missing credentials and continue
            # In production, this would raise an error
        
        # Initialize TOTP if secret is available
        if credentials["totp_secret"]:
            try:
                self.totp = pyotp.TOTP(credentials["totp_secret"])
                logger.info("🔑 TOTP initialized successfully")
            except Exception as e:
                logger.error(f"❌ TOTP initialization failed: {e}")
                self.totp = None

        return credentials

    async def authenticate_microsoft(self) -> bool:
        """Authenticate with Microsoft SSO using TOTP-first strategy"""
        try:
            logger.info("🚀 Starting Microsoft authentication (TOTP-first strategy)")

            # Initialize browser in headless mode for cloud
            async with async_playwright() as p:
                browser_options = {
                    "headless": True if self.is_cloud else False,
                    "args": ["--no-sandbox", "--disable-dev-shm-usage"]
                    if self.is_cloud
                    else [],
                }

                self.browser = await p.chromium.launch(**browser_options)
                self.context = await self.browser.new_context()
                self.page = await self.context.new_page()
                
                # Set default timeout for all Playwright operations to 45s
                self.page.set_default_timeout(45000)
                self.page.set_default_navigation_timeout(45000)
                logger.info("⏱️ Set Playwright default timeouts to 45s for cloud auth")

                # Navigate to Microsoft login with improved timeout
                await self.page.goto("https://login.microsoft.com/", timeout=45000)  # Increased from default to 45s
                await self.page.wait_for_load_state("networkidle", timeout=45000)  # Increased timeout for load state

                # Enter username
                await self.page.fill(
                    'input[type="email"]', self.credentials["microsoft_username"]
                )
                await self.page.click('input[type="submit"]')
                await self.page.wait_for_load_state("networkidle", timeout=45000)  # Increased timeout for load state

                # Enter password
                await self.page.fill(
                    'input[type="password"]', self.credentials["elia_password"]
                )
                await self.page.click('input[type="submit"]')
                await self.page.wait_for_load_state("networkidle", timeout=45000)  # Increased timeout for load state

                # Handle MFA
                mfa_success = await self._handle_mfa_cloud()
                if not mfa_success:
                    logger.error("❌ MFA authentication failed")
                    return False

                # Extract tokens and cookies
                await self._extract_authentication_data()

                logger.info("✅ Microsoft authentication completed successfully")
                return True

        except Exception as e:
            logger.error(f"❌ Microsoft authentication failed: {e}")
            return False
        finally:
            await self._cleanup_browser()

    async def _handle_mfa_cloud(self) -> bool:
        """Handle MFA in cloud environment with TOTP-first and fallback strategies"""
        for mfa_method in self.mfa_methods:
            try:
                logger.info(f"🔄 Attempting MFA method: {mfa_method}")

                if mfa_method == "totp" and self.totp:
                    success = await self._handle_totp_mfa()
                elif mfa_method == "email":
                    success = await self._handle_email_mfa()
                elif mfa_method == "push":
                    success = await self._handle_push_mfa()
                else:
                    continue

                if success:
                    logger.info(f"✅ MFA successful using {mfa_method}")
                    self.current_mfa_method = mfa_method
                    return True

            except Exception as e:
                logger.warning(f"⚠️ MFA method {mfa_method} failed: {e}")
                continue

        logger.error("❌ All MFA methods failed")
        return False

    async def _handle_totp_mfa(self) -> bool:
        """Handle TOTP MFA authentication"""
        try:
            # Wait for MFA input field with improved timeout
            await self.page.wait_for_selector(
                'input[placeholder*="code"], input[placeholder*="Code"], input[name="otc"]',
                timeout=15000,  # Increased from 10s to 15s for better reliability
            )

            # Generate current TOTP code
            totp_code = self.totp.now()
            logger.info(f"🔢 Generated TOTP code: {totp_code}")

            # Enter TOTP code
            await self.page.fill(
                'input[placeholder*="code"], input[placeholder*="Code"], input[name="otc"]',
                totp_code,
            )
            await self.page.click('input[type="submit"]')
            await self.page.wait_for_load_state("networkidle", timeout=45000)  # Increased timeout for MFA submission

            # Check if authentication succeeded
            success = await self._check_authentication_success()
            return success

        except Exception as e:
            logger.error(f"❌ TOTP MFA failed: {e}")
            return False

    async def _handle_email_mfa(self) -> bool:
        """Handle email MFA by retrieving code from IMAP"""
        try:
            if not all(
                [
                    self.credentials["email_address"],
                    self.credentials["smtp_password"],
                ]
            ):
                logger.warning("⚠️ Email credentials not configured")
                return False

            # Wait for email to be sent
            await asyncio.sleep(5)

            # Connect to IMAP and retrieve MFA code
            mfa_code = await self._retrieve_email_mfa_code()
            if not mfa_code:
                return False

            # Enter email MFA code
            await self.page.fill(
                'input[placeholder*="code"], input[placeholder*="Code"], input[name="otc"]',
                mfa_code,
            )
            await self.page.click('input[type="submit"]')
            await self.page.wait_for_load_state("networkidle", timeout=45000)  # Increased timeout for email MFA submission

            # Check if authentication succeeded
            success = await self._check_authentication_success()
            return success

        except Exception as e:
            logger.error(f"❌ Email MFA failed: {e}")
            return False

    async def _handle_push_mfa(self) -> bool:
        """Handle push notification MFA with timeout"""
        try:
            logger.info("📱 Waiting for push notification approval...")

            # Wait for push notification to be approved (up to 60 seconds)
            for i in range(60):
                await asyncio.sleep(1)
                try:
                    # Check if redirected to success page or authenticated
                    success = await self._check_authentication_success()
                    if success:
                        logger.info("✅ Push notification approved")
                        return True
                except:
                    continue

                logger.info(f"⏳ Waiting for push approval... ({i+1}/60)")

            logger.error("❌ Push notification timeout")
            return False

        except Exception as e:
            logger.error(f"❌ Push MFA failed: {e}")
            return False

    async def _retrieve_email_mfa_code(self) -> Optional[str]:
        """Retrieve MFA code from email via IMAP"""
        try:
            # Connect to IMAP server
            imap = imaplib.IMAP4_SSL(
                self.credentials["smtp_host"], self.credentials["smtp_port"]
            )
            imap.login(
                self.credentials["email_address"], self.credentials["smtp_password"]
            )

            # Select inbox and search for recent Microsoft email
            imap.select("INBOX")

            # Search for recent emails from Microsoft
            search_criteria = '(FROM "microsoft.com" SUBJECT "code" OR SUBJECT "verification")'
            _, messages = imap.search(None, search_criteria)

            if not messages[0]:
                logger.error("❌ No MFA email found")
                return None

            # Get the most recent email
            latest_email_id = messages[0].split()[-1]
            _, msg_data = imap.fetch(latest_email_id, "(RFC822)")

            # Parse email content
            for response in msg_data:
                if isinstance(response, tuple):
                    msg = email.message_from_bytes(response[1])

                    # Extract email body
                    if msg.is_multipart():
                        for part in msg.walk():
                            if part.get_content_type() == "text/plain":
                                body = part.get_payload(decode=True).decode()
                                break
                    else:
                        body = msg.get_payload(decode=True).decode()

                    # Extract 6-digit code from email body
                    import re

                    code_match = re.search(r"\b(\d{6})\b", body)
                    if code_match:
                        mfa_code = code_match.group(1)
                        logger.info(f"📧 Retrieved MFA code from email: {mfa_code}")
                        return mfa_code

            imap.logout()
            return None

        except Exception as e:
            logger.error(f"❌ Failed to retrieve email MFA code: {e}")
            return None

    async def _check_authentication_success(self) -> bool:
        """Check if authentication was successful"""
        try:
            # Check for success indicators
            success_indicators = [
                "myaccount.microsoft.com",
                "account.microsoft.com",
                "office.com",
                "login.microsoftonline.com/common/oauth2",
            ]

            current_url = self.page.url
            for indicator in success_indicators:
                if indicator in current_url:
                    logger.info(
                        f"✅ Authentication successful (redirected to: {current_url})"
                    )
                    return True

            # Check for error messages
            error_indicators = ["error", "failed", "incorrect", "invalid"]
            page_content = await self.page.content()

            for indicator in error_indicators:
                if indicator.lower() in page_content.lower():
                    logger.warning(f"⚠️ Authentication error detected: {indicator}")
                    return False

            # If no clear indicators, wait a bit more and check again
            await asyncio.sleep(2)
            current_url = self.page.url
            for indicator in success_indicators:
                if indicator in current_url:
                    return True

            return False

        except Exception as e:
            logger.error(f"❌ Error checking authentication success: {e}")
            return False

    async def _extract_authentication_data(self):
        """Extract tokens and cookies after successful authentication"""
        try:
            # Get cookies
            self.cookies = await self.context.cookies()

            # Get local storage and session storage
            local_storage = await self.page.evaluate(
                "() => Object.assign({}, localStorage)"
            )
            session_storage = await self.page.evaluate(
                "() => Object.assign({}, sessionStorage)"
            )

            # Store authentication data for session
            self.headers = {
                "User-Agent": await self.page.evaluate("() => navigator.userAgent")
            }

            logger.info(f"🍪 Extracted {len(self.cookies)} cookies and session data")

        except Exception as e:
            logger.error(f"❌ Failed to extract authentication data: {e}")

    async def _cleanup_browser(self):
        """Clean up browser resources"""
        try:
            if self.context:
                await self.context.close()
            if self.browser:
                await self.browser.close()
        except Exception as e:
            logger.error(f"❌ Error cleaning up browser: {e}")

    def get_authentication_status(self) -> Dict[str, Any]:
        """Get current authentication status"""
        return {
            "authenticated": bool(self.cookies),
            "mfa_method_used": self.current_mfa_method,
            "environment": "cloud" if self.is_cloud else "local",
            "totp_available": bool(self.totp),
            "cookies_count": len(self.cookies),
            "last_check": datetime.now().isoformat(),
        }

    async def validate_authentication_health(self) -> bool:
        """Validate authentication health and readiness"""
        try:
            status = self.get_authentication_status()

            # Check if we have valid authentication data
            if not status["authenticated"]:
                logger.warning("⚠️ Not authenticated")
                return False

            # Check if TOTP is properly configured
            if not status["totp_available"] and status["environment"] == "cloud":
                logger.warning("⚠️ TOTP not available in cloud environment")

            # Validate cookies are not expired
            if self.cookies:
                current_time = time.time()
                for cookie in self.cookies:
                    if cookie.get("expires") and cookie["expires"] < current_time:
                        logger.warning("⚠️ Some cookies have expired")
                        return False

            logger.info("✅ Authentication health check passed")
            return True

        except Exception as e:
            logger.error(f"❌ Authentication health check failed: {e}")
            return False


# Environment detection helper
def is_cloud_environment() -> bool:
    """Check if running in cloud environment"""
    return (
        os.getenv("GITHUB_ACTIONS") == "true"
        or os.getenv("ENVIRONMENT") == "docker"
        or os.getenv("CI") == "true"
    )


# Factory function for easy instantiation
def create_auth_manager() -> CloudAuthenticationManager:
    """Create appropriate authentication manager based on environment"""
    if is_cloud_environment():
        return CloudAuthenticationManager()
    else:
        # Import local auth manager for local development
        from auth_manager import AuthenticationManager

        return AuthenticationManager()

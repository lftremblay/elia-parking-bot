#!/usr/bin/env python3
"""
Improved Authentication Flow
Enhanced authentication with better timeout handling and retry logic
"""

import asyncio
import time
from typing import Optional
from loguru import logger

class ImprovedAuthFlow:
    """Improved authentication flow with timeout fixes"""
    
    def __init__(self, page, config, totp):
        self.page = page
        self.config = config
        self.totp = totp
        self.max_auth_timeout = 45000  # 45 seconds
        self.mfa_timeout = 15000      # 15 seconds
        self.retry_attempts = 3
        self.retry_backoff = [5000, 10000, 15000]  # 5s, 10s, 15s
    
    async def authenticate_with_improved_timeout(self):
        """Enhanced authentication with better timeout handling"""
        
        for attempt in range(self.retry_attempts):
            try:
                logger.info(f"🔐 Authentication attempt {attempt + 1}/{self.retry_attempts}")
                
                # Step 1: Navigate to login with extended timeout
                await self.page.goto(self.config["elia"]["url"], timeout=self.max_auth_timeout)
                await self.page.wait_for_load_state("networkidle", timeout=self.max_auth_timeout)
                
                # Step 2: Handle organization entry
                await self._handle_organization_improved()
                
                # Step 3: Handle SSO with retry logic
                auth_success = await self._handle_sso_with_retry()
                if auth_success:
                    return True
                    
            except Exception as e:
                logger.error(f"❌ Authentication attempt {attempt + 1} failed: {e}")
                
                if attempt < self.retry_attempts - 1:
                    wait_time = self.retry_backoff[attempt]
                    logger.info(f"⏳ Waiting {wait_time}ms before retry...")
                    await asyncio.sleep(wait_time / 1000)
                else:
                    logger.error("❌ All authentication attempts failed")
                    return False
        
        return False
    
    async def _handle_organization_improved(self):
        """Handle organization entry with better error handling"""
        try:
            # Wait for organization field with extended timeout
            org_input = await self.page.wait_for_selector(
                'input[name="organization"], input[placeholder*="organization"]',
                timeout=15000  # 15 seconds
            )
            
            await org_input.fill(self.config["elia"]["organization"])
            await self.page.click('button[type="submit"], input[type="submit"]')
            await self.page.wait_for_load_state("networkidle", timeout=15000)
            
        except Exception as e:
            logger.warning(f"⚠️ Organization handling issue: {e}")
            # Continue anyway - might already be logged in
    
    async def _handle_sso_with_retry(self):
        """Handle SSO authentication with improved timeout"""
        try:
            # Wait for SSO redirect with extended timeout
            await self.page.wait_for_url(
                "**/elia.kinde.com/**", 
                timeout=self.max_auth_timeout
            )
            
            # Handle email input
            email_input = await self.page.wait_for_selector(
                'input[type="email"]',
                timeout=15000
            )
            await email_input.fill(self.config["elia"]["credentials"]["email"])
            await self.page.click('input[type="submit"], button[type="submit"]')
            
            # Handle MFA with improved timeout
            return await self._handle_mfa_improved()
            
        except Exception as e:
            logger.error(f"❌ SSO handling failed: {e}")
            return False
    
    async def _handle_mfa_improved(self):
        """Handle MFA with better timeout and error detection"""
        try:
            # Wait for MFA input with extended timeout
            mfa_input = await self.page.wait_for_selector(
                'input[placeholder*="code"], input[placeholder*="Code"], input[name="otc"]',
                timeout=self.mfa_timeout
            )
            
            # Generate and enter TOTP code
            totp_code = self.totp.now()
            await mfa_input.fill(totp_code)
            await self.page.click('input[type="submit"]')
            
            # Wait for authentication completion with multiple checks
            try:
                # Check for successful redirect to dashboard
                await self.page.wait_for_url(
                    "**/dashboard**",
                    timeout=10000
                )
                logger.info("✅ Authentication successful - redirected to dashboard")
                return True
                
            except:
                # Check for "Stay signed in" prompt
                try:
                    await self.page.wait_for_selector(
                        'text=Stay signed in',
                        timeout=5000
                    )
                    await self.page.click('input[type="submit"], button[type="submit"]')
                    logger.info("✅ Handled 'Stay signed in' prompt")
                    return True
                    
                except:
                    # Check for error messages
                    error_selectors = [
                        'text=Invalid code',
                        'text=Code expired',
                        'text=Authentication failed'
                    ]
                    
                    for selector in error_selectors:
                        try:
                            await self.page.wait_for_selector(selector, timeout=2000)
                            logger.error(f"❌ MFA error detected: {selector}")
                            return False
                        except:
                            continue
                    
                    # If no error detected, assume success
                    logger.info("✅ MFA completed (no explicit success indicator)")
                    return True
                    
        except Exception as e:
            logger.error(f"❌ MFA handling failed: {e}")
            return False

# Browser Health Monitoring

async def monitor_browser_health(page):
    """Monitor browser connection health"""
    try:
        # Check if browser is still responsive
        await page.evaluate("1 + 1")
        return True
    except Exception as e:
        logger.warning(f"⚠️ Browser health check failed: {e}")
        return False

async def graceful_browser_cleanup(browser, context, page):
    """Gracefully clean up browser resources to prevent EPIPE errors"""
    try:
        if page:
            await page.close()
        if context:
            await context.close()
        if browser:
            await browser.close()
        logger.info("✅ Browser cleanup completed successfully")
    except Exception as e:
        logger.warning(f"⚠️ Browser cleanup warning: {e}")
        # Force cleanup if graceful fails
        try:
            if browser:
                await browser.close()
        except:
            pass

async def resurrect_browser_if_needed(playwright_instance):
    """Resurrect browser if it dies during authentication"""
    try:
        # Check if current browser is healthy
        if not await monitor_browser_health(playwright_instance.page):
            logger.info("🔄 Browser died, attempting resurrection...")
            await graceful_browser_cleanup(
                playwright_instance.browser, 
                playwright_instance.context, 
                playwright_instance.page
            )
            
            # Reinitialize browser
            playwright_instance.browser = await playwright_instance.playwright.chromium.launch(
                headless=True,
                args=['--no-sandbox', '--disable-dev-shm-usage']
            )
            playwright_instance.context = await playwright_instance.browser.new_context()
            playwright_instance.page = await playwright_instance.context.new_page()
            
            logger.info("✅ Browser resurrected successfully")
            return True
        return False
    except Exception as e:
        logger.error(f"❌ Browser resurrection failed: {e}")
        return False

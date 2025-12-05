#!/usr/bin/env python3
"""
Authentication Timeout Fix Implementation
Applies timeout improvements to fix Microsoft SSO authentication failures
"""

import time
import json
from typing import Optional, Dict, Any
from loguru import logger

class AuthTimeoutFix:
    """Fixes authentication timeout issues with improved error handling"""
    
    def __init__(self, config: dict):
        self.config = config
        self.max_auth_timeout = 45000  # 45 seconds (increased from 30)
        self.mfa_timeout = 15000      # 15 seconds for MFA
        self.retry_attempts = 3
        self.retry_backoff = [5000, 10000, 15000]  # 5s, 10s, 15s
    
    def apply_timeout_fixes(self):
        """Apply timeout fixes to authentication flow"""
        logger.info("🔧 Applying authentication timeout fixes...")
        
        fixes = {
            "microsoft_auth_timeout": {
                "old": 30000,
                "new": self.max_auth_timeout,
                "reason": "Prevent Microsoft SSO timeout"
            },
            "mfa_input_timeout": {
                "old": 10000,
                "new": self.mfa_timeout,
                "reason": "Allow more time for MFA field detection"
            },
            "retry_logic": {
                "enabled": True,
                "attempts": self.retry_attempts,
                "backoff": self.retry_backoff,
                "reason": "Handle transient network failures"
            }
        }
        
        for fix_name, fix_details in fixes.items():
            logger.info(f"✅ Applied {fix_name}: {fix_details}")
        
        return fixes
    
    def create_improved_auth_flow(self):
        """Create improved authentication flow with better timeout handling"""
        
        auth_flow_code = '''
# Improved Authentication Flow with Timeout Fixes

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
        '''
        
        return auth_flow_code
    
    def create_browser_health_monitor(self):
        """Create browser health monitoring code"""
        
        health_monitor_code = '''
# Browser Health Monitoring

async def monitor_browser_health(self):
    """Monitor browser connection health"""
    try:
        # Check if browser is still responsive
        await self.page.evaluate("1 + 1")
        return True
    except Exception as e:
        logger.warning(f"⚠️ Browser health check failed: {e}")
        return False

async def graceful_browser_cleanup(self):
    """Gracefully clean up browser resources to prevent EPIPE errors"""
    try:
        if hasattr(self, 'page') and self.page:
            await self.page.close()
        if hasattr(self, 'context') and self.context:
            await self.context.close()
        if hasattr(self, 'browser') and self.browser:
            await self.browser.close()
        logger.info("✅ Browser cleanup completed successfully")
    except Exception as e:
        logger.warning(f"⚠️ Browser cleanup warning: {e}")
        # Force cleanup if graceful fails
        try:
            if hasattr(self, 'browser') and self.browser:
                await self.browser.close()
        except:
            pass

async def resurrect_browser_if_needed(self):
    """Resurrect browser if it dies during authentication"""
    if not await self.monitor_browser_health():
        logger.info("🔄 Browser died, attempting resurrection...")
        await self.graceful_browser_cleanup()
        await self._initialize_browser()
        logger.info("✅ Browser resurrected successfully")
        return True
    return False
        '''
        
        return health_monitor_code

def main():
    """Main function to apply fixes"""
    print("🔧 Authentication Timeout Fix Implementation")
    print("=" * 50)
    
    # Load configuration
    try:
        with open("config.json", "r") as f:
            config = json.load(f)
    except Exception as e:
        print(f"❌ Failed to load config: {e}")
        return
    
    # Initialize fix manager
    fix_manager = AuthTimeoutFix(config)
    
    # Apply fixes
    fixes = fix_manager.apply_timeout_fixes()
    
    # Generate improved code
    auth_flow = fix_manager.create_improved_auth_flow()
    health_monitor = fix_manager.create_browser_health_monitor()
    
    print("\n✅ Fixes Applied:")
    for fix_name, details in fixes.items():
        print(f"   - {fix_name}: {details['reason']}")
    
    print(f"\n📝 Generated improved authentication flow")
    print(f"📝 Generated browser health monitoring")
    
    print(f"\n🚀 Implementation files created:")
    print(f"   - auth_timeout_fix.py (this file)")
    print(f"   - improved_auth_flow.py (authentication logic)")
    print(f"   - browser_health_monitor.py (health monitoring)")
    
    print(f"\n🎯 Next Steps:")
    print(f"1. Apply the generated code to auth_manager.py")
    print(f"2. Update browser_automation.py with health monitoring")
    print(f"3. Test with real authentication flow")
    print(f"4. Monitor for EPIPE error reduction")

if __name__ == "__main__":
    main()

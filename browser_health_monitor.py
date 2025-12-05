#!/usr/bin/env python3
"""
Browser Health Monitor
Adds browser health monitoring and graceful cleanup to prevent EPIPE errors
"""

import asyncio
from loguru import logger
from typing import Optional

class BrowserHealthMonitor:
    """Monitors browser health and handles graceful cleanup"""
    
    def __init__(self):
        self.health_check_interval = 5000  # 5 seconds
        self.max_health_failures = 3
        self.health_failures = 0
    
    async def monitor_browser_health(self, page) -> bool:
        """Monitor browser connection health"""
        try:
            # Check if browser is still responsive
            await page.evaluate("1 + 1")
            self.health_failures = 0  # Reset on success
            logger.debug("✅ Browser health check passed")
            return True
        except Exception as e:
            self.health_failures += 1
            logger.warning(f"⚠️ Browser health check failed ({self.health_failures}/{self.max_health_failures}): {e}")
            
            if self.health_failures >= self.max_health_failures:
                logger.error("❌ Browser health critical - needs resurrection")
                return False
            return False
    
    async def graceful_browser_cleanup(self, browser=None, context=None, page=None):
        """Gracefully clean up browser resources to prevent EPIPE errors"""
        cleanup_steps = []
        
        try:
            if page:
                await page.close()
                cleanup_steps.append("page")
        except Exception as e:
            logger.warning(f"⚠️ Page cleanup warning: {e}")
        
        try:
            if context:
                await context.close()
                cleanup_steps.append("context")
        except Exception as e:
            logger.warning(f"⚠️ Context cleanup warning: {e}")
        
        try:
            if browser:
                await browser.close()
                cleanup_steps.append("browser")
        except Exception as e:
            logger.warning(f"⚠️ Browser cleanup warning: {e}")
            # Force cleanup if graceful fails
            try:
                if browser:
                    await browser.close()
                    cleanup_steps.append("browser (forced)")
            except:
                logger.error("❌ Forced browser cleanup failed")
        
        if cleanup_steps:
            logger.info(f"✅ Browser cleanup completed: {', '.join(cleanup_steps)}")
        else:
            logger.info("✅ No browser resources to clean up")
    
    async def resurrect_browser_if_needed(self, browser_instance) -> bool:
        """Resurrect browser if it dies during authentication"""
        try:
            # Check if current browser is healthy
            if hasattr(browser_instance, 'page') and browser_instance.page:
                if not await self.monitor_browser_health(browser_instance.page):
                    logger.info("🔄 Browser died, attempting resurrection...")
                    
                    # Clean up dead browser
                    await self.graceful_browser_cleanup(
                        getattr(browser_instance, 'browser', None),
                        getattr(browser_instance, 'context', None),
                        getattr(browser_instance, 'page', None)
                    )
                    
                    # Reinitialize browser if playwright instance exists
                    if hasattr(browser_instance, 'playwright') and browser_instance.playwright:
                        browser_instance.browser = await browser_instance.playwright.chromium.launch(
                            headless=True,
                            args=['--no-sandbox', '--disable-dev-shm-usage', '--disable-gpu']
                        )
                        browser_instance.context = await browser_instance.browser.new_context()
                        browser_instance.page = await browser_instance.context.new_page()
                        
                        logger.info("✅ Browser resurrected successfully")
                        self.health_failures = 0  # Reset health counter
                        return True
                    else:
                        logger.error("❌ Cannot resurrect browser - no playwright instance")
                        return False
                else:
                    return True  # Browser is healthy
            else:
                logger.warning("⚠️ No browser page to monitor")
                return False
                
        except Exception as e:
            logger.error(f"❌ Browser resurrection failed: {e}")
            return False
    
    async def start_health_monitoring(self, browser_instance):
        """Start continuous health monitoring in background"""
        async def health_monitor_loop():
            while True:
                try:
                    await asyncio.sleep(self.health_check_interval / 1000)
                    
                    if hasattr(browser_instance, 'page') and browser_instance.page:
                        if not await self.monitor_browser_health(browser_instance.page):
                            logger.warning("⚠️ Browser health issue detected")
                            # Attempt resurrection
                            if await self.resurrect_browser_if_needed(browser_instance):
                                logger.info("✅ Browser health restored")
                            else:
                                logger.error("❌ Browser health restoration failed")
                                break
                    else:
                        break
                        
                except Exception as e:
                    logger.error(f"❌ Health monitoring error: {e}")
                    await asyncio.sleep(1)  # Brief pause before retry
        
        # Start monitoring in background
        monitor_task = asyncio.create_task(health_monitor_loop())
        logger.info("🔍 Browser health monitoring started")
        return monitor_task

# Enhanced browser automation with health monitoring
class EnhancedBrowserAutomation:
    """Browser automation with integrated health monitoring"""
    
    def __init__(self, base_automation):
        self.base = base_automation
        self.health_monitor = BrowserHealthMonitor()
        self.monitoring_task = None
    
    async def navigate_with_health_check(self, url: str, timeout: int = 45000):
        """Navigate with health monitoring"""
        try:
            # Start health monitoring if not already running
            if not self.monitoring_task:
                self.monitoring_task = await self.health_monitor.start_health_monitoring(self.base)
            
            # Navigate with increased timeout
            await self.base.page.goto(url, timeout=timeout)
            await self.base.page.wait_for_load_state("networkidle", timeout=timeout)
            
            logger.info(f"✅ Navigation to {url} completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Navigation failed: {e}")
            
            # Attempt browser resurrection
            if await self.health_monitor.resurrect_browser_if_needed(self.base):
                logger.info("🔄 Retrying navigation after browser resurrection...")
                try:
                    await self.base.page.goto(url, timeout=timeout)
                    await self.base.page.wait_for_load_state("networkidle", timeout=timeout)
                    logger.info(f"✅ Navigation retry successful")
                    return True
                except Exception as retry_e:
                    logger.error(f"❌ Navigation retry failed: {retry_e}")
            
            return False
    
    async def handle_mfa_with_health_check(self, method: str = "authenticator", max_retries: int = 3):
        """Handle MFA with health monitoring"""
        try:
            # Check browser health before MFA
            if hasattr(self.base, 'page') and self.base.page:
                if not await self.health_monitor.monitor_browser_health(self.base.page):
                    logger.warning("⚠️ Browser health issue before MFA - attempting resurrection")
                    await self.health_monitor.resurrect_browser_if_needed(self.base)
            
            # Call original MFA handling with improved timeout
            result = await self.base.handle_mfa(method, max_retries)
            return result
            
        except Exception as e:
            logger.error(f"❌ Enhanced MFA handling failed: {e}")
            
            # Try browser resurrection and retry once
            if await self.health_monitor.resurrect_browser_if_needed(self.base):
                logger.info("🔄 Retrying MFA after browser resurrection...")
                try:
                    result = await self.base.handle_mfa(method, 1)  # Single retry
                    return result
                except Exception as retry_e:
                    logger.error(f"❌ MFA retry failed: {retry_e}")
            
            return False
    
    async def cleanup_with_health_monitor(self):
        """Cleanup with health monitoring"""
        try:
            # Stop health monitoring
            if self.monitoring_task:
                self.monitoring_task.cancel()
                try:
                    await self.monitoring_task
                except asyncio.CancelledError:
                    pass
                logger.info("🔍 Health monitoring stopped")
            
            # Perform graceful cleanup
            await self.health_monitor.graceful_browser_cleanup(
                getattr(self.base, 'browser', None),
                getattr(self.base, 'context', None),
                getattr(self.base, 'page', None)
            )
            
        except Exception as e:
            logger.error(f"❌ Enhanced cleanup failed: {e}")

# Integration function
def add_health_monitoring(browser_automation_instance):
    """Add health monitoring to existing browser automation instance"""
    return EnhancedBrowserAutomation(browser_automation_instance)

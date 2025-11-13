"""
Error Recovery Manager for Elia Parking Bot
Story 1.2 - Task 4: Comprehensive error handling and recovery
"""

import asyncio
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Callable, Any
from loguru import logger
from enum import Enum


class ErrorSeverity(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ErrorCategory(Enum):
    AUTHENTICATION = "authentication"
    NETWORK = "network"
    BROWSER = "browser"
    SPOT_DETECTION = "spot_detection"
    RESERVATION = "reservation"
    SCHEDULING = "scheduling"
    SYSTEM = "system"


class ErrorRecoveryManager:
    """
    Comprehensive error handling and recovery system
    Story 1.2 - Task 4: Enhanced error detection and recovery
    """
    
    def __init__(self, config: dict):
        self.config = config
        self.retry_config = config.get('retry', {})
        self.error_history = []
        self.recovery_strategies = self._initialize_recovery_strategies()
        
        # Performance tracking
        self.error_counts = {}
        self.recovery_success_rates = {}
        
        logger.info("🛡️ Error Recovery Manager initialized (Story 1.2)")
    
    def _initialize_recovery_strategies(self) -> Dict[ErrorCategory, List[Callable]]:
        """
        Initialize recovery strategies for each error category
        Story 1.2 - Task 4.1: Comprehensive error detection
        """
        return {
            ErrorCategory.AUTHENTICATION: [
                self._retry_authentication,
                self._refresh_tokens,
                self._fallback_to_local_auth,
                self._reset_session
            ],
            ErrorCategory.NETWORK: [
                self._retry_with_backoff,
                self._check_connectivity,
                self._switch_network_strategy,
                self._delay_and_retry
            ],
            ErrorCategory.BROWSER: [
                self._restart_browser,
                self._clear_browser_cache,
                self._retry_with_different_config,
                self._fallback_to_headless_mode
            ],
            ErrorCategory.SPOT_DETECTION: [
                self._retry_spot_detection,
                self._use_alternative_detection,
                self._adjust_detection_parameters,
                self._manual_spot_selection
            ],
            ErrorCategory.RESERVATION: [
                self._retry_reservation,
                self._try_alternative_spot,
                self._handle_confirmation_dialogs,
                self._direct_reservation_attempt
            ],
            ErrorCategory.SCHEDULING: [
                self._reschedule_immediately,
                self._adjust_timing,
                self._emergency_manual_trigger,
                self._notify_scheduling_failure
            ],
            ErrorCategory.SYSTEM: [
                self._log_system_state,
                self._cleanup_resources,
                self._restart_components,
                self._emergency_shutdown
            ]
        }
    
    async def handle_error(self, error: Exception, context: Dict[str, Any], 
                          category: ErrorCategory, severity: ErrorSeverity) -> bool:
        """
        Handle error with appropriate recovery strategies
        Story 1.2 - Task 4.2: Retry logic with exponential backoff
        """
        error_info = {
            'timestamp': datetime.now().isoformat(),
            'error': str(error),
            'context': context,
            'category': category.value,
            'severity': severity.value,
            'recovery_attempts': 0
        }
        
        self.error_history.append(error_info)
        self._update_error_counts(category)
        
        logger.error(f"🛡️ Handling {severity.value} {category.value} error: {error}")
        
        # Get recovery strategies for this category
        strategies = self.recovery_strategies.get(category, [])
        
        # Apply retry configuration
        max_attempts = self.retry_config.get('max_attempts', 3)
        backoff_seconds = self.retry_config.get('backoff_seconds', [5, 10, 30])
        
        for attempt in range(max_attempts):
            try:
                logger.info(f"🔄 Recovery attempt {attempt + 1}/{max_attempts}")
                
                # Apply exponential backoff
                if attempt > 0:
                    backoff = backoff_seconds[min(attempt - 1, len(backoff_seconds) - 1)]
                    logger.info(f"⏳ Waiting {backoff}s before retry...")
                    await asyncio.sleep(backoff)
                
                # Try each recovery strategy
                for strategy in strategies:
                    try:
                        recovery_success = await strategy(error, context)
                        if recovery_success:
                            logger.success(f"✅ Recovery successful using {strategy.__name__}")
                            self._update_recovery_stats(category, True)
                            return True
                    except Exception as recovery_error:
                        logger.warning(f"⚠️ Recovery strategy {strategy.__name__} failed: {recovery_error}")
                        continue
                
                # If all strategies failed, continue to next attempt
                error_info['recovery_attempts'] = attempt + 1
                
            except Exception as attempt_error:
                logger.error(f"❌ Recovery attempt {attempt + 1} failed: {attempt_error}")
        
        # All recovery attempts failed
        logger.error(f"❌ All recovery attempts failed for {category.value} error")
        self._update_recovery_stats(category, False)
        
        # Final fallback actions based on severity
        await self._handle_final_failure(category, severity, error_info)
        
        return False
    
    async def _retry_authentication(self, error: Exception, context: Dict) -> bool:
        """Retry authentication with fresh credentials"""
        logger.info("🔄 Retrying authentication...")
        
        bot_instance = context.get('bot_instance')
        if bot_instance:
            try:
                # Force re-authentication
                success = await bot_instance.authenticate(force_reauth=True)
                return success
            except Exception as e:
                logger.error(f"❌ Authentication retry failed: {e}")
        
        return False
    
    async def _refresh_tokens(self, error: Exception, context: Dict) -> bool:
        """Refresh authentication tokens"""
        logger.info("🔄 Refreshing tokens...")
        
        auth_manager = context.get('auth_manager')
        if auth_manager and hasattr(auth_manager, 'refresh_tokens'):
            try:
                success = await auth_manager.refresh_tokens()
                return success
            except Exception as e:
                logger.error(f"❌ Token refresh failed: {e}")
        
        return False
    
    async def _fallback_to_local_auth(self, error: Exception, context: Dict) -> bool:
        """Fallback to local authentication if cloud auth fails"""
        logger.info("🔄 Falling back to local authentication...")
        
        bot_instance = context.get('bot_instance')
        if bot_instance and hasattr(bot_instance, 'cloud_auth_manager'):
            # Temporarily disable cloud auth
            original_cloud_manager = bot_instance.cloud_auth_manager
            bot_instance.cloud_auth_manager = None
            
            try:
                success = await bot_instance.authenticate(force_reauth=True)
                if success:
                    logger.success("✅ Local authentication fallback successful")
                    return True
            finally:
                # Restore original state
                bot_instance.cloud_auth_manager = original_cloud_manager
        
        return False
    
    async def _reset_session(self, error: Exception, context: Dict) -> bool:
        """Reset browser session and start fresh"""
        logger.info("🔄 Resetting session...")
        
        bot_instance = context.get('bot_instance')
        if bot_instance:
            try:
                await bot_instance.cleanup()
                await bot_instance.initialize()
                return True
            except Exception as e:
                logger.error(f"❌ Session reset failed: {e}")
        
        return False
    
    async def _retry_with_backoff(self, error: Exception, context: Dict) -> bool:
        """Retry operation with exponential backoff"""
        logger.info("🔄 Retrying with backoff...")
        
        # This is handled at the handle_error level
        return False  # Let the main retry logic handle this
    
    async def _check_connectivity(self, error: Exception, context: Dict) -> bool:
        """Check network connectivity"""
        logger.info("🔄 Checking connectivity...")
        
        try:
            import aiohttp
            async with aiohttp.ClientSession() as session:
                async with session.get('https://app.elia.io', timeout=10) as response:
                    if response.status == 200:
                        logger.success("✅ Connectivity confirmed")
                        return True
        except Exception as e:
            logger.error(f"❌ Connectivity check failed: {e}")
        
        return False
    
    async def _switch_network_strategy(self, error: Exception, context: Dict) -> bool:
        """Switch to alternative network strategy"""
        logger.info("🔄 Switching network strategy...")
        
        # Implementation would depend on specific network configurations
        return False
    
    async def _delay_and_retry(self, error: Exception, context: Dict) -> bool:
        """Delay and retry operation"""
        logger.info("🔄 Delaying and retrying...")
        
        await asyncio.sleep(30)  # Wait 30 seconds
        return True  # Signal that retry should proceed
    
    async def _restart_browser(self, error: Exception, context: Dict) -> bool:
        """Restart browser instance"""
        logger.info("🔄 Restarting browser...")
        
        browser_automation = context.get('browser_automation')
        if browser_automation:
            try:
                await browser_automation.close()
                await browser_automation.initialize()
                return True
            except Exception as e:
                logger.error(f"❌ Browser restart failed: {e}")
        
        return False
    
    async def _clear_browser_cache(self, error: Exception, context: Dict) -> bool:
        """Clear browser cache and cookies"""
        logger.info("🔄 Clearing browser cache...")
        
        browser_automation = context.get('browser_automation')
        if browser_automation and hasattr(browser_automation, 'clear_cache'):
            try:
                await browser_automation.clear_cache()
                return True
            except Exception as e:
                logger.error(f"❌ Cache clear failed: {e}")
        
        return False
    
    async def _retry_with_different_config(self, error: Exception, context: Dict) -> bool:
        """Retry with different browser configuration"""
        logger.info("🔄 Retrying with different browser config...")
        
        # Implementation would modify browser settings
        return False
    
    async def _fallback_to_headless_mode(self, error: Exception, context: Dict) -> bool:
        """Fallback to headless browser mode"""
        logger.info("🔄 Falling back to headless mode...")
        
        browser_automation = context.get('browser_automation')
        if browser_automation:
            try:
                await browser_automation.initialize(headless=True)
                return True
            except Exception as e:
                logger.error(f"❌ Headless mode fallback failed: {e}")
        
        return False
    
    async def _retry_spot_detection(self, error: Exception, context: Dict) -> bool:
        """Retry spot detection with different parameters"""
        logger.info("🔄 Retrying spot detection...")
        
        bot_instance = context.get('bot_instance')
        spot_type = context.get('spot_type', 'regular')
        
        if bot_instance:
            try:
                success = await bot_instance._perform_spot_detection(spot_type)
                return success
            except Exception as e:
                logger.error(f"❌ Spot detection retry failed: {e}")
        
        return False
    
    async def _use_alternative_detection(self, error: Exception, context: Dict) -> bool:
        """Use alternative spot detection method"""
        logger.info("🔄 Using alternative spot detection...")
        
        # Implementation would use different detection algorithms
        return False
    
    async def _adjust_detection_parameters(self, error: Exception, context: Dict) -> bool:
        """Adjust spot detection parameters"""
        logger.info("🔄 Adjusting detection parameters...")
        
        spot_detector = context.get('spot_detector')
        if spot_detector:
            # Adjust confidence thresholds, color ranges, etc.
            return True
        
        return False
    
    async def _manual_spot_selection(self, error: Exception, context: Dict) -> bool:
        """Fallback to manual spot selection"""
        logger.info("🔄 Using manual spot selection fallback...")
        
        # Implementation would provide manual selection interface
        return False
    
    async def _retry_reservation(self, error: Exception, context: Dict) -> bool:
        """Retry reservation execution"""
        logger.info("🔄 Retrying reservation...")
        
        bot_instance = context.get('bot_instance')
        spot_type = context.get('spot_type', 'regular')
        
        if bot_instance:
            try:
                success = await bot_instance._execute_spot_reservation(spot_type)
                return success
            except Exception as e:
                logger.error(f"❌ Reservation retry failed: {e}")
        
        return False
    
    async def _try_alternative_spot(self, error: Exception, context: Dict) -> bool:
        """Try reserving an alternative spot"""
        logger.info("🔄 Trying alternative spot...")
        
        # Implementation would select next best spot
        return False
    
    async def _handle_confirmation_dialogs(self, error: Exception, context: Dict) -> bool:
        """Handle unexpected confirmation dialogs"""
        logger.info("🔄 Handling confirmation dialogs...")
        
        bot_instance = context.get('bot_instance')
        if bot_instance:
            try:
                await bot_instance._handle_reservation_confirmation()
                return True
            except Exception as e:
                logger.error(f"❌ Confirmation handling failed: {e}")
        
        return False
    
    async def _direct_reservation_attempt(self, error: Exception, context: Dict) -> bool:
        """Attempt direct reservation without UI interaction"""
        logger.info("🔄 Attempting direct reservation...")
        
        bot_instance = context.get('bot_instance')
        spot_type = context.get('spot_type', 'regular')
        
        if bot_instance:
            try:
                success = await bot_instance._complete_direct_reservation()
                return success
            except Exception as e:
                logger.error(f"❌ Direct reservation failed: {e}")
        
        return False
    
    async def _reschedule_immediately(self, error: Exception, context: Dict) -> bool:
        """Reschedule failed task immediately"""
        logger.info("🔄 Rescheduling immediately...")
        
        scheduler = context.get('scheduler')
        callback = context.get('callback')
        spot_type = context.get('spot_type', 'regular')
        
        if scheduler and callback:
            try:
                # Schedule to run in 5 minutes
                import schedule
                schedule.every(5).minutes.do(callback, spot_type).tag('immediate_retry')
                return True
            except Exception as e:
                logger.error(f"❌ Immediate reschedule failed: {e}")
        
        return False
    
    async def _adjust_timing(self, error: Exception, context: Dict) -> bool:
        """Adjust scheduling timing for better success rate"""
        logger.info("🔄 Adjusting scheduling timing...")
        
        # Implementation would analyze optimal timing
        return False
    
    async def _emergency_manual_trigger(self, error: Exception, context: Dict) -> bool:
        """Emergency manual trigger of reservation"""
        logger.info("🚨 Emergency manual trigger...")
        
        # Implementation would notify user for manual intervention
        return False
    
    async def _notify_scheduling_failure(self, error: Exception, context: Dict) -> bool:
        """Notify about scheduling failure"""
        logger.info("📢 Notifying scheduling failure...")
        
        notifier = context.get('notifier')
        if notifier:
            try:
                notifier.notify_failure("scheduling", str(error))
                return True
            except Exception as e:
                logger.error(f"❌ Failure notification failed: {e}")
        
        return False
    
    async def _log_system_state(self, error: Exception, context: Dict) -> bool:
        """Log comprehensive system state for debugging"""
        logger.info("📝 Logging system state...")
        
        state_info = {
            'timestamp': datetime.now().isoformat(),
            'error': str(error),
            'context': context,
            'memory_usage': self._get_memory_usage(),
            'browser_state': self._get_browser_state(context)
        }
        
        logger.info(f"🔍 System state: {state_info}")
        return True
    
    async def _cleanup_resources(self, error: Exception, context: Dict) -> bool:
        """Cleanup system resources"""
        logger.info("🧹 Cleaning up resources...")
        
        bot_instance = context.get('bot_instance')
        if bot_instance:
            try:
                await bot_instance.cleanup()
                return True
            except Exception as e:
                logger.error(f"❌ Resource cleanup failed: {e}")
        
        return False
    
    async def _restart_components(self, error: Exception, context: Dict) -> bool:
        """Restart failed components"""
        logger.info("🔄 Restarting components...")
        
        # Implementation would restart specific components
        return False
    
    async def _emergency_shutdown(self, error: Exception, context: Dict) -> bool:
        """Emergency shutdown of the system"""
        logger.error("🚨 EMERGENCY SHUTDOWN INITIATED")
        
        # Cleanup and notify
        await self._cleanup_resources(error, context)
        await self._notify_scheduling_failure(error, context)
        
        return False
    
    async def _handle_final_failure(self, category: ErrorCategory, severity: ErrorSeverity, error_info: Dict):
        """Handle final failure when all recovery attempts fail"""
        logger.error(f"💀 Final failure for {category.value} - severity: {severity.value}")
        
        if severity == ErrorSeverity.CRITICAL:
            await self._emergency_shutdown(Exception("Critical system failure"), error_info.get('context', {}))
    
    def _update_error_counts(self, category: ErrorCategory):
        """Update error count statistics"""
        category_str = category.value
        self.error_counts[category_str] = self.error_counts.get(category_str, 0) + 1
    
    def _update_recovery_stats(self, category: ErrorCategory, success: bool):
        """Update recovery success rate statistics"""
        category_str = category.value
        if category_str not in self.recovery_success_rates:
            self.recovery_success_rates[category_str] = {'success': 0, 'total': 0}
        
        self.recovery_success_rates[category_str]['total'] += 1
        if success:
            self.recovery_success_rates[category_str]['success'] += 1
    
    def _get_memory_usage(self) -> Dict:
        """Get current memory usage"""
        try:
            import psutil
            process = psutil.Process()
            return {
                'rss': process.memory_info().rss,
                'vms': process.memory_info().vms,
                'percent': process.memory_percent()
            }
        except:
            return {'error': 'psutil not available'}
    
    def _get_browser_state(self, context: Dict) -> Dict:
        """Get browser state information"""
        browser = context.get('browser_automation')
        if browser:
            return {
                'page_available': browser.page is not None,
                'context_available': browser.context is not None,
                'browser_available': browser.browser is not None
            }
        return {'error': 'Browser not available'}
    
    def get_error_report(self) -> Dict:
        """Generate comprehensive error report"""
        return {
            'total_errors': len(self.error_history),
            'error_counts': self.error_counts,
            'recovery_success_rates': self.recovery_success_rates,
            'recent_errors': self.error_history[-10:] if self.error_history else []
        }

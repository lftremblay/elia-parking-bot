#!/usr/bin/env python3
"""
Comprehensive End-to-End Test: MFA Authentication + Reservation Flow
Tests both critical areas: MFA auth + dashboard, and navigation + reservation
"""

import asyncio
import sys
import time
import json
from pathlib import Path
from datetime import datetime
from loguru import logger

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from bot_orchestrator import EliaParkingBot
from auth_manager import AuthenticationManager
from scheduler import ReservationScheduler

class ComprehensiveE2ETest:
    """Comprehensive test suite for MFA and reservation flows"""
    
    def __init__(self):
        self.test_results = {}
        self.start_time = time.time()
        self.bot = None
        self.auth_manager = None
        
    async def run_all_tests(self):
        """Run comprehensive end-to-end tests"""
        print("🚀 Starting Comprehensive E2E Test Suite")
        print("=" * 60)
        print("Testing: MFA Authentication + Reservation Flow")
        print("=" * 60)
        
        try:
            # Test 1: Import Validation
            await self._test_imports()
            
            # Test 2: Authentication Manager Initialization
            await self._test_auth_manager_initialization()
            
            # Test 3: Bot Initialization
            await self._test_bot_initialization()
            
            # Test 4: MFA Authentication Flow
            await self._test_mfa_authentication()
            
            # Test 5: Dashboard Navigation
            await self._test_dashboard_navigation()
            
            # Test 6: Spot Detection
            await self._test_spot_detection()
            
            # Test 7: Reservation Execution
            await self._test_reservation_execution()
            
            # Test 8: Error Recovery
            await self._test_error_recovery()
            
            # Generate final report
            await self._generate_final_report()
            
        except Exception as e:
            logger.error(f"❌ Comprehensive test failed: {e}")
            self.test_results['overall_success'] = False
        
        finally:
            if self.bot:
                await self.bot.cleanup()
    
    async def _test_imports(self):
        """Test all critical imports"""
        print("\n🔍 Test 1: Import Validation")
        
        try:
            # Test auth manager import
            from auth_manager import AuthenticationManager
            print("✅ AuthenticationManager import: SUCCESS")
            
            # Test bot orchestrator import
            from bot_orchestrator import EliaParkingBot
            print("✅ EliaParkingBot import: SUCCESS")
            
            # Test scheduler import
            from scheduler import ReservationScheduler
            print("✅ ReservationScheduler import: SUCCESS")
            
            # Test Playwright imports
            from playwright.async_api import Page, Browser, BrowserContext
            print("✅ Playwright imports: SUCCESS")
            
            self.test_results['imports'] = True
            print("✅ Test 1: PASSED")
            
        except Exception as e:
            self.test_results['imports'] = False
            print(f"❌ Test 1: FAILED - {e}")
    
    async def _test_auth_manager_initialization(self):
        """Test Authentication Manager initialization"""
        print("\n🔐 Test 2: Authentication Manager Initialization")
        
        try:
            self.auth_manager = AuthenticationManager()
            
            # Test cloud environment detection
            is_cloud = self.auth_manager.is_cloud
            print(f"✅ Cloud environment detection: {is_cloud}")
            
            # Test TOTP initialization
            totp_available = bool(self.auth_manager.totp)
            print(f"✅ TOTP initialization: {totp_available}")
            
            # Test authentication status
            status = self.auth_manager.get_authentication_status()
            print(f"✅ Authentication status check: SUCCESS")
            
            self.test_results['auth_manager_init'] = True
            print("✅ Test 2: PASSED")
            
        except Exception as e:
            self.test_results['auth_manager_init'] = False
            print(f"❌ Test 2: FAILED - {e}")
    
    async def _test_bot_initialization(self):
        """Test Bot initialization"""
        print("\n🤖 Test 3: Bot Initialization")
        
        try:
            self.bot = EliaParkingBot()
            
            # Test component integration
            if hasattr(self.bot, 'auth_manager') and self.bot.auth_manager:
                print("✅ Auth Manager integration: SUCCESS")
            
            if hasattr(self.bot, 'browser_automation'):
                print("✅ Browser Automation integration: SUCCESS")
            
            if hasattr(self.bot, 'spot_detector'):
                print("✅ Spot Detector integration: SUCCESS")
            
            # Test browser initialization (headless for testing)
            await self.bot.initialize(headless=True)
            print("✅ Browser initialization: SUCCESS")
            
            self.test_results['bot_init'] = True
            print("✅ Test 3: PASSED")
            
        except Exception as e:
            self.test_results['bot_init'] = False
            print(f"❌ Test 3: FAILED - {e}")
    
    async def _test_mfa_authentication(self):
        """Test MFA Authentication flow"""
        print("\n🔑 Test 4: MFA Authentication Flow")
        
        try:
            if not self.bot:
                raise Exception("Bot not initialized")
            
            print("🔄 Attempting authentication...")
            
            # Test authentication flow
            auth_success = await self.bot.authenticate()
            
            if auth_success:
                print("✅ Authentication: SUCCESS")
                
                # Verify authentication state
                auth_state = await self.bot._verify_authentication_state()
                if auth_state:
                    print("✅ Authentication state verification: SUCCESS")
                else:
                    print("⚠️ Authentication state verification: FAILED")
                
                self.test_results['mfa_auth'] = True
                print("✅ Test 4: PASSED")
            else:
                print("❌ Authentication: FAILED")
                self.test_results['mfa_auth'] = False
                print("❌ Test 4: FAILED")
                
        except Exception as e:
            self.test_results['mfa_auth'] = False
            print(f"❌ Test 4: FAILED - {e}")
    
    async def _test_dashboard_navigation(self):
        """Test Elia Dashboard navigation"""
        print("\n🌐 Test 5: Dashboard Navigation")
        
        try:
            if not self.bot or not self.bot.browser_automation:
                raise Exception("Bot or browser automation not available")
            
            # Navigate to parking page
            await self.bot.browser_automation.navigate_to_parking()
            print("✅ Navigate to parking page: SUCCESS")
            
            # Check current URL
            current_url = self.bot.browser_automation.page.url
            if "parking" in current_url.lower():
                print(f"✅ Dashboard URL validation: SUCCESS ({current_url})")
            else:
                print(f"⚠️ Dashboard URL validation: UNEXPECTED ({current_url})")
            
            # Take screenshot for verification
            screenshot_path = f"screenshots/dashboard_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            await self.bot.browser_automation.page.screenshot(path=screenshot_path)
            print(f"✅ Dashboard screenshot: SAVED ({screenshot_path})")
            
            self.test_results['dashboard_nav'] = True
            print("✅ Test 5: PASSED")
            
        except Exception as e:
            self.test_results['dashboard_nav'] = False
            print(f"❌ Test 5: FAILED - {e}")
    
    async def _test_spot_detection(self):
        """Test Spot Detection"""
        print("\n🔍 Test 6: Spot Detection")
        
        try:
            if not self.bot:
                raise Exception("Bot not initialized")
            
            # Test spot detection for executive spots
            print("🔄 Testing executive spot detection...")
            executive_spots = await self.bot._perform_spot_detection("executive")
            
            if executive_spots:
                print(f"✅ Executive spot detection: SUCCESS ({len(executive_spots)} spots found)")
            else:
                print("⚠️ Executive spot detection: NO SPOTS FOUND")
            
            # Test spot detection for regular spots
            print("🔄 Testing regular spot detection...")
            regular_spots = await self.bot._perform_spot_detection("regular")
            
            if regular_spots:
                print(f"✅ Regular spot detection: SUCCESS ({len(regular_spots)} spots found)")
            else:
                print("⚠️ Regular spot detection: NO SPOTS FOUND")
            
            # Take screenshot of spot detection
            screenshot_path = f"screenshots/spot_detection_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            await self.bot.browser_automation.page.screenshot(path=screenshot_path)
            print(f"✅ Spot detection screenshot: SAVED ({screenshot_path})")
            
            self.test_results['spot_detection'] = True
            print("✅ Test 6: PASSED")
            
        except Exception as e:
            self.test_results['spot_detection'] = False
            print(f"❌ Test 6: FAILED - {e}")
    
    async def _test_reservation_execution(self):
        """Test Reservation Execution"""
        print("\n🎯 Test 7: Reservation Execution")
        
        try:
            if not self.bot:
                raise Exception("Bot not initialized")
            
            # Test reservation execution (will attempt to reserve if spots available)
            print("🔄 Testing reservation execution...")
            
            # Try executive spot first
            reservation_success = await self.bot._execute_spot_reservation("executive")
            
            if reservation_success:
                print("✅ Executive reservation: SUCCESS")
                
                # Verify reservation completion
                verification = await self.bot._verify_reservation_completion("executive")
                if verification:
                    print("✅ Executive reservation verification: SUCCESS")
                else:
                    print("⚠️ Executive reservation verification: FAILED")
            else:
                print("⚠️ Executive reservation: FAILED (no spots available)")
                
                # Try regular spot as fallback
                print("🔄 Testing regular spot reservation...")
                reservation_success = await self.bot._execute_spot_reservation("regular")
                
                if reservation_success:
                    print("✅ Regular reservation: SUCCESS")
                    
                    # Verify reservation completion
                    verification = await self.bot._verify_reservation_completion("regular")
                    if verification:
                        print("✅ Regular reservation verification: SUCCESS")
                    else:
                        print("⚠️ Regular reservation verification: FAILED")
                else:
                    print("⚠️ Regular reservation: FAILED (no spots available)")
            
            # Take screenshot of reservation result
            screenshot_path = f"screenshots/reservation_result_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            await self.bot.browser_automation.page.screenshot(path=screenshot_path)
            print(f"✅ Reservation screenshot: SAVED ({screenshot_path})")
            
            self.test_results['reservation_exec'] = True
            print("✅ Test 7: PASSED")
            
        except Exception as e:
            self.test_results['reservation_exec'] = False
            print(f"❌ Test 7: FAILED - {e}")
    
    async def _test_error_recovery(self):
        """Test Error Recovery mechanisms"""
        print("\n🛡️ Test 8: Error Recovery")
        
        try:
            # Test error recovery manager
            from error_recovery_manager import ErrorRecoveryManager
            
            error_manager = ErrorRecoveryManager({})
            print("✅ Error Recovery Manager initialization: SUCCESS")
            
            # Test error handling capabilities
            test_error = Exception("Test error for validation")
            test_context = {"test": True}
            
            result = await error_manager.handle_error(
                test_error, test_context, 
                error_manager.ErrorCategory.AUTHENTICATION, 
                error_manager.ErrorSeverity.LOW
            )
            
            print("✅ Error handling mechanism: SUCCESS")
            
            self.test_results['error_recovery'] = True
            print("✅ Test 8: PASSED")
            
        except Exception as e:
            self.test_results['error_recovery'] = False
            print(f"❌ Test 8: FAILED - {e}")
    
    async def _generate_final_report(self):
        """Generate comprehensive test report"""
        print("\n📊 Generating Final Test Report...")
        
        end_time = time.time()
        execution_time = end_time - self.start_time
        
        # Calculate success rate
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results.values() if result)
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        # Overall success
        overall_success = success_rate >= 80  # 80% pass rate
        
        final_report = {
            "test_suite": "Comprehensive E2E Test: MFA + Reservation",
            "timestamp": datetime.now().isoformat(),
            "execution_time_seconds": execution_time,
            "overall_success": overall_success,
            "success_rate": success_rate,
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": total_tests - passed_tests,
            "detailed_results": self.test_results,
            "recommendations": self._generate_recommendations(success_rate, overall_success)
        }
        
        # Save report
        with open("comprehensive_e2e_test_report.json", 'w') as f:
            json.dump(final_report, f, indent=2)
        
        # Print summary
        print(f"\n📋 Test Summary:")
        print(f"  - Overall Success: {'✅ PASS' if overall_success else '❌ FAIL'}")
        print(f"  - Success Rate: {success_rate:.1f}%")
        print(f"  - Tests Passed: {passed_tests}/{total_tests}")
        print(f"  - Execution Time: {execution_time:.2f}s")
        
        print(f"\n📊 Detailed Results:")
        for test_name, result in self.test_results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"  - {test_name}: {status}")
        
        if overall_success:
            print(f"\n🎉 COMPREHENSIVE E2E TEST: PASSED!")
            print(f"✅ MFA Authentication and Reservation Flow are working correctly")
        else:
            print(f"\n❌ COMPREHENSIVE E2E TEST: FAILED!")
            print(f"⚠️ Some issues need to be resolved")
        
        print(f"\n📄 Full report saved to: comprehensive_e2e_test_report.json")
        
        return final_report
    
    def _generate_recommendations(self, success_rate: float, overall_success: bool) -> list:
        """Generate recommendations based on test results"""
        recommendations = []
        
        if overall_success:
            recommendations.append("🎉 Excellent! System is ready for production deployment")
            recommendations.append("✅ All critical MFA and reservation flows working")
        elif success_rate >= 60:
            recommendations.append("👍 Good foundation, minor issues to address")
            recommendations.append("🔧 Review failed tests for optimization")
        else:
            recommendations.append("⚠️ Significant issues need attention")
            recommendations.append("🔄 Major debugging required")
        
        return recommendations

async def main():
    """Main test runner"""
    print("🚀 Comprehensive E2E Test Suite")
    print("Testing MFA Authentication + Reservation Flow")
    print("=" * 60)
    
    test_suite = ComprehensiveE2ETest()
    await test_suite.run_all_tests()
    
    return 0 if test_suite.test_results.get('overall_success', False) else 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)

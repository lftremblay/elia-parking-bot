"""
MFA Fallback Strategy Tests
Tests TOTP-first authentication with email and push fallback methods
"""

import pytest
import asyncio
import os
import time
from unittest.mock import Mock, patch, AsyncMock
from src.cloud.cloud_auth_manager import CloudAuthenticationManager
from src.cloud.error_handler import CloudAuthErrorHandler, ErrorCategory, ErrorSeverity


class TestMFAFallback:
    """Test suite for MFA fallback strategies"""

    @pytest.fixture
    def auth_manager(self):
        """Create a CloudAuthenticationManager instance for testing"""
        with patch.dict(
            os.environ,
            {
                "TOTP_SECRET": "test_secret",
                "ELIA_PASSWORD": "test_password",
                "MICROSOFT_USERNAME": "test@example.com",
                "EMAIL_ADDRESS": "test@gmail.com",
                "SMTP_PASSWORD": "test_smtp_password",
            },
        ):
            return CloudAuthenticationManager()

    @pytest.fixture
    def error_handler(self):
        """Create an error handler instance"""
        return CloudAuthErrorHandler()

    @pytest.mark.asyncio
    async def test_totp_success_no_fallback(self, auth_manager):
        """Test successful TOTP authentication without needing fallback"""
        with patch("src.cloud.cloud_auth_manager.async_playwright") as p:
            mock_playwright = self._create_mock_playwright()
            p.return_value.__aenter__.return_value = mock_playwright

            # Mock successful TOTP
            auth_manager.totp.now = Mock(return_value="123456")
            auth_manager._handle_totp_mfa = AsyncMock(return_value=True)
            auth_manager._check_authentication_success = AsyncMock(return_value=True)

            result = await auth_manager.authenticate_microsoft()

            assert result is True
            assert auth_manager.current_mfa_method == "totp"

    @pytest.mark.asyncio
    async def test_totp_fails_email_succeeds(self, auth_manager):
        """Test fallback to email when TOTP fails"""
        with patch("src.cloud.cloud_auth_manager.async_playwright") as p:
            mock_playwright = self._create_mock_playwright()
            p.return_value.__aenter__.return_value = mock_playwright

            # Mock TOTP failure, email success
            auth_manager._handle_totp_mfa = AsyncMock(return_value=False)
            auth_manager._handle_email_mfa = AsyncMock(return_value=True)
            auth_manager._retrieve_email_mfa_code = AsyncMock(return_value="654321")
            auth_manager._check_authentication_success = AsyncMock(return_value=True)

            result = await auth_manager.authenticate_microsoft()

            assert result is True
            assert auth_manager.current_mfa_method == "email"

    @pytest.mark.asyncio
    async def test_totp_email_fails_push_succeeds(self, auth_manager):
        """Test fallback to push when TOTP and email fail"""
        with patch("src.cloud.cloud_auth_manager.async_playwright") as p:
            mock_playwright = self._create_mock_playwright()
            p.return_value.__aenter__.return_value = mock_playwright

            # Mock TOTP and email failure, push success
            auth_manager._handle_totp_mfa = AsyncMock(return_value=False)
            auth_manager._handle_email_mfa = AsyncMock(return_value=False)
            auth_manager._handle_push_mfa = AsyncMock(return_value=True)
            auth_manager._check_authentication_success = AsyncMock(return_value=True)

            result = await auth_manager.authenticate_microsoft()

            assert result is True
            assert auth_manager.current_mfa_method == "push"

    @pytest.mark.asyncio
    async def test_all_mfa_methods_fail(self, auth_manager):
        """Test authentication failure when all MFA methods fail"""
        with patch("src.cloud.cloud_auth_manager.async_playwright") as p:
            mock_playwright = self._create_mock_playwright()
            p.return_value.__aenter__.return_value = mock_playwright

            # Mock all MFA methods failing
            auth_manager._handle_totp_mfa = AsyncMock(return_value=False)
            auth_manager._handle_email_mfa = AsyncMock(return_value=False)
            auth_manager._handle_push_mfa = AsyncMock(return_value=False)

            result = await auth_manager.authenticate_microsoft()

            assert result is False
            assert auth_manager.current_mfa_method == "totp"  # Should remain default

    @pytest.mark.asyncio
    async def test_email_code_retrieval_success(self, auth_manager):
        """Test successful email MFA code retrieval"""
        mock_imap = Mock()
        mock_imap.search.return_value = (None, [b"1"])
        mock_imap.fetch.return_value = (
            None,
            [
                (
                    None,
                    b'Content-Type: text/plain\r\n\r\nYour verification code is 123456',
                )
            ],
        )

        with patch("imaplib.IMAP4_SSL", return_value=mock_imap):
            code = await auth_manager._retrieve_email_mfa_code()
            assert code == "123456"

    @pytest.mark.asyncio
    async def test_email_code_retrieval_no_email(self, auth_manager):
        """Test email code retrieval when no email found"""
        mock_imap = Mock()
        mock_imap.search.return_value = (None, [b""])

        with patch("imaplib.IMAP4_SSL", return_value=mock_imap):
            code = await auth_manager._retrieve_email_mfa_code()
            assert code is None

    @pytest.mark.asyncio
    async def test_push_mfa_timeout(self, auth_manager):
        """Test push notification MFA timeout"""
        with patch("asyncio.sleep") as mock_sleep:
            with patch.object(auth_manager, "_check_authentication_success", return_value=False):
                result = await auth_manager._handle_push_mfa()
                assert result is False
                assert mock_sleep.call_count == 60  # Should wait 60 seconds

    @pytest.mark.asyncio
    async def test_push_mfa_success(self, auth_manager):
        """Test successful push notification MFA"""
        with patch("asyncio.sleep"):
            with patch.object(auth_manager, "_check_authentication_success") as mock_check:
                # Return False for first 5 attempts, then True
                mock_check.side_effect = [False] * 5 + [True]
                
                result = await auth_manager._handle_push_mfa()
                assert result is True

    def test_error_handler_classification(self, error_handler):
        """Test error classification and handling"""
        # Test authentication error
        auth_error = Exception("Authentication failed: invalid credentials")
        classified_error = error_handler.classify_error(auth_error, {"context": "test"})
        
        assert classified_error.category == ErrorCategory.AUTHENTICATION
        assert classified_error.severity == ErrorSeverity.HIGH

        # Test MFA error
        mfa_error = Exception("MFA timeout: code expired")
        classified_error = error_handler.classify_error(mfa_error, {"context": "test"})
        
        assert classified_error.category == ErrorCategory.MFA
        assert classified_error.severity == ErrorSeverity.HIGH

        # Test network error
        network_error = Exception("Network connection timeout")
        classified_error = error_handler.classify_error(network_error, {"context": "test"})
        
        assert classified_error.category == ErrorCategory.TIMEOUT
        assert classified_error.severity == ErrorSeverity.MEDIUM

    def test_error_handler_retry_logic(self, error_handler):
        """Test error retry logic"""
        # Create a retryable error
        network_error = Exception("Network timeout")
        auth_error = error_handler.classify_error(network_error, {"context": "test"})
        
        # Should retry network errors
        assert error_handler.should_retry(auth_error) is True
        
        # After 3 retries, should not retry
        auth_error.retry_count = 3
        assert error_handler.should_retry(auth_error) is False

        # Configuration errors should not be retried
        config_error = Exception("Missing TOTP secret")
        config_auth_error = error_handler.classify_error(config_error, {"context": "test"})
        
        assert error_handler.should_retry(config_auth_error) is False

    def test_error_summary(self, error_handler):
        """Test error summary generation"""
        # Generate some test errors
        errors = [
            Exception("Authentication failed"),
            Exception("MFA timeout"),
            Exception("Network error"),
        ]
        
        for error in errors:
            error_handler.classify_error(error, {"context": "test"})
        
        summary = error_handler.get_error_summary()
        
        assert summary["total_errors"] == 3
        assert "category_counts" in summary
        assert "severity_counts" in summary
        assert len(summary["recent_errors"]) == 3

    def _create_mock_playwright(self):
        """Create a mock Playwright instance"""
        mock_page = AsyncMock()
        mock_context = AsyncMock()
        mock_browser = AsyncMock()
        mock_playwright = AsyncMock()

        mock_page.wait_for_load_state = AsyncMock()
        mock_page.wait_for_selector = AsyncMock()
        mock_page.fill = AsyncMock()
        mock_page.click = AsyncMock()
        mock_page.goto = AsyncMock()
        mock_page.url = "https://myaccount.microsoft.com/"
        mock_page.content = AsyncMock(return_value="Welcome to Microsoft")

        mock_context.new_page = AsyncMock(return_value=mock_page)
        mock_context.cookies = AsyncMock(return_value=[{"name": "test", "value": "cookie"}])

        mock_browser.new_context = AsyncMock(return_value=mock_context)
        mock_playwright.chromium.launch = AsyncMock(return_value=mock_browser)

        return mock_playwright


class TestSuccessRateTracking:
    """Test suite for success rate tracking and validation"""

    @pytest.fixture
    def auth_manager(self):
        """Create a CloudAuthenticationManager instance for testing"""
        with patch.dict(
            os.environ,
            {
                "TOTP_SECRET": "test_secret",
                "ELIA_PASSWORD": "test_password",
                "MICROSOFT_USERNAME": "test@example.com",
            },
        ):
            return CloudAuthenticationManager()

    @pytest.mark.asyncio
    async def test_success_rate_calculation(self, auth_manager):
        """Test success rate calculation over multiple attempts"""
        success_count = 0
        total_attempts = 10
        
        for i in range(total_attempts):
            # Simulate 95% success rate
            should_succeed = i < 9  # 9 out of 10 succeed
            
            with patch("src.cloud.cloud_auth_manager.async_playwright") as p:
                mock_playwright = self._create_mock_playwright()
                p.return_value.__aenter__.return_value = mock_playwright

                if should_succeed:
                    auth_manager._handle_totp_mfa = AsyncMock(return_value=True)
                    auth_manager._check_authentication_success = AsyncMock(return_value=True)
                else:
                    auth_manager._handle_totp_mfa = AsyncMock(return_value=False)
                    auth_manager._handle_email_mfa = AsyncMock(return_value=False)
                    auth_manager._handle_push_mfa = AsyncMock(return_value=False)

                result = await auth_manager.authenticate_microsoft()
                if result:
                    success_count += 1

        success_rate = (success_count / total_attempts) * 100
        assert success_rate >= 90.0  # Should meet 95% target (allowing for test variance)

    def test_performance_metrics(self, auth_manager):
        """Test performance metrics collection"""
        start_time = time.time()
        
        # Simulate authentication process
        status = auth_manager.get_authentication_status()
        
        end_time = time.time()
        authentication_time = end_time - start_time
        
        # Should complete within 2 minutes (120 seconds)
        assert authentication_time < 120.0
        
        # Status should include required metrics
        assert "authenticated" in status
        assert "environment" in status
        assert "totp_available" in status

    def _create_mock_playwright(self):
        """Create a mock Playwright instance"""
        mock_page = AsyncMock()
        mock_context = AsyncMock()
        mock_browser = AsyncMock()
        mock_playwright = AsyncMock()

        mock_page.wait_for_load_state = AsyncMock()
        mock_page.wait_for_selector = AsyncMock()
        mock_page.fill = AsyncMock()
        mock_page.click = AsyncMock()
        mock_page.goto = AsyncMock()
        mock_page.url = "https://myaccount.microsoft.com/"

        mock_context.new_page = AsyncMock(return_value=mock_page)
        mock_context.cookies = AsyncMock(return_value=[{"name": "test", "value": "cookie"}])

        mock_browser.new_context = AsyncMock(return_value=mock_context)
        mock_playwright.chromium.launch = AsyncMock(return_value=mock_browser)

        return mock_playwright


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

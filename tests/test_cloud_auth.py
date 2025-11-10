"""
Cloud Authentication Tests for Elia Parking Bot
Tests GitHub Actions optimized authentication flows
"""

import pytest
import asyncio
import os
from unittest.mock import Mock, patch, AsyncMock
from src.cloud.cloud_auth_manager import CloudAuthenticationManager, is_cloud_environment


class TestCloudAuthenticationManager:
    """Test suite for CloudAuthenticationManager"""

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
    def mock_playwright(self):
        """Mock Playwright browser automation"""
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

        return mock_playwright, mock_browser, mock_context, mock_page

    def test_environment_detection(self):
        """Test cloud environment detection"""
        # Test cloud environment
        with patch.dict(os.environ, {"GITHUB_ACTIONS": "true"}):
            assert is_cloud_environment() is True

        # Test local environment
        with patch.dict(os.environ, {}, clear=True):
            assert is_cloud_environment() is False

    def test_auth_manager_initialization(self):
        """Test CloudAuthenticationManager initialization"""
        with patch.dict(
            os.environ,
            {
                "TOTP_SECRET": "test_secret",
                "ELIA_PASSWORD": "test_password",
                "MICROSOFT_USERNAME": "test@example.com",
            },
        ):
            manager = CloudAuthenticationManager()
            assert manager.is_cloud is False
            assert manager.credentials["totp_secret"] == "test_secret"
            assert manager.totp is not None

    def test_missing_credentials_error(self):
        """Test error handling for missing credentials"""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError, match="Missing required credentials"):
                CloudAuthenticationManager()

    @pytest.mark.asyncio
    async def test_totp_mfa_success(self, auth_manager, mock_playwright):
        """Test successful TOTP MFA authentication"""
        mock_playwright, mock_browser, mock_context, mock_page = mock_playwright

        with patch("src.cloud.cloud_auth_manager.async_playwright") as p:
            p.return_value.__aenter__.return_value = mock_playwright

            # Mock TOTP code generation
            auth_manager.totp.now = Mock(return_value="123456")

            # Mock authentication success check
            auth_manager._check_authentication_success = AsyncMock(return_value=True)

            result = await auth_manager.authenticate_microsoft()

            assert result is True
            assert auth_manager.current_mfa_method == "totp"

    @pytest.mark.asyncio
    async def test_email_mfa_fallback(self, auth_manager, mock_playwright):
        """Test email MFA fallback when TOTP fails"""
        mock_playwright, mock_browser, mock_context, mock_page = mock_playwright

        with patch("src.cloud.cloud_auth_manager.async_playwright") as p:
            p.return_value.__aenter__.return_value = mock_playwright

            # Mock TOTP failure
            auth_manager._handle_totp_mfa = AsyncMock(return_value=False)
            auth_manager.totp = None  # No TOTP available

            # Mock email MFA success
            auth_manager._handle_email_mfa = AsyncMock(return_value=True)
            auth_manager._retrieve_email_mfa_code = AsyncMock(return_value="654321")

            # Mock authentication success check
            auth_manager._check_authentication_success = AsyncMock(return_value=True)

            result = await auth_manager.authenticate_microsoft()

            assert result is True
            assert auth_manager.current_mfa_method == "email"

    @pytest.mark.asyncio
    async def test_push_mfa_fallback(self, auth_manager, mock_playwright):
        """Test push notification MFA fallback"""
        mock_playwright, mock_browser, mock_context, mock_page = mock_playwright

        with patch("src.cloud.cloud_auth_manager.async_playwright") as p:
            p.return_value.__aenter__.return_value = mock_playwright

            # Mock TOTP and email failure
            auth_manager._handle_totp_mfa = AsyncMock(return_value=False)
            auth_manager._handle_email_mfa = AsyncMock(return_value=False)
            auth_manager.totp = None

            # Mock push MFA success
            auth_manager._handle_push_mfa = AsyncMock(return_value=True)

            # Mock authentication success check
            auth_manager._check_authentication_success = AsyncMock(return_value=True)

            result = await auth_manager.authenticate_microsoft()

            assert result is True
            assert auth_manager.current_mfa_method == "push"

    @pytest.mark.asyncio
    async def test_all_mfa_methods_fail(self, auth_manager, mock_playwright):
        """Test authentication failure when all MFA methods fail"""
        mock_playwright, mock_browser, mock_context, mock_page = mock_playwright

        with patch("src.cloud.cloud_auth_manager.async_playwright") as p:
            p.return_value.__aenter__.return_value = mock_playwright

            # Mock all MFA methods failing
            auth_manager._handle_totp_mfa = AsyncMock(return_value=False)
            auth_manager._handle_email_mfa = AsyncMock(return_value=False)
            auth_manager._handle_push_mfa = AsyncMock(return_value=False)

            result = await auth_manager.authenticate_microsoft()

            assert result is False

    @pytest.mark.asyncio
    async def test_email_code_retrieval(self, auth_manager):
        """Test email MFA code retrieval"""
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

    def test_authentication_status(self, auth_manager):
        """Test authentication status reporting"""
        auth_manager.cookies = [{"name": "test", "value": "cookie"}]
        auth_manager.current_mfa_method = "totp"

        status = auth_manager.get_authentication_status()

        assert status["authenticated"] is True
        assert status["mfa_method_used"] == "totp"
        assert status["environment"] == "local"
        assert status["totp_available"] is True
        assert status["cookies_count"] == 1

    @pytest.mark.asyncio
    async def test_authentication_health_validation(self, auth_manager):
        """Test authentication health validation"""
        # Test healthy authentication
        auth_manager.cookies = [{"name": "test", "value": "cookie"}]
        auth_manager.totp = Mock()

        result = await auth_manager.validate_authentication_health()
        assert result is True

        # Test unhealthy authentication (no cookies)
        auth_manager.cookies = []
        result = await auth_manager.validate_authentication_health()
        assert result is False

    @pytest.mark.asyncio
    async def test_browser_cleanup(self, auth_manager):
        """Test browser resource cleanup"""
        mock_context = AsyncMock()
        mock_browser = AsyncMock()
        auth_manager.context = mock_context
        auth_manager.browser = mock_browser

        await auth_manager._cleanup_browser()

        mock_context.close.assert_called_once()
        mock_browser.close.assert_called_once()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

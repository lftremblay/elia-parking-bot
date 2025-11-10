"""
Cloud Authentication Configuration for Elia Parking Bot
GitHub Actions environment settings and credential management
"""

import os
from typing import Dict, Any, Optional
from dataclasses import dataclass
from pathlib import Path


@dataclass
class CloudAuthConfig:
    """Configuration for cloud authentication environment"""

    # Environment detection
    is_cloud: bool = False
    environment_type: str = "local"

    # GitHub Secrets mapping
    totp_secret: Optional[str] = None
    elia_password: Optional[str] = None
    smtp_password: Optional[str] = None
    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 993
    email_address: Optional[str] = None
    microsoft_username: Optional[str] = None

    # Authentication settings
    mfa_timeout: int = 60
    totp_first: bool = True
    backup_mfa_methods: list = None

    # Browser settings for cloud
    headless_mode: bool = True
    browser_args: list = None

    # Session management
    ephemeral_sessions: bool = True
    session_timeout: int = 7200  # 2 hours

    def __post_init__(self):
        """Initialize default values and detect environment"""
        if self.backup_mfa_methods is None:
            self.backup_mfa_methods = ["totp", "email", "push"]

        if self.browser_args is None:
            self.browser_args = (
                ["--no-sandbox", "--disable-dev-shm-usage"]
                if self.is_cloud
                else []
            )

        # Auto-detect environment
        self._detect_environment()

        # Load credentials from environment
        self._load_credentials()

    def _detect_environment(self):
        """Detect if running in cloud environment"""
        self.is_cloud = (
            os.getenv("GITHUB_ACTIONS") == "true"
            or os.getenv("ENVIRONMENT") == "docker"
            or os.getenv("CI") == "true"
        )

        self.environment_type = "cloud" if self.is_cloud else "local"
        self.headless_mode = True if self.is_cloud else False

        # Update browser args based on environment
        if self.is_cloud:
            self.browser_args = ["--no-sandbox", "--disable-dev-shm-usage"]
        else:
            self.browser_args = []

    def _load_credentials(self):
        """Load credentials from environment variables"""
        self.totp_secret = os.getenv("TOTP_SECRET")
        self.elia_password = os.getenv("ELIA_PASSWORD")
        self.smtp_password = os.getenv("SMTP_PASSWORD")
        self.email_address = os.getenv("EMAIL_ADDRESS")
        self.microsoft_username = os.getenv("MICROSOFT_USERNAME")

        # Override SMTP settings if provided
        if os.getenv("SMTP_HOST"):
            self.smtp_host = os.getenv("SMTP_HOST")
        if os.getenv("SMTP_PORT"):
            self.smtp_port = int(os.getenv("SMTP_PORT"))

    def validate_credentials(self) -> Dict[str, Any]:
        """Validate required credentials are present"""
        required = ["totp_secret", "elia_password", "microsoft_username"]
        missing = []

        for cred in required:
            if not getattr(self, cred):
                missing.append(cred)

        return {
            "valid": len(missing) == 0,
            "missing": missing,
            "environment": self.environment_type,
            "totp_available": bool(self.totp_secret),
            "email_mfa_available": all(
                [self.email_address, self.smtp_password]
            ),
        }

    def get_auth_method_priority(self) -> list:
        """Get MFA method priority based on availability"""
        methods = []

        if self.totp_secret:
            methods.append("totp")

        if all([self.email_address, self.smtp_password]):
            methods.append("email")

        methods.append("push")  # Always available as last resort

        return methods

    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary (excluding secrets)"""
        return {
            "environment_type": self.environment_type,
            "is_cloud": self.is_cloud,
            "headless_mode": self.headless_mode,
            "mfa_timeout": self.mfa_timeout,
            "totp_first": self.totp_first,
            "backup_mfa_methods": self.backup_mfa_methods,
            "ephemeral_sessions": self.ephemeral_sessions,
            "session_timeout": self.session_timeout,
            "totp_available": bool(self.totp_secret),
            "email_mfa_available": all(
                [self.email_address, self.smtp_password]
            ),
            "microsoft_username_configured": bool(self.microsoft_username),
        }


# Factory function
def create_cloud_config() -> CloudAuthConfig:
    """Create and return cloud authentication configuration"""
    return CloudAuthConfig()


# Environment helpers
def is_github_actions() -> bool:
    """Check if running in GitHub Actions"""
    return os.getenv("GITHUB_ACTIONS") == "true"


def is_docker_environment() -> bool:
    """Check if running in Docker environment"""
    return (
        os.getenv("ENVIRONMENT") == "docker" or os.path.exists("/.dockerenv")
    )


def is_ci_environment() -> bool:
    """Check if running in any CI environment"""
    return os.getenv("CI") == "true" or is_github_actions() or is_docker_environment()

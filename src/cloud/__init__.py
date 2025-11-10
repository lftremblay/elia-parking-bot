"""
Cloud Authentication Module for Elia Parking Bot
GitHub Actions optimized authentication components
"""

from .cloud_auth_manager import (
    CloudAuthenticationManager,
    create_auth_manager,
    is_cloud_environment,
)

__all__ = [
    "CloudAuthenticationManager",
    "create_auth_manager",
    "is_cloud_environment",
]
__version__ = "1.0.0"

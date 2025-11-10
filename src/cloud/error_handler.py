"""
Enhanced Error Handler for Cloud Authentication
Provides comprehensive error classification, logging, and notification
"""

import os
import sys
import traceback
from enum import Enum
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from datetime import datetime
from loguru import logger


class ErrorSeverity(Enum):
    """Error severity levels for classification"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ErrorCategory(Enum):
    """Error categories for better classification"""
    AUTHENTICATION = "authentication"
    MFA = "mfa"
    NETWORK = "network"
    BROWSER = "browser"
    CONFIGURATION = "configuration"
    ENVIRONMENT = "environment"
    TIMEOUT = "timeout"
    SYSTEM = "system"


@dataclass
class AuthError:
    """Structured error information for authentication failures"""
    error_id: str
    category: ErrorCategory
    severity: ErrorSeverity
    message: str
    details: Dict[str, Any]
    timestamp: datetime
    retry_count: int = 0
    resolved: bool = False


class CloudAuthErrorHandler:
    """Enhanced error handler for cloud authentication"""
    
    def __init__(self):
        """Initialize error handler with notification settings"""
        self.error_history: List[AuthError] = []
        self.error_counts: Dict[str, int] = {}
        self.max_error_history = 100
        
        # Notification settings
        self.enable_notifications = os.getenv("ENABLE_ERROR_NOTIFICATIONS", "false").lower() == "true"
        self.discord_webhook = os.getenv("DISCORD_WEBHOOK_URL")
        self.telegram_bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
        self.telegram_chat_id = os.getenv("TELEGRAM_CHAT_ID")
        
        logger.info("🛡️ CloudAuthErrorHandler initialized")
    
    def classify_error(self, error: Exception, context: Dict[str, Any] = None) -> AuthError:
        """
        Classify and structure authentication errors
        """
        error_id = f"auth_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{id(error)}"
        error_message = str(error)
        error_type = type(error).__name__
        
        # Determine category and severity
        category, severity = self._analyze_error(error, error_message, error_type)
        
        # Create structured error
        auth_error = AuthError(
            error_id=error_id,
            category=category,
            severity=severity,
            message=error_message,
            details={
                "error_type": error_type,
                "context": context or {},
                "traceback": traceback.format_exc(),
                "environment": os.getenv("ENVIRONMENT", "local"),
                "cloud_environment": os.getenv("GITHUB_ACTIONS") == "true"
            },
            timestamp=datetime.now()
        )
        
        # Store error
        self._store_error(auth_error)
        
        # Log error with appropriate level
        self._log_error(auth_error)
        
        # Send notifications if enabled
        if self.enable_notifications and severity in [ErrorSeverity.HIGH, ErrorSeverity.CRITICAL]:
            self._send_notification(auth_error)
        
        return auth_error
    
    def _analyze_error(self, error: Exception, message: str, error_type: str) -> tuple[ErrorCategory, ErrorSeverity]:
        """
        Analyze error to determine category and severity
        """
        message_lower = message.lower()
        
        # Authentication errors
        if any(keyword in message_lower for keyword in ["authentication", "login", "credential", "unauthorized"]):
            if "failed" in message_lower or "invalid" in message_lower:
                return ErrorCategory.AUTHENTICATION, ErrorSeverity.HIGH
            return ErrorCategory.AUTHENTICATION, ErrorSeverity.MEDIUM
        
        # MFA errors
        if any(keyword in message_lower for keyword in ["mfa", "totp", "verification", "code"]):
            if "timeout" in message_lower or "expired" in message_lower:
                return ErrorCategory.MFA, ErrorSeverity.HIGH
            return ErrorCategory.MFA, ErrorSeverity.MEDIUM
        
        # Network errors
        if any(keyword in message_lower for keyword in ["network", "connection", "timeout", "dns"]):
            if "timeout" in message_lower:
                return ErrorCategory.TIMEOUT, ErrorSeverity.MEDIUM
            return ErrorCategory.NETWORK, ErrorSeverity.MEDIUM
        
        # Browser errors
        if any(keyword in message_lower for keyword in ["browser", "playwright", "selenium", "chrome"]):
            return ErrorCategory.BROWSER, ErrorSeverity.MEDIUM
        
        # Configuration errors
        if any(keyword in message_lower for keyword in ["config", "missing", "secret", "credential"]):
            return ErrorCategory.CONFIGURATION, ErrorSeverity.HIGH
        
        # Environment errors
        if any(keyword in message_lower for keyword in ["environment", "docker", "github"]):
            return ErrorCategory.ENVIRONMENT, ErrorSeverity.MEDIUM
        
        # System errors
        if any(keyword in message_lower for keyword in ["system", "memory", "disk", "permission"]):
            return ErrorCategory.SYSTEM, ErrorSeverity.HIGH
        
        # Default classification
        return ErrorCategory.SYSTEM, ErrorSeverity.MEDIUM
    
    def _store_error(self, error: AuthError):
        """Store error in history and update counts"""
        self.error_history.append(error)
        
        # Limit history size
        if len(self.error_history) > self.max_error_history:
            self.error_history = self.error_history[-self.max_error_history:]
        
        # Update error counts
        error_key = f"{error.category.value}_{error.severity.value}"
        self.error_counts[error_key] = self.error_counts.get(error_key, 0) + 1
    
    def _log_error(self, error: AuthError):
        """Log error with appropriate level and details"""
        log_message = (
            f"🚨 [{error.severity.value.upper()}] {error.category.value.upper()} Error: {error.message} "
            f"(ID: {error.error_id})"
        )
        
        # Choose log level based on severity
        if error.severity == ErrorSeverity.CRITICAL:
            logger.error(log_message)
            logger.error(f"🔍 Details: {error.details}")
        elif error.severity == ErrorSeverity.HIGH:
            logger.error(log_message)
        elif error.severity == ErrorSeverity.MEDIUM:
            logger.warning(log_message)
        else:
            logger.info(log_message)
    
    def _send_notification(self, error: AuthError):
        """Send error notification via configured channels"""
        try:
            # Discord notification
            if self.discord_webhook:
                self._send_discord_notification(error)
            
            # Telegram notification
            if self.telegram_bot_token and self.telegram_chat_id:
                self._send_telegram_notification(error)
                
        except Exception as e:
            logger.error(f"❌ Failed to send error notification: {e}")
    
    def _send_discord_notification(self, error: AuthError):
        """Send Discord webhook notification"""
        import requests
        
        embed = {
            "title": f"🚨 {error.severity.value.upper()} Authentication Error",
            "description": f"**Category:** {error.category.value.title()}\n"
                          f"**Message:** {error.message}\n"
                          f"**Error ID:** {error.error_id}\n"
                          f"**Time:** {error.timestamp.strftime('%Y-%m-%d %H:%M:%S UTC')}",
            "color": self._get_discord_color(error.severity),
            "fields": [
                {
                    "name": "Environment",
                    "value": "Cloud (GitHub Actions)" if error.details.get("cloud_environment") else "Local",
                    "inline": True
                },
                {
                    "name": "Error Type",
                    "value": error.details.get("error_type", "Unknown"),
                    "inline": True
                }
            ]
        }
        
        data = {"embeds": [embed]}
        requests.post(self.discord_webhook, json=data, timeout=10)
    
    def _send_telegram_notification(self, error: AuthError):
        """Send Telegram notification"""
        import requests
        
        message = (
            f"🚨 *{error.severity.value.upper()} Authentication Error*\n\n"
            f"📋 *Category:* {error.category.value.title()}\n"
            f"💬 *Message:* {error.message}\n"
            f"🆔 *Error ID:* {error.error_id}\n"
            f"🕐 *Time:* {error.timestamp.strftime('%Y-%m-%d %H:%M:%S UTC')}\n"
            f"🌐 *Environment:* {'Cloud (GitHub Actions)' if error.details.get('cloud_environment') else 'Local'}"
        )
        
        url = f"https://api.telegram.org/bot{self.telegram_bot_token}/sendMessage"
        data = {
            "chat_id": self.telegram_chat_id,
            "text": message,
            "parse_mode": "Markdown"
        }
        requests.post(url, data=data, timeout=10)
    
    def _get_discord_color(self, severity: ErrorSeverity) -> int:
        """Get Discord embed color based on severity"""
        colors = {
            ErrorSeverity.LOW: 0x00ff00,    # Green
            ErrorSeverity.MEDIUM: 0xffff00,  # Yellow
            ErrorSeverity.HIGH: 0xff6600,    # Orange
            ErrorSeverity.CRITICAL: 0xff0000  # Red
        }
        return colors.get(severity, 0xffff00)
    
    def get_error_summary(self) -> Dict[str, Any]:
        """Get summary of recent errors"""
        if not self.error_history:
            return {"total_errors": 0, "recent_errors": []}
        
        # Count errors by category and severity
        category_counts = {}
        severity_counts = {}
        
        for error in self.error_history:
            category_counts[error.category.value] = category_counts.get(error.category.value, 0) + 1
            severity_counts[error.severity.value] = severity_counts.get(error.severity.value, 0) + 1
        
        # Get recent errors (last 10)
        recent_errors = [
            {
                "error_id": error.error_id,
                "category": error.category.value,
                "severity": error.severity.value,
                "message": error.message,
                "timestamp": error.timestamp.isoformat()
            }
            for error in self.error_history[-10:]
        ]
        
        return {
            "total_errors": len(self.error_history),
            "category_counts": category_counts,
            "severity_counts": severity_counts,
            "recent_errors": recent_errors,
            "last_error": self.error_history[-1].timestamp.isoformat() if self.error_history else None
        }
    
    def should_retry(self, error: AuthError) -> bool:
        """Determine if an error should be retried"""
        # Don't retry configuration errors
        if error.category == ErrorCategory.CONFIGURATION:
            return False
        
        # Limit retry attempts
        if error.retry_count >= 3:
            return False
        
        # Retry network and timeout errors
        if error.category in [ErrorCategory.NETWORK, ErrorCategory.TIMEOUT]:
            return True
        
        # Retry medium severity authentication errors
        if error.category == ErrorCategory.AUTHENTICATION and error.severity == ErrorSeverity.MEDIUM:
            return True
        
        return False
    
    def clear_error_history(self):
        """Clear error history"""
        self.error_history.clear()
        self.error_counts.clear()
        logger.info("🧹 Error history cleared")


# Global error handler instance
error_handler = CloudAuthErrorHandler()


def handle_auth_error(error: Exception, context: Dict[str, Any] = None) -> AuthError:
    """
    Convenience function to handle authentication errors
    """
    return error_handler.classify_error(error, context)


def get_error_summary() -> Dict[str, Any]:
    """
    Convenience function to get error summary
    """
    return error_handler.get_error_summary()


def should_retry_error(error: AuthError) -> bool:
    """
    Convenience function to check if error should be retried
    """
    return error_handler.should_retry(error)

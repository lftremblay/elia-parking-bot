"""
Advanced Authentication Manager for Elia Parking Bot
Handles Microsoft SSO, MFA, and aggressive token refresh strategies
"""

import json
import time
import pyotp
import base64
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from loguru import logger
from cryptography.fernet import Fernet
from pathlib import Path
import pickle


class AuthenticationManager:
    """Manages authentication with multiple fallback strategies"""
    
    def __init__(self, config_path: str = "config.json", config: dict = None):
        if config is not None:
            self.config = config
        else:
            self.config = self._load_config(config_path)
        self.session_file = Path("./session_data/auth_session.pkl")
        self.token_file = Path("./session_data/tokens.enc")
        self.session_file.parent.mkdir(exist_ok=True)
        
        # Initialize encryption key
        self.cipher = self._init_encryption()
        
        # Session state
        self.access_token = None
        self.refresh_token = None
        self.token_expiry = None
        self.cookies = {}
        self.headers = {}
        
        logger.info("🔐 AuthenticationManager initialized")
    
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load configuration from file"""
        with open(config_path, 'r') as f:
            return json.load(f)
    
    def _init_encryption(self) -> Fernet:
        """Initialize or load encryption key for secure storage"""
        key_file = Path("./session_data/.key")
        
        if key_file.exists():
            with open(key_file, 'rb') as f:
                key = f.read()
        else:
            key = Fernet.generate_key()
            key_file.parent.mkdir(exist_ok=True)
            with open(key_file, 'wb') as f:
                f.write(key)
            logger.info("🔑 Generated new encryption key")
        
        return Fernet(key)
    
    def save_session(self):
        """Save encrypted session data"""
        session_data = {
            'access_token': self.access_token,
            'refresh_token': self.refresh_token,
            'token_expiry': self.token_expiry.isoformat() if self.token_expiry else None,
            'cookies': self.cookies,
            'headers': self.headers,
            'timestamp': datetime.now().isoformat()
        }
        
        # Encrypt and save
        encrypted_data = self.cipher.encrypt(pickle.dumps(session_data))
        with open(self.token_file, 'wb') as f:
            f.write(encrypted_data)
        
        logger.info("💾 Session data saved and encrypted")
    
    def load_session(self) -> bool:
        """Load and decrypt session data"""
        if not self.token_file.exists():
            logger.warning("⚠️  No saved session found")
            return False
        
        try:
            with open(self.token_file, 'rb') as f:
                encrypted_data = f.read()
            
            decrypted_data = self.cipher.decrypt(encrypted_data)
            session_data = pickle.loads(decrypted_data)
            
            self.access_token = session_data.get('access_token')
            self.refresh_token = session_data.get('refresh_token')
            
            expiry_str = session_data.get('token_expiry')
            self.token_expiry = datetime.fromisoformat(expiry_str) if expiry_str else None
            
            self.cookies = session_data.get('cookies', {})
            self.headers = session_data.get('headers', {})
            
            logger.info("✅ Session data loaded successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to load session: {e}")
            return False
    
    def is_session_valid(self) -> bool:
        """Check if current session is valid"""
        if not self.access_token:
            return False
        
        if self.token_expiry:
            # Consider expired if less than 5 minutes remaining
            return datetime.now() < (self.token_expiry - timedelta(minutes=5))
        
        # If no expiry time, assume valid for now
        return True
    
    def get_totp_code(self) -> Optional[str]:
        """Generate TOTP code for MFA"""
        # First try config file
        totp_secret = self.config.get('mfa', {}).get('totp_secret')
        
        # If not in config, try environment variable
        if not totp_secret:
            import os
            from dotenv import load_dotenv
            load_dotenv()
            totp_secret = os.getenv('TOTP_SECRET')
        
        if not totp_secret:
            logger.warning("⚠️  No TOTP secret configured (check config.json or .env)")
            return None
        
        try:
            totp = pyotp.TOTP(totp_secret)
            code = totp.now()
            logger.info(f"🔢 Generated TOTP code: {code[:2]}****")
            return code
        except Exception as e:
            logger.error(f"❌ TOTP generation failed: {e}")
            return None
    
    def prepare_auth_headers(self) -> Dict[str, str]:
        """Prepare authentication headers"""
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9,fr;q=0.8',
            'Origin': 'https://app.elia.io',
            'Referer': 'https://app.elia.io/',
        }
        
        if self.access_token:
            headers['Authorization'] = f'Bearer {self.access_token}'
        
        return headers
    
    def aggressive_token_refresh(self, force: bool = False) -> bool:
        """
        Aggressively refresh tokens with multiple retry strategies
        Returns True if refresh successful
        """
        if not force and self.is_session_valid():
            logger.info("✅ Session still valid, no refresh needed")
            return True
        
        logger.info("🔄 Starting aggressive token refresh...")
        
        strategies = [
            self._refresh_with_refresh_token,
            self._refresh_with_stored_cookies,
            self._refresh_with_browser_profile,
        ]
        
        for i, strategy in enumerate(strategies, 1):
            logger.info(f"🎯 Attempting refresh strategy {i}/{len(strategies)}")
            try:
                if strategy():
                    logger.success(f"✅ Refresh successful with strategy {i}")
                    self.save_session()
                    return True
            except Exception as e:
                logger.warning(f"⚠️  Strategy {i} failed: {e}")
                continue
        
        logger.error("❌ All refresh strategies failed")
        return False
    
    def _refresh_with_refresh_token(self) -> bool:
        """Strategy 1: Use refresh token"""
        if not self.refresh_token:
            logger.warning("No refresh token available")
            return False
        
        # This would call the Microsoft token endpoint
        # Implementation depends on the actual OAuth flow used by Elia
        logger.info("🔄 Attempting refresh with refresh token...")
        
        # TODO: Implement actual refresh token call
        # This is a placeholder for the actual Microsoft OAuth refresh
        return False
    
    def _refresh_with_stored_cookies(self) -> bool:
        """Strategy 2: Use stored cookies"""
        if not self.cookies:
            logger.warning("No stored cookies available")
            return False
        
        logger.info("🍪 Attempting refresh with stored cookies...")
        
        # TODO: Validate cookies are still valid
        return False
    
    def _refresh_with_browser_profile(self) -> bool:
        """Strategy 3: Extract from persistent browser profile"""
        profile_path = Path(self.config.get('advanced', {}).get('browser_profile_path', './browser_data'))
        
        if not profile_path.exists():
            logger.warning("No browser profile found")
            return False
        
        logger.info("🌐 Attempting refresh from browser profile...")
        
        # TODO: Extract cookies/tokens from browser profile
        return False
    
    def update_tokens(self, access_token: str, refresh_token: str = None, expires_in: int = 3600):
        """Update tokens after successful authentication"""
        self.access_token = access_token
        if refresh_token:
            self.refresh_token = refresh_token
        
        self.token_expiry = datetime.now() + timedelta(seconds=expires_in)
        
        logger.success(f"✅ Tokens updated, expires at {self.token_expiry}")
        self.save_session()
    
    def clear_session(self):
        """Clear all session data"""
        self.access_token = None
        self.refresh_token = None
        self.token_expiry = None
        self.cookies = {}
        self.headers = {}
        
        if self.token_file.exists():
            self.token_file.unlink()
        
        logger.info("🧹 Session data cleared")


if __name__ == "__main__":
    # Test the authentication manager
    auth = AuthenticationManager()
    
    # Load existing session if available
    if auth.load_session():
        print(f"Session valid: {auth.is_session_valid()}")
    
    # Generate TOTP if configured
    code = auth.get_totp_code()
    if code:
        print(f"TOTP Code: {code}")

"""
Security Module

Authentication, authorization, and security utilities.
"""

import hashlib
import hmac
import secrets
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import jwt
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from passlib.context import CryptContext
from app.core.config import settings
from app.core.logger import get_logger

logger = get_logger(__name__)

class SecurityManager:
    """Security manager for authentication and authorization"""
    
    def __init__(self):
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        self.secret_key = settings.SECRET_KEY
        self.algorithm = "HS256"
        self.access_token_expire_minutes = 30
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify password against hash"""
        return self.pwd_context.verify(plain_password, hashed_password)
    
    def get_password_hash(self, password: str) -> str:
        """Hash password"""
        return self.pwd_context.hash(password)
    
    def create_access_token(self, data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        """Create JWT access token"""
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        
        return encoded_jwt
    
    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify and decode JWT token"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except jwt.PyJWTError as e:
            logger.warning(f"Token verification failed: {e}")
            return None
    
    def generate_api_key(self, user_id: str) -> str:
        """Generate API key for user"""
        data = f"{user_id}:{datetime.utcnow().isoformat()}:{secrets.token_hex(16)}"
        return hashlib.sha256(data.encode()).hexdigest()
    
    def validate_api_key(self, api_key: str, user_id: str) -> bool:
        """Validate API key (simplified for demo)"""
        # In production, store and validate against database
        return len(api_key) == 64 and api_key.isalnum()
    
    def create_session_token(self, user_id: str) -> str:
        """Create session token for anonymous users"""
        timestamp = datetime.utcnow().isoformat()
        data = f"{user_id}:{timestamp}"
        
        signature = hmac.new(
            self.secret_key.encode(),
            data.encode(),
            hashlib.sha256
        ).hexdigest()
        
        return f"{data}:{signature}"
    
    def verify_session_token(self, token: str) -> Optional[str]:
        """Verify session token and extract user_id"""
        try:
            parts = token.split(":")
            if len(parts) != 3:
                return None
            
            user_id, timestamp, signature = parts
            data = f"{user_id}:{timestamp}"
            
            expected_signature = hmac.new(
                self.secret_key.encode(),
                data.encode(),
                hashlib.sha256
            ).hexdigest()
            
            if hmac.compare_digest(signature, expected_signature):
                # Check if token is not expired (24 hours)
                token_time = datetime.fromisoformat(timestamp)
                if datetime.utcnow() - token_time < timedelta(hours=24):
                    return user_id
            
            return None
            
        except Exception as e:
            logger.warning(f"Session token verification failed: {e}")
            return None
    
    def sanitize_input(self, user_input: str) -> str:
        """Sanitize user input to prevent injection attacks"""
        if not user_input:
            return ""
        
        # Remove potentially dangerous characters
        dangerous_chars = ["<", ">", "&", "\"", "'", ";", "(", ")", "{", "}", "[", "]"]
        sanitized = user_input
        
        for char in dangerous_chars:
            sanitized = sanitized.replace(char, "")
        
        # Limit length
        max_length = 1000
        if len(sanitized) > max_length:
            sanitized = sanitized[:max_length]
        
        return sanitized.strip()
    
    def check_rate_limit(self, user_id: str, action: str, limit: int = 60, window: int = 60) -> bool:
        """Check if user has exceeded rate limit"""
        # Simplified rate limiting (in production, use Redis)
        # This is a basic implementation for demo purposes
        
        if not hasattr(self, '_rate_limits'):
            self._rate_limits = {}
        
        key = f"{user_id}:{action}"
        current_time = datetime.utcnow()
        
        if key not in self._rate_limits:
            self._rate_limits[key] = []
        
        # Clean old entries
        cutoff_time = current_time - timedelta(seconds=window)
        self._rate_limits[key] = [
            timestamp for timestamp in self._rate_limits[key]
            if timestamp > cutoff_time
        ]
        
        # Check limit
        if len(self._rate_limits[key]) >= limit:
            return False
        
        # Add current request
        self._rate_limits[key].append(current_time)
        return True

# Global security manager instance
security_manager = SecurityManager()
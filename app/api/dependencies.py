"""
FastAPI Dependencies

Common dependencies for request validation, rate limiting, and security.
"""

from fastapi import HTTPException, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
import time
from collections import defaultdict
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from app.core.logger import get_logger
from app.core.exceptions import InvalidInputError

logger = get_logger(__name__)
security = HTTPBearer(auto_error=False)

# Rate limiting storage (in production, use Redis)
request_counts = defaultdict(list)

async def validate_request_size(request: Request):
    """Validate request size to prevent large payloads"""
    content_length = request.headers.get("content-length")
    
    if content_length:
        content_length = int(content_length)
        max_size = 1024 * 1024  # 1MB limit
        
        if content_length > max_size:
            raise HTTPException(
                status_code=413,
                detail="Request payload too large"
            )
    
    return True

async def rate_limit_dependency(request: Request):
    """Rate limiting dependency"""
    client_ip = request.client.host
    current_time = time.time()
    
    # Clean old requests (older than 1 minute)
    minute_ago = current_time - 60
    request_counts[client_ip] = [
        req_time for req_time in request_counts[client_ip] 
        if req_time > minute_ago
    ]
    
    # Check rate limit (60 requests per minute)
    if len(request_counts[client_ip]) >= 60:
        raise HTTPException(
            status_code=429,
            detail="Rate limit exceeded. Maximum 60 requests per minute."
        )
    
    # Add current request
    request_counts[client_ip].append(current_time)
    
    return True

async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Optional[str]:
    """Get current user from JWT token (optional for this demo)"""
    if not credentials:
        return None
    
    # In production, validate JWT token here
    # For demo purposes, just return the token as user_id
    return credentials.credentials

async def validate_message_content(message: str) -> str:
    """Validate and sanitize message content"""
    if not message or not message.strip():
        raise InvalidInputError("Message cannot be empty")
    
    message = message.strip()
    
    # Check message length
    if len(message) > 1000:
        raise InvalidInputError("Message too long. Maximum 1000 characters.")
    
    # Basic content filtering (extend as needed)
    prohibited_words = ["spam", "abuse"]  # Add more as needed
    message_lower = message.lower()
    
    for word in prohibited_words:
        if word in message_lower:
            logger.warning(f"Blocked message containing prohibited word: {word}")
            raise InvalidInputError("Message contains inappropriate content")
    
    return message

async def log_request(request: Request):
    """Log incoming requests for analytics"""
    logger.info(
        f"Request: {request.method} {request.url.path} "
        f"from {request.client.host}"
    )
    return True

# Dependency combinations for different endpoints
common_dependencies = [
    Depends(validate_request_size),
    Depends(rate_limit_dependency),
    Depends(log_request)
]

chat_dependencies = common_dependencies + [
    Depends(get_current_user)
]
"""
Core Module

Core utilities, configuration, logging, and security components.
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from app.core.config import settings
from app.core.logger import get_logger, setup_logging
from app.core.exceptions import (
    CustomerServiceAIException,
    AgentProcessingError,
    DatabaseConnectionError,
    HuggingFaceAPIError,
    InvalidInputError
)
from app.core.security import SecurityManager

__all__ = [
    "settings",
    "get_logger",
    "setup_logging",
    "CustomerServiceAIException",
    "AgentProcessingError", 
    "DatabaseConnectionError",
    "HuggingFaceAPIError",
    "InvalidInputError",
    "SecurityManager"
]
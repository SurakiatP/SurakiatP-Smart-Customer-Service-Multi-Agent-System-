"""
Customer Service AI Application

A multi-agent customer service system built with FastAPI, LangGraph, and Hugging Face.
Provides intelligent routing and automated responses for customer inquiries.
"""

__version__ = "1.0.0"
__author__ = "SurakiatP"
__description__ = "Smart Customer Service Multi-Agent System"

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

# Import main components for easy access
from app.core.config import settings
from app.core.logger import get_logger

# Initialize logging on import
from app.core.logger import setup_logging
setup_logging()

logger = get_logger(__name__)
logger.info(f"Customer Service AI v{__version__} initialized")
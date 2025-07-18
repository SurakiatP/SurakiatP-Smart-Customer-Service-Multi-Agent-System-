"""
Testing Suite for Customer Service AI

This module contains comprehensive tests for the customer service AI system:
- Unit tests for individual components
- Integration tests for end-to-end workflows
- Performance tests for system scalability
"""

__version__ = "1.0.0"
__description__ = "Customer Service AI Testing Suite"

# Test configuration
TEST_CONFIG = {
    "timeout": 30,
    "max_retries": 3,
    "test_data_path": "tests/data/",
    "mock_responses": True
}

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

# Import test utilities
from tests.conftest import (
    async_client,
    sample_message,
    sample_product_query,
    sample_refund_query,
    sample_technical_query
)

__all__ = [
    "TEST_CONFIG",
    "async_client",
    "sample_message",
    "sample_product_query", 
    "sample_refund_query",
    "sample_technical_query"
]
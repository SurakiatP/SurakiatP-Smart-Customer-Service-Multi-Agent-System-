"""
Unit Tests Module

Tests individual components in isolation:
- Agent functionality
- API endpoints
- Database operations
- Service integrations
"""

# Unit test configuration
UNIT_TEST_CONFIG = {
    "use_mock_data": True,
    "timeout": 10,
    "test_database": "test_db"
}

# Test categories
TEST_CATEGORIES = {
    "agents": ["ProductAgent", "RefundAgent", "TechnicalAgent", "RouterAgent"],
    "api": ["chat_routes", "health_routes", "analytics_routes"],
    "database": ["chroma_client", "redis_client", "models"],
    "services": ["huggingface_client", "external_apis", "cache_service"]
}

__all__ = [
    "UNIT_TEST_CONFIG",
    "TEST_CATEGORIES"
]
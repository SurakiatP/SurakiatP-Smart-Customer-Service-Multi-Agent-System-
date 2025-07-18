"""
Integration Tests Module

Tests system components working together:
- End-to-end workflows
- Performance and load testing
- UI integration testing
- External API integration
"""

# Integration test configuration
INTEGRATION_TEST_CONFIG = {
    "use_real_apis": False,  # Set to True for full integration testing
    "timeout": 60,
    "max_concurrent_users": 100,
    "performance_thresholds": {
        "response_time": 5.0,
        "success_rate": 0.95,
        "concurrent_users": 50
    }
}

# Test scenarios
TEST_SCENARIOS = {
    "workflow": [
        "complete_conversation_flow",
        "agent_routing",
        "conversation_persistence"
    ],
    "performance": [
        "response_time_sla",
        "concurrent_requests",
        "load_testing",
        "stress_testing"
    ],
    "ui": [
        "streamlit_initialization",
        "chat_interface",
        "metrics_display"
    ]
}

# Performance benchmarks
PERFORMANCE_BENCHMARKS = {
    "response_time": {
        "excellent": 2.0,
        "good": 3.0,
        "acceptable": 5.0,
        "poor": 10.0
    },
    "success_rate": {
        "excellent": 0.99,
        "good": 0.95,
        "acceptable": 0.90,
        "poor": 0.85
    }
}

__all__ = [
    "INTEGRATION_TEST_CONFIG",
    "TEST_SCENARIOS",
    "PERFORMANCE_BENCHMARKS"
]
import pytest
import asyncio
from httpx import AsyncClient
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from app.main import app
from app.database.models import Message, MessageType

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
async def async_client():
    """Create async HTTP client for testing"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client

@pytest.fixture
def sample_message():
    """Create sample message for testing"""
    return Message(
        content="What's the price of premium plan?",
        type=MessageType.USER,
        user_id="test_user",
        conversation_id="test_conv"
    )

@pytest.fixture
def sample_product_query():
    return "Tell me about your premium features and pricing"

@pytest.fixture
def sample_refund_query():
    return "I want to return my order and get a refund"

@pytest.fixture
def sample_technical_query():
    return "I'm having trouble logging into my account"
import pytest
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from app.services.huggingface_client import HuggingFaceClient
from app.services.cache_service import CacheService

@pytest.mark.asyncio
async def test_huggingface_classification():
    client = HuggingFaceClient()
    result = await client.classify_text(
        "What's the price?", 
        ["product_inquiry", "technical_issue"]
    )
    assert "labels" in result
    assert "scores" in result

@pytest.mark.asyncio
async def test_cache_service():
    cache = CacheService()
    await cache.cache_ai_response("ProductAgent", "test", {"response": "test"})
    cached = await cache.get_ai_response_cache("ProductAgent", "test")
    assert cached is not None
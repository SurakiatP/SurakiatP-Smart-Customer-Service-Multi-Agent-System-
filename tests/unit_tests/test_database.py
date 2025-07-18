import pytest
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from app.database.chroma_client import ChromaClient
from app.database.redis_client import RedisClient

@pytest.mark.asyncio
async def test_chroma_search():
    client = ChromaClient()
    results = await client.search_products("premium plan", limit=3)
    assert len(results) <= 3
    assert all("content" in result for result in results)

@pytest.mark.asyncio  
async def test_redis_cache():
    client = RedisClient()
    await client.cache_response("test_key", "test_value", 60)
    cached = await client.get_cached_response("test_key")
    assert cached == "test_value"
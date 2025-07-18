import pytest
import asyncio
import time
from httpx import AsyncClient
from app.main import app

@pytest.mark.asyncio
async def test_response_time_sla():
    """Test that response times meet SLA requirements"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        start_time = time.time()
        
        response = await client.post("/api/v1/chat", json={
            "message": "What's the price of premium plan?",
            "user_id": "test_user"
        })
        
        end_time = time.time()
        response_time = end_time - start_time
        
        assert response.status_code == 200
        assert response_time < 5.0  # 5 second SLA

@pytest.mark.asyncio
async def test_concurrent_requests():
    """Test system under concurrent load"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        
        async def make_request():
            return await client.post("/api/v1/chat", json={
                "message": "Test message",
                "user_id": f"user_{time.time()}"
            })
        
        # Test 50 concurrent requests
        tasks = [make_request() for _ in range(50)]
        responses = await asyncio.gather(*tasks)
        
        # Check all requests succeeded
        success_count = sum(1 for r in responses if r.status_code == 200)
        assert success_count >= 45  # 90% success rate minimum
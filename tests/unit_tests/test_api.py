import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_health_check(async_client: AsyncClient):
    """Test health check endpoint"""
    response = await async_client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

@pytest.mark.asyncio
async def test_chat_endpoint(async_client: AsyncClient):
    """Test chat endpoint with valid request"""
    payload = {
        "message": "What's the price of premium plan?",
        "user_id": "test_user"
    }
    
    response = await async_client.post("/api/v1/chat", json=payload)
    assert response.status_code == 200
    
    data = response.json()
    assert "response" in data
    assert "agent_used" in data
    assert "confidence" in data
    assert "response_time" in data

@pytest.mark.asyncio
async def test_chat_endpoint_invalid_input(async_client: AsyncClient):
    """Test chat endpoint with invalid input"""
    payload = {
        "message": "",  # Empty message
        "user_id": "test_user"
    }
    
    response = await async_client.post("/api/v1/chat", json=payload)
    assert response.status_code == 422  # Validation error

@pytest.mark.asyncio
async def test_chat_history_endpoint(async_client: AsyncClient):
    """Test chat history retrieval"""
    response = await async_client.get("/api/v1/chat/history/test_user")
    assert response.status_code == 200
    
    data = response.json()
    assert "history" in data
    assert isinstance(data["history"], list)
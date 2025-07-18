import pytest
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from app.agents.orchestrator import AgentOrchestrator

@pytest.mark.asyncio
async def test_end_to_end_workflow():
    """Test complete conversation workflow"""
    orchestrator = AgentOrchestrator()
    
    # Test product inquiry
    response = await orchestrator.process_message(
        user_id="test_user",
        message="What's the price of premium plan?",
        conversation_id="test_conv_1"
    )
    
    assert response.agent_used == "ProductAgent"
    assert response.confidence > 0.5
    assert "premium" in response.response.lower()

@pytest.mark.asyncio
async def test_agent_routing():
    """Test that messages are routed to correct agents"""
    orchestrator = AgentOrchestrator()
    
    test_cases = [
        ("What's the price of premium plan?", "ProductAgent"),
        ("I want a refund for my order", "RefundAgent"),
        ("I can't log into my account", "TechnicalAgent")
    ]
    
    for message, expected_agent in test_cases:
        response = await orchestrator.process_message(
            user_id="test_user",
            message=message
        )
        assert response.agent_used == expected_agent

@pytest.mark.asyncio
async def test_conversation_persistence():
    """Test that conversation history is maintained"""
    orchestrator = AgentOrchestrator()
    conversation_id = "test_persistence"
    
    # Send first message
    await orchestrator.process_message(
        user_id="test_user",
        message="Hello, I need help",
        conversation_id=conversation_id
    )
    
    # Send second message
    await orchestrator.process_message(
        user_id="test_user", 
        message="What are your prices?",
        conversation_id=conversation_id
    )
    
    # Check history
    history = await orchestrator.get_conversation_history("test_user")
    assert len(history) >= 2
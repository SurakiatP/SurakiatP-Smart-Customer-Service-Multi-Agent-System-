# Chat API endpoints
from fastapi import APIRouter, HTTPException, Depends
from typing import List
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from app.database.models import ChatRequest, ChatResponse
from app.agents.orchestrator import AgentOrchestrator
from app.core.logger import get_logger

router = APIRouter()
logger = get_logger(__name__)
orchestrator = AgentOrchestrator()

@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """Main chat endpoint for customer interactions"""
    try:
        logger.info(f"Processing chat request: {request.message[:50]}...")
        
        # Process message through agent orchestrator
        response = await orchestrator.process_message(
            user_id=request.user_id,
            message=request.message,
            conversation_id=request.conversation_id
        )
        
        logger.info(f"Generated response with confidence: {response.confidence}")
        return response
        
    except Exception as e:
        logger.error(f"Error processing chat: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/chat/history/{user_id}")
async def get_chat_history(user_id: str, limit: int = 10):
    """Retrieve chat history for a user"""
    try:
        history = await orchestrator.get_conversation_history(user_id, limit)
        return {"history": history}
    except Exception as e:
        logger.error(f"Error retrieving history: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve history")
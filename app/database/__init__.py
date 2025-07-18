"""
Database Module

Database connections and models for ChromaDB vector database and Redis cache.
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from app.database.chroma_client import ChromaClient
from app.database.redis_client import RedisClient
from app.database.models import (
    Message,
    MessageType,
    AgentResponse,
    ChatRequest,
    ChatResponse
)

# Database clients
chroma_client = ChromaClient()
redis_client = RedisClient()

__all__ = [
    "ChromaClient",
    "RedisClient", 
    "Message",
    "MessageType",
    "AgentResponse",
    "ChatRequest",
    "ChatResponse",
    "chroma_client",
    "redis_client"
]
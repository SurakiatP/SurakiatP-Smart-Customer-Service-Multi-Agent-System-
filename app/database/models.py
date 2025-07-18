# Pydantic data models
import uuid
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class MessageType(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"

class Message(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    content: str
    type: MessageType
    timestamp: datetime = Field(default_factory=datetime.now)
    user_id: str
    conversation_id: str

class AgentResponse(BaseModel):
    agent_name: str
    content: str
    confidence: float = Field(ge=0.0, le=1.0)
    sources: List[str] = []
    processing_time: float
    metadata: Dict[str, Any] = {}

class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=1000)
    user_id: str
    conversation_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    agent_used: str
    confidence: float
    response_time: float
    conversation_id: str
    suggestions: List[str] = []
# Abstract base class for all agents
from abc import ABC, abstractmethod
from typing import Dict, Any
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from app.database.models import Message, AgentResponse

class BaseAgent(ABC):
    def __init__(self, name: str):
        self.name = name
        self.confidence_threshold = 0.7
    
    @abstractmethod
    async def process_message(self, message: Message) -> AgentResponse:
        """Process incoming message and return response"""
        pass
    
    @abstractmethod
    async def get_confidence_score(self, message: Message) -> float:
        """Calculate confidence score for handling this message"""
        pass
    
    def can_handle(self, message: Message) -> bool:
        """Check if agent can handle this message type"""
        return self.get_confidence_score(message) >= self.confidence_threshold
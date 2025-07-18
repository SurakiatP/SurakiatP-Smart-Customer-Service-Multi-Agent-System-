from typing import Dict, List

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from app.agents.base_agent import BaseAgent
from app.services.huggingface_client import LangChainHuggingFaceClient
from app.database.models import Message, AgentResponse
from app.core.logger import get_logger

logger = get_logger(__name__)

class RouterAgent(BaseAgent):
    """Router agent using LangChain for intent classification"""
    
    def __init__(self):
        super().__init__("RouterAgent")
        self.langchain_client = LangChainHuggingFaceClient()
        self.intent_labels = [
            "product_inquiry",
            "refund_request", 
            "technical_issue",
            "general_question"
        ]
    
    async def classify_intent(self, message: str) -> Dict[str, float]:
        """Classify user intent using LangChain"""
        try:
            result = await self.langchain_client.classify_text(
                text=message,
                candidate_labels=self.intent_labels
            )
            
            # Convert to dict of label: score
            intent_scores = {}
            for label, score in zip(result["labels"], result["scores"]):
                intent_scores[label] = score
                
            logger.info(f"Intent classification: {intent_scores}")
            return intent_scores
            
        except Exception as e:
            logger.error(f"Intent classification failed: {e}")
            return {"general_question": 1.0}  # Fallback
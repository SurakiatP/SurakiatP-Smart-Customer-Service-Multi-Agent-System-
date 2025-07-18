import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from app.agents.base_agent import BaseAgent
from app.database.models import Message, AgentResponse
from app.services.huggingface_client import LangChainHuggingFaceClient
from app.database.chroma_client import ChromaClient
from app.core.logger import get_logger

logger = get_logger(__name__)

class ProductAgent(BaseAgent):
   """Product agent with LangChain RAG implementation"""
   
   def __init__(self):
       super().__init__("ProductAgent")
       self.langchain_client = LangChainHuggingFaceClient()
       self.chroma_client = ChromaClient()
   
   async def process_message(self, message: Message) -> AgentResponse:
       """Process message using LangChain RAG"""
       try:
           # 1. RETRIEVE: Get relevant documents from ChromaDB
           similar_docs = await self.chroma_client.search_products(
               query=message.content,
               limit=5
           )
           
           # 2. AUGMENT: Create context from retrieved documents
           context = "\n".join([doc.get("content", "") for doc in similar_docs])
           
           # 3. GENERATE: Use LangChain to generate response
           response = await self.langchain_client.generate_with_rag(
               query=message.content,
               agent_type="product",
               context=context
           )
           
           return AgentResponse(
               agent_name=self.name,
               content=response,
               confidence=await self.get_confidence_score(message),
               sources=[doc.get("source", "") for doc in similar_docs],
               processing_time=0.5
           )
           
       except Exception as e:
           logger.error(f"ProductAgent error: {e}")
           return AgentResponse(
               agent_name=self.name,
               content="I apologize, but I'm having trouble accessing product information right now.",
               confidence=0.3,
               sources=[],
               processing_time=0.1
           )
   
   async def get_confidence_score(self, message: Message) -> float:
       """Calculate confidence for product queries"""
       product_keywords = ["price", "features", "product", "buy", "purchase", "plan"]
       score = sum(1 for keyword in product_keywords 
                  if keyword.lower() in message.content.lower())
       return min(score / len(product_keywords), 1.0)
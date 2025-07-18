import chromadb
from chromadb.config import Settings
from typing import List, Dict, Any
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from app.core.config import settings
from app.core.logger import get_logger

logger = get_logger(__name__)

class ChromaClient:
    """ChromaDB vector database client"""
    
    def __init__(self):
        self.client = chromadb.PersistentClient(
            path=settings.CHROMA_PERSIST_DIRECTORY,
            settings=Settings(anonymized_telemetry=False)
        )
        self.products_collection = self.client.get_or_create_collection("products")
        self.faqs_collection = self.client.get_or_create_collection("faqs")
    
    async def search_products(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Search product information using vector similarity"""
        try:
            results = self.products_collection.query(
                query_texts=[query],
                n_results=limit
            )
            
            documents = []
            for i, doc in enumerate(results['documents'][0]):
                documents.append({
                    'content': doc,
                    'source': results['metadatas'][0][i].get('source', 'products_db'),
                    'score': results['distances'][0][i] if results['distances'] else 1.0
                })
            
            return documents
            
        except Exception as e:
            logger.error(f"Product search error: {e}")
            return []
    
    async def search_faqs(self, query: str, limit: int = 3) -> List[Dict[str, Any]]:
        """Search FAQ database"""
        try:
            results = self.faqs_collection.query(
                query_texts=[query],
                n_results=limit
            )
            
            documents = []
            for i, doc in enumerate(results['documents'][0]):
                documents.append({
                    'content': doc,
                    'source': 'faqs',
                    'score': results['distances'][0][i] if results['distances'] else 1.0
                })
            
            return documents
            
        except Exception as e:
            logger.error(f"FAQ search error: {e}")
            return []
    
    async def add_product(self, content: str, metadata: Dict[str, Any], doc_id: str):
        """Add product to knowledge base"""
        try:
            self.products_collection.add(
                documents=[content],
                metadatas=[metadata],
                ids=[doc_id]
            )
            logger.info(f"Added product document: {doc_id}")
        except Exception as e:
            logger.error(f"Failed to add product: {e}")
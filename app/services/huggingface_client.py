"""
LangChain Hugging Face Client - Real Implementation
Uses actual LangChain components for LLM integration
"""

import httpx
import asyncio
from typing import Dict, List, Any, Optional
from langchain_huggingface import HuggingFacePipeline
from langchain.chains import ConversationalRetrievalChain, LLMChain
from langchain.memory import ConversationBufferMemory, ConversationSummaryBufferMemory
from langchain.prompts import PromptTemplate
from langchain.schema import BaseRetriever, Document
from langchain.callbacks.base import BaseCallbackHandler
from langchain.vectorstores import Chroma
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
import torch
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from app.core.config import settings
from app.core.logger import get_logger
from app.database.chroma_client import ChromaClient

logger = get_logger(__name__)

class StreamingCallbackHandler(BaseCallbackHandler):
    """Callback handler for streaming responses"""
    
    def __init__(self):
        self.tokens = []
    
    def on_llm_new_token(self, token: str, **kwargs) -> None:
        self.tokens.append(token)

class ChromaRetriever(BaseRetriever):
    """Custom retriever for ChromaDB integration"""
    
    def __init__(self, chroma_client: ChromaClient, collection_name: str = "products"):
        self.chroma_client = chroma_client
        self.collection_name = collection_name
    
    def get_relevant_documents(self, query: str) -> List[Document]:
        """Retrieve relevant documents from ChromaDB"""
        try:
            if self.collection_name == "products":
                results = asyncio.run(self.chroma_client.search_products(query, limit=5))
            else:
                results = asyncio.run(self.chroma_client.search_faqs(query, limit=5))
            
            documents = []
            for result in results:
                doc = Document(
                    page_content=result.get("content", ""),
                    metadata={
                        "source": result.get("source", "unknown"),
                        "score": result.get("score", 0.0)
                    }
                )
                documents.append(doc)
            
            return documents
            
        except Exception as e:
            logger.error(f"ChromaRetriever error: {e}")
            return []

class LangChainHuggingFaceClient:
    """LangChain-powered Hugging Face client"""
    
    def __init__(self):
        self.api_url = settings.HUGGINGFACE_API_URL
        self.api_key = settings.HUGGINGFACE_API_KEY
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # Models configuration
        self.models = {
            "classification": "facebook/bart-large-mnli",
            "generation": "meta-llama/Llama-2-7b-chat-hf",
            "embeddings": "sentence-transformers/all-MiniLM-L6-v2"
        }
        
        # Initialize LangChain components
        self.llm = None
        self.embeddings = None
        self.memory = None
        self.chains = {}
        self.chroma_client = ChromaClient()
        
        # Initialize components
        self._initialize_components()
    
    def _initialize_components(self):
        """Initialize LangChain components"""
        try:
            # Initialize embeddings
            self.embeddings = HuggingFaceEmbeddings(
                model_name=self.models["embeddings"],
                model_kwargs={'device': 'cpu'}
            )
            
            # Initialize memory
            self.memory = ConversationBufferMemory(
                memory_key="chat_history",
                return_messages=True,
                output_key="answer"
            )
            
            # Initialize LLM (using API for better performance)
            self.llm = self._create_api_llm()
            
            # Initialize chains
            self._initialize_chains()
            
            logger.info("LangChain components initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize LangChain components: {e}")
    
    def _create_api_llm(self):
        """Create LLM using Hugging Face API"""
        
        class HuggingFaceAPILLM:
            """Custom LLM class for Hugging Face API"""
            
            def __init__(self, client):
                self.client = client
            
            def __call__(self, prompt: str) -> str:
                return asyncio.run(self.client._generate_with_api(prompt))
            
            async def agenerate(self, prompt: str) -> str:
                return await self.client._generate_with_api(prompt)
        
        return HuggingFaceAPILLM(self)
    
    def _initialize_chains(self):
        """Initialize various LangChain chains"""
        
        # Product inquiry chain
        product_template = """
        You are a helpful product consultant. Use the following context to answer questions about products.
        
        Context: {context}
        
        Chat History: {chat_history}
        
        Human: {question}
        
        Assistant: I'll help you with your product inquiry. Based on the available information:
        """
        
        product_prompt = PromptTemplate(
            template=product_template,
            input_variables=["context", "chat_history", "question"]
        )
        
        self.chains["product"] = LLMChain(
            llm=self.llm,
            prompt=product_prompt,
            memory=self.memory,
            verbose=True
        )
        
        # Refund chain
        refund_template = """
        You are a customer service representative handling refund requests. Use the following policy information.
        
        Policy Context: {context}
        
        Chat History: {chat_history}
        
        Human: {question}
        
        Assistant: I'll help you with your refund request. According to our policies:
        """
        
        refund_prompt = PromptTemplate(
            template=refund_template,
            input_variables=["context", "chat_history", "question"]
        )
        
        self.chains["refund"] = LLMChain(
            llm=self.llm,
            prompt=refund_prompt,
            memory=self.memory,
            verbose=True
        )
        
        # Technical support chain
        technical_template = """
        You are a technical support specialist. Use the following troubleshooting information.
        
        Technical Context: {context}
        
        Chat History: {chat_history}
        
        Human: {question}
        
        Assistant: I'll help you resolve this technical issue. Here's what I recommend:
        """
        
        technical_prompt = PromptTemplate(
            template=technical_template,
            input_variables=["context", "chat_history", "question"]
        )
        
        self.chains["technical"] = LLMChain(
            llm=self.llm,
            prompt=technical_prompt,
            memory=self.memory,
            verbose=True
        )
    
    async def classify_text(self, text: str, candidate_labels: List[str]) -> Dict[str, Any]:
        """Classify text using BART model with LangChain"""
        url = f"{self.api_url}/models/{self.models['classification']}"
        
        payload = {
            "inputs": text,
            "parameters": {
                "candidate_labels": candidate_labels
            }
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    url,
                    headers=self.headers,
                    json=payload,
                    timeout=30.0
                )
                response.raise_for_status()
                result = response.json()
                
                # Log classification for monitoring
                logger.info(f"Classification result: {result}")
                
                return result
                
        except httpx.HTTPError as e:
            logger.error(f"HF classification error: {e}")
            return self._fallback_classification(text, candidate_labels)
        
        except Exception as e:
            logger.error(f"Unexpected error in classification: {e}")
            return self._fallback_classification(text, candidate_labels)
    
    async def generate_with_rag(self, query: str, agent_type: str = "product", context: str = "") -> str:
        """Generate response using RAG with LangChain"""
        try:
            # Get relevant documents if context not provided
            if not context:
                retriever = ChromaRetriever(self.chroma_client, collection_name="products")
                docs = retriever.get_relevant_documents(query)
                context = "\n".join([doc.page_content for doc in docs[:3]])
            
            # Get appropriate chain
            chain = self.chains.get(agent_type, self.chains["product"])
            
            # Generate response
            response = await chain.arun(
                question=query,
                context=context,
                chat_history=self.memory.chat_memory.messages
            )
            
            return response.strip()
            
        except Exception as e:
            logger.error(f"RAG generation error: {e}")
            return self._fallback_response(query)
    
    async def generate_conversational_response(self, query: str, conversation_id: str) -> str:
        """Generate response with conversation memory"""
        try:
            # Create conversation-specific memory
            conversation_memory = ConversationSummaryBufferMemory(
                llm=self.llm,
                max_token_limit=1000,
                memory_key="chat_history",
                return_messages=True
            )
            
            # Get retriever for context
            retriever = ChromaRetriever(self.chroma_client)
            
            # Create conversational retrieval chain
            qa_chain = ConversationalRetrievalChain.from_llm(
                llm=self.llm,
                retriever=retriever,
                memory=conversation_memory,
                return_source_documents=True,
                verbose=True
            )
            
            # Generate response
            result = await qa_chain.arun({"question": query})
            
            return result
            
        except Exception as e:
            logger.error(f"Conversational generation error: {e}")
            return self._fallback_response(query)
    
    async def _generate_with_api(self, prompt: str, max_length: int = 150) -> str:
        """Generate response using Hugging Face API"""
        url = f"{self.api_url}/models/{self.models['generation']}"
        
        payload = {
            "inputs": prompt,
            "parameters": {
                "max_length": max_length,
                "temperature": 0.7,
                "do_sample": True,
                "top_p": 0.95,
                "repetition_penalty": 1.1
            }
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    url,
                    headers=self.headers,
                    json=payload,
                    timeout=60.0
                )
                response.raise_for_status()
                result = response.json()
                
                if isinstance(result, list) and len(result) > 0:
                    generated_text = result[0].get("generated_text", "")
                    # Remove the prompt from response
                    if prompt in generated_text:
                        generated_text = generated_text.replace(prompt, "").strip()
                    return generated_text
                else:
                    return "I apologize, but I couldn't generate a proper response."
                    
        except httpx.HTTPError as e:
            logger.error(f"HF generation error: {e}")
            return self._fallback_response(prompt)
        
        except Exception as e:
            logger.error(f"Unexpected error in generation: {e}")
            return self._fallback_response(prompt)
    
    async def create_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Create embeddings using LangChain"""
        try:
            if not self.embeddings:
                self.embeddings = HuggingFaceEmbeddings(
                    model_name=self.models["embeddings"]
                )
            
            embeddings = await self.embeddings.aembed_documents(texts)
            return embeddings
            
        except Exception as e:
            logger.error(f"Embedding generation error: {e}")
            return []
    
    def _fallback_classification(self, text: str, labels: List[str]) -> Dict[str, Any]:
        """Simple keyword-based fallback classification"""
        text_lower = text.lower()
        scores = []
        
        for label in labels:
            if "product" in label and any(word in text_lower for word in ["price", "buy", "product", "features"]):
                scores.append(0.8)
            elif "refund" in label and any(word in text_lower for word in ["refund", "return", "money"]):
                scores.append(0.8)
            elif "technical" in label and any(word in text_lower for word in ["error", "bug", "help", "issue"]):
                scores.append(0.8)
            else:
                scores.append(0.2)
        
        return {
            "labels": labels,
            "scores": scores
        }
    
    def _fallback_response(self, prompt: str) -> str:
        """Simple fallback response when API fails"""
        if "product" in prompt.lower():
            return "I'd be happy to help you with product information. Could you please be more specific about what you'd like to know?"
        elif "refund" in prompt.lower():
            return "For refund requests, please provide your order number and I'll help you with the process."
        elif "technical" in prompt.lower():
            return "I understand you're having a technical issue. Please describe the problem in detail so I can assist you better."
        else:
            return "Thank you for your question. Could you please provide more details so I can assist you better?"
    
    def clear_memory(self):
        """Clear conversation memory"""
        if self.memory:
            self.memory.clear()
    
    def get_memory_summary(self) -> str:
        """Get summary of conversation memory"""
        if isinstance(self.memory, ConversationSummaryBufferMemory):
            return self.memory.moving_summary_buffer
        return ""

# For backward compatibility
HuggingFaceClient = LangChainHuggingFaceClient
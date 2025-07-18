import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from app.agents.base_agent import BaseAgent
from app.database.models import Message, AgentResponse
from app.services.huggingface_client import LangChainHuggingFaceClient
from app.database.chroma_client import ChromaClient
from app.core.logger import get_logger

logger = get_logger(__name__)

class TechnicalAgent(BaseAgent):
    """Technical support agent with LangChain RAG implementation"""
    
    def __init__(self):
        super().__init__("TechnicalAgent")
        self.langchain_client = LangChainHuggingFaceClient()
        self.chroma_client = ChromaClient()
        self.troubleshooting_db = self._load_troubleshooting_solutions()
    
    def _load_troubleshooting_solutions(self) -> dict:
        """Load common technical solutions"""
        return {
            "login_issues": {
                "steps": [
                    "Check your internet connection",
                    "Clear browser cache and cookies", 
                    "Try incognito/private browsing mode",
                    "Reset your password if needed"
                ],
                "escalation": "If issue persists, contact technical support"
            },
            "app_crashes": {
                "steps": [
                    "Force close and restart the app",
                    "Check for app updates",
                    "Restart your device",
                    "Reinstall the app if necessary"
                ],
                "escalation": "Provide crash logs to support team"
            },
            "payment_issues": {
                "steps": [
                    "Verify payment method details",
                    "Check account balance/credit limit",
                    "Try different payment method",
                    "Contact your bank if card is declined"
                ],
                "escalation": "Contact billing support for further assistance"
            },
            "performance_issues": {
                "steps": [
                    "Check your internet connection speed",
                    "Update your browser to latest version",
                    "Close unnecessary browser tabs",
                    "Try a different browser"
                ],
                "escalation": "Contact technical support if issues persist"
            },
            "api_errors": {
                "steps": [
                    "Check API endpoint documentation",
                    "Verify authentication credentials",
                    "Check rate limiting status",
                    "Review request payload format"
                ],
                "escalation": "Contact API support team"
            }
        }
    
    async def process_message(self, message: Message) -> AgentResponse:
        """Process technical support queries using LangChain RAG"""
        try:
            # 1. RETRIEVE: Search troubleshooting database using ChromaDB
            troubleshooting_docs = await self.chroma_client.search_faqs(
                query=f"technical issue {message.content}",
                limit=3
            )
            
            # 2. AUGMENT: Create context from retrieved documents and local knowledge
            context = await self._create_technical_context(message.content, troubleshooting_docs)
            
            # 3. GENERATE: Use LangChain to generate technical solution
            response = await self.langchain_client.generate_with_rag(
                query=message.content,
                agent_type="technical",
                context=context
            )
            
            # Enhance response with step-by-step solution if available
            issue_type = self._identify_issue_type(message.content)
            if issue_type in self.troubleshooting_db:
                structured_solution = await self._provide_structured_solution(issue_type, message.content)
                response = f"{response}\n\n{structured_solution}"
            
            return AgentResponse(
                agent_name=self.name,
                content=response,
                confidence=await self.get_confidence_score(message),
                sources=[doc.get("source", "") for doc in troubleshooting_docs] + ["troubleshooting_db"],
                processing_time=0.7
            )
            
        except Exception as e:
            logger.error(f"Technical agent error: {e}")
            return AgentResponse(
                agent_name=self.name,
                content="I'm experiencing technical difficulties. Please try again or contact our technical support team.",
                confidence=0.2,
                sources=[],
                processing_time=0.1
            )
    
    async def _create_technical_context(self, query: str, retrieved_docs: list) -> str:
        """Create comprehensive technical context"""
        context_parts = []
        
        # Add retrieved documents
        for doc in retrieved_docs:
            context_parts.append(f"Knowledge Base: {doc.get('content', '')}")
        
        # Add relevant troubleshooting steps
        issue_type = self._identify_issue_type(query)
        if issue_type in self.troubleshooting_db:
            solution = self.troubleshooting_db[issue_type]
            context_parts.append(f"Standard Solution for {issue_type}: {'; '.join(solution['steps'])}")
        
        # Add general technical context
        context_parts.append("""
        Technical Support Guidelines:
        - Always provide step-by-step solutions
        - Include specific troubleshooting steps
        - Mention when to escalate to human support
        - Be clear about system requirements
        - Provide alternative solutions when possible
        """)
        
        return "\n\n".join(context_parts)
    
    def _identify_issue_type(self, query: str) -> str:
        """Identify the type of technical issue using enhanced detection"""
        query_lower = query.lower()
        
        # Enhanced keyword matching
        issue_patterns = {
            "login_issues": ["login", "sign in", "password", "authentication", "access denied", "locked out"],
            "app_crashes": ["crash", "freeze", "stuck", "not working", "stops responding", "hangs"],
            "payment_issues": ["payment", "billing", "card", "charge", "transaction", "declined"],
            "performance_issues": ["slow", "loading", "timeout", "lag", "performance", "speed"],
            "api_errors": ["api", "endpoint", "error code", "400", "500", "unauthorized", "forbidden"]
        }
        
        for issue_type, keywords in issue_patterns.items():
            if any(keyword in query_lower for keyword in keywords):
                return issue_type
        
        return "general_technical"
    
    async def _provide_structured_solution(self, issue_type: str, query: str) -> str:
        """Provide structured step-by-step solution"""
        solution = self.troubleshooting_db[issue_type]
        
        response = f"🔧 **Troubleshooting Steps for {issue_type.replace('_', ' ').title()}:**\n\n"
        
        for i, step in enumerate(solution["steps"], 1):
            response += f"{i}. {step}\n"
        
        response += f"\n⚠️ **Escalation**: {solution['escalation']}"
        
        return response
    
    async def _general_technical_help(self, query: str) -> str:
        """Provide general technical assistance using LangChain"""
        try:
            # Use LangChain for more sophisticated response generation
            context = """
            You are an expert technical support specialist. 
            Provide clear, step-by-step solutions for technical issues.
            Always include specific troubleshooting steps and when to escalate.
            """
            
            response = await self.langchain_client.generate_with_rag(
                query=f"Technical issue: {query}",
                agent_type="technical",
                context=context
            )
            
            return response
            
        except Exception as e:
            logger.error(f"General technical help error: {e}")
            return "I understand you're having a technical issue. Please describe the problem in detail so I can provide specific troubleshooting steps."
    
    async def get_confidence_score(self, message: Message) -> float:
        """Calculate confidence for handling technical queries"""
        technical_keywords = [
            "error", "bug", "crash", "login", "technical", "support", "help", 
            "issue", "problem", "not working", "freeze", "stuck", "slow",
            "api", "code", "system", "server", "connection", "timeout"
        ]
        
        content_lower = message.content.lower()
        score = sum(1 for keyword in technical_keywords if keyword in content_lower)
        
        # Boost confidence for specific technical patterns
        if any(pattern in content_lower for pattern in ["error code", "exception", "stack trace", "debug"]):
            score += 2
        
        return min(score / len(technical_keywords), 1.0)
    
    async def diagnose_issue(self, message: Message) -> dict:
        """Advanced issue diagnosis using LangChain"""
        try:
            diagnosis_prompt = f"""
            Analyze this technical issue and provide a diagnosis:
            
            User Report: {message.content}
            
            Provide:
            1. Issue Category
            2. Severity Level (Low/Medium/High)
            3. Estimated Resolution Time
            4. Required Information
            5. Next Steps
            """
            
            diagnosis = await self.langchain_client.generate_with_rag(
                query=diagnosis_prompt,
                agent_type="technical",
                context="Technical diagnosis guidelines"
            )
            
            return {
                "diagnosis": diagnosis,
                "issue_type": self._identify_issue_type(message.content),
                "confidence": await self.get_confidence_score(message)
            }
            
        except Exception as e:
            logger.error(f"Issue diagnosis error: {e}")
            return {
                "diagnosis": "Unable to complete diagnosis",
                "issue_type": "unknown",
                "confidence": 0.1
            }
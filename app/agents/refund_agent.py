import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from app.agents.base_agent import BaseAgent
from app.database.models import Message, AgentResponse
from app.services.huggingface_client import LangChainHuggingFaceClient
from app.database.chroma_client import ChromaClient
from app.services.external_apis import ExternalAPIClient
from app.core.logger import get_logger

logger = get_logger(__name__)

class RefundAgent(BaseAgent):
    """Refund agent with LangChain RAG implementation"""
    
    def __init__(self):
        super().__init__("RefundAgent")
        self.langchain_client = LangChainHuggingFaceClient()
        self.chroma_client = ChromaClient()
        self.external_api = ExternalAPIClient()
        self.refund_policies = self._load_refund_policies()
    
    def _load_refund_policies(self) -> dict:
        """Load comprehensive refund policies"""
        return {
            "standard_refund": {
                "period": "14 days",
                "conditions": [
                    "Product must be in original condition",
                    "Proof of purchase required",
                    "No physical damage"
                ],
                "process_time": "3-5 business days"
            },
            "premium_refund": {
                "period": "30 days",
                "conditions": [
                    "Premium customer status",
                    "Product must be in original condition",
                    "Proof of purchase required"
                ],
                "process_time": "1-3 business days"
            },
            "digital_refund": {
                "period": "7 days",
                "conditions": [
                    "No downloads or usage after purchase",
                    "Account verification required"
                ],
                "process_time": "1-2 business days"
            },
            "subscription_refund": {
                "period": "Pro-rated to end of billing cycle",
                "conditions": [
                    "Cancellation before next billing cycle",
                    "Account in good standing"
                ],
                "process_time": "5-7 business days"
            },
            "non_refundable": [
                "Customized products",
                "Gift cards",
                "Used digital content",
                "Services already rendered"
            ]
        }
    
    async def process_message(self, message: Message) -> AgentResponse:
        """Process refund-related queries using LangChain RAG"""
        try:
            # 1. RETRIEVE: Search policy documents using ChromaDB
            policy_docs = await self.chroma_client.search_faqs(
                query=f"refund policy {message.content}",
                limit=3
            )
            
            # 2. AUGMENT: Create comprehensive context
            context = await self._create_refund_context(message.content, policy_docs)
            
            # 3. Determine if this is a policy inquiry or refund request
            request_type = self._classify_refund_request(message.content)
            
            # 4. GENERATE: Use LangChain to generate appropriate response
            if request_type == "policy_inquiry":
                response = await self._handle_policy_inquiry(message.content, context)
            elif request_type == "refund_request":
                response = await self._handle_refund_request(message.content, context)
            else:
                response = await self._handle_general_refund_query(message.content, context)
            
            return AgentResponse(
                agent_name=self.name,
                content=response,
                confidence=await self.get_confidence_score(message),
                sources=[doc.get("source", "") for doc in policy_docs] + ["refund_policy"],
                processing_time=0.5
            )
            
        except Exception as e:
            logger.error(f"Refund agent error: {e}")
            return AgentResponse(
                agent_name=self.name,
                content="I apologize, but I'm having trouble processing your refund request. Please contact our support team.",
                confidence=0.3,
                sources=[],
                processing_time=0.1
            )
    
    async def _create_refund_context(self, query: str, retrieved_docs: list) -> str:
        """Create comprehensive refund context"""
        context_parts = []
        
        # Add retrieved policy documents
        for doc in retrieved_docs:
            context_parts.append(f"Policy Document: {doc.get('content', '')}")
        
        # Add relevant policy information
        relevant_policies = self._get_relevant_policies(query)
        for policy_name, policy_info in relevant_policies.items():
            context_parts.append(f"""
            {policy_name.replace('_', ' ').title()}:
            - Period: {policy_info['period']}
            - Conditions: {', '.join(policy_info['conditions'])}
            - Processing Time: {policy_info['process_time']}
            """)
        
        # Add non-refundable items
        context_parts.append(f"Non-refundable items: {', '.join(self.refund_policies['non_refundable'])}")
        
        # Add general refund guidelines
        context_parts.append("""
        Refund Guidelines:
        - Always check customer eligibility first
        - Provide clear timelines and expectations
        - Explain required documentation
        - Offer alternative solutions when appropriate
        - Be empathetic and professional
        """)
        
        return "\n\n".join(context_parts)
    
    def _classify_refund_request(self, query: str) -> str:
        """Classify the type of refund request"""
        query_lower = query.lower()
        
        # Policy inquiry indicators
        policy_keywords = ["policy", "how long", "can i", "what is", "explain", "rules", "terms"]
        if any(keyword in query_lower for keyword in policy_keywords):
            return "policy_inquiry"
        
        # Refund request indicators
        request_keywords = ["want refund", "return", "cancel", "money back", "process refund", "order"]
        if any(keyword in query_lower for keyword in request_keywords):
            return "refund_request"
        
        return "general_inquiry"
    
    def _get_relevant_policies(self, query: str) -> dict:
        """Get relevant policies based on query content"""
        query_lower = query.lower()
        relevant = {}
        
        # Check for specific product types
        if "premium" in query_lower:
            relevant["premium_refund"] = self.refund_policies["premium_refund"]
        elif "digital" in query_lower or "download" in query_lower:
            relevant["digital_refund"] = self.refund_policies["digital_refund"]
        elif "subscription" in query_lower or "monthly" in query_lower:
            relevant["subscription_refund"] = self.refund_policies["subscription_refund"]
        else:
            relevant["standard_refund"] = self.refund_policies["standard_refund"]
        
        return relevant
    
    async def _handle_policy_inquiry(self, query: str, context: str) -> str:
        """Handle policy-related inquiries using LangChain"""
        try:
            policy_prompt = f"""
            You are a customer service representative explaining refund policies.
            Be clear, helpful, and provide specific information.
            
            Context: {context}
            
            Customer Question: {query}
            
            Provide a helpful explanation of the relevant refund policy.
            """
            
            response = await self.langchain_client.generate_with_rag(
                query=policy_prompt,
                agent_type="refund",
                context=context
            )
            
            return response
            
        except Exception as e:
            logger.error(f"Policy inquiry error: {e}")
            return self._fallback_policy_response(query)
    
    async def _handle_refund_request(self, query: str, context: str) -> str:
        """Handle actual refund requests using LangChain"""
        try:
            # Check if order information is provided
            order_info = self._extract_order_info(query)
            
            if order_info:
                # Try to process the refund request
                refund_response = await self._process_refund_with_order(order_info, query, context)
            else:
                # Request order information
                refund_response = await self._request_order_information(query, context)
            
            return refund_response
            
        except Exception as e:
            logger.error(f"Refund request error: {e}")
            return self._fallback_refund_response()
    
    async def _handle_general_refund_query(self, query: str, context: str) -> str:
        """Handle general refund queries using LangChain"""
        try:
            general_prompt = f"""
            You are a helpful customer service agent handling refund inquiries.
            
            Context: {context}
            
            Customer Message: {query}
            
            Provide a helpful response addressing their refund concern.
            """
            
            response = await self.langchain_client.generate_with_rag(
                query=general_prompt,
                agent_type="refund",
                context=context
            )
            
            return response
            
        except Exception as e:
            logger.error(f"General refund query error: {e}")
            return "I'd be happy to help you with your refund inquiry. Could you please provide more details about what you'd like to know?"
    
    def _extract_order_info(self, query: str) -> dict:
        """Extract order information from query"""
        import re
        
        # Look for order patterns
        order_patterns = {
            "order_number": r"order\s*(?:number|#)?\s*:?\s*([A-Z0-9]+)",
            "email": r"([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})",
            "transaction_id": r"transaction\s*(?:id)?\s*:?\s*([A-Z0-9]+)"
        }
        
        extracted = {}
        for info_type, pattern in order_patterns.items():
            match = re.search(pattern, query, re.IGNORECASE)
            if match:
                extracted[info_type] = match.group(1)
        
        return extracted
    
    async def _process_refund_with_order(self, order_info: dict, query: str, context: str) -> str:
        """Process refund request with order information"""
        try:
            # Validate order information (using external API)
            order_id = order_info.get("order_number")
            if order_id:
                order_details = await self.external_api.get_order_details(order_id)
                
                if order_details:
                    # Check refund eligibility
                    eligibility = self._check_refund_eligibility(order_details)
                    
                    if eligibility["eligible"]:
                        # Generate processing response
                        response = await self._generate_refund_processing_response(order_details, eligibility, context)
                    else:
                        # Generate ineligible response
                        response = await self._generate_ineligible_response(order_details, eligibility, context)
                    
                    return response
                else:
                    return "I couldn't find an order with that number. Please check your order number and try again."
            else:
                return await self._request_order_information(query, context)
                
        except Exception as e:
            logger.error(f"Refund processing error: {e}")
            return self._fallback_refund_response()
    
    async def _request_order_information(self, query: str, context: str) -> str:
        """Request necessary order information"""
        return """To process your refund request, I'll need the following information:
        
        📋 **Required Information:**
        1. Order number or purchase receipt
        2. Email address used for the purchase
        3. Reason for return
        4. Product condition details
        
        📞 **Alternative Options:**
        - Email us at support@company.com
        - Call our support line: 1-800-SUPPORT
        - Live chat available 24/7
        
        Once you provide this information, I'll help you start the refund process. Most refunds are processed within 3-5 business days."""
    
    def _check_refund_eligibility(self, order_details: dict) -> dict:
        """Check if order is eligible for refund"""
        from datetime import datetime, timedelta
        
        # Simple eligibility check
        order_date = datetime.fromisoformat(order_details.get("order_date", ""))
        current_date = datetime.now()
        days_since_purchase = (current_date - order_date).days
        
        # Determine policy based on customer tier
        customer_tier = order_details.get("customer_tier", "standard")
        
        if customer_tier == "premium":
            eligible = days_since_purchase <= 30
            policy = "premium_refund"
        else:
            eligible = days_since_purchase <= 14
            policy = "standard_refund"
        
        return {
            "eligible": eligible,
            "policy": policy,
            "days_since_purchase": days_since_purchase,
            "order_details": order_details
        }
    
    async def _generate_refund_processing_response(self, order_details: dict, eligibility: dict, context: str) -> str:
        """Generate response for eligible refund"""
        policy = self.refund_policies[eligibility["policy"]]
        
        response = f"""✅ **Refund Request Approved**
        
        📦 **Order Details:**
        - Order ID: {order_details.get('order_id')}
        - Amount: ${order_details.get('total_amount')}
        - Date: {order_details.get('order_date')}
        
        ⏰ **Processing Information:**
        - Refund will be processed within {policy['process_time']}
        - Refund will be credited to your original payment method
        - You'll receive a confirmation email shortly
        
        📋 **Next Steps:**
        1. Keep your order confirmation for records
        2. Monitor your payment method for the refund
        3. Contact us if you don't see the refund within the expected timeframe
        
        Is there anything else I can help you with regarding this refund?"""
        
        return response
    
    async def _generate_ineligible_response(self, order_details: dict, eligibility: dict, context: str) -> str:
        """Generate response for ineligible refund"""
        days_since = eligibility["days_since_purchase"]
        
        response = f"""❌ **Refund Request Status**
        
        📦 **Order Details:**
        - Order ID: {order_details.get('order_id')}
        - Purchase Date: {order_details.get('order_date')}
        - Days Since Purchase: {days_since}
        
        ⚠️ **Refund Policy:**
        Unfortunately, this order is outside our refund window. Our standard refund policy allows returns within 14 days of purchase (30 days for premium customers).
        
        🔄 **Alternative Options:**
        - Store credit for future purchases
        - Product exchange for different item
        - Contact our billing team for special considerations
        
        Would you like me to explore any of these alternatives for you?"""
        
        return response
    
    def _fallback_policy_response(self, query: str) -> str:
        """Fallback response for policy inquiries"""
        return f"""Our refund policy varies by product type:
        
        📋 **Standard Products**: 14 days
        🌟 **Premium Customers**: 30 days
        💻 **Digital Products**: 7 days
        
        **Conditions Apply:**
        - Product must be in original condition
        - Proof of purchase required
        - No refund for customized items
        
        Would you like more specific information about any of these policies?"""
    
    def _fallback_refund_response(self) -> str:
        """Fallback response for refund requests"""
        return """I'd be happy to help you with your refund request. To get started, I'll need:
        
        1. Your order number
        2. Email address used for purchase
        3. Reason for the return
        
        Please provide this information and I'll process your request right away."""
    
    async def get_confidence_score(self, message: Message) -> float:
        """Calculate confidence for handling refund queries"""
        refund_keywords = [
            "refund", "return", "money back", "cancel order", "policy",
            "reimburse", "charge back", "dispute", "billing", "payment"
        ]
        
        content_lower = message.content.lower()
        score = sum(1 for keyword in refund_keywords if keyword in content_lower)
        
        # Boost confidence for specific refund patterns
        if any(pattern in content_lower for pattern in ["want refund", "return policy", "money back"]):
            score += 2
        
        return min(score / len(refund_keywords), 1.0)
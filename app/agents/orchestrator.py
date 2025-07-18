"""
LangGraph Orchestrator - Real Implementation
Uses actual LangGraph for multi-agent workflow orchestration
"""

from typing import Dict, Any, List
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from pydantic import BaseModel, Field
import asyncio
import time
import uuid

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from app.agents.router_agent import RouterAgent
from app.agents.product_agent import ProductAgent
from app.agents.refund_agent import RefundAgent
from app.agents.technical_agent import TechnicalAgent
from app.database.models import Message, ChatResponse, MessageType
from app.database.redis_client import RedisClient
from app.core.logger import get_logger

logger = get_logger(__name__)

class ConversationState(BaseModel):
    """State object for LangGraph workflow"""
    user_id: str
    conversation_id: str
    original_message: str
    current_message: str
    intent: str = ""
    intent_confidence: float = 0.0
    selected_agent: str = ""
    agent_response: str = ""
    response_confidence: float = 0.0
    sources: List[str] = Field(default_factory=list)
    suggestions: List[str] = Field(default_factory=list)
    error: str = ""
    metadata: Dict[str, Any] = Field(default_factory=dict)

class LangGraphOrchestrator:
    """Real LangGraph implementation for multi-agent orchestration"""
    
    def __init__(self):
        self.router = RouterAgent()
        self.agents = {
            "ProductAgent": ProductAgent(),
            "RefundAgent": RefundAgent(),
            "TechnicalAgent": TechnicalAgent()
        }
        self.redis_client = RedisClient()
        self.memory = MemorySaver()
        self.workflow = self._create_workflow()
    
    def _create_workflow(self):
        """Create LangGraph workflow with proper state management"""
        
        # Create state graph
        workflow = StateGraph(ConversationState)
        
        # Add nodes (each step in the workflow)
        workflow.add_node("classify_intent", self._classify_intent_node)
        workflow.add_node("route_to_agent", self._route_to_agent_node)
        workflow.add_node("process_with_agent", self._process_with_agent_node)
        workflow.add_node("generate_suggestions", self._generate_suggestions_node)
        workflow.add_node("handle_error", self._handle_error_node)
        
        # Set entry point
        workflow.set_entry_point("classify_intent")
        
        # Add conditional edges
        workflow.add_conditional_edges(
            "classify_intent",
            self._should_continue_after_classification,
            {
                "continue": "route_to_agent",
                "error": "handle_error"
            }
        )
        
        workflow.add_conditional_edges(
            "route_to_agent",
            self._should_continue_after_routing,
            {
                "continue": "process_with_agent",
                "error": "handle_error"
            }
        )
        
        workflow.add_conditional_edges(
            "process_with_agent",
            self._should_continue_after_processing,
            {
                "continue": "generate_suggestions",
                "error": "handle_error"
            }
        )
        
        # Add edges to END
        workflow.add_edge("generate_suggestions", END)
        workflow.add_edge("handle_error", END)
        
        return workflow.compile(checkpointer=self.memory)
    
    async def _classify_intent_node(self, state: ConversationState) -> ConversationState:
        """Node: Classify user intent"""
        try:
            logger.info(f"Classifying intent for: {state.current_message[:50]}...")
            
            # Use router agent to classify intent
            message = Message(
                content=state.current_message,
                type=MessageType.USER,
                user_id=state.user_id,
                conversation_id=state.conversation_id
            )
            
            # Get intent classification
            intent_scores = await self.router.classify_intent(message.content)
            
            # Get best intent
            best_intent = max(intent_scores, key=intent_scores.get)
            confidence = intent_scores[best_intent]
            
            # Update state
            state.intent = best_intent
            state.intent_confidence = confidence
            state.metadata["intent_scores"] = intent_scores
            
            logger.info(f"Intent classified: {best_intent} (confidence: {confidence:.2f})")
            
        except Exception as e:
            logger.error(f"Intent classification error: {e}")
            state.error = f"Intent classification failed: {str(e)}"
        
        return state
    
    async def _route_to_agent_node(self, state: ConversationState) -> ConversationState:
        """Node: Route to appropriate agent"""
        try:
            logger.info(f"Routing intent '{state.intent}' to agent...")
            
            # Agent mapping based on intent
            agent_mapping = {
                "product_inquiry": "ProductAgent",
                "refund_request": "RefundAgent",
                "technical_issue": "TechnicalAgent",
                "general_question": "ProductAgent"  # Default
            }
            
            # Select agent based on intent and confidence
            if state.intent_confidence > 0.7:
                selected_agent = agent_mapping.get(state.intent, "ProductAgent")
            else:
                # Low confidence - use general agent
                selected_agent = "ProductAgent"
            
            state.selected_agent = selected_agent
            state.metadata["routing_reason"] = f"Intent: {state.intent}, Confidence: {state.intent_confidence:.2f}"
            
            logger.info(f"Routed to: {selected_agent}")
            
        except Exception as e:
            logger.error(f"Routing error: {e}")
            state.error = f"Routing failed: {str(e)}"
        
        return state
    
    async def _process_with_agent_node(self, state: ConversationState) -> ConversationState:
        """Node: Process message with selected agent"""
        try:
            logger.info(f"Processing with {state.selected_agent}...")
            
            # Get the selected agent
            agent = self.agents[state.selected_agent]
            
            # Create message object
            message = Message(
                content=state.current_message,
                type=MessageType.USER,
                user_id=state.user_id,
                conversation_id=state.conversation_id
            )
            
            # Process with agent
            agent_response = await agent.process_message(message)
            
            # Update state
            state.agent_response = agent_response.content
            state.response_confidence = agent_response.confidence
            state.sources = agent_response.sources
            state.metadata["agent_processing_time"] = getattr(agent_response, 'processing_time', 0)
            
            logger.info(f"Agent response generated (confidence: {agent_response.confidence:.2f})")
            
        except Exception as e:
            logger.error(f"Agent processing error: {e}")
            state.error = f"Agent processing failed: {str(e)}"
        
        return state
    
    async def _generate_suggestions_node(self, state: ConversationState) -> ConversationState:
        """Node: Generate follow-up suggestions"""
        try:
            logger.info("Generating suggestions...")
            
            suggestions_map = {
                "ProductAgent": [
                    "Compare with other products",
                    "Check current promotions",
                    "View product reviews"
                ],
                "RefundAgent": [
                    "Check refund status",
                    "Contact billing support",
                    "View purchase history"
                ],
                "TechnicalAgent": [
                    "Try advanced troubleshooting",
                    "Contact technical support",
                    "Check system status"
                ]
            }
            
            state.suggestions = suggestions_map.get(
                state.selected_agent, 
                ["Ask another question", "Contact support"]
            )
            
            logger.info(f"Generated {len(state.suggestions)} suggestions")
            
        except Exception as e:
            logger.error(f"Suggestion generation error: {e}")
            state.error = f"Suggestion generation failed: {str(e)}"
        
        return state
    
    async def _handle_error_node(self, state: ConversationState) -> ConversationState:
        """Node: Handle errors gracefully"""
        logger.error(f"Handling error: {state.error}")
        
        # Generate fallback response
        state.agent_response = "I apologize, but I'm experiencing technical difficulties. Please try again or contact support."
        state.selected_agent = "ErrorHandler"
        state.response_confidence = 0.1
        state.suggestions = [
            "Try asking your question differently",
            "Contact human support",
            "Check system status"
        ]
        
        return state
    
    def _should_continue_after_classification(self, state: ConversationState) -> str:
        """Conditional edge: Continue after intent classification"""
        if state.error:
            return "error"
        return "continue"
    
    def _should_continue_after_routing(self, state: ConversationState) -> str:
        """Conditional edge: Continue after routing"""
        if state.error:
            return "error"
        return "continue"
    
    def _should_continue_after_processing(self, state: ConversationState) -> str:
        """Conditional edge: Continue after agent processing"""
        if state.error:
            return "error"
        return "continue"
    
    async def process_message(self, user_id: str, message: str, conversation_id: str = None) -> ChatResponse:
        """Main method to process message through LangGraph workflow"""
        start_time = time.time()
        
        try:
            # Create conversation ID if not provided
            if not conversation_id:
                conversation_id = f"conv_{uuid.uuid4().hex[:8]}"
            
            # Create initial state
            initial_state = ConversationState(
                user_id=user_id,
                conversation_id=conversation_id,
                original_message=message,
                current_message=message
            )
            
            # Store user message
            await self._store_user_message(user_id, message, conversation_id)
            
            # Process through LangGraph workflow
            config = {"configurable": {"thread_id": conversation_id}}
            
            logger.info(f"Starting LangGraph workflow for conversation: {conversation_id}")
            
            # Execute workflow
            final_state = await self.workflow.ainvoke(initial_state, config)
            
            # Store assistant message
            await self._store_assistant_message(
                user_id, 
                final_state.agent_response, 
                conversation_id,
                final_state.selected_agent
            )
            
            # Calculate response time
            response_time = time.time() - start_time
            
            # Create final response
            response = ChatResponse(
                response=final_state.agent_response,
                agent_used=final_state.selected_agent,
                confidence=final_state.response_confidence,
                response_time=response_time,
                conversation_id=conversation_id,
                suggestions=final_state.suggestions
            )
            
            logger.info(f"LangGraph workflow completed in {response_time:.2f}s")
            return response
            
        except Exception as e:
            logger.error(f"LangGraph orchestration error: {e}")
            response_time = time.time() - start_time
            
            return ChatResponse(
                response="I apologize, but I'm experiencing technical difficulties. Please try again.",
                agent_used="ErrorHandler",
                confidence=0.1,
                response_time=response_time,
                conversation_id=conversation_id or f"error_{uuid.uuid4().hex[:8]}",
                suggestions=["Try asking your question differently", "Contact human support"]
            )
    
    async def _store_user_message(self, user_id: str, message: str, conversation_id: str):
        """Store user message in Redis"""
        try:
            user_message = Message(
                content=message,
                type=MessageType.USER,
                user_id=user_id,
                conversation_id=conversation_id
            )
            await self.redis_client.store_message(user_message)
        except Exception as e:
            logger.warning(f"Failed to store user message: {e}")
    
    async def _store_assistant_message(self, user_id: str, response: str, conversation_id: str, agent_name: str):
        """Store assistant message in Redis"""
        try:
            assistant_message = Message(
                content=response,
                type=MessageType.ASSISTANT,
                user_id=user_id,
                conversation_id=conversation_id
            )
            await self.redis_client.store_message(assistant_message)
        except Exception as e:
            logger.warning(f"Failed to store assistant message: {e}")
    
    async def get_conversation_history(self, user_id: str, limit: int = 10) -> list:
        """Retrieve conversation history from Redis"""
        try:
            return await self.redis_client.get_conversation_history(user_id, limit)
        except Exception as e:
            logger.error(f"Failed to retrieve history: {e}")
            return []
    
    async def get_workflow_state(self, conversation_id: str) -> Dict[str, Any]:
        """Get current workflow state for debugging"""
        try:
            config = {"configurable": {"thread_id": conversation_id}}
            state = await self.workflow.aget_state(config)
            return {
                "values": state.values,
                "next": state.next,
                "metadata": state.metadata
            }
        except Exception as e:
            logger.error(f"Failed to get workflow state: {e}")
            return {}

# For backward compatibility
AgentOrchestrator = LangGraphOrchestrator
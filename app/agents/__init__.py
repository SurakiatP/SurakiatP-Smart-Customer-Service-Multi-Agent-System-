"""
AI Agents Module

Contains all specialized agents for handling different types of customer inquiries:
- RouterAgent: Intent classification and routing
- ProductAgent: Product inquiries and recommendations
- RefundAgent: Refund requests and policy information
- TechnicalAgent: Technical support and troubleshooting
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from app.agents.base_agent import BaseAgent
from app.agents.router_agent import RouterAgent
from app.agents.product_agent import ProductAgent
from app.agents.refund_agent import RefundAgent
from app.agents.technical_agent import TechnicalAgent
from app.agents.orchestrator import AgentOrchestrator

# Available agents registry
AVAILABLE_AGENTS = {
    "router": RouterAgent,
    "product": ProductAgent,
    "refund": RefundAgent,
    "technical": TechnicalAgent
}

# Agent factory function
def create_agent(agent_type: str) -> BaseAgent:
    """Factory function to create agents"""
    if agent_type not in AVAILABLE_AGENTS:
        raise ValueError(f"Unknown agent type: {agent_type}")
    
    return AVAILABLE_AGENTS[agent_type]()

__all__ = [
    "BaseAgent",
    "RouterAgent", 
    "ProductAgent",
    "RefundAgent",
    "TechnicalAgent",
    "AgentOrchestrator",
    "AVAILABLE_AGENTS",
    "create_agent"
]
"""
Analytics Routes

Analytics and metrics endpoints for monitoring system performance.
"""

from fastapi import APIRouter, Depends, Query
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import json
import random
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from app.api.dependencies import common_dependencies
from app.database.redis_client import RedisClient
from app.core.logger import get_logger

logger = get_logger(__name__)
router = APIRouter()

@router.get("/metrics/overview", dependencies=common_dependencies)
async def get_metrics_overview() -> Dict[str, Any]:
    """Get high-level metrics overview"""
    
    redis_client = RedisClient()
    
    # Mock metrics for demo (in production, calculate from real data)
    return {
        "timestamp": datetime.now().isoformat(),
        "metrics": {
            "total_conversations": 1247,
            "avg_response_time": 2.3,
            "customer_satisfaction": 4.8,
            "first_contact_resolution": 85.2,
            "daily_active_users": 156,
            "cost_savings_monthly": 4167  # $50K annual / 12
        },
        "agent_distribution": {
            "ProductAgent": 45.2,
            "TechnicalAgent": 32.1,
            "RefundAgent": 18.5,
            "GeneralAgent": 4.2
        },
        "trending": {
            "conversations_change": "+12%",
            "response_time_change": "-8%",
            "satisfaction_change": "+3%"
        }
    }

@router.get("/metrics/real-time", dependencies=common_dependencies)
async def get_real_time_metrics() -> Dict[str, Any]:
    """Get real-time system metrics"""
    
    # Simulate real-time data
    import random
    
    return {
        "timestamp": datetime.now().isoformat(),
        "current_metrics": {
            "active_conversations": random.randint(5, 25),
            "avg_response_time_last_hour": round(random.uniform(2.0, 3.5), 1),
            "requests_per_minute": random.randint(15, 45),
            "success_rate": round(random.uniform(95.0, 99.9), 1)
        },
        "agent_status": {
            "ProductAgent": "active",
            "RefundAgent": "active", 
            "TechnicalAgent": "active",
            "RouterAgent": "active"
        },
        "system_health": {
            "api_latency": round(random.uniform(50, 150), 0),
            "database_connections": random.randint(8, 15),
            "cache_hit_rate": round(random.uniform(75.0, 95.0), 1)
        }
    }

@router.get("/conversations/stats", dependencies=common_dependencies)
async def get_conversation_stats(
    days: int = Query(7, description="Number of days to analyze"),
    agent: Optional[str] = Query(None, description="Filter by agent type")
) -> Dict[str, Any]:
    """Get conversation statistics"""
    
    # Mock conversation stats
    dates = [(datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d") 
             for i in range(days)]
    
    stats = {
        "period": f"Last {days} days",
        "agent_filter": agent,
        "daily_stats": []
    }
    
    for date in reversed(dates):
        daily_stat = {
            "date": date,
            "total_conversations": random.randint(50, 150),
            "avg_response_time": round(random.uniform(2.0, 4.0), 1),
            "satisfaction_score": round(random.uniform(4.2, 4.9), 1),
            "resolution_rate": round(random.uniform(80.0, 90.0), 1)
        }
        
        if agent:
            daily_stat["agent_specific"] = {
                "conversations": random.randint(10, 50),
                "avg_confidence": round(random.uniform(0.7, 0.95), 2)
            }
        
        stats["daily_stats"].append(daily_stat)
    
    # Summary statistics
    stats["summary"] = {
        "total_conversations": sum(day["total_conversations"] for day in stats["daily_stats"]),
        "avg_response_time": round(
            sum(day["avg_response_time"] for day in stats["daily_stats"]) / len(stats["daily_stats"]), 1
        ),
        "avg_satisfaction": round(
            sum(day["satisfaction_score"] for day in stats["daily_stats"]) / len(stats["daily_stats"]), 1
        )
    }
    
    return stats

@router.get("/performance/agents", dependencies=common_dependencies)
async def get_agent_performance() -> Dict[str, Any]:
    """Get individual agent performance metrics"""
    
    agents_performance = {
        "ProductAgent": {
            "total_requests": 1205,
            "avg_response_time": 2.1,
            "avg_confidence": 0.87,
            "success_rate": 94.2,
            "popular_queries": [
                "pricing information",
                "product features", 
                "plan comparison"
            ]
        },
        "TechnicalAgent": {
            "total_requests": 856,
            "avg_response_time": 3.2,
            "avg_confidence": 0.82,
            "success_rate": 88.5,
            "popular_queries": [
                "login issues",
                "app crashes",
                "payment problems"
            ]
        },
        "RefundAgent": {
            "total_requests": 492,
            "avg_response_time": 2.8,
            "avg_confidence": 0.91,
            "success_rate": 96.1,
            "popular_queries": [
                "refund policy",
                "return process",
                "refund status"
            ]
        }
    }
    
    return {
        "timestamp": datetime.now().isoformat(),
        "agents": agents_performance,
        "top_performer": "RefundAgent",
        "improvement_opportunities": [
            "Optimize TechnicalAgent response time",
            "Improve overall confidence scores",
            "Expand ProductAgent knowledge base"
        ]
    }

@router.post("/feedback", dependencies=common_dependencies)
async def record_feedback(feedback_data: Dict[str, Any]) -> Dict[str, str]:
    """Record user feedback for analysis"""
    
    required_fields = ["conversation_id", "rating", "user_id"]
    
    for field in required_fields:
        if field not in feedback_data:
            return {"error": f"Missing required field: {field}"}
    
    # In production, store in database
    logger.info(f"Received feedback: {feedback_data}")
    
    # Mock storage
    feedback_entry = {
        "timestamp": datetime.now().isoformat(),
        "conversation_id": feedback_data["conversation_id"],
        "rating": feedback_data["rating"],
        "user_id": feedback_data["user_id"],
        "comment": feedback_data.get("comment", ""),
        "agent_used": feedback_data.get("agent_used", "unknown")
    }
    
    return {
        "status": "success",
        "message": "Feedback recorded successfully",
        "feedback_id": f"fb_{feedback_data['conversation_id'][:8]}"
    }
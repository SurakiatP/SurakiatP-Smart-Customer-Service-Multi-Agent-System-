"""
API Module

FastAPI endpoints and routing for the customer service system.
Includes chat endpoints, health checks, and analytics.
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from app.api.chat_routes import router as chat_router
from app.api.health_routes import router as health_router
from app.api.analytics_routes import router as analytics_router

# Available routers
ROUTERS = [
    (chat_router, "/api/v1", "chat"),
    (health_router, "/health", "health"),
    (analytics_router, "/api/v1/analytics", "analytics")
]

__all__ = [
    "chat_router",
    "health_router", 
    "analytics_router",
    "ROUTERS"
]
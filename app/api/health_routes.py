"""
Health Check Routes

System health monitoring and status endpoints.
"""

from fastapi import APIRouter, Depends
from typing import Dict, Any
import asyncio
import time
from datetime import datetime
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from app.api.dependencies import common_dependencies
from app.database.chroma_client import ChromaClient
from app.database.redis_client import RedisClient
from app.services.huggingface_client import HuggingFaceClient
from app.core.logger import get_logger

logger = get_logger(__name__)
router = APIRouter()

@router.get("/", dependencies=common_dependencies)
async def health_check() -> Dict[str, Any]:
    """Basic health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "Customer Service AI",
        "version": "1.0.0"
    }

@router.get("/detailed", dependencies=common_dependencies)
async def detailed_health_check() -> Dict[str, Any]:
    """Detailed health check with service status"""
    
    services_status = {}
    overall_status = "healthy"
    
    # Check Redis connection
    try:
        redis_client = RedisClient()
        await redis_client.redis.ping()
        services_status["redis"] = "connected"
    except Exception as e:
        logger.error(f"Redis health check failed: {e}")
        services_status["redis"] = "disconnected"
        overall_status = "degraded"
    
    # Check ChromaDB
    try:
        chroma_client = ChromaClient()
        # Simple test query
        chroma_client.client.heartbeat()
        services_status["chromadb"] = "connected"
    except Exception as e:
        logger.error(f"ChromaDB health check failed: {e}")
        services_status["chromadb"] = "disconnected"
        overall_status = "degraded"
    
    # Check Hugging Face API
    try:
        hf_client = HuggingFaceClient()
        # Test with a simple request (timeout quickly)
        test_result = await asyncio.wait_for(
            hf_client.classify_text("test", ["positive", "negative"]),
            timeout=5.0
        )
        services_status["huggingface"] = "available"
    except asyncio.TimeoutError:
        services_status["huggingface"] = "timeout"
        overall_status = "degraded"
    except Exception as e:
        logger.error(f"Hugging Face health check failed: {e}")
        services_status["huggingface"] = "unavailable"
        overall_status = "degraded"
    
    return {
        "status": overall_status,
        "timestamp": datetime.now().isoformat(),
        "services": services_status,
        "uptime_seconds": time.time() - start_time if 'start_time' in globals() else 0
    }

@router.get("/metrics", dependencies=common_dependencies)
async def get_system_metrics() -> Dict[str, Any]:
    """Get basic system performance metrics"""
    import psutil
    import os
    
    # Get process info
    process = psutil.Process(os.getpid())
    
    return {
        "timestamp": datetime.now().isoformat(),
        "system": {
            "cpu_percent": psutil.cpu_percent(interval=1),
            "memory_percent": psutil.virtual_memory().percent,
            "disk_percent": psutil.disk_usage('/').percent
        },
        "process": {
            "memory_mb": process.memory_info().rss / 1024 / 1024,
            "cpu_percent": process.cpu_percent(),
            "threads": process.num_threads(),
            "uptime_seconds": time.time() - process.create_time()
        }
    }

# Track service start time
start_time = time.time()
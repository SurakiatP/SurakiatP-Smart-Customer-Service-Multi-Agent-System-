import redis.asyncio as redis
import json
from typing import List, Optional
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from app.database.models import Message
from app.core.config import settings
from app.core.logger import get_logger

logger = get_logger(__name__)

class RedisClient:
    """Redis client for caching and session management"""
    
    def __init__(self):
        self.redis = redis.from_url(settings.REDIS_URL, decode_responses=True)
    
    async def store_message(self, message: Message):
        """Store message in conversation history"""
        try:
            key = f"conversation:{message.conversation_id}"
            message_data = {
                "id": message.id,
                "content": message.content,
                "type": message.type.value,
                "timestamp": message.timestamp.isoformat(),
                "user_id": message.user_id
            }
            
            await self.redis.lpush(key, json.dumps(message_data))
            await self.redis.expire(key, 86400)  # 24 hours TTL
            
        except Exception as e:
            logger.error(f"Failed to store message: {e}")
    
    async def get_conversation_history(self, conversation_id: str, limit: int = 10) -> List[dict]:
        """Retrieve conversation history"""
        try:
            key = f"conversation:{conversation_id}"
            messages = await self.redis.lrange(key, 0, limit - 1)
            
            return [json.loads(msg) for msg in messages]
            
        except Exception as e:
            logger.error(f"Failed to retrieve conversation: {e}")
            return []
    
    async def cache_response(self, key: str, response: str, ttl: int = 3600):
        """Cache API response"""
        try:
            await self.redis.setex(key, ttl, response)
        except Exception as e:
            logger.error(f"Failed to cache response: {e}")
    
    async def get_cached_response(self, key: str) -> Optional[str]:
        """Get cached response"""
        try:
            return await self.redis.get(key)
        except Exception as e:
            logger.error(f"Failed to get cached response: {e}")
            return None
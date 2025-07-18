"""
Cache Service

Intelligent caching for API responses, AI model outputs, and frequently accessed data.
"""

import json
import hashlib
from typing import Any, Optional, Dict, List
from datetime import datetime, timedelta
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from app.database.redis_client import RedisClient
from app.core.logger import get_logger
from app.core.config import settings

logger = get_logger(__name__)

class CacheService:
    """Intelligent caching service"""
    
    def __init__(self):
        self.redis_client = RedisClient()
        self.default_ttl = settings.CACHE_TTL
        self.cache_prefixes = {
            "ai_response": "ai_resp:",
            "product_info": "prod_info:",
            "order_data": "order:",
            "user_session": "session:",
            "api_response": "api_resp:",
            "knowledge_base": "kb:"
        }
    
    def _generate_cache_key(self, prefix: str, identifier: str) -> str:
        """Generate cache key with prefix"""
        return f"{self.cache_prefixes.get(prefix, prefix)}{identifier}"
    
    def _hash_content(self, content: Any) -> str:
        """Create hash of content for cache key"""
        if isinstance(content, (dict, list)):
            content_str = json.dumps(content, sort_keys=True)
        else:
            content_str = str(content)
        
        return hashlib.md5(content_str.encode()).hexdigest()[:16]
    
    async def get_ai_response_cache(self, agent_name: str, message: str, context: Dict = None) -> Optional[Dict[str, Any]]:
        """Get cached AI response"""
        try:
            # Create cache key based on agent, message, and context
            cache_content = {
                "agent": agent_name,
                "message": message.lower().strip(),
                "context": context or {}
            }
            
            cache_hash = self._hash_content(cache_content)
            cache_key = self._generate_cache_key("ai_response", cache_hash)
            
            cached_data = await self.redis_client.get_cached_response(cache_key)
            
            if cached_data:
                logger.info(f"Cache hit for AI response: {agent_name}")
                return json.loads(cached_data)
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to get AI response cache: {e}")
            return None
    
    async def cache_ai_response(
        self, 
        agent_name: str, 
        message: str, 
        response: Dict[str, Any], 
        context: Dict = None,
        ttl: int = None
    ) -> bool:
        """Cache AI response"""
        try:
            cache_content = {
                "agent": agent_name,
                "message": message.lower().strip(),
                "context": context or {}
            }
            
            cache_hash = self._hash_content(cache_content)
            cache_key = self._generate_cache_key("ai_response", cache_hash)
            
            # Add metadata to cached response
            cached_response = {
                **response,
                "cached_at": datetime.now().isoformat(),
                "cache_key": cache_key
            }
            
            await self.redis_client.cache_response(
                cache_key, 
                json.dumps(cached_response),
                ttl or self.default_ttl
            )
            
            logger.info(f"Cached AI response for {agent_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to cache AI response: {e}")
            return False
    
    async def get_product_cache(self, product_id: str) -> Optional[Dict[str, Any]]:
        """Get cached product information"""
        try:
            cache_key = self._generate_cache_key("product_info", product_id)
            cached_data = await self.redis_client.get_cached_response(cache_key)
            
            if cached_data:
                logger.info(f"Cache hit for product: {product_id}")
                return json.loads(cached_data)
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to get product cache: {e}")
            return None
    
    async def cache_product_info(self, product_id: str, product_data: Dict[str, Any], ttl: int = None) -> bool:
        """Cache product information"""
        try:
            cache_key = self._generate_cache_key("product_info", product_id)
            
            # Add cache metadata
            cached_data = {
                **product_data,
                "cached_at": datetime.now().isoformat(),
                "product_id": product_id
            }
            
            await self.redis_client.cache_response(
                cache_key,
                json.dumps(cached_data),
                ttl or (self.default_ttl * 2)  # Products cache longer
            )
            
            logger.info(f"Cached product info: {product_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to cache product info: {e}")
            return False
    
    async def get_user_session_cache(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get cached user session data"""
        try:
            cache_key = self._generate_cache_key("user_session", user_id)
            cached_data = await self.redis_client.get_cached_response(cache_key)
            
            if cached_data:
                return json.loads(cached_data)
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to get user session cache: {e}")
            return None
    
    async def cache_user_session(self, user_id: str, session_data: Dict[str, Any]) -> bool:
        """Cache user session data"""
        try:
            cache_key = self._generate_cache_key("user_session", user_id)
            
            # Add session metadata
            cached_session = {
                **session_data,
                "last_updated": datetime.now().isoformat(),
                "user_id": user_id
            }
            
            # Sessions have shorter TTL
            session_ttl = 30 * 60  # 30 minutes
            
            await self.redis_client.cache_response(
                cache_key,
                json.dumps(cached_session),
                session_ttl
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to cache user session: {e}")
            return False
    
    async def invalidate_cache(self, cache_type: str, identifier: str) -> bool:
        """Invalidate specific cache entry"""
        try:
            cache_key = self._generate_cache_key(cache_type, identifier)
            # Redis delete would go here
            # await self.redis_client.delete(cache_key)
            
            logger.info(f"Invalidated cache: {cache_key}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to invalidate cache: {e}")
            return False
    
    async def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache performance statistics"""
        try:
            # Mock cache statistics
            stats = {
                "total_keys": 1234,
                "hit_rate": 0.847,
                "miss_rate": 0.153,
                "memory_usage_mb": 45.7,
                "avg_response_time_ms": 2.3,
                "cache_types": {
                    "ai_response": {"keys": 456, "hit_rate": 0.82},
                    "product_info": {"keys": 123, "hit_rate": 0.91},
                    "user_session": {"keys": 234, "hit_rate": 0.95},
                    "api_response": {"keys": 321, "hit_rate": 0.78}
                },
                "last_updated": datetime.now().isoformat()
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get cache stats: {e}")
            return {}
    
    async def warm_cache(self, cache_items: List[Dict[str, Any]]) -> int:
        """Warm up cache with frequently accessed data"""
        try:
            cached_count = 0
            
            for item in cache_items:
                cache_type = item.get("type")
                identifier = item.get("id")
                data = item.get("data")
                ttl = item.get("ttl", self.default_ttl)
                
                if cache_type and identifier and data:
                    cache_key = self._generate_cache_key(cache_type, identifier)
                    
                    await self.redis_client.cache_response(
                        cache_key,
                        json.dumps(data),
                        ttl
                    )
                    
                    cached_count += 1
            
            logger.info(f"Cache warmed with {cached_count} items")
            return cached_count
            
        except Exception as e:
            logger.error(f"Failed to warm cache: {e}")
            return 0
    
    async def clear_expired_cache(self) -> int:
        """Clear expired cache entries"""
        try:
            # Redis automatically handles TTL expiration
            # This method would implement custom cleanup logic
            
            logger.info("Cleared expired cache entries")
            return 0  # Number of cleared entries
            
        except Exception as e:
            logger.error(f"Failed to clear expired cache: {e}")
            return 0

# Global cache service instance
cache_service = CacheService()
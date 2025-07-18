"""
Services Module

External service integrations and utility services.
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from app.services.huggingface_client import HuggingFaceClient
from app.services.external_apis import ExternalAPIClient
from app.services.cache_service import CacheService

# Service instances
hf_client = HuggingFaceClient()
external_api_client = ExternalAPIClient()
cache_service = CacheService()

__all__ = [
    "HuggingFaceClient",
    "ExternalAPIClient",
    "CacheService",
    "hf_client",
    "external_api_client", 
    "cache_service"
]
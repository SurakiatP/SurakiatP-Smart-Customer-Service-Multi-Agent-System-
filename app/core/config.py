# Application configuration settings
from pydantic_settings  import BaseSettings
from typing import List, Optional
import secrets
from dotenv import load_dotenv
import os

class Settings(BaseSettings):
    # API Configuration
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Customer Service AI"
    VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # Hugging Face Configuration
    HUGGINGFACE_API_KEY: Optional[str] = os.getenv("HUGGINGFACE_API_KEY")
    HUGGINGFACE_API_URL: str = "https://api-inference.huggingface.co"
    HUGGINGFACE_TIMEOUT: int = 30
    
    # Database Configuration
    CHROMA_PERSIST_DIRECTORY: str = "./data/chroma_db"
    REDIS_URL: str = "redis://localhost:6379"
    REDIS_PASSWORD: Optional[str] = None
    REDIS_DB: int = 0
    
    # Security
    # SECRET_KEY: str = secrets.token_urlsafe(32)
    SECRET_KEY: str = os.getenv("SECRET_KEY")
    ALLOWED_HOSTS: List[str] = ["*"]
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8501"]
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 30
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "./logs/app.log"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Performance
    MAX_CONCURRENT_REQUESTS: int = 100
    REQUEST_TIMEOUT: int = 30
    CACHE_TTL: int = 3600  # 1 hour
    
    # Rate Limiting
    RATE_LIMIT_REQUESTS: int = 60
    RATE_LIMIT_WINDOW: int = 60  # seconds
    
    # External APIs
    EXTERNAL_API_TIMEOUT: int = 10
    EXTERNAL_API_RETRIES: int = 3
    
    # Monitoring
    METRICS_ENABLED: bool = True
    HEALTH_CHECK_INTERVAL: int = 30
    
    # Environment
    ENVIRONMENT: str = "development"  # development, staging, production
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        
    def get_database_url(self) -> str:
        """Get complete Redis URL"""
        if self.REDIS_PASSWORD:
            return f"redis://:{self.REDIS_PASSWORD}@{self.REDIS_URL.split('://')[-1]}/{self.REDIS_DB}"
        return f"{self.REDIS_URL}/{self.REDIS_DB}"

settings = Settings()
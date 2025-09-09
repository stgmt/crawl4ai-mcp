import os
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

class Settings:
    """Configuration settings loaded from environment variables"""
    
    # Crawl4ai Backend
    CRAWL4AI_ENDPOINT: str = os.getenv("CRAWL4AI_ENDPOINT", "https://stigmat-rudnev.crawl4ai-dev.fvds.ru")
    
    # Server Ports
    HTTP_PORT: int = int(os.getenv("HTTP_PORT", "3000"))
    SSE_PORT: int = int(os.getenv("SSE_PORT", "9001"))
    
    # Authentication
    BEARER_TOKEN: Optional[str] = os.getenv("BEARER_TOKEN")
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    
    # HTTP Client Configuration
    REQUEST_TIMEOUT: int = int(os.getenv("REQUEST_TIMEOUT", "30"))
    
    @classmethod
    def get_crawl4ai_url(cls, endpoint: str) -> str:
        """Get full URL for crawl4ai API endpoint"""
        return f"{cls.CRAWL4AI_ENDPOINT.rstrip('/')}/{endpoint.lstrip('/')}"

# Global settings instance
settings = Settings()
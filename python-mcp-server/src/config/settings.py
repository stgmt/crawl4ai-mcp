import os
import logging
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

class Settings:
    """Configuration settings loaded from environment variables"""
    
    def __init__(self):
        # Crawl4ai Backend - REQUIRED
        self.CRAWL4AI_ENDPOINT: str = os.getenv("CRAWL4AI_ENDPOINT", "")
        
        # Server Ports
        self.HTTP_PORT: int = int(os.getenv("HTTP_PORT", "3000"))
        self.SSE_PORT: int = int(os.getenv("SSE_PORT", "9001"))
        
        # Authentication - OPTIONAL
        self.CRAWL4AI_BEARER_TOKEN: Optional[str] = os.getenv("CRAWL4AI_BEARER_TOKEN")
        
        # Logging
        self.LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
        self.DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
        
        # HTTP Client Configuration
        self.REQUEST_TIMEOUT: int = int(os.getenv("REQUEST_TIMEOUT", "30"))
        
        # Validate settings after initialization
        self._validate_settings()
    
    def _validate_settings(self):
        """Validate required settings and log configuration"""
        logger = logging.getLogger(__name__)
        
        # Check required CRAWL4AI_ENDPOINT
        if not self.CRAWL4AI_ENDPOINT:
            raise ValueError(
                "❌ ОБЯЗАТЕЛЬНЫЙ ПАРАМЕТР НЕ УКАЗАН: CRAWL4AI_ENDPOINT\n"
                "Укажите URL вашего Crawl4AI API сервера через переменную окружения:\n"
                "export CRAWL4AI_ENDPOINT='https://your-api-server.com'\n\n"
                "Для тестирования можете использовать:\n" 
                "export CRAWL4AI_ENDPOINT='https://stigmat-rudnev.crawl4ai-dev.fvds.ru'"
            )
        
        if not self.CRAWL4AI_ENDPOINT.startswith(('http://', 'https://')):
            raise ValueError(
                f"❌ НЕПРАВИЛЬНЫЙ ФОРМАТ URL: {self.CRAWL4AI_ENDPOINT}\n"
                "URL должен начинаться с http:// или https://"
            )
        
        # Log configuration
        logger.info(f"✅ Crawl4AI endpoint: {self.CRAWL4AI_ENDPOINT}")
        
        if self.CRAWL4AI_BEARER_TOKEN:
            masked_token = f"{self.CRAWL4AI_BEARER_TOKEN[:10]}...{self.CRAWL4AI_BEARER_TOKEN[-4:]}"
            logger.info(f"🔐 Bearer token configured: {masked_token}")
        else:
            logger.warning("⚠️ Bearer token not provided - некоторые API могут требовать аутентификацию")
    
    def get_crawl4ai_url(self, endpoint: str) -> str:
        """Get full URL for crawl4ai API endpoint"""
        return f"{self.CRAWL4AI_ENDPOINT.rstrip('/')}/{endpoint.lstrip('/')}"

# Global settings instance
settings = Settings()
import abc
import httpx
import logging
from typing import Dict, Any, Sequence, List
from mcp import Tool
from mcp.types import TextContent
from config.settings import settings

logger = logging.getLogger(__name__)

class BaseHandler(abc.ABC):
    """Base class for all MCP tool handlers"""
    
    name: str
    description: str
    
    @abc.abstractmethod
    def get_tool_description(self) -> Tool:
        """Return the tool description for MCP clients"""
        pass
    
    @abc.abstractmethod
    async def run_tool(self, arguments: Dict[str, Any]) -> Sequence[TextContent]:
        """Execute the tool with given arguments"""
        pass
    
    async def call_crawl4ai_api(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Make HTTP call to crawl4ai API"""
        url = settings.get_crawl4ai_url(endpoint)
        
        try:
            async with httpx.AsyncClient(timeout=settings.REQUEST_TIMEOUT) as client:
                headers = {
                    "Content-Type": "application/json"
                }
                # Исправлено: используем правильную переменную
                if settings.CRAWL4AI_BEARER_TOKEN:
                    headers["Authorization"] = f"Bearer {settings.CRAWL4AI_BEARER_TOKEN}"
                
                # Детальное логирование запроса
                logger.info(f"Calling crawl4ai API: {url}")
                logger.debug(f"Request headers: {headers}")
                logger.debug(f"Request data: {data}")
                
                response = await client.post(url, json=data, headers=headers)
                
                # Логирование ответа
                logger.info(f"Response status: {response.status_code}")
                logger.debug(f"Response headers: {dict(response.headers)}")
                
                # Проверка статуса
                response.raise_for_status()
                
                result = response.json()
                logger.info(f"Crawl4ai API response received: {len(str(result))} chars")
                logger.debug(f"Response data (first 500 chars): {str(result)[:500]}")
                return result
                
        except httpx.HTTPStatusError as e:
            error_msg = f"❌ HTTP {e.response.status_code} Error: {e.response.text}\n"
            error_msg += f"URL: {url}\n"
            error_msg += f"Endpoint: {endpoint}"
            logger.error(f"Crawl4ai API HTTP error: {error_msg}")
            raise Exception(error_msg)
        except httpx.TimeoutException:
            error_msg = f"⏱️ Timeout Error: Request to {url} timed out after {settings.REQUEST_TIMEOUT}s\n"
            error_msg += f"Проверьте доступность API сервера: {settings.CRAWL4AI_ENDPOINT}"
            logger.error(error_msg)
            raise Exception(error_msg)
        except httpx.ConnectError as e:
            error_msg = f"🔌 Connection Error: Cannot connect to {url}\n"
            error_msg += f"Проверьте:\n"
            error_msg += f"1. Правильность URL: {settings.CRAWL4AI_ENDPOINT}\n"
            error_msg += f"2. Доступность сервера\n"
            error_msg += f"3. Настройки сети/firewall\n"
            error_msg += f"Original error: {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg)
        except Exception as e:
            error_msg = f"💥 Unexpected Error calling crawl4ai API: {str(e)}\n"
            error_msg += f"URL: {url}\n"
            error_msg += f"Type: {type(e).__name__}"
            logger.error(error_msg)
            raise Exception(error_msg)

class ToolRegistry:
    """Registry for all available MCP tools"""
    
    _tools: Dict[str, BaseHandler] = {}
    
    @classmethod
    def register_tool(cls, tool: BaseHandler) -> None:
        """Register a tool handler"""
        cls._tools[tool.name] = tool
        logger.info(f"Registered tool: {tool.name}")
    
    @classmethod
    def get_tool(cls, name: str) -> BaseHandler:
        """Get tool handler by name"""
        if name not in cls._tools:
            raise ValueError(f"Unknown tool: {name}")
        return cls._tools[name]
    
    @classmethod
    def get_all_tools(cls) -> List[Tool]:
        """Get all tool descriptions"""
        return [tool.get_tool_description() for tool in cls._tools.values()]
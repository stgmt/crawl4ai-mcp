import abc
import logging
from collections.abc import Sequence
from typing import Any

import httpx
from mcp import Tool
from mcp.types import TextContent

from crawl4ai_mcp.config.settings import settings

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
    async def run_tool(self, arguments: dict[str, Any]) -> Sequence[TextContent]:
        """Execute the tool with given arguments"""
        pass

    async def call_crawl4ai_api(self, endpoint: str, data: dict[str, Any]) -> dict[str, Any]:
        """Make HTTP call to crawl4ai API"""
        url = settings.get_crawl4ai_url(endpoint)

        try:
            async with httpx.AsyncClient(timeout=settings.REQUEST_TIMEOUT) as client:
                headers = {"Content-Type": "application/json"}
                if settings.BEARER_TOKEN:
                    headers["Authorization"] = f"Bearer {settings.BEARER_TOKEN}"

                # Detailed request logging
                logger.info(f"Calling crawl4ai API: {url}")
                logger.debug(f"Request headers: {headers}")
                logger.debug(f"Request data: {data}")

                response = await client.post(url, json=data, headers=headers)

                # Response logging
                logger.info(f"Response status: {response.status_code}")
                logger.debug(f"Response headers: {dict(response.headers)}")

                # Status check
                response.raise_for_status()

                result = response.json()
                logger.info(f"Crawl4ai API response received: {len(str(result))} chars")
                logger.debug(f"Response data (first 500 chars): {str(result)[:500]}")
                return result

        except httpx.HTTPStatusError as e:
            error_msg = f"HTTP {e.response.status_code}: {e.response.text}"
            logger.error(f"Crawl4ai API error: {error_msg}")
            raise Exception(error_msg) from e
        except httpx.TimeoutException as e:
            error_msg = f"Timeout calling crawl4ai API: {url}"
            logger.error(error_msg)
            raise Exception(error_msg) from e
        except Exception as e:
            error_msg = f"Error calling crawl4ai API: {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg) from e


class ToolRegistry:
    """Registry for all available MCP tools"""

    _tools: dict[str, BaseHandler] = {}

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
    def get_all_tools(cls) -> list[Tool]:
        """Get all tool descriptions"""
        return [tool.get_tool_description() for tool in cls._tools.values()]

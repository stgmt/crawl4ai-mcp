from collections.abc import Sequence
from typing import Any

from mcp import Tool
from mcp.types import TextContent

from .base import BaseHandler, ToolRegistry


class Crawl4aiMd(BaseHandler):
    """Convert webpage content to clean markdown format with content filtering"""

    name = "md"
    description = "Convert webpage to clean markdown format with content filtering options"

    def get_tool_description(self) -> Tool:
        return Tool(
            name=self.name,
            description=self.description,
            inputSchema={
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "Target URL to crawl and convert to markdown",
                    },
                    "c": {
                        "type": "string",
                        "default": "0",
                        "description": "Cache-bust counter for forcing fresh content",
                    },
                    "f": {
                        "type": "string",
                        "default": "fit",
                        "enum": ["raw", "fit", "bm25", "llm"],
                        "description": "Content filter strategy: raw, fit, bm25, or llm",
                    },
                    "q": {
                        "type": "string",
                        "description": "Query string for BM25/LLM content filtering",
                    },
                    "provider": {
                        "type": "string",
                        "description": "LLM provider override (e.g., 'anthropic/claude-3-opus')",
                    },
                },
                "required": ["url"],
            },
        )

    async def run_tool(self, arguments: dict[str, Any]) -> Sequence[TextContent]:
        """Execute markdown conversion via crawl4ai API"""
        try:
            # API requires urls (array), not url
            request_data = {
                "urls": [arguments["url"]],  # API expects array of URLs
                "wait_for": "body",
                "timeout": 30000,
                "remove_overlay_elements": True,
                "magic": True,
                "exclude_external_links": True,
            }

            # Call /crawl endpoint instead of /md
            result = await self.call_crawl4ai_api("crawl", request_data)

            # API returns array of results for each URL
            if isinstance(result, list) and len(result) > 0:
                first_result = result[0]
                if isinstance(first_result, dict):
                    # Extract markdown from first result
                    content = first_result.get("markdown", "")
                    if not content and "markdown_v2" in first_result:
                        # Use markdown_v2 if regular markdown is missing
                        markdown_v2 = first_result.get("markdown_v2", {})
                        content = markdown_v2.get("raw_markdown", str(first_result))
                    elif not content:
                        # Fallback to full result
                        content = str(first_result)
                else:
                    content = str(result)
            elif isinstance(result, dict) and "markdown" in result:
                # In case API returns object instead of array
                content = result["markdown"]
            else:
                content = str(result)

            return [TextContent(type="text", text=content)]

        except Exception as e:
            return [TextContent(type="text", text=f"Error converting to markdown: {str(e)}")]


# Register the tool
ToolRegistry.register_tool(Crawl4aiMd())

from typing import Dict, Any, Sequence
from mcp import Tool
from mcp.types import TextContent
from .base import BaseHandler, ToolRegistry

class Crawl4aiHtml(BaseHandler):
    """Get preprocessed HTML structure for schema extraction"""
    
    name = "html"
    description = "Get cleaned and preprocessed HTML content for further processing"
    
    def get_tool_description(self) -> Tool:
        return Tool(
            name=self.name,
            description=self.description,
            inputSchema={
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "Target URL to crawl and extract HTML from"
                    }
                },
                "required": ["url"]
            }
        )
    
    async def run_tool(self, arguments: Dict[str, Any]) -> Sequence[TextContent]:
        """Execute HTML extraction via crawl4ai API"""
        try:
            # API требует urls (массив), а не url
            request_data = {
                "urls": [arguments["url"]],
                "wait_for": "body",
                "timeout": 30000,
                "remove_overlay_elements": True
            }
            
            # Используем /crawl endpoint
            result = await self.call_crawl4ai_api("crawl", request_data)
            
            # Обрабатываем массив результатов
            if isinstance(result, list) and len(result) > 0:
                first_result = result[0]
                if isinstance(first_result, dict):
                    content = first_result.get("html", first_result.get("cleaned_html", str(first_result)))
                else:
                    content = str(result)
            elif isinstance(result, dict) and "html" in result:
                content = result["html"]
            else:
                content = str(result)
            
            return [TextContent(type="text", text=content)]
            
        except Exception as e:
            return [TextContent(type="text", text=f"Error extracting HTML: {str(e)}")]

# Register the tool
ToolRegistry.register_tool(Crawl4aiHtml())
from typing import Dict, Any, Sequence
from mcp import Tool
from mcp.types import TextContent
from .base import BaseHandler, ToolRegistry

class Crawl4aiScreenshot(BaseHandler):
    """Capture full-page PNG screenshot with optional delay"""
    
    name = "screenshot"
    description = "Capture full-page PNG screenshot of specified URL with configurable wait time"
    
    def get_tool_description(self) -> Tool:
        return Tool(
            name=self.name,
            description=self.description,
            inputSchema={
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "Target URL to capture screenshot from"
                    },
                    "output_path": {
                        "type": "string",
                        "description": "Optional path to save screenshot file (if not provided, returns base64 data)"
                    },
                    "screenshot_wait_for": {
                        "type": "number",
                        "default": 2,
                        "description": "Wait time in seconds before capturing screenshot"
                    }
                },
                "required": ["url"]
            }
        )
    
    async def run_tool(self, arguments: Dict[str, Any]) -> Sequence[TextContent]:
        """Execute screenshot capture via crawl4ai API"""
        try:
            request_data = {
                "url": arguments["url"],
                "screenshot_wait_for": arguments.get("screenshot_wait_for", 2)
            }
            
            if "output_path" in arguments:
                request_data["output_path"] = arguments["output_path"]
            
            result = await self.call_crawl4ai_api("screenshot", request_data)
            
            # Handle response
            if isinstance(result, dict):
                if "screenshot_path" in result:
                    content = f"Screenshot saved to: {result['screenshot_path']}"
                elif "screenshot" in result:
                    content = f"Screenshot captured (base64 data: {len(result['screenshot'])} chars)"
                else:
                    content = str(result)
            else:
                content = str(result)
            
            return [TextContent(type="text", text=content)]
            
        except Exception as e:
            return [TextContent(type="text", text=f"Error capturing screenshot: {str(e)}")]

# Register the tool
ToolRegistry.register_tool(Crawl4aiScreenshot())
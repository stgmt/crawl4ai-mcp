from typing import Dict, Any, Sequence, List
from mcp import Tool
from mcp.types import TextContent
from .base import BaseHandler, ToolRegistry
import json

class Crawl4aiExecuteJs(BaseHandler):
    """Execute JavaScript snippets on URL and return full CrawlResult"""
    
    name = "execute_js"
    description = "Execute JavaScript code on specified URL and return comprehensive results"
    
    def get_tool_description(self) -> Tool:
        return Tool(
            name=self.name,
            description=self.description,
            inputSchema={
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "Target URL to execute JavaScript on"
                    },
                    "scripts": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of JavaScript snippets to execute in order (each should be an expression that returns a value)"
                    }
                },
                "required": ["url", "scripts"]
            }
        )
    
    async def run_tool(self, arguments: Dict[str, Any]) -> Sequence[TextContent]:
        """Execute JavaScript via crawl4ai API"""
        try:
            request_data = {
                "url": arguments["url"],
                "scripts": arguments["scripts"]
            }
            
            result = await self.call_crawl4ai_api("execute_js", request_data)
            
            # Format comprehensive result
            if isinstance(result, dict):
                # Extract key information from CrawlResult
                formatted_result = {
                    "url": result.get("url"),
                    "success": result.get("success", False),
                    "js_execution_result": result.get("js_execution_result"),
                    "extracted_content": result.get("extracted_content"),
                    "links": result.get("links", {}),
                    "media": result.get("media", {}),
                }
                
                # Include markdown if available
                if "markdown" in result:
                    formatted_result["markdown"] = result["markdown"]
                
                content = json.dumps(formatted_result, indent=2, ensure_ascii=False)
            else:
                content = str(result)
            
            return [TextContent(type="text", text=content)]
            
        except Exception as e:
            return [TextContent(type="text", text=f"Error executing JavaScript: {str(e)}")]

# Register the tool
ToolRegistry.register_tool(Crawl4aiExecuteJs())
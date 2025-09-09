from typing import Dict, Any, Sequence, List
from mcp import Tool
from mcp.types import TextContent
from .base import BaseHandler, ToolRegistry
import json

class Crawl4aiCrawl(BaseHandler):
    """Crawl multiple URLs and return results as JSON"""
    
    name = "crawl"
    description = "Crawl multiple URLs simultaneously and return comprehensive results for each"
    
    def get_tool_description(self) -> Tool:
        return Tool(
            name=self.name,
            description=self.description,
            inputSchema={
                "type": "object",
                "properties": {
                    "urls": {
                        "type": "array",
                        "items": {"type": "string"},
                        "maxItems": 100,
                        "minItems": 1,
                        "description": "List of URLs to crawl (maximum 100 URLs)"
                    },
                    "browser_config": {
                        "type": "object",
                        "description": "Browser configuration options (optional)",
                        "additionalProperties": True
                    },
                    "crawler_config": {
                        "type": "object", 
                        "description": "Crawler configuration options (optional)",
                        "additionalProperties": True
                    }
                },
                "required": ["urls"]
            }
        )
    
    async def run_tool(self, arguments: Dict[str, Any]) -> Sequence[TextContent]:
        """Execute multi-URL crawling via crawl4ai API"""
        try:
            request_data = {"urls": arguments["urls"]}
            
            # Add optional configurations
            if "browser_config" in arguments:
                request_data["browser_config"] = arguments["browser_config"]
            if "crawler_config" in arguments:
                request_data["crawler_config"] = arguments["crawler_config"]
            
            result = await self.call_crawl4ai_api("crawl", request_data)
            
            # Format results
            if isinstance(result, dict) or isinstance(result, list):
                # Pretty print JSON results
                content = json.dumps(result, indent=2, ensure_ascii=False)
            else:
                content = str(result)
            
            # Add summary information
            if isinstance(result, list):
                summary = f"Crawled {len(result)} URLs successfully.\n\n"
                content = summary + content
            elif isinstance(result, dict) and "results" in result:
                results_count = len(result.get("results", []))
                summary = f"Crawled {results_count} URLs successfully.\n\n"
                content = summary + content
            
            return [TextContent(type="text", text=content)]
            
        except Exception as e:
            return [TextContent(type="text", text=f"Error crawling URLs: {str(e)}")]

# Register the tool
ToolRegistry.register_tool(Crawl4aiCrawl())
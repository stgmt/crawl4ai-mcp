from typing import Dict, Any, Sequence
from mcp import Tool
from mcp.types import TextContent
from .base import BaseHandler, ToolRegistry

class Crawl4aiAsk(BaseHandler):
    """Query Crawl4ai library documentation and code context"""
    
    name = "ask"
    description = "Query Crawl4ai library documentation and code context for development assistance"
    
    def get_tool_description(self) -> Tool:
        return Tool(
            name=self.name,
            description=self.description,
            inputSchema={
                "type": "object",
                "properties": {
                    "context_type": {
                        "type": "string",
                        "enum": ["code", "doc", "all"],
                        "default": "all",
                        "description": "Type of context to retrieve: code, doc, or all"
                    },
                    "query": {
                        "type": "string",
                        "description": "Search query to filter documentation paragraphs using BM25"
                    },
                    "score_ratio": {
                        "type": "number",
                        "description": "Minimum score as fraction of maximum score for filtering results"
                    },
                    "max_results": {
                        "type": "integer",
                        "default": 20,
                        "description": "Maximum number of results to return"
                    }
                }
            }
        )
    
    async def run_tool(self, arguments: Dict[str, Any]) -> Sequence[TextContent]:
        """Query Crawl4ai documentation via API"""
        try:
            # Prepare request data - use GET parameters for ask endpoint
            params = {}
            if "context_type" in arguments:
                params["context_type"] = arguments["context_type"]
            if "query" in arguments:
                params["query"] = arguments["query"]
            if "score_ratio" in arguments:
                params["score_ratio"] = arguments["score_ratio"]
            if "max_results" in arguments:
                params["max_results"] = arguments["max_results"]
            
            # For ask endpoint, we might need to use GET with params instead of POST
            # This is a special case since it's documentation query
            import httpx
            from config.settings import settings
            
            url = settings.get_crawl4ai_url("ask")
            
            async with httpx.AsyncClient(timeout=settings.REQUEST_TIMEOUT) as client:
                headers = {}
                if settings.BEARER_TOKEN:
                    headers["Authorization"] = f"Bearer {settings.BEARER_TOKEN}"
                
                # Try GET first, then POST if needed
                try:
                    response = await client.get(url, params=params, headers=headers)
                    response.raise_for_status()
                except:
                    # Fallback to POST if GET doesn't work
                    response = await client.post(url, json=arguments, headers=headers)
                    response.raise_for_status()
                
                result = response.text if response.headers.get("content-type", "").startswith("text") else response.json()
            
            # Format result
            if isinstance(result, dict):
                content = str(result.get("content", result))
            else:
                content = str(result)
            
            return [TextContent(type="text", text=content)]
            
        except Exception as e:
            return [TextContent(type="text", text=f"Error querying Crawl4ai documentation: {str(e)}")]

# Register the tool
ToolRegistry.register_tool(Crawl4aiAsk())
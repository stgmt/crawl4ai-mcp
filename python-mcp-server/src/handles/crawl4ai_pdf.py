from typing import Dict, Any, Sequence
from mcp import Tool
from mcp.types import TextContent
from .base import BaseHandler, ToolRegistry

class Crawl4aiPdf(BaseHandler):
    """Generate PDF document of specified URL"""
    
    name = "pdf"
    description = "Generate PDF document from webpage for archival or printing purposes"
    
    def get_tool_description(self) -> Tool:
        return Tool(
            name=self.name,
            description=self.description,
            inputSchema={
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "Target URL to convert to PDF document"
                    },
                    "output_path": {
                        "type": "string",
                        "description": "Optional path to save PDF file (if not provided, returns base64 data)"
                    }
                },
                "required": ["url"]
            }
        )
    
    async def run_tool(self, arguments: Dict[str, Any]) -> Sequence[TextContent]:
        """Execute PDF generation via crawl4ai API"""
        try:
            request_data = {"url": arguments["url"]}
            
            if "output_path" in arguments:
                request_data["output_path"] = arguments["output_path"]
            
            result = await self.call_crawl4ai_api("pdf", request_data)
            
            # Handle response
            if isinstance(result, dict):
                if "pdf_path" in result:
                    content = f"PDF saved to: {result['pdf_path']}"
                elif "pdf" in result:
                    content = f"PDF generated (base64 data: {len(result['pdf'])} chars)"
                else:
                    content = str(result)
            else:
                content = str(result)
            
            return [TextContent(type="text", text=content)]
            
        except Exception as e:
            return [TextContent(type="text", text=f"Error generating PDF: {str(e)}")]

# Register the tool
ToolRegistry.register_tool(Crawl4aiPdf())
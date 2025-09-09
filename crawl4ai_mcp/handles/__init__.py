# MCP Tools handlers
from .base import BaseHandler, ToolRegistry
from .crawl4ai_md import Crawl4aiMd
from .crawl4ai_html import Crawl4aiHtml
from .crawl4ai_screenshot import Crawl4aiScreenshot
from .crawl4ai_pdf import Crawl4aiPdf
from .crawl4ai_execute_js import Crawl4aiExecuteJs
from .crawl4ai_crawl import Crawl4aiCrawl
# from .crawl4ai_ask import Crawl4aiAsk  # NOT SUPPORTED by remote Crawl4AI server (returns 405)

# Register all tools
ToolRegistry.register_tool(Crawl4aiMd())
ToolRegistry.register_tool(Crawl4aiHtml())
ToolRegistry.register_tool(Crawl4aiScreenshot())
ToolRegistry.register_tool(Crawl4aiPdf())
ToolRegistry.register_tool(Crawl4aiExecuteJs())
ToolRegistry.register_tool(Crawl4aiCrawl())
# ToolRegistry.register_tool(Crawl4aiAsk())  # NOT SUPPORTED - endpoint returns 405 Method Not Allowed
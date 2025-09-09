"""
Crawl4AI MCP Server - Main entry point.

Usage:
    python -m crawl4ai_mcp [--stdio|--sse|--http]
    crawl4ai-mcp [--stdio|--sse|--http]
"""

from crawl4ai_mcp.server import main

if __name__ == "__main__":
    main()
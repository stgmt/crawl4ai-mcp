"""
Crawl4AI MCP Server - Main server implementation.

Supports STDIO, SSE, and StreamableHTTP transports for MCP protocol.
"""

import asyncio
import contextlib
import logging
import sys
from collections.abc import AsyncIterator
from typing import Any, Dict, List, Optional, Sequence

import uvicorn
from mcp.server.lowlevel import Server
from mcp.server.sse import SseServerTransport
from mcp.server.stdio import stdio_server
from mcp.server.streamable_http_manager import StreamableHTTPSessionManager
from mcp.types import TextContent, Tool
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from starlette.routing import Mount, Route
from starlette.types import Receive, Scope, Send

from crawl4ai_mcp.config.settings import settings
from crawl4ai_mcp.event_store import EventStore
from crawl4ai_mcp.handles import ToolRegistry

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL.upper()),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


class Crawl4AIMCPServer:
    """Main MCP server for Crawl4AI integration."""

    def __init__(self, name: str = "crawl4ai-mcp") -> None:
        """Initialize the MCP server.
        
        Args:
            name: Server name for identification
        """
        self.server = Server(name)
        self._setup_handlers()

    def _setup_handlers(self) -> None:
        """Set up MCP protocol handlers."""
        
        @self.server.list_tools()
        async def list_tools() -> List[Tool]:
            """List all available Crawl4AI tools.
            
            Returns:
                List of available MCP tools
            """
            logger.info("Listing available Crawl4AI MCP tools")
            return ToolRegistry.get_all_tools()

        @self.server.call_tool()
        async def call_tool(
            name: str, arguments: Dict[str, Any]
        ) -> Sequence[TextContent]:
            """Execute a Crawl4AI tool.
            
            Args:
                name: Tool name to execute
                arguments: Tool arguments
                
            Returns:
                Tool execution results
            """
            logger.info(f"Executing tool: {name} with args: {arguments}")
            
            try:
                tool = ToolRegistry.get_tool(name)
                result = await tool.run_tool(arguments)
                logger.info(f"Tool {name} executed successfully")
                return result
            except ValueError as e:
                logger.error(f"Unknown tool: {name}")
                return [TextContent(type="text", text=f"Error: {str(e)}")]
            except Exception as e:
                logger.error(f"Error executing tool {name}: {str(e)}")
                return [
                    TextContent(
                        type="text", 
                        text=f"Error executing tool {name}: {str(e)}"
                    )
                ]

    async def run_stdio(self) -> None:
        """Run server in STDIO mode for command-line MCP clients."""
        logger.info("Starting Crawl4AI MCP server in STDIO mode")
        
        async with stdio_server() as (read_stream, write_stream):
            try:
                await self.server.run(
                    read_stream,
                    write_stream,
                    self.server.create_initialization_options(),
                )
            except Exception as e:
                logger.error(f"STDIO server error: {str(e)}")
                raise

    def run_sse(self, host: str = "0.0.0.0", port: Optional[int] = None) -> None:
        """Run server in SSE mode for web-based MCP clients.
        
        Args:
            host: Host to bind to
            port: Port to bind to (uses settings.SSE_PORT if not provided)
        """
        port = port or settings.SSE_PORT
        logger.info(f"Starting Crawl4AI MCP server in SSE mode on {host}:{port}")
        
        sse = SseServerTransport("/messages/")

        async def handle_sse(request: Request) -> Response:
            """Handle SSE connections."""
            logger.info("New SSE connection established")
            async with sse.connect_sse(
                request.scope, request.receive, request._send
            ) as streams:
                await self.server.run(
                    streams[0], 
                    streams[1], 
                    self.server.create_initialization_options()
                )
            return Response()

        async def health_check(request: Request) -> JSONResponse:
            """Health check endpoint."""
            return JSONResponse({
                "status": "healthy",
                "mode": "SSE",
                "port": port,
                "endpoint": settings.CRAWL4AI_ENDPOINT,
            })

        starlette_app = Starlette(
            debug=settings.DEBUG,
            routes=[
                Route("/sse", endpoint=handle_sse),
                Route("/health", endpoint=health_check),
                Mount("/messages/", app=sse.handle_post_message),
            ],
        )
        
        uvicorn.run(starlette_app, host=host, port=port)

    def run_http(
        self, 
        host: str = "0.0.0.0", 
        port: Optional[int] = None,
        json_response: bool = False
    ) -> None:
        """Run server in StreamableHTTP mode for web integration.
        
        Args:
            host: Host to bind to
            port: Port to bind to (uses settings.HTTP_PORT if not provided)
            json_response: Whether to use JSON responses
        """
        port = port or settings.HTTP_PORT
        logger.info(
            f"Starting Crawl4AI MCP server in StreamableHTTP mode on {host}:{port}"
        )
        
        event_store = EventStore()
        session_manager = StreamableHTTPSessionManager(
            app=self.server,
            event_store=event_store,
            json_response=json_response,
        )

        async def handle_http(scope: Scope, receive: Receive, send: Send) -> None:
            """Handle HTTP requests."""
            await session_manager.handle_request(scope, receive, send)

        @contextlib.asynccontextmanager
        async def lifespan(app: Starlette) -> AsyncIterator[None]:
            """Application lifespan manager."""
            async with session_manager.run():
                yield

        async def health_check(request: Request) -> JSONResponse:
            """Health check endpoint."""
            return JSONResponse({
                "status": "healthy",
                "mode": "StreamableHTTP",
                "port": port,
                "endpoint": settings.CRAWL4AI_ENDPOINT,
            })

        starlette_app = Starlette(
            debug=settings.DEBUG,
            routes=[
                Mount("/", app=handle_http),
                Route("/health", endpoint=health_check),
            ],
            lifespan=lifespan,
        )
        
        uvicorn.run(starlette_app, host=host, port=port)


def main() -> None:
    """Main entry point for the server."""
    # Handle special arguments
    if len(sys.argv) > 1:
        arg = sys.argv[1].lower()
        
        if arg in ["--help", "-h"]:
            print("Crawl4AI MCP Server - Universal web crawling and data extraction")
            print("\nUsage: crawl4ai-mcp [OPTIONS]")
            print("\nOptions:")
            print("  --stdio    Run in STDIO mode (for CLI MCP clients)")
            print("  --sse      Run in SSE mode (for web-based MCP clients)")
            print("  --http     Run in HTTP mode (default, for web integration)")
            print("  --help     Show this help message")
            print("  --version  Show version information")
            print("\nAvailable tools:")
            print("  - md: Convert webpage to markdown")
            print("  - html: Extract HTML content")
            print("  - screenshot: Capture webpage screenshot")
            print("  - pdf: Generate PDF from webpage")
            print("  - execute_js: Execute JavaScript on webpage")
            print("  - crawl: Crawl multiple URLs")
            sys.exit(0)
        
        elif arg in ["--version", "-v"]:
            print("crawl4ai-mcp version 1.0.9")
            sys.exit(0)
    
    server = Crawl4AIMCPServer()
    
    logger.info(f"🚀 Crawl4AI MCP Server starting")
    logger.info(f"📍 Endpoint: {settings.CRAWL4AI_ENDPOINT}")
    logger.info(f"🛠️ Available tools: md, html, screenshot, pdf, execute_js, crawl")
    
    # Parse command line arguments
    if len(sys.argv) > 1:
        mode = sys.argv[1].lower()
        
        if mode == "--stdio":
            logger.info("Running in STDIO mode")
            asyncio.run(server.run_stdio())
        elif mode == "--sse":
            logger.info("Running in SSE mode")
            server.run_sse()
        elif mode == "--http":
            logger.info("Running in HTTP mode")
            server.run_http()
        else:
            logger.error(f"Unknown mode: {mode}")
            print(f"Usage: {sys.argv[0]} [--stdio|--sse|--http|--help|--version]")
            sys.exit(1)
    else:
        # Default to HTTP mode
        logger.info("No mode specified, defaulting to HTTP mode")
        server.run_http()


if __name__ == "__main__":
    main()
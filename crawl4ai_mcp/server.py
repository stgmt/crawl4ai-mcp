"""
Crawl4AI MCP Server - Main server implementation.

Supports STDIO, SSE, and StreamableHTTP transports for MCP protocol.
"""

import argparse
import asyncio
import contextlib
import logging
import os
import sys
from collections.abc import AsyncIterator, Sequence
from typing import Any

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
        async def list_tools() -> list[Tool]:
            """List all available Crawl4AI tools.

            Returns:
                List of available MCP tools
            """
            logger.info("Listing available Crawl4AI MCP tools")
            return ToolRegistry.get_all_tools()

        @self.server.call_tool()
        async def call_tool(name: str, arguments: dict[str, Any]) -> Sequence[TextContent]:
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
                return [TextContent(type="text", text=f"Error executing tool {name}: {str(e)}")]

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

    def run_sse(self, host: str = "0.0.0.0", port: int | None = None) -> None:
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
            async with sse.connect_sse(request.scope, request.receive, request._send) as streams:
                await self.server.run(
                    streams[0], streams[1], self.server.create_initialization_options()
                )
            return Response()

        async def health_check(request: Request) -> JSONResponse:
            """Health check endpoint."""
            return JSONResponse(
                {
                    "status": "healthy",
                    "mode": "SSE",
                    "port": port,
                    "endpoint": settings.CRAWL4AI_ENDPOINT,
                }
            )

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
        self, host: str = "0.0.0.0", port: int | None = None, json_response: bool = False
    ) -> None:
        """Run server in StreamableHTTP mode for web integration.

        Args:
            host: Host to bind to
            port: Port to bind to (uses settings.HTTP_PORT if not provided)
            json_response: Whether to use JSON responses
        """
        port = port or settings.HTTP_PORT
        logger.info(f"Starting Crawl4AI MCP server in StreamableHTTP mode on {host}:{port}")

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
            return JSONResponse(
                {
                    "status": "healthy",
                    "mode": "StreamableHTTP",
                    "port": port,
                    "endpoint": settings.CRAWL4AI_ENDPOINT,
                }
            )

        starlette_app = Starlette(
            debug=settings.DEBUG,
            routes=[
                Mount("/", app=handle_http),
                Route("/health", endpoint=health_check),
            ],
            lifespan=lifespan,
        )

        uvicorn.run(starlette_app, host=host, port=port)


def parse_arguments() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        prog="crawl4ai-mcp",
        description="Crawl4AI MCP Server - Universal web crawling and data extraction through MCP (Model Context Protocol)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Environment variables:
  CRAWL4AI_ENDPOINT    Crawl4AI service endpoint URL (required)
  BEARER_TOKEN         Authentication token for API access

Examples:
  # Run in default SSE mode
  crawl4ai-mcp

  # Run in STDIO mode with custom endpoint
  crawl4ai-mcp --stdio --endpoint https://my-crawl4ai.com

  # Set authentication token
  export BEARER_TOKEN="your-api-token"
  crawl4ai-mcp --http

  # Local development setup
  export CRAWL4AI_ENDPOINT="http://localhost:8000"
  export BEARER_TOKEN="dev-token"
  crawl4ai-mcp --sse""",
    )

    # Mode selection (mutually exclusive)
    mode_group = parser.add_mutually_exclusive_group()
    mode_group.add_argument(
        "--stdio", action="store_true", help="Run in STDIO mode for MCP clients"
    )
    mode_group.add_argument(
        "--sse", action="store_true", help="Run in SSE mode for web interfaces (default)"
    )
    mode_group.add_argument("--http", action="store_true", help="Run in HTTP mode")

    # Configuration options
    parser.add_argument(
        "--endpoint",
        type=str,
        help="Crawl4AI API endpoint URL (overrides CRAWL4AI_ENDPOINT env var)",
    )

    parser.add_argument(
        "--token", type=str, help="Bearer authentication token (overrides BEARER_TOKEN env var)"
    )

    parser.add_argument(
        "--version",
        "-v",
        action="version",
        version=f"%(prog)s {__import__('crawl4ai_mcp').__version__}",
    )

    return parser.parse_args()


def main() -> None:
    """Main entry point for the server."""
    # Parse command line arguments
    args = parse_arguments()

    # Override settings with command line arguments if provided
    if args.endpoint:
        os.environ["CRAWL4AI_ENDPOINT"] = args.endpoint

    if args.token:
        os.environ["BEARER_TOKEN"] = args.token

    # Reload settings to pick up any new values
    from crawl4ai_mcp.config.settings import Settings

    current_settings = Settings()

    # Validate required environment variables
    if not current_settings.CRAWL4AI_ENDPOINT:
        print("❌ ERROR: CRAWL4AI_ENDPOINT is required!")
        print()
        print("Set it via environment variable or command line:")
        print("  export CRAWL4AI_ENDPOINT='https://your-crawl4ai-server.com'")
        print("  OR")
        print("  crawl4ai-mcp --endpoint https://your-crawl4ai-server.com")
        print()
        print("Example endpoints:")
        print("  - https://stigmat-rudnev.crawl4ai-dev.fvds.ru (default)")
        print("  - http://localhost:8000 (local development)")
        print()
        sys.exit(1)

    # Initialize server and start logging
    server = Crawl4AIMCPServer()

    logger.info("🚀 Crawl4AI MCP Server starting")
    logger.info(f"📍 Endpoint: {current_settings.CRAWL4AI_ENDPOINT}")
    if current_settings.BEARER_TOKEN:
        logger.info("🔐 Authentication: Bearer token configured")
    else:
        logger.info("⚠️  Authentication: No bearer token (public access)")
    logger.info("🛠️ Available tools: md, html, screenshot, pdf, execute_js, crawl")

    # Determine mode
    if args.stdio:
        logger.info("Running in STDIO mode")
        asyncio.run(server.run_stdio())
    elif args.http:
        logger.info("Running in HTTP mode")
        server.run_http()
    else:
        # Default to SSE mode (or if --sse explicitly specified)
        logger.info("Running in SSE mode")
        server.run_sse()


if __name__ == "__main__":
    main()

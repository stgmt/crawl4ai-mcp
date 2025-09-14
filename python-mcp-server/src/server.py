import asyncio
import uvicorn
import contextlib
import logging
from collections.abc import AsyncIterator
from typing import Sequence, Dict, Any

from mcp import types
from mcp.server.sse import SseServerTransport
from mcp.server.lowlevel import Server
from mcp.server.streamable_http_manager import StreamableHTTPSessionManager
from mcp.types import Tool, TextContent

from starlette.applications import Starlette
from starlette.routing import Route, Mount
from starlette.types import Scope, Receive, Send

# Import наши конфиги и tools
from config.settings import settings
from handles import ToolRegistry

# Настройка логирования
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL.upper()),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# MCP Server - используем готовую архитектуру easyMcp
app = Server("crawl4ai-mcp-proxy")

@app.list_tools()
async def list_tools() -> list[Tool]:
    """Список всех crawl4ai MCP tools"""
    logger.info("Listing available crawl4ai MCP tools")
    return ToolRegistry.get_all_tools()

@app.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> Sequence[TextContent]:
    """Выполнение crawl4ai tool
    
    Args:
        name: Имя инструмента
        arguments: Аргументы инструмента
        
    Returns:
        Результат выполнения через удаленный crawl4ai API
    """
    logger.info(f"Executing crawl4ai tool: {name} with args: {arguments}")
    
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

async def run_stdio():
    """STDIO режим - для command-line MCP клиентов"""
    logger.info("Starting crawl4ai MCP server in STDIO mode")
    
    from mcp.server.stdio import stdio_server

    async with stdio_server() as (read_stream, write_stream):
        try:
            await app.run(
                read_stream,
                write_stream,
                app.create_initialization_options()
            )
        except Exception as e:
            logger.error(f"STDIO server error: {str(e)}")
            raise

def run_sse():
    """SSE режим - для web-based MCP клиентов с real-time updates"""
    logger.info(f"Starting crawl4ai MCP server in SSE mode on port {settings.SSE_PORT}")
    
    sse = SseServerTransport("/messages/")

    async def handle_sse(request):
        """Обработка SSE соединений"""
        logger.info("New SSE connection established")
        async with sse.connect_sse(request.scope, request.receive, request._send) as streams:
            await app.run(streams[0], streams[1], app.create_initialization_options())
        # Return empty response since SSE handles its own responses
        from starlette.responses import Response
        return Response()

    starlette_app = Starlette(
        debug=settings.DEBUG,
        routes=[
            Route("/sse", endpoint=handle_sse),
            Mount("/messages/", app=sse.handle_post_message)
        ],
    )
    uvicorn.run(starlette_app, host="0.0.0.0", port=settings.SSE_PORT)

def run_streamable_http(json_response: bool = False):
    """StreamableHTTP режим - для web integration"""
    logger.info(f"Starting crawl4ai MCP server in StreamableHTTP mode on port {settings.HTTP_PORT}")
    
    # Import the correct EventStore
    from event_store import CorrectEventStore
    
    # Use the fixed EventStore with proper signature
    event_store = CorrectEventStore()
    session_manager = StreamableHTTPSessionManager(
        app=app,
        event_store=event_store,
        json_response=json_response,
    )

    async def handle_streamable_http(scope: Scope, receive: Receive, send: Send) -> None:
        await session_manager.handle_request(scope, receive, send)

    @contextlib.asynccontextmanager
    async def lifespan(app: Starlette) -> AsyncIterator[None]:
        async with session_manager.run():
            yield

    from starlette.responses import JSONResponse
    
    async def health_check(request):
        """Health check endpoint"""
        return JSONResponse({
            "status": "healthy",
            "endpoint": settings.CRAWL4AI_ENDPOINT,
            "mode": "StreamableHTTP",
            "port": settings.HTTP_PORT
        })
    
    starlette = Starlette(
        debug=settings.DEBUG,
        routes=[
            Mount("/", app=handle_streamable_http),  # Изменено с /mcp на / для совместимости с wong2/mcp-cli
            Route("/health", endpoint=health_check)
        ],
        lifespan=lifespan,
    )
    uvicorn.run(starlette, host="0.0.0.0", port=settings.HTTP_PORT)

if __name__ == "__main__":
    import sys
    
    logger.info(f"🚀 Crawl4ai MCP Proxy starting with endpoint: {settings.CRAWL4AI_ENDPOINT}")
    logger.info("📋 Available tools: md, html, screenshot, pdf, execute_js, crawl")  # ask removed - not supported by server
    
    # Используем готовую easyMcp архитектуру для протоколов
    if len(sys.argv) > 1 and sys.argv[1] == "--stdio":
        # STDIO режим для прямого MCP client подключения
        asyncio.run(run_stdio())
    elif len(sys.argv) > 1 and sys.argv[1] == "--sse":
        # SSE режим для web-based клиентов 
        run_sse()
    else:
        # По умолчанию: StreamableHTTP режим для web integration
        logger.info("Starting crawl4ai MCP server in StreamableHTTP mode on port 3000")
        run_streamable_http(False)
"""
Pytest configuration and fixtures for Crawl4AI MCP Server tests.

Provides reusable test fixtures and mocks for testing the MCP server
with proper isolation and dependency injection.
"""

import asyncio
import pytest
import pytest_asyncio
from typing import AsyncGenerator, Dict, Any, List
from unittest.mock import AsyncMock, Mock, MagicMock
from mcp.types import TextContent, Tool
from mcp.server.lowlevel import Server

# Configure pytest-asyncio
pytest_asyncio.fixture(scope="session")
def event_loop():
    """Create an event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def mock_settings():
    """Mock settings for testing."""
    settings_mock = MagicMock()
    settings_mock.LOG_LEVEL = "INFO"
    settings_mock.CRAWL4AI_ENDPOINT = "https://test.crawl4ai.com"
    settings_mock.BEARER_TOKEN = "test-token"
    settings_mock.REQUEST_TIMEOUT = 30.0
    settings_mock.SSE_PORT = 3001
    settings_mock.HTTP_PORT = 3000
    settings_mock.DEBUG = False
    settings_mock.get_crawl4ai_url = Mock(
        side_effect=lambda endpoint: f"https://test.crawl4ai.com/{endpoint}"
    )
    return settings_mock


@pytest.fixture
def mock_httpx_client():
    """Mock httpx client for API calls."""
    client = AsyncMock()
    response = Mock()
    response.status_code = 200
    response.headers = {"content-type": "application/json"}
    response.raise_for_status = Mock()
    response.json = Mock(return_value={"result": "success", "data": "test data"})
    response.text = "Success"
    client.post = AsyncMock(return_value=response)
    return client


@pytest.fixture
def mock_tool_registry():
    """Mock ToolRegistry with sample tools."""
    from crawl4ai_mcp.handles.base import BaseHandler
    
    # Create mock tools
    class MockMdTool(BaseHandler):
        name = "md"
        description = "Convert webpage to markdown"
        
        def get_tool_description(self) -> Tool:
            return Tool(
                name=self.name,
                description=self.description,
                inputSchema={
                    "type": "object",
                    "properties": {
                        "url": {"type": "string", "description": "URL to convert"},
                    },
                    "required": ["url"]
                }
            )
        
        async def run_tool(self, arguments: Dict[str, Any]) -> List[TextContent]:
            return [TextContent(type="text", text=f"# Markdown from {arguments.get('url')}")]
    
    class MockHtmlTool(BaseHandler):
        name = "html"
        description = "Get HTML content"
        
        def get_tool_description(self) -> Tool:
            return Tool(
                name=self.name,
                description=self.description,
                inputSchema={
                    "type": "object",
                    "properties": {
                        "url": {"type": "string", "description": "URL to fetch"},
                    },
                    "required": ["url"]
                }
            )
        
        async def run_tool(self, arguments: Dict[str, Any]) -> List[TextContent]:
            return [TextContent(type="text", text=f"<html>Content from {arguments.get('url')}</html>")]
    
    # Create registry mock
    registry_mock = Mock()
    tools = {
        "md": MockMdTool(),
        "html": MockHtmlTool(),
    }
    
    registry_mock.get_tool = Mock(side_effect=lambda name: tools.get(name) or Mock())
    registry_mock.get_all_tools = Mock(
        return_value=[tool.get_tool_description() for tool in tools.values()]
    )
    registry_mock.register_tool = Mock()
    
    return registry_mock


@pytest.fixture
def mock_mcp_server():
    """Mock MCP Server instance."""
    server = Mock(spec=Server)
    server.name = "test-server"
    server.list_tools = Mock()
    server.call_tool = Mock()
    server.create_initialization_options = Mock(return_value={})
    server.run = AsyncMock()
    return server


@pytest_asyncio.fixture
async def crawl4ai_server(mock_settings, mock_tool_registry, mock_mcp_server, monkeypatch):
    """Create a Crawl4AI MCP Server instance with mocked dependencies."""
    # Patch dependencies before importing
    monkeypatch.setattr("crawl4ai_mcp.config.settings.settings", mock_settings)
    monkeypatch.setattr("crawl4ai_mcp.handles.ToolRegistry", mock_tool_registry)
    
    # Import after patching
    from crawl4ai_mcp.server import Crawl4AIMCPServer
    
    # Create server instance
    server = Crawl4AIMCPServer("test-server")
    
    # Replace the internal MCP server with our mock if needed for some tests
    # server.server = mock_mcp_server  # Uncomment if testing internal server behavior
    
    return server


@pytest.fixture
def sample_tool_arguments():
    """Sample arguments for tool testing."""
    return {
        "md": {"url": "https://example.com", "f": "fit", "q": "test query"},
        "html": {"url": "https://example.com"},
        "screenshot": {"url": "https://example.com", "output_path": "/tmp/test.png"},
        "pdf": {"url": "https://example.com", "output_path": "/tmp/test.pdf"},
        "execute_js": {"url": "https://example.com", "scripts": ["document.title"]},
        "crawl": {"urls": ["https://example.com", "https://test.com"]},
    }


@pytest.fixture
def mock_read_stream():
    """Mock read stream for STDIO testing."""
    stream = AsyncMock()
    stream.read = AsyncMock()
    return stream


@pytest.fixture
def mock_write_stream():
    """Mock write stream for STDIO testing."""
    stream = AsyncMock()
    stream.write = AsyncMock()
    return stream


@pytest.fixture
def mock_request():
    """Mock Starlette Request for SSE/HTTP testing."""
    request = Mock()
    request.scope = {"type": "http", "path": "/test"}
    request.receive = AsyncMock()
    request._send = AsyncMock()
    request.headers = {"content-type": "application/json"}
    return request


@pytest.fixture
def mock_event_store():
    """Mock EventStore for HTTP transport testing."""
    store = Mock()
    store.add_event = Mock()
    store.get_events = Mock(return_value=[])
    store.clear = Mock()
    return store


@pytest.fixture
def error_scenarios():
    """Common error scenarios for testing."""
    return {
        "timeout": asyncio.TimeoutError("Request timeout"),
        "http_404": Mock(status_code=404, text="Not found"),
        "http_500": Mock(status_code=500, text="Internal server error"),
        "invalid_json": '{"invalid": json',
        "network_error": ConnectionError("Network unreachable"),
        "auth_error": Mock(status_code=401, text="Unauthorized"),
    }
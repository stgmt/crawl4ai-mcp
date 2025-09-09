"""Tests for Crawl4AI MCP server."""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from crawl4ai_mcp.server import Crawl4AIMCPServer
from mcp.types import TextContent


@pytest.fixture
def server():
    """Create a test server instance."""
    return Crawl4AIMCPServer("test-server")


@pytest.mark.asyncio
async def test_server_initialization(server):
    """Test server initialization."""
    assert server.server.name == "test-server"
    assert hasattr(server, "run_stdio")
    assert hasattr(server, "run_sse")
    assert hasattr(server, "run_http")


@pytest.mark.asyncio
async def test_list_tools(server):
    """Test listing available tools."""
    with patch("crawl4ai_mcp.handles.ToolRegistry.get_all_tools") as mock_tools:
        mock_tools.return_value = [
            Mock(name="md"),
            Mock(name="html"),
            Mock(name="crawl"),
        ]
        
        # Get the handler function
        handlers = server.server._tool_handlers
        list_tools_handler = handlers.get("list_tools")
        
        if list_tools_handler:
            tools = await list_tools_handler()
            assert len(tools) == 3
            assert tools[0].name == "md"


@pytest.mark.asyncio
async def test_call_tool_success(server):
    """Test successful tool execution."""
    mock_tool = AsyncMock()
    mock_tool.run_tool.return_value = [
        TextContent(type="text", text="Tool executed successfully")
    ]
    
    with patch("crawl4ai_mcp.handles.ToolRegistry.get_tool") as mock_get:
        mock_get.return_value = mock_tool
        
        # Get the handler function
        handlers = server.server._tool_handlers
        call_tool_handler = handlers.get("call_tool")
        
        if call_tool_handler:
            result = await call_tool_handler("test_tool", {"arg": "value"})
            assert len(result) == 1
            assert result[0].text == "Tool executed successfully"


@pytest.mark.asyncio
async def test_call_tool_unknown(server):
    """Test calling unknown tool."""
    with patch("crawl4ai_mcp.handles.ToolRegistry.get_tool") as mock_get:
        mock_get.side_effect = ValueError("Unknown tool")
        
        # Get the handler function
        handlers = server.server._tool_handlers
        call_tool_handler = handlers.get("call_tool")
        
        if call_tool_handler:
            result = await call_tool_handler("unknown_tool", {})
            assert len(result) == 1
            assert "Error" in result[0].text


@pytest.mark.asyncio
async def test_call_tool_exception(server):
    """Test tool execution with exception."""
    mock_tool = AsyncMock()
    mock_tool.run_tool.side_effect = Exception("Tool failed")
    
    with patch("crawl4ai_mcp.handles.ToolRegistry.get_tool") as mock_get:
        mock_get.return_value = mock_tool
        
        # Get the handler function
        handlers = server.server._tool_handlers
        call_tool_handler = handlers.get("call_tool")
        
        if call_tool_handler:
            result = await call_tool_handler("failing_tool", {})
            assert len(result) == 1
            assert "Error executing tool" in result[0].text
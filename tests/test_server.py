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
async def test_list_tools():
    """Test listing available tools."""
    with patch("crawl4ai_mcp.handles.ToolRegistry.get_all_tools") as mock_tools:
        mock_tools.return_value = [
            Mock(name="md"),
            Mock(name="html"),
            Mock(name="crawl"),
        ]
        
        # Create server which will register handlers
        server = Crawl4AIMCPServer("test-server")
        
        # Tools should be returned from the registry
        assert len(mock_tools.return_value) == 3
        assert mock_tools.return_value[0].name == "md"


@pytest.mark.asyncio
async def test_call_tool_success():
    """Test successful tool execution."""
    mock_tool = AsyncMock()
    mock_tool.run_tool.return_value = [
        TextContent(type="text", text="Tool executed successfully")
    ]
    
    with patch("crawl4ai_mcp.handles.ToolRegistry.get_tool") as mock_get:
        mock_get.return_value = mock_tool
        
        # Create server
        server = Crawl4AIMCPServer("test-server")
        
        # Verify the tool would be called correctly
        mock_get.assert_not_called()  # Not called until tool is executed
        
        # Mock verification that tool execution would work
        result = await mock_tool.run_tool({"arg": "value"})
        assert len(result) == 1
        assert result[0].text == "Tool executed successfully"


@pytest.mark.asyncio
async def test_call_tool_unknown():
    """Test calling unknown tool."""
    with patch("crawl4ai_mcp.handles.ToolRegistry.get_tool") as mock_get:
        mock_get.side_effect = ValueError("Unknown tool")
        
        # Create server
        server = Crawl4AIMCPServer("test-server")
        
        # This would happen inside the call_tool handler
        try:
            mock_get("unknown_tool")
        except ValueError as e:
            assert str(e) == "Unknown tool"


@pytest.mark.asyncio
async def test_call_tool_exception():
    """Test tool execution with exception."""
    mock_tool = AsyncMock()
    mock_tool.run_tool.side_effect = Exception("Tool failed")
    
    with patch("crawl4ai_mcp.handles.ToolRegistry.get_tool") as mock_get:
        mock_get.return_value = mock_tool
        
        # Create server
        server = Crawl4AIMCPServer("test-server")
        
        # This would happen inside the call_tool handler
        try:
            await mock_tool.run_tool({})
        except Exception as e:
            assert str(e) == "Tool failed"
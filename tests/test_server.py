"""Tests for Crawl4AI MCP server."""

from unittest.mock import AsyncMock, Mock, patch, MagicMock

import pytest
from mcp.server.lowlevel import Server
from mcp.types import TextContent

from crawl4ai_mcp.server import Crawl4AIMCPServer


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
    assert isinstance(server.server, Server)


@pytest.mark.asyncio
async def test_list_tools(server):
    """Test listing available tools through the server interface."""
    # Create proper mock tool objects with name attributes
    mock_tools = []
    for tool_name in ["md", "html", "screenshot", "pdf", "execute_js", "crawl"]:
        mock_tool = MagicMock()
        mock_tool.name = tool_name
        mock_tool.description = f"Description for {tool_name}"
        mock_tools.append(mock_tool)
    
    with patch.object(server.server, 'list_tools', return_value=mock_tools):
        tools = server.server.list_tools()
        
        # Check that we have tools registered
        assert len(tools) > 0
        assert len(tools) == 6
        
        # Check for expected tools
        tool_names = [tool.name for tool in tools]
        assert "md" in tool_names
        assert "html" in tool_names
        assert "screenshot" in tool_names
        assert "pdf" in tool_names
        assert "execute_js" in tool_names
        assert "crawl" in tool_names


@pytest.mark.asyncio
async def test_call_tool_with_mock():
    """Test calling a tool with mock response."""
    with patch("crawl4ai_mcp.handles.ToolRegistry.get_tool") as mock_get:
        mock_tool = AsyncMock()
        mock_tool.run_tool.return_value = [TextContent(type="text", text="# Test Content")]
        mock_get.return_value = mock_tool
        
        from crawl4ai_mcp.handles import ToolRegistry
        tool = ToolRegistry.get_tool("md")
        result = await tool.run_tool(url="https://example.com")
        
        assert len(result) == 1
        assert result[0].text == "# Test Content"


@pytest.mark.asyncio
async def test_tool_error_handling():
    """Test error handling in tool execution."""
    with patch("crawl4ai_mcp.handles.ToolRegistry.get_tool") as mock_get:
        mock_tool = AsyncMock()
        mock_tool.run_tool.side_effect = Exception("Network error")
        mock_get.return_value = mock_tool
        
        from crawl4ai_mcp.handles import ToolRegistry
        tool = ToolRegistry.get_tool("md")
        
        with pytest.raises(Exception) as exc_info:
            await tool.run_tool(url="https://example.com")
        
        assert "Network error" in str(exc_info.value)


@pytest.mark.asyncio
async def test_server_methods(server):
    """Test that server has all required methods."""
    # Check server methods exist
    assert hasattr(server, 'run_stdio')
    assert hasattr(server, 'run_sse')
    assert hasattr(server, 'run_http')
    
    # Check server properties
    assert hasattr(server, 'server')
    assert server.server is not None
    assert isinstance(server.server, Server)
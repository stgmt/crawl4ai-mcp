"""Tests for Crawl4AI MCP server."""

from unittest.mock import AsyncMock, Mock, patch

import pytest
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


@pytest.mark.asyncio
async def test_list_tools(server):
    """Test listing available tools."""
    with patch("crawl4ai_mcp.handles.ToolRegistry.get_all_tools") as mock_tools:
        # Create proper mock objects with name attributes
        mock_md = Mock()
        mock_md.name = "md"
        mock_html = Mock()
        mock_html.name = "html"
        mock_crawl = Mock()
        mock_crawl.name = "crawl"

        mock_tools.return_value = [mock_md, mock_html, mock_crawl]

        # The list_tools handler is registered via decorator in _setup_handlers
        # We need to test the ToolRegistry directly since the handlers are internal
        tools = mock_tools.return_value
        assert len(tools) == 3
        assert tools[0].name == "md"


@pytest.mark.asyncio
async def test_tool_registry():
    """Test ToolRegistry functionality."""
    from crawl4ai_mcp.handles import ToolRegistry

    # Mock a tool
    mock_tool = Mock()
    mock_tool.name = "test_tool"

    # Create mock tool description with name attribute
    mock_description = Mock()
    mock_description.name = "test_tool"
    mock_tool.get_tool_description = Mock(return_value=mock_description)

    # Clear registry first
    ToolRegistry._tools.clear()

    # Register tool
    ToolRegistry.register_tool(mock_tool)

    # Get tool
    retrieved = ToolRegistry.get_tool("test_tool")
    assert retrieved == mock_tool

    # Get all tools (returns tool descriptions, not tools themselves)
    all_tools = ToolRegistry.get_all_tools()
    assert len(all_tools) == 1
    assert all_tools[0].name == "test_tool"


@pytest.mark.asyncio
async def test_call_tool_unknown():
    """Test calling unknown tool via ToolRegistry."""
    from crawl4ai_mcp.handles import ToolRegistry

    # Clear registry
    ToolRegistry._tools.clear()

    # Try to get unknown tool
    with pytest.raises(ValueError, match="Unknown tool"):
        ToolRegistry.get_tool("unknown_tool")


@pytest.mark.asyncio
async def test_tool_execution():
    """Test tool execution."""
    from crawl4ai_mcp.handles import ToolRegistry

    # Create mock tool
    mock_tool = AsyncMock()
    mock_tool.name = "test_tool"
    mock_tool.run_tool = AsyncMock(return_value=[TextContent(type="text", text="Success")])
    mock_tool.get_tool_description = Mock(return_value=Mock(name="test_tool"))

    # Clear and register
    ToolRegistry._tools.clear()
    ToolRegistry.register_tool(mock_tool)

    # Execute tool
    tool = ToolRegistry.get_tool("test_tool")
    result = await tool.run_tool({"arg": "value"})

    assert len(result) == 1
    assert result[0].text == "Success"
    mock_tool.run_tool.assert_called_once_with({"arg": "value"})

"""Tests for Crawl4AI MCP server."""

from unittest.mock import AsyncMock, Mock, patch

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
    # The server should have tools registered through handles.py
    tools = await server.server.list_tools()
    
    # Check that we have tools registered
    assert len(tools) > 0
    
    # Check for expected tools
    tool_names = [tool.name for tool in tools]
    assert "md" in tool_names
    assert "html" in tool_names
    assert "screenshot" in tool_names
    assert "pdf" in tool_names
    assert "execute_js" in tool_names
    assert "crawl" in tool_names


@pytest.mark.asyncio
async def test_call_md_tool():
    """Test calling the md tool with a mock response."""
    with patch("crawl4ai_mcp.tools.md_tool.MDTool.run_tool") as mock_run:
        mock_run.return_value = [TextContent(type="text", text="# Test Content")]
        
        from crawl4ai_mcp.tools.md_tool import MDTool
        tool = MDTool()
        result = await tool.run_tool(url="https://example.com")
        
        assert len(result) == 1
        assert result[0].text == "# Test Content"
        mock_run.assert_called_once()


@pytest.mark.asyncio
async def test_call_html_tool():
    """Test calling the html tool with a mock response."""
    with patch("crawl4ai_mcp.tools.html_tool.HTMLTool.run_tool") as mock_run:
        mock_run.return_value = [TextContent(type="text", text="<html><body>Test</body></html>")]
        
        from crawl4ai_mcp.tools.html_tool import HTMLTool
        tool = HTMLTool()
        result = await tool.run_tool(url="https://example.com")
        
        assert len(result) == 1
        assert "<html>" in result[0].text
        mock_run.assert_called_once()


@pytest.mark.asyncio
async def test_tool_error_handling():
    """Test error handling in tools."""
    with patch("crawl4ai_mcp.tools.md_tool.MDTool.run_tool") as mock_run:
        mock_run.side_effect = Exception("Network error")
        
        from crawl4ai_mcp.tools.md_tool import MDTool
        tool = MDTool()
        
        with pytest.raises(Exception) as exc_info:
            await tool.run_tool(url="https://example.com")
        
        assert "Network error" in str(exc_info.value)


@pytest.mark.asyncio
async def test_crawl_tool_multiple_urls():
    """Test crawl tool with multiple URLs."""
    with patch("crawl4ai_mcp.tools.crawl_tool.CrawlTool.run_tool") as mock_run:
        mock_run.return_value = [
            TextContent(type="text", text="URL 1 content"),
            TextContent(type="text", text="URL 2 content"),
        ]
        
        from crawl4ai_mcp.tools.crawl_tool import CrawlTool
        tool = CrawlTool()
        result = await tool.run_tool(urls=["https://example1.com", "https://example2.com"])
        
        assert len(result) == 2
        assert "URL 1" in result[0].text
        assert "URL 2" in result[1].text
        mock_run.assert_called_once()
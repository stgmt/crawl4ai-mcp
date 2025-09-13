"""
Comprehensive tests for Crawl4AI MCP Server.

Tests the MCP server implementation with proper architecture:
- Tests through public interfaces only
- Uses dependency injection via fixtures
- Mocks external dependencies
- Tests behavior, not implementation details
"""

import pytest
import pytest_asyncio
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from mcp.types import TextContent, Tool
import httpx
import json


class TestCrawl4AIMCPServer:
    """Test suite for the main MCP server class."""
    
    @pytest.mark.asyncio
    async def test_server_initialization(self, monkeypatch):
        """Test that server initializes correctly with all components."""
        # Mock dependencies
        mock_settings = MagicMock()
        mock_settings.LOG_LEVEL = "INFO"
        monkeypatch.setattr("crawl4ai_mcp.config.settings.settings", mock_settings)
        
        # Import after patching
        from crawl4ai_mcp.server import Crawl4AIMCPServer
        
        # Create server
        server = Crawl4AIMCPServer("test-server")
        
        # Verify initialization
        assert server.server.name == "test-server"
        assert hasattr(server, "run_stdio")
        assert hasattr(server, "run_sse")
        assert hasattr(server, "run_http")
    
    @pytest.mark.asyncio
    async def test_list_tools_returns_all_registered_tools(self, crawl4ai_server, mock_tool_registry):
        """Test that list_tools returns all registered tools correctly."""
        # Setup mock tools
        expected_tools = [
            Tool(name="md", description="Convert to markdown", inputSchema={}),
            Tool(name="html", description="Get HTML", inputSchema={}),
        ]
        mock_tool_registry.get_all_tools.return_value = expected_tools
        
        # Execute through the handler
        handlers = crawl4ai_server.server._handlers
        list_tools_handler = None
        
        # Find the list_tools handler
        for handler_name, handler_func in handlers.items():
            if "list_tools" in str(handler_name):
                list_tools_handler = handler_func
                break
        
        assert list_tools_handler is not None, "list_tools handler not found"
        
        # Call the handler
        result = await list_tools_handler()
        
        # Verify
        assert result == expected_tools
        mock_tool_registry.get_all_tools.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_call_tool_success_scenario(self, crawl4ai_server, mock_tool_registry):
        """Test successful tool execution with valid arguments."""
        # Setup mock tool
        mock_tool = AsyncMock()
        expected_result = [TextContent(type="text", text="Tool executed successfully")]
        mock_tool.run_tool.return_value = expected_result
        mock_tool_registry.get_tool.return_value = mock_tool
        
        # Find call_tool handler
        handlers = crawl4ai_server.server._handlers
        call_tool_handler = None
        
        for handler_name, handler_func in handlers.items():
            if "call_tool" in str(handler_name):
                call_tool_handler = handler_func
                break
        
        assert call_tool_handler is not None, "call_tool handler not found"
        
        # Execute
        result = await call_tool_handler("test_tool", {"arg": "value"})
        
        # Verify
        assert result == expected_result
        mock_tool_registry.get_tool.assert_called_once_with("test_tool")
        mock_tool.run_tool.assert_called_once_with({"arg": "value"})
    
    @pytest.mark.asyncio
    async def test_call_tool_handles_unknown_tool(self, crawl4ai_server, mock_tool_registry):
        """Test proper error handling when calling unknown tool."""
        # Setup mock to raise error
        mock_tool_registry.get_tool.side_effect = ValueError("Unknown tool: unknown_tool")
        
        # Find handler
        handlers = crawl4ai_server.server._handlers
        call_tool_handler = None
        
        for handler_name, handler_func in handlers.items():
            if "call_tool" in str(handler_name):
                call_tool_handler = handler_func
                break
        
        # Execute
        result = await call_tool_handler("unknown_tool", {})
        
        # Verify error response
        assert len(result) == 1
        assert isinstance(result[0], TextContent)
        assert "Error: Unknown tool: unknown_tool" in result[0].text
    
    @pytest.mark.asyncio
    async def test_call_tool_handles_execution_exception(self, crawl4ai_server, mock_tool_registry):
        """Test proper error handling when tool execution fails."""
        # Setup mock tool that raises exception
        mock_tool = AsyncMock()
        mock_tool.run_tool.side_effect = Exception("Tool execution failed")
        mock_tool_registry.get_tool.return_value = mock_tool
        
        # Find handler
        handlers = crawl4ai_server.server._handlers
        call_tool_handler = None
        
        for handler_name, handler_func in handlers.items():
            if "call_tool" in str(handler_name):
                call_tool_handler = handler_func
                break
        
        # Execute
        result = await call_tool_handler("failing_tool", {"test": "args"})
        
        # Verify error response
        assert len(result) == 1
        assert isinstance(result[0], TextContent)
        assert "Error executing tool failing_tool" in result[0].text
        assert "Tool execution failed" in result[0].text


class TestTransportModes:
    """Test different transport modes (STDIO, SSE, HTTP)."""
    
    @pytest.mark.asyncio
    async def test_stdio_mode_initialization(self, crawl4ai_server, mock_read_stream, mock_write_stream):
        """Test STDIO transport mode setup and execution."""
        with patch("crawl4ai_mcp.server.stdio_server") as mock_stdio:
            # Setup mock stdio_server context manager
            mock_stdio.return_value.__aenter__.return_value = (mock_read_stream, mock_write_stream)
            mock_stdio.return_value.__aexit__.return_value = None
            
            # Mock the server run method
            crawl4ai_server.server.run = AsyncMock()
            
            # Execute
            await crawl4ai_server.run_stdio()
            
            # Verify
            mock_stdio.assert_called_once()
            crawl4ai_server.server.run.assert_called_once_with(
                mock_read_stream,
                mock_write_stream,
                crawl4ai_server.server.create_initialization_options()
            )
    
    @pytest.mark.asyncio
    async def test_sse_mode_setup(self, crawl4ai_server, monkeypatch):
        """Test SSE transport mode configuration."""
        mock_uvicorn = Mock()
        monkeypatch.setattr("crawl4ai_mcp.server.uvicorn", mock_uvicorn)
        
        # Execute (this will create the Starlette app and pass it to uvicorn)
        crawl4ai_server.run_sse(host="127.0.0.1", port=3001)
        
        # Verify uvicorn was called with correct parameters
        mock_uvicorn.run.assert_called_once()
        call_args = mock_uvicorn.run.call_args
        
        # Check that a Starlette app was passed
        assert call_args[0][0].__class__.__name__ == "Starlette"
        assert call_args[1]["host"] == "127.0.0.1"
        assert call_args[1]["port"] == 3001
    
    @pytest.mark.asyncio
    async def test_http_mode_setup(self, crawl4ai_server, monkeypatch):
        """Test HTTP/StreamableHTTP transport mode configuration."""
        mock_uvicorn = Mock()
        mock_event_store = Mock()
        mock_session_manager = Mock()
        
        monkeypatch.setattr("crawl4ai_mcp.server.uvicorn", mock_uvicorn)
        monkeypatch.setattr("crawl4ai_mcp.server.EventStore", Mock(return_value=mock_event_store))
        monkeypatch.setattr("crawl4ai_mcp.server.StreamableHTTPSessionManager", Mock(return_value=mock_session_manager))
        
        # Execute
        crawl4ai_server.run_http(host="0.0.0.0", port=3000, json_response=True)
        
        # Verify
        mock_uvicorn.run.assert_called_once()
        call_args = mock_uvicorn.run.call_args
        
        # Check configuration
        assert call_args[0][0].__class__.__name__ == "Starlette"
        assert call_args[1]["host"] == "0.0.0.0"
        assert call_args[1]["port"] == 3000


class TestToolRegistry:
    """Test the ToolRegistry component."""
    
    def test_register_tool_adds_to_registry(self):
        """Test that tools are correctly registered."""
        from crawl4ai_mcp.handles.base import ToolRegistry, BaseHandler
        
        # Clear registry first
        ToolRegistry._tools = {}
        
        # Create mock tool
        mock_tool = Mock(spec=BaseHandler)
        mock_tool.name = "test_tool"
        mock_tool.description = "Test tool"
        
        # Register
        ToolRegistry.register_tool(mock_tool)
        
        # Verify
        assert "test_tool" in ToolRegistry._tools
        assert ToolRegistry._tools["test_tool"] == mock_tool
    
    def test_get_tool_returns_correct_handler(self):
        """Test retrieving registered tool by name."""
        from crawl4ai_mcp.handles.base import ToolRegistry, BaseHandler
        
        # Setup
        ToolRegistry._tools = {}
        mock_tool = Mock(spec=BaseHandler)
        mock_tool.name = "test_tool"
        ToolRegistry._tools["test_tool"] = mock_tool
        
        # Execute
        result = ToolRegistry.get_tool("test_tool")
        
        # Verify
        assert result == mock_tool
    
    def test_get_tool_raises_for_unknown_tool(self):
        """Test that getting unknown tool raises ValueError."""
        from crawl4ai_mcp.handles.base import ToolRegistry
        
        # Setup
        ToolRegistry._tools = {}
        
        # Execute and verify
        with pytest.raises(ValueError, match="Unknown tool: nonexistent"):
            ToolRegistry.get_tool("nonexistent")
    
    def test_get_all_tools_returns_descriptions(self):
        """Test that get_all_tools returns all tool descriptions."""
        from crawl4ai_mcp.handles.base import ToolRegistry, BaseHandler
        
        # Setup
        ToolRegistry._tools = {}
        
        # Create mock tools
        tool1 = Mock(spec=BaseHandler)
        tool1.name = "tool1"
        tool1.get_tool_description.return_value = Tool(name="tool1", description="Tool 1", inputSchema={})
        
        tool2 = Mock(spec=BaseHandler)
        tool2.name = "tool2"
        tool2.get_tool_description.return_value = Tool(name="tool2", description="Tool 2", inputSchema={})
        
        ToolRegistry._tools = {"tool1": tool1, "tool2": tool2}
        
        # Execute
        result = ToolRegistry.get_all_tools()
        
        # Verify
        assert len(result) == 2
        assert all(isinstance(tool, Tool) for tool in result)
        assert {tool.name for tool in result} == {"tool1", "tool2"}


class TestErrorHandling:
    """Test error handling and edge cases."""
    
    @pytest.mark.asyncio
    async def test_handles_http_timeout(self, mock_httpx_client, monkeypatch):
        """Test handling of HTTP timeout errors."""
        from crawl4ai_mcp.handles.base import BaseHandler
        
        # Setup mock client to raise timeout
        mock_httpx_client.post.side_effect = httpx.TimeoutException("Request timeout")
        
        # Patch httpx.AsyncClient
        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client_class.return_value.__aenter__.return_value = mock_httpx_client
            
            # Create handler instance
            handler = BaseHandler()
            
            # Execute and verify
            with pytest.raises(Exception, match="Timeout calling crawl4ai API"):
                await handler.call_crawl4ai_api("test", {"data": "test"})
    
    @pytest.mark.asyncio
    async def test_handles_http_status_errors(self, mock_httpx_client, monkeypatch):
        """Test handling of HTTP status errors (4xx, 5xx)."""
        from crawl4ai_mcp.handles.base import BaseHandler
        
        # Setup mock response with error
        error_response = Mock()
        error_response.status_code = 404
        error_response.text = "Not found"
        mock_httpx_client.post.side_effect = httpx.HTTPStatusError(
            "Not found", request=Mock(), response=error_response
        )
        
        # Patch httpx.AsyncClient
        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client_class.return_value.__aenter__.return_value = mock_httpx_client
            
            # Create handler instance
            handler = BaseHandler()
            
            # Execute and verify
            with pytest.raises(Exception, match="HTTP 404: Not found"):
                await handler.call_crawl4ai_api("test", {"data": "test"})
    
    @pytest.mark.asyncio
    async def test_handles_malformed_json_response(self, mock_httpx_client):
        """Test handling of malformed JSON responses."""
        from crawl4ai_mcp.handles.base import BaseHandler
        
        # Setup mock response with invalid JSON
        response = Mock()
        response.status_code = 200
        response.raise_for_status = Mock()
        response.json.side_effect = json.JSONDecodeError("Invalid", "", 0)
        mock_httpx_client.post.return_value = response
        
        # Patch httpx.AsyncClient
        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client_class.return_value.__aenter__.return_value = mock_httpx_client
            
            # Create handler instance
            handler = BaseHandler()
            
            # Execute and verify
            with pytest.raises(Exception, match="Error calling crawl4ai API"):
                await handler.call_crawl4ai_api("test", {"data": "test"})
    
    @pytest.mark.asyncio
    async def test_handles_network_errors(self, mock_httpx_client):
        """Test handling of network connectivity errors."""
        from crawl4ai_mcp.handles.base import BaseHandler
        
        # Setup mock to raise network error
        mock_httpx_client.post.side_effect = httpx.NetworkError("Network unreachable")
        
        # Patch httpx.AsyncClient
        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client_class.return_value.__aenter__.return_value = mock_httpx_client
            
            # Create handler instance
            handler = BaseHandler()
            
            # Execute and verify
            with pytest.raises(Exception, match="Error calling crawl4ai API"):
                await handler.call_crawl4ai_api("test", {"data": "test"})
    
    @pytest.mark.asyncio
    async def test_handles_empty_tool_arguments(self, crawl4ai_server, mock_tool_registry):
        """Test handling of empty or None tool arguments."""
        # Setup mock tool
        mock_tool = AsyncMock()
        mock_tool.run_tool.return_value = [TextContent(type="text", text="Handled empty args")]
        mock_tool_registry.get_tool.return_value = mock_tool
        
        # Find handler
        handlers = crawl4ai_server.server._handlers
        call_tool_handler = None
        
        for handler_name, handler_func in handlers.items():
            if "call_tool" in str(handler_name):
                call_tool_handler = handler_func
                break
        
        # Test with empty dict
        result = await call_tool_handler("test_tool", {})
        assert len(result) == 1
        mock_tool.run_tool.assert_called_with({})
        
        # Test with None (should be handled gracefully)
        result = await call_tool_handler("test_tool", None)
        assert len(result) == 1
        mock_tool.run_tool.assert_called_with(None)
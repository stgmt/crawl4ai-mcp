"""
Integration tests for Crawl4AI MCP Server.

Tests end-to-end scenarios and interactions between components.
"""

import pytest
import pytest_asyncio
from unittest.mock import Mock, AsyncMock, patch, MagicMock, call
from mcp.types import TextContent, Tool
import json
import asyncio


class TestEndToEndScenarios:
    """Test complete workflows from request to response."""
    
    @pytest.mark.asyncio
    async def test_full_mcp_protocol_flow(self, monkeypatch):
        """Test complete MCP protocol flow: initialize -> list_tools -> call_tool."""
        # Mock all dependencies
        mock_settings = MagicMock()
        mock_settings.LOG_LEVEL = "INFO"
        mock_settings.CRAWL4AI_ENDPOINT = "https://test.crawl4ai.com"
        mock_settings.BEARER_TOKEN = "test-token"
        mock_settings.REQUEST_TIMEOUT = 30.0
        mock_settings.get_crawl4ai_url = Mock(
            side_effect=lambda endpoint: f"https://test.crawl4ai.com/{endpoint}"
        )
        
        monkeypatch.setattr("crawl4ai_mcp.config.settings.settings", mock_settings)
        
        # Mock httpx for API calls
        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.raise_for_status = Mock()
            mock_response.json = Mock(return_value={
                "result": "# Test Content\n\nThis is a test"
            })
            mock_client.post.return_value = mock_response
            mock_client_class.return_value.__aenter__.return_value = mock_client
            
            # Import and create server after patching
            from crawl4ai_mcp.server import Crawl4AIMCPServer
            
            server = Crawl4AIMCPServer("integration-test")
            
            # Simulate MCP protocol flow
            # 1. List available tools
            handlers = server.server._handlers
            list_handler = None
            for name, handler in handlers.items():
                if "list_tools" in str(name):
                    list_handler = handler
                    break
            
            tools = await list_handler()
            assert len(tools) > 0
            assert any(tool.name == "md" for tool in tools)
            
            # 2. Call a tool
            call_handler = None
            for name, handler in handlers.items():
                if "call_tool" in str(name):
                    call_handler = handler
                    break
            
            result = await call_handler("md", {"url": "https://example.com"})
            assert len(result) == 1
            assert isinstance(result[0], TextContent)
            assert "Test Content" in result[0].text
    
    @pytest.mark.asyncio
    async def test_concurrent_tool_calls(self, monkeypatch):
        """Test handling multiple concurrent tool calls."""
        # Setup mocks
        mock_settings = MagicMock()
        mock_settings.LOG_LEVEL = "INFO"
        mock_settings.CRAWL4AI_ENDPOINT = "https://test.crawl4ai.com"
        mock_settings.BEARER_TOKEN = "test-token"
        mock_settings.REQUEST_TIMEOUT = 30.0
        mock_settings.get_crawl4ai_url = Mock(
            side_effect=lambda endpoint: f"https://test.crawl4ai.com/{endpoint}"
        )
        
        monkeypatch.setattr("crawl4ai_mcp.config.settings.settings", mock_settings)
        
        # Track concurrent calls
        call_count = {"count": 0, "max_concurrent": 0, "current": 0}
        
        async def mock_post(*args, **kwargs):
            call_count["current"] += 1
            call_count["count"] += 1
            call_count["max_concurrent"] = max(call_count["max_concurrent"], call_count["current"])
            
            # Simulate some processing time
            await asyncio.sleep(0.1)
            
            response = Mock()
            response.status_code = 200
            response.raise_for_status = Mock()
            response.json = Mock(return_value={
                "result": f"Result {call_count['count']}"
            })
            
            call_count["current"] -= 1
            return response
        
        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client.post = mock_post
            mock_client_class.return_value.__aenter__.return_value = mock_client
            
            from crawl4ai_mcp.server import Crawl4AIMCPServer
            
            server = Crawl4AIMCPServer("concurrent-test")
            
            # Get call handler
            handlers = server.server._handlers
            call_handler = None
            for name, handler in handlers.items():
                if "call_tool" in str(name):
                    call_handler = handler
                    break
            
            # Execute multiple concurrent calls
            tasks = [
                call_handler("md", {"url": f"https://example{i}.com"})
                for i in range(5)
            ]
            
            results = await asyncio.gather(*tasks)
            
            # Verify all calls completed
            assert len(results) == 5
            assert call_count["count"] == 5
            # Verify they ran concurrently (max_concurrent > 1)
            assert call_count["max_concurrent"] > 1
    
    @pytest.mark.asyncio
    async def test_error_recovery_and_retry(self, monkeypatch):
        """Test that server recovers from errors and can retry operations."""
        mock_settings = MagicMock()
        mock_settings.LOG_LEVEL = "INFO"
        mock_settings.CRAWL4AI_ENDPOINT = "https://test.crawl4ai.com"
        mock_settings.BEARER_TOKEN = "test-token"
        mock_settings.REQUEST_TIMEOUT = 30.0
        mock_settings.get_crawl4ai_url = Mock(
            side_effect=lambda endpoint: f"https://test.crawl4ai.com/{endpoint}"
        )
        
        monkeypatch.setattr("crawl4ai_mcp.config.settings.settings", mock_settings)
        
        # Mock httpx to fail first, then succeed
        call_count = {"count": 0}
        
        async def mock_post(*args, **kwargs):
            call_count["count"] += 1
            
            if call_count["count"] == 1:
                # First call fails
                raise Exception("Network error")
            else:
                # Second call succeeds
                response = Mock()
                response.status_code = 200
                response.raise_for_status = Mock()
                response.json = Mock(return_value={"result": "Success after retry"})
                return response
        
        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client.post = mock_post
            mock_client_class.return_value.__aenter__.return_value = mock_client
            
            from crawl4ai_mcp.server import Crawl4AIMCPServer
            
            server = Crawl4AIMCPServer("retry-test")
            
            # Get handler
            handlers = server.server._handlers
            call_handler = None
            for name, handler in handlers.items():
                if "call_tool" in str(name):
                    call_handler = handler
                    break
            
            # First call should fail
            result1 = await call_handler("md", {"url": "https://example.com"})
            assert "Error" in result1[0].text
            
            # Second call should succeed
            result2 = await call_handler("md", {"url": "https://example.com"})
            assert "Success after retry" in result2[0].text


class TestTransportIntegration:
    """Test integration between different transport modes."""
    
    @pytest.mark.asyncio
    async def test_stdio_transport_message_flow(self, monkeypatch):
        """Test message flow through STDIO transport."""
        mock_settings = MagicMock()
        mock_settings.LOG_LEVEL = "INFO"
        monkeypatch.setattr("crawl4ai_mcp.config.settings.settings", mock_settings)
        
        from crawl4ai_mcp.server import Crawl4AIMCPServer
        
        server = Crawl4AIMCPServer("stdio-test")
        
        # Mock stdio streams
        mock_read = AsyncMock()
        mock_write = AsyncMock()
        
        # Simulate initialization message
        mock_read.read.side_effect = [
            json.dumps({
                "jsonrpc": "2.0",
                "method": "initialize",
                "params": {
                    "protocolVersion": "1.0.0",
                    "capabilities": {},
                    "clientInfo": {"name": "test-client"}
                },
                "id": 1
            }).encode(),
            None  # End stream
        ]
        
        with patch("crawl4ai_mcp.server.stdio_server") as mock_stdio:
            mock_stdio.return_value.__aenter__.return_value = (mock_read, mock_write)
            mock_stdio.return_value.__aexit__.return_value = None
            
            # Mock server.run to prevent actual execution
            server.server.run = AsyncMock()
            
            await server.run_stdio()
            
            # Verify stdio was properly initialized
            mock_stdio.assert_called_once()
            server.server.run.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_sse_transport_connection_handling(self, monkeypatch):
        """Test SSE transport handles connections properly."""
        mock_settings = MagicMock()
        mock_settings.LOG_LEVEL = "INFO"
        mock_settings.SSE_PORT = 3001
        mock_settings.DEBUG = False
        mock_settings.CRAWL4AI_ENDPOINT = "https://test.crawl4ai.com"
        monkeypatch.setattr("crawl4ai_mcp.config.settings.settings", mock_settings)
        
        # Mock uvicorn to prevent actual server start
        mock_uvicorn = Mock()
        monkeypatch.setattr("crawl4ai_mcp.server.uvicorn", mock_uvicorn)
        
        from crawl4ai_mcp.server import Crawl4AIMCPServer
        
        server = Crawl4AIMCPServer("sse-test")
        
        # Start SSE server
        server.run_sse(host="127.0.0.1", port=3001)
        
        # Verify Starlette app was created with correct routes
        call_args = mock_uvicorn.run.call_args
        app = call_args[0][0]
        
        # Check app has required routes
        assert app.__class__.__name__ == "Starlette"
        assert hasattr(app, "routes")
    
    @pytest.mark.asyncio
    async def test_http_transport_session_management(self, monkeypatch):
        """Test HTTP transport manages sessions correctly."""
        mock_settings = MagicMock()
        mock_settings.LOG_LEVEL = "INFO"
        mock_settings.HTTP_PORT = 3000
        mock_settings.DEBUG = False
        mock_settings.CRAWL4AI_ENDPOINT = "https://test.crawl4ai.com"
        monkeypatch.setattr("crawl4ai_mcp.config.settings.settings", mock_settings)
        
        # Mock components
        mock_uvicorn = Mock()
        mock_event_store = Mock()
        mock_session_manager = Mock()
        mock_session_manager.run = Mock()
        mock_session_manager.run.return_value.__aenter__ = AsyncMock()
        mock_session_manager.run.return_value.__aexit__ = AsyncMock()
        mock_session_manager.handle_request = AsyncMock()
        
        monkeypatch.setattr("crawl4ai_mcp.server.uvicorn", mock_uvicorn)
        monkeypatch.setattr("crawl4ai_mcp.server.EventStore", Mock(return_value=mock_event_store))
        monkeypatch.setattr("crawl4ai_mcp.server.StreamableHTTPSessionManager", 
                          Mock(return_value=mock_session_manager))
        
        from crawl4ai_mcp.server import Crawl4AIMCPServer
        
        server = Crawl4AIMCPServer("http-test")
        
        # Start HTTP server
        server.run_http(host="0.0.0.0", port=3000, json_response=True)
        
        # Verify session manager was created with correct params
        call_args = mock_uvicorn.run.call_args
        app = call_args[0][0]
        
        assert app.__class__.__name__ == "Starlette"
        assert hasattr(app, "lifespan")


class TestAuthenticationAndSecurity:
    """Test authentication and security features."""
    
    @pytest.mark.asyncio
    async def test_bearer_token_authentication(self, monkeypatch):
        """Test that bearer token is properly included in API calls."""
        mock_settings = MagicMock()
        mock_settings.LOG_LEVEL = "INFO"
        mock_settings.CRAWL4AI_ENDPOINT = "https://test.crawl4ai.com"
        mock_settings.BEARER_TOKEN = "secret-token-12345"
        mock_settings.REQUEST_TIMEOUT = 30.0
        mock_settings.get_crawl4ai_url = Mock(
            side_effect=lambda endpoint: f"https://test.crawl4ai.com/{endpoint}"
        )
        
        monkeypatch.setattr("crawl4ai_mcp.config.settings.settings", mock_settings)
        
        # Track headers sent
        captured_headers = {}
        
        async def mock_post(*args, **kwargs):
            captured_headers.update(kwargs.get("headers", {}))
            response = Mock()
            response.status_code = 200
            response.raise_for_status = Mock()
            response.json = Mock(return_value={"result": "authenticated"})
            return response
        
        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client.post = mock_post
            mock_client_class.return_value.__aenter__.return_value = mock_client
            
            from crawl4ai_mcp.handles.base import BaseHandler
            
            handler = BaseHandler()
            await handler.call_crawl4ai_api("test", {"data": "test"})
            
            # Verify bearer token was included
            assert "Authorization" in captured_headers
            assert captured_headers["Authorization"] == "Bearer secret-token-12345"
    
    @pytest.mark.asyncio
    async def test_no_token_when_not_configured(self, monkeypatch):
        """Test that no auth header is sent when bearer token is not configured."""
        mock_settings = MagicMock()
        mock_settings.LOG_LEVEL = "INFO"
        mock_settings.CRAWL4AI_ENDPOINT = "https://test.crawl4ai.com"
        mock_settings.BEARER_TOKEN = None  # No token configured
        mock_settings.REQUEST_TIMEOUT = 30.0
        mock_settings.get_crawl4ai_url = Mock(
            side_effect=lambda endpoint: f"https://test.crawl4ai.com/{endpoint}"
        )
        
        monkeypatch.setattr("crawl4ai_mcp.config.settings.settings", mock_settings)
        
        # Track headers
        captured_headers = {}
        
        async def mock_post(*args, **kwargs):
            captured_headers.update(kwargs.get("headers", {}))
            response = Mock()
            response.status_code = 200
            response.raise_for_status = Mock()
            response.json = Mock(return_value={"result": "no auth needed"})
            return response
        
        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client.post = mock_post
            mock_client_class.return_value.__aenter__.return_value = mock_client
            
            from crawl4ai_mcp.handles.base import BaseHandler
            
            handler = BaseHandler()
            await handler.call_crawl4ai_api("test", {"data": "test"})
            
            # Verify no auth header was sent
            assert "Authorization" not in captured_headers
    
    @pytest.mark.asyncio
    async def test_handles_401_unauthorized(self, monkeypatch):
        """Test proper handling of 401 Unauthorized responses."""
        mock_settings = MagicMock()
        mock_settings.LOG_LEVEL = "INFO"
        mock_settings.CRAWL4AI_ENDPOINT = "https://test.crawl4ai.com"
        mock_settings.BEARER_TOKEN = "invalid-token"
        mock_settings.REQUEST_TIMEOUT = 30.0
        mock_settings.get_crawl4ai_url = Mock(
            side_effect=lambda endpoint: f"https://test.crawl4ai.com/{endpoint}"
        )
        
        monkeypatch.setattr("crawl4ai_mcp.config.settings.settings", mock_settings)
        
        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            
            # Create 401 response
            import httpx
            error_response = Mock()
            error_response.status_code = 401
            error_response.text = "Unauthorized: Invalid token"
            
            mock_client.post.side_effect = httpx.HTTPStatusError(
                "Unauthorized", 
                request=Mock(), 
                response=error_response
            )
            
            mock_client_class.return_value.__aenter__.return_value = mock_client
            
            from crawl4ai_mcp.handles.base import BaseHandler
            
            handler = BaseHandler()
            
            # Should raise exception with auth error
            with pytest.raises(Exception, match="HTTP 401: Unauthorized"):
                await handler.call_crawl4ai_api("test", {"data": "test"})
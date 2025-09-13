"""
Tests for individual Crawl4AI tool handlers.

Tests each tool handler implementation with proper mocking
and edge case handling.
"""

import pytest
import pytest_asyncio
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from mcp.types import TextContent, Tool
import httpx
import base64
import json


class TestMdTool:
    """Test the Markdown conversion tool."""
    
    @pytest.mark.asyncio
    async def test_md_tool_basic_conversion(self, mock_httpx_client):
        """Test basic markdown conversion functionality."""
        from crawl4ai_mcp.handles.crawl4ai_md import Crawl4aiMd
        
        # Setup mock response
        mock_response = {
            "result": "# Test Page\n\nThis is test content",
            "url": "https://example.com"
        }
        mock_httpx_client.post.return_value.json.return_value = mock_response
        mock_httpx_client.post.return_value.status_code = 200
        mock_httpx_client.post.return_value.raise_for_status = Mock()
        
        # Patch httpx
        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client_class.return_value.__aenter__.return_value = mock_httpx_client
            
            # Create tool and execute
            tool = Crawl4aiMd()
            result = await tool.run_tool({"url": "https://example.com"})
            
            # Verify
            assert len(result) == 1
            assert isinstance(result[0], TextContent)
            assert "# Test Page" in result[0].text
    
    @pytest.mark.asyncio
    async def test_md_tool_with_filters(self, mock_httpx_client):
        """Test markdown tool with content filters."""
        from crawl4ai_mcp.handles.crawl4ai_md import Crawl4aiMd
        
        # Setup
        mock_response = {"result": "Filtered content"}
        mock_httpx_client.post.return_value.json.return_value = mock_response
        mock_httpx_client.post.return_value.status_code = 200
        mock_httpx_client.post.return_value.raise_for_status = Mock()
        
        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client_class.return_value.__aenter__.return_value = mock_httpx_client
            
            # Test with BM25 filter
            tool = Crawl4aiMd()
            result = await tool.run_tool({
                "url": "https://example.com",
                "f": "bm25",
                "q": "search query"
            })
            
            # Verify the request was made with correct params
            call_args = mock_httpx_client.post.call_args
            assert call_args[1]["json"]["f"] == "bm25"
            assert call_args[1]["json"]["q"] == "search query"
    
    def test_md_tool_description(self):
        """Test that tool description is properly defined."""
        from crawl4ai_mcp.handles.crawl4ai_md import Crawl4aiMd
        
        tool = Crawl4aiMd()
        description = tool.get_tool_description()
        
        assert description.name == "md"
        assert "markdown" in description.description.lower()
        assert "url" in description.inputSchema["properties"]
        assert "url" in description.inputSchema["required"]


class TestHtmlTool:
    """Test the HTML extraction tool."""
    
    @pytest.mark.asyncio
    async def test_html_tool_extraction(self, mock_httpx_client):
        """Test HTML content extraction."""
        from crawl4ai_mcp.handles.crawl4ai_html import Crawl4aiHtml
        
        # Setup
        mock_response = {
            "result": "<html><body><h1>Test</h1></body></html>",
            "url": "https://example.com"
        }
        mock_httpx_client.post.return_value.json.return_value = mock_response
        mock_httpx_client.post.return_value.status_code = 200
        mock_httpx_client.post.return_value.raise_for_status = Mock()
        
        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client_class.return_value.__aenter__.return_value = mock_httpx_client
            
            tool = Crawl4aiHtml()
            result = await tool.run_tool({"url": "https://example.com"})
            
            assert len(result) == 1
            assert "<h1>Test</h1>" in result[0].text


class TestScreenshotTool:
    """Test the screenshot capture tool."""
    
    @pytest.mark.asyncio
    async def test_screenshot_base64_response(self, mock_httpx_client):
        """Test screenshot tool returns base64 data when no output path."""
        from crawl4ai_mcp.handles.crawl4ai_screenshot import Crawl4aiScreenshot
        
        # Setup
        mock_base64 = base64.b64encode(b"fake image data").decode()
        mock_response = {
            "result": mock_base64,
            "url": "https://example.com"
        }
        mock_httpx_client.post.return_value.json.return_value = mock_response
        mock_httpx_client.post.return_value.status_code = 200
        mock_httpx_client.post.return_value.raise_for_status = Mock()
        
        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client_class.return_value.__aenter__.return_value = mock_httpx_client
            
            tool = Crawl4aiScreenshot()
            result = await tool.run_tool({
                "url": "https://example.com"
            })
            
            assert len(result) == 1
            assert "base64" in result[0].text or mock_base64 in result[0].text
    
    @pytest.mark.asyncio
    async def test_screenshot_save_to_file(self, mock_httpx_client, tmp_path):
        """Test screenshot tool saves to file when output path provided."""
        from crawl4ai_mcp.handles.crawl4ai_screenshot import Crawl4aiScreenshot
        
        # Setup
        mock_base64 = base64.b64encode(b"fake image data").decode()
        mock_response = {
            "result": mock_base64,
            "url": "https://example.com"
        }
        mock_httpx_client.post.return_value.json.return_value = mock_response
        mock_httpx_client.post.return_value.status_code = 200
        mock_httpx_client.post.return_value.raise_for_status = Mock()
        
        output_file = tmp_path / "test_screenshot.png"
        
        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client_class.return_value.__aenter__.return_value = mock_httpx_client
            
            tool = Crawl4aiScreenshot()
            result = await tool.run_tool({
                "url": "https://example.com",
                "output_path": str(output_file)
            })
            
            # Verify file would be created (in real implementation)
            assert len(result) == 1
            assert "saved" in result[0].text.lower() or str(output_file) in result[0].text


class TestExecuteJsTool:
    """Test JavaScript execution tool."""
    
    @pytest.mark.asyncio
    async def test_execute_js_single_script(self, mock_httpx_client):
        """Test executing a single JavaScript snippet."""
        from crawl4ai_mcp.handles.crawl4ai_execute_js import Crawl4aiExecuteJs
        
        # Setup
        mock_response = {
            "result": ["document title", "page content"],
            "url": "https://example.com"
        }
        mock_httpx_client.post.return_value.json.return_value = mock_response
        mock_httpx_client.post.return_value.status_code = 200
        mock_httpx_client.post.return_value.raise_for_status = Mock()
        
        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client_class.return_value.__aenter__.return_value = mock_httpx_client
            
            tool = Crawl4aiExecuteJs()
            result = await tool.run_tool({
                "url": "https://example.com",
                "scripts": ["document.title"]
            })
            
            assert len(result) == 1
            assert "document title" in result[0].text or "page content" in result[0].text
    
    @pytest.mark.asyncio
    async def test_execute_js_multiple_scripts(self, mock_httpx_client):
        """Test executing multiple JavaScript snippets."""
        from crawl4ai_mcp.handles.crawl4ai_execute_js import Crawl4aiExecuteJs
        
        # Setup
        mock_response = {
            "result": ["Title: Test", "URL: https://example.com", "Count: 42"],
            "url": "https://example.com"
        }
        mock_httpx_client.post.return_value.json.return_value = mock_response
        mock_httpx_client.post.return_value.status_code = 200
        mock_httpx_client.post.return_value.raise_for_status = Mock()
        
        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client_class.return_value.__aenter__.return_value = mock_httpx_client
            
            tool = Crawl4aiExecuteJs()
            result = await tool.run_tool({
                "url": "https://example.com",
                "scripts": [
                    "document.title",
                    "window.location.href",
                    "document.querySelectorAll('div').length"
                ]
            })
            
            # Verify request was made with all scripts
            call_args = mock_httpx_client.post.call_args
            assert len(call_args[1]["json"]["scripts"]) == 3


class TestCrawlTool:
    """Test bulk crawling tool."""
    
    @pytest.mark.asyncio
    async def test_crawl_single_url(self, mock_httpx_client):
        """Test crawling a single URL."""
        from crawl4ai_mcp.handles.crawl4ai_crawl import Crawl4aiCrawl
        
        # Setup
        mock_response = {
            "results": [
                {
                    "url": "https://example.com",
                    "content": "Page content",
                    "success": True
                }
            ]
        }
        mock_httpx_client.post.return_value.json.return_value = mock_response
        mock_httpx_client.post.return_value.status_code = 200
        mock_httpx_client.post.return_value.raise_for_status = Mock()
        
        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client_class.return_value.__aenter__.return_value = mock_httpx_client
            
            tool = Crawl4aiCrawl()
            result = await tool.run_tool({
                "urls": ["https://example.com"]
            })
            
            assert len(result) == 1
            assert "Page content" in result[0].text or "example.com" in result[0].text
    
    @pytest.mark.asyncio
    async def test_crawl_multiple_urls(self, mock_httpx_client):
        """Test crawling multiple URLs in batch."""
        from crawl4ai_mcp.handles.crawl4ai_crawl import Crawl4aiCrawl
        
        # Setup
        mock_response = {
            "results": [
                {"url": "https://example1.com", "content": "Content 1", "success": True},
                {"url": "https://example2.com", "content": "Content 2", "success": True},
                {"url": "https://example3.com", "content": "Content 3", "success": True}
            ]
        }
        mock_httpx_client.post.return_value.json.return_value = mock_response
        mock_httpx_client.post.return_value.status_code = 200
        mock_httpx_client.post.return_value.raise_for_status = Mock()
        
        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client_class.return_value.__aenter__.return_value = mock_httpx_client
            
            tool = Crawl4aiCrawl()
            result = await tool.run_tool({
                "urls": [
                    "https://example1.com",
                    "https://example2.com", 
                    "https://example3.com"
                ]
            })
            
            # Verify batch processing
            call_args = mock_httpx_client.post.call_args
            assert len(call_args[1]["json"]["urls"]) == 3
    
    @pytest.mark.asyncio
    async def test_crawl_with_config(self, mock_httpx_client):
        """Test crawling with browser and crawler configuration."""
        from crawl4ai_mcp.handles.crawl4ai_crawl import Crawl4aiCrawl
        
        # Setup
        mock_response = {"results": [{"url": "https://example.com", "content": "Test"}]}
        mock_httpx_client.post.return_value.json.return_value = mock_response
        mock_httpx_client.post.return_value.status_code = 200
        mock_httpx_client.post.return_value.raise_for_status = Mock()
        
        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client_class.return_value.__aenter__.return_value = mock_httpx_client
            
            tool = Crawl4aiCrawl()
            result = await tool.run_tool({
                "urls": ["https://example.com"],
                "browser_config": {"headless": True, "viewport": {"width": 1920}},
                "crawler_config": {"wait_for": "networkidle"}
            })
            
            # Verify configs were passed
            call_args = mock_httpx_client.post.call_args
            assert "browser_config" in call_args[1]["json"]
            assert "crawler_config" in call_args[1]["json"]
    
    @pytest.mark.asyncio
    async def test_crawl_exceeds_url_limit(self):
        """Test that crawl tool rejects more than 100 URLs."""
        from crawl4ai_mcp.handles.crawl4ai_crawl import Crawl4aiCrawl
        
        tool = Crawl4aiCrawl()
        
        # Create 101 URLs
        urls = [f"https://example{i}.com" for i in range(101)]
        
        # Should raise or return error
        result = await tool.run_tool({"urls": urls})
        
        assert len(result) == 1
        assert "error" in result[0].text.lower() or "100" in result[0].text


class TestPdfTool:
    """Test PDF generation tool."""
    
    @pytest.mark.asyncio
    async def test_pdf_generation_base64(self, mock_httpx_client):
        """Test PDF generation returns base64 when no output path."""
        from crawl4ai_mcp.handles.crawl4ai_pdf import Crawl4aiPdf
        
        # Setup
        mock_base64 = base64.b64encode(b"fake pdf data").decode()
        mock_response = {
            "result": mock_base64,
            "url": "https://example.com"
        }
        mock_httpx_client.post.return_value.json.return_value = mock_response
        mock_httpx_client.post.return_value.status_code = 200
        mock_httpx_client.post.return_value.raise_for_status = Mock()
        
        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client_class.return_value.__aenter__.return_value = mock_httpx_client
            
            tool = Crawl4aiPdf()
            result = await tool.run_tool({
                "url": "https://example.com"
            })
            
            assert len(result) == 1
            assert "base64" in result[0].text or mock_base64 in result[0].text
    
    @pytest.mark.asyncio
    async def test_pdf_save_to_file(self, mock_httpx_client, tmp_path):
        """Test PDF generation saves to file when path provided."""
        from crawl4ai_mcp.handles.crawl4ai_pdf import Crawl4aiPdf
        
        # Setup
        mock_base64 = base64.b64encode(b"fake pdf data").decode()
        mock_response = {
            "result": mock_base64,
            "url": "https://example.com"
        }
        mock_httpx_client.post.return_value.json.return_value = mock_response
        mock_httpx_client.post.return_value.status_code = 200
        mock_httpx_client.post.return_value.raise_for_status = Mock()
        
        output_file = tmp_path / "test.pdf"
        
        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client_class.return_value.__aenter__.return_value = mock_httpx_client
            
            tool = Crawl4aiPdf()
            result = await tool.run_tool({
                "url": "https://example.com",
                "output_path": str(output_file)
            })
            
            assert len(result) == 1
            assert "saved" in result[0].text.lower() or str(output_file) in result[0].text
"""Basic tests for the MCP server."""

import pytest


def test_imports():
    """Test that basic imports work."""
    from src import server
    assert server is not None


def test_server_can_start():
    """Test that the server can be imported without errors."""
    from src.server import main
    assert main is not None


@pytest.mark.asyncio
async def test_basic_functionality():
    """Test basic server functionality."""
    # This is a placeholder test
    assert True
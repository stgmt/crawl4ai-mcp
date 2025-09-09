# Contributing to Crawl4AI MCP Server

Thanks for your interest in contributing! This guide explains how to get involved.

## Getting Started

1. Fork the repository and clone it locally
2. Install dependencies with `pip install -e .[dev]`
3. Run `python -m crawl4ai_mcp --stdio` to start the server in development mode
4. Test your changes with the test suite

## Development Process & Pull Requests

1. Create a new branch for your changes
2. Make your changes following existing code style and conventions
   - Run `black crawl4ai_mcp tests` to format code
   - Run `ruff check crawl4ai_mcp tests` to check code style
   - Run `mypy crawl4ai_mcp` to verify type hints
3. Test changes thoroughly:
   - Run `pytest` to run all tests
   - Test with real MCP clients when possible
4. Update documentation as needed (README.md, inline docstrings)
5. Use clear commit messages explaining your changes
6. Verify all changes work as expected
7. Submit a pull request with a clear description of changes
8. PRs will be reviewed quickly by maintainers

## Development Commands

- `python -m crawl4ai_mcp --stdio` - Run server in STDIO mode
- `python -m crawl4ai_mcp --sse` - Run server in SSE mode
- `python -m crawl4ai_mcp --http` - Run server in HTTP mode
- `pytest` - Run all tests
- `pytest --cov=crawl4ai_mcp` - Run tests with coverage
- `black crawl4ai_mcp tests` - Format code
- `ruff check crawl4ai_mcp tests` - Check code style
- `mypy crawl4ai_mcp` - Check type hints

## Testing Guidelines

- Add unit tests for new functionality
- Include integration tests for MCP protocol handlers
- Test with various MCP client configurations
- Verify all transport modes work correctly
- Check edge cases and error handling

## Code Style

- Follow PEP 8 conventions
- Use type hints for all functions
- Add docstrings for all public APIs
- Keep functions focused and testable
- Use the existing error handling patterns

## Adding New Tools

To add a new Crawl4AI tool:

1. Create a new handler in `crawl4ai_mcp/handles/`
2. Register it in `ToolRegistry`
3. Add tests in `tests/`
4. Update README.md with tool documentation

Example tool handler:

```python
from typing import Any, Dict, Sequence
from mcp.types import TextContent
from crawl4ai_mcp.handles.base import BaseToolHandler

class MyToolHandler(BaseToolHandler):
    """Handler for my custom tool."""
    
    name = "my_tool"
    description = "Does something useful"
    
    async def run_tool(self, arguments: Dict[str, Any]) -> Sequence[TextContent]:
        """Execute the tool."""
        # Your implementation here
        result = await self.process(arguments)
        return [TextContent(type="text", text=result)]
```

## Questions?

Feel free to open an issue for questions or create a discussion for general topics about MCP server development.

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
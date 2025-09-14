# 🕷️ Crawl4AI MCP Server

[![PyPI version](https://badge.fury.io/py/crawl4ai-mcp.svg)](https://badge.fury.io/py/crawl4ai-mcp)
[![Python](https://img.shields.io/pypi/pyversions/crawl4ai-mcp.svg)](https://pypi.org/project/crawl4ai-mcp/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Downloads](https://pepy.tech/badge/crawl4ai-mcp)](https://pepy.tech/project/crawl4ai-mcp)

**MCP (Model Context Protocol) server for Crawl4AI** - Universal web crawling and data extraction for AI agents.

Integrate powerful web scraping capabilities into Claude, ChatGPT, and any MCP-compatible AI assistant.

## 📑 Table of Contents

- [🎯 Why This Tool?](#-why-this-tool)
- [⚡ Quick Start](#-quick-start)
- [🚀 Features](#-features)
- [📦 Installation](#-installation)
- [🔧 Usage](#-usage)
- [🛠️ Available Tools](#️-available-tools)
- [🌐 Transport Protocols](#-transport-protocols)
- [⚙️ Configuration](#️-configuration)
- [🐳 Docker Support](#-docker-support)
- [🤝 Contributing](#-contributing)
- [📄 License](#-license)

## 🎯 Why This Tool?

### The Problem

- 🔴 **No MCP servers for web scraping** - AI agents can't access web content
- 🔴 **Complex scraping setup** - Crawl4AI requires custom integration
- 🔴 **Limited protocol support** - Most tools only support one transport
- 🔴 **Poor AI integration** - Existing scrapers aren't optimized for LLMs

### Our Solution  

- ✅ **First Crawl4AI MCP server** - Native MCP integration
- ✅ **All MCP transports** - STDIO, SSE, and HTTP support
- ✅ **AI-optimized extraction** - Clean markdown, structured data
- ✅ **One-line execution** - `crawl4ai-mcp --stdio`
- ✅ **Python 3.10+ support** - Latest MCP compatibility
- ✅ **Production ready** - Type hints, tests, Docker support

## ⚡ Quick Start

### One-Line Execution

```bash
# Install and run
pip install crawl4ai-mcp

# Set required endpoint and run
export CRAWL4AI_ENDPOINT="https://your-crawl4ai-server.com"
crawl4ai-mcp --stdio

# Or with command line argument (required)
crawl4ai-mcp --stdio --endpoint https://your-crawl4ai-server.com

# With optional bearer token
export CRAWL4AI_BEARER_TOKEN="your-token"
crawl4ai-mcp --stdio --endpoint https://your-crawl4ai-server.com

# Or all in one command
CRAWL4AI_ENDPOINT="https://your-crawl4ai-server.com" CRAWL4AI_BEARER_TOKEN="your-token" crawl4ai-mcp --stdio
```

### With Claude Desktop

Add to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "crawl4ai": {
      "command": "crawl4ai-mcp",
      "args": ["--stdio", "--endpoint", "https://your-crawl4ai-server.com"],
      "env": {
        "CRAWL4AI_ENDPOINT": "https://your-crawl4ai-server.com",
        "CRAWL4AI_BEARER_TOKEN": "your-optional-token"
      }
    }
  }
}
```

### With Any MCP Client

```bash
# REQUIRED: Set Crawl4AI endpoint first
export CRAWL4AI_ENDPOINT="https://your-crawl4ai-server.com"

# Default SSE mode (recommended)
crawl4ai-mcp

# STDIO mode (for CLI tools)
crawl4ai-mcp --stdio

# HTTP mode (for REST API)
crawl4ai-mcp --http

# With command line argument (alternative to env var)
crawl4ai-mcp --stdio --endpoint https://your-crawl4ai-server.com

# With optional bearer token
crawl4ai-mcp --endpoint https://your-crawl4ai-server.com --token your-optional-token
```

## 🚀 Features

### Core Capabilities

- 🌐 **Universal Web Scraping** - Extract content from any website
- 📝 **Markdown Conversion** - Clean, formatted markdown output
- 📸 **Screenshots** - Capture visual content
- 📄 **PDF Generation** - Save pages as PDF
- 🎭 **JavaScript Execution** - Interact with dynamic content
- 🔄 **Multiple Transports** - STDIO, SSE, HTTP protocols

### Why Choose crawl4ai-mcp?

| Feature | crawl4ai-mcp | Other Tools |
|---------|--------------|-------------|
| MCP Protocol Support | ✅ Full | ❌ None |
| Crawl4AI Integration | ✅ Native | ❌ Manual |
| Transport Protocols | ✅ All 3 | ⚠️ Usually 1 |
| AI Optimization | ✅ Built-in | ❌ Generic |
| Production Ready | ✅ Yes | ⚠️ Varies |
| Docker Support | ✅ Yes | ⚠️ Limited |

## 📦 Installation

### From PyPI

```bash
pip install crawl4ai-mcp
```

### From Source

```bash
git clone https://github.com/stgmt/crawl4ai-mcp.git
cd crawl4ai-mcp
pip install -e .
```

### With Docker

```bash
docker pull stgmt/crawl4ai-mcp
docker run -p 3000:3000 stgmt/crawl4ai-mcp
```

## 🔧 Usage

### Basic Command Line

```bash
# REQUIRED: Set Crawl4AI endpoint first
export CRAWL4AI_ENDPOINT="https://your-crawl4ai-server.com"

# Default SSE mode (recommended)
crawl4ai-mcp

# STDIO mode for CLI integration
crawl4ai-mcp --stdio

# HTTP mode for REST API
crawl4ai-mcp --http

# Alternative: using command line arguments
crawl4ai-mcp --stdio --endpoint https://your-crawl4ai-server.com

# With optional bearer token (env + args)
export CRAWL4AI_BEARER_TOKEN="your-optional-token"
crawl4ai-mcp --endpoint https://your-crawl4ai-server.com --token your-optional-token

# All via environment variables
export CRAWL4AI_ENDPOINT="https://your-crawl4ai-server.com"
export CRAWL4AI_BEARER_TOKEN="your-optional-token"
crawl4ai-mcp --sse
```

### Python Integration

```python
import asyncio
from crawl4ai_mcp import Crawl4AIMCPServer

async def main():
    server = Crawl4AIMCPServer()
    
    # Run in STDIO mode
    await server.run_stdio()
    
    # Or run in HTTP mode
    # server.run_http(host="0.0.0.0", port=3000)

asyncio.run(main())
```

### With MCP Clients

#### Using mcp-client SDK

```python
from mcp import ClientSession, StdioServerParameters
import asyncio

async def main():
    server_params = StdioServerParameters(
        command="crawl4ai-mcp",
        args=["--stdio", "--endpoint", "https://your-crawl4ai-server.com"]
    )
    
    async with ClientSession(server_params) as session:
        # List available tools
        tools = await session.list_tools()
        
        # Crawl a webpage
        result = await session.call_tool(
            "crawl",
            {"url": "https://example.com"}
        )
        print(result)

asyncio.run(main())
```

## 🛠️ Available Tools

### 1. `crawl` - Full Web Crawling

Extract complete content from any webpage.

```json
{
  "name": "crawl",
  "arguments": {
    "url": "https://example.com",
    "wait_for": "css:.content",
    "timeout": 30000
  }
}
```

### 2. `md` - Markdown Extraction

Get clean markdown content from webpages.

```json
{
  "name": "md", 
  "arguments": {
    "url": "https://docs.example.com",
    "clean": true
  }
}
```

### 3. `html` - Raw HTML

Retrieve raw HTML content.

```json
{
  "name": "html",
  "arguments": {
    "url": "https://example.com"
  }
}
```

### 4. `screenshot` - Visual Capture

Take screenshots of webpages.

```json
{
  "name": "screenshot",
  "arguments": {
    "url": "https://example.com",
    "full_page": true
  }
}
```

### 5. `pdf` - PDF Generation

Convert webpages to PDF.

```json
{
  "name": "pdf",
  "arguments": {
    "url": "https://example.com",
    "format": "A4"
  }
}
```

### 6. `execute_js` - JavaScript Execution

Execute JavaScript on webpages.

```json
{
  "name": "execute_js",
  "arguments": {
    "url": "https://example.com",
    "script": "document.title"
  }
}
```

## 🌐 Transport Protocols

### STDIO Transport

Best for command-line tools and local development.

```bash
# Set required endpoint
export CRAWL4AI_ENDPOINT="https://your-crawl4ai-server.com"
crawl4ai-mcp --stdio
```

**Use cases:**
- Claude Desktop app
- Terminal-based MCP clients
- Local development and testing
- CI/CD pipelines

### SSE Transport (Server-Sent Events)

Ideal for real-time web applications.

```bash
# Set required endpoint
export CRAWL4AI_ENDPOINT="https://your-crawl4ai-server.com"
crawl4ai-mcp --sse
```

**Use cases:**
- Web-based MCP clients
- Real-time streaming applications
- Browser extensions
- Progressive web apps

### HTTP Transport

Standard REST API for maximum compatibility.

```bash
# Set required endpoint
export CRAWL4AI_ENDPOINT="https://your-crawl4ai-server.com"
crawl4ai-mcp --http
```

**Use cases:**
- REST API clients
- Microservice architectures
- Cloud deployments
- Load-balanced environments

## ⚙️ Configuration

### Environment Variables

```bash
# REQUIRED: Crawl4AI endpoint
CRAWL4AI_ENDPOINT=https://your-crawl4ai-server.com

# Authentication token (optional)
CRAWL4AI_BEARER_TOKEN=your-api-token

# Server ports
HTTP_PORT=3000
SSE_PORT=9001

# Logging
LOG_LEVEL=INFO
DEBUG=false

# Performance
REQUEST_TIMEOUT=30
```

### Command Line Arguments

```bash
crawl4ai-mcp --help

Options:
  --stdio              Run in STDIO mode for MCP clients
  --sse                Run in SSE mode for web interfaces (default)
  --http               Run in HTTP mode
  --endpoint ENDPOINT  Crawl4AI API endpoint URL (overrides CRAWL4AI_ENDPOINT)
  --token TOKEN        Bearer authentication token (overrides CRAWL4AI_BEARER_TOKEN)
  --version, -v        Show program's version number and exit
```

### Configuration File

Create `.env` file:

```env
# Required: Crawl4AI API endpoint
CRAWL4AI_ENDPOINT=https://your-crawl4ai-server.com
# Optional: Authentication token
CRAWL4AI_BEARER_TOKEN=your-api-token
# Server configuration
HTTP_PORT=3000
SSE_PORT=9001
LOG_LEVEL=INFO
DEBUG=false
REQUEST_TIMEOUT=30
```

### Error Handling & Validation

The server now includes automatic configuration validation:

```bash
# Without CRAWL4AI_ENDPOINT:
❌ ERROR: CRAWL4AI_ENDPOINT is required!

Set it via environment variable or command line:
  export CRAWL4AI_ENDPOINT='https://your-crawl4ai-server.com'
  OR
  crawl4ai-mcp --endpoint https://your-crawl4ai-server.com

Example endpoints:
  - https://your-crawl4ai-server.com (default)
  - http://localhost:8000 (local development)
```

### Advanced Settings

```python
# config/settings.py
from pydantic import BaseSettings

class Settings(BaseSettings):
    crawl4ai_endpoint: str = "http://localhost:8000"
    http_port: int = 3000
    sse_port: int = 3001
    log_level: str = "INFO"
    debug: bool = False
    max_concurrent_requests: int = 10
    request_timeout: int = 30
    
    class Config:
        env_file = ".env"

settings = Settings()
```

## 🐳 Docker Support

### Quick Start with Docker

```bash
# Run with default settings
docker run -p 3000:3000 stgmt/crawl4ai-mcp

# With environment variables
docker run -p 3000:3000 \
  -e CRAWL4AI_ENDPOINT=http://crawl4ai:8000 \
  -e LOG_LEVEL=DEBUG \
  stgmt/crawl4ai-mcp

# With Docker Compose
docker-compose up
```

### Docker Compose

```yaml
version: '3.8'

services:
  crawl4ai-mcp:
    image: stgmt/crawl4ai-mcp
    ports:
      - "3000:3000"
      - "3001:3001"
    environment:
      - CRAWL4AI_ENDPOINT=http://crawl4ai:8000
      - LOG_LEVEL=INFO
    depends_on:
      - crawl4ai
      
  crawl4ai:
    image: crawl4ai/crawl4ai
    ports:
      - "8000:8000"
```

### Building Custom Image

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN pip install -e .

EXPOSE 3000 3001

CMD ["crawl4ai-mcp", "--http"]
```

## 🧪 Testing

### Running Tests

```bash
# Install test dependencies
pip install -e .[test]

# Run all tests
pytest

# Run with coverage
pytest --cov=crawl4ai_mcp

# Run specific test
pytest tests/test_server.py::test_crawl_tool
```

### Testing with MCP Server Tester

This MCP server can be comprehensively tested using the [MCP Server Tester](https://github.com/stgmt/mcp-server-tester-sse-http-stdio) that supports all three transport protocols (STDIO, SSE, HTTP).

#### Install MCP Server Tester

```bash
# Option 1: Using Docker (recommended)
docker run -it stgmt/mcp-server-tester test --help

# Option 2: Using NPM
npm install -g mcp-server-tester-sse-http-stdio
mcp-server-tester test --help

# Option 3: Using Python
pip install mcp-server-tester-sse-http-stdio
mcp-server-tester test --help
```

#### Test Examples

**Test STDIO mode:**

```bash
# Docker
docker run -it stgmt/mcp-server-tester test \
  --transport stdio \
  --command "CRAWL4AI_ENDPOINT=https://your-crawl4ai-server.com crawl4ai-mcp --stdio"

# NPM/Python
mcp-server-tester test \
  --transport stdio \
  --command "crawl4ai-mcp --stdio"
```

**Test HTTP mode:**

```bash
# Start the server first
crawl4ai-mcp --http &

# Run tests
mcp-server-tester test \
  --transport http \
  --url http://localhost:3000
```

**Test SSE mode:**

```bash
# Start the server first
crawl4ai-mcp --sse &

# Run tests
mcp-server-tester test \
  --transport sse \
  --url http://localhost:3001
```

**Test with configuration file:**

Create `test-config.yaml`:

```yaml
name: Crawl4AI Comprehensive Tests
transport: stdio
command: crawl4ai-mcp --stdio
tests:
  - name: Test markdown extraction
    tool: md
    arguments:
      url: https://example.com
      f: fit
    assert:
      - type: contains
        value: "Example Domain"
  
  - name: Test screenshot
    tool: screenshot
    arguments:
      url: https://example.com
      screenshot_wait_for: 2
    assert:
      - type: exists
        path: result
  
  - name: Test HTML extraction
    tool: html
    arguments:
      url: https://example.com
    assert:
      - type: contains
        value: "<html"
  
  - name: Test JavaScript execution
    tool: execute_js
    arguments:
      url: https://example.com
      scripts: ["document.title"]
    assert:
      - type: contains
        value: "Example"
```

Run the test:

```bash
mcp-server-tester test -f test-config.yaml
```

#### Interactive Testing

The tester also provides an interactive mode for manual testing:

```bash
# Interactive STDIO mode
mcp-server-tester interactive \
  --transport stdio \
  --command "crawl4ai-mcp --stdio"

# Interactive HTTP mode
mcp-server-tester interactive \
  --transport http \
  --url http://localhost:3000
```

## 📚 Examples

### Example 1: Extract Documentation

```python
# Extract markdown from documentation
result = await session.call_tool("md", {
    "url": "https://docs.python.org/3/",
    "clean": True
})
```

### Example 2: Monitor Price Changes

```python
# Screenshot for visual comparison
screenshot = await session.call_tool("screenshot", {
    "url": "https://store.example.com/product",
    "full_page": False
})

# Extract price via JavaScript
price = await session.call_tool("execute_js", {
    "url": "https://store.example.com/product",
    "script": "document.querySelector('.price').innerText"
})
```

### Example 3: Generate Reports

```python
# Generate PDF report
pdf = await session.call_tool("pdf", {
    "url": "https://analytics.example.com/report",
    "format": "A4",
    "landscape": True
})
```

## 🤝 Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Development Setup

```bash
# Clone the repository
git clone https://github.com/stgmt/crawl4ai-mcp.git
cd crawl4ai-mcp

# Install in development mode
pip install -e .[dev]

# Run tests
pytest

# Format code
black crawl4ai_mcp tests
ruff check --fix crawl4ai_mcp tests
```

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🔗 Links

- **PyPI Package**: [https://pypi.org/project/crawl4ai-mcp/](https://pypi.org/project/crawl4ai-mcp/)
- **GitHub Repository**: [https://github.com/stgmt/crawl4ai-mcp](https://github.com/stgmt/crawl4ai-mcp)
- **Documentation**: [https://github.com/stgmt/crawl4ai-mcp#readme](https://github.com/stgmt/crawl4ai-mcp#readme)
- **Issues**: [https://github.com/stgmt/crawl4ai-mcp/issues](https://github.com/stgmt/crawl4ai-mcp/issues)

## 🙏 Acknowledgments

- [Crawl4AI](https://github.com/unclecode/crawl4ai) - The powerful crawling engine
- [MCP](https://modelcontextprotocol.io) - Model Context Protocol specification
- [Anthropic](https://anthropic.com) - For creating the MCP standard

---

**Made with ❤️ for the AI community**
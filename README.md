# 🕷️ Crawl4AI MCP Server

[![PyPI version](https://badge.fury.io/py/crawl4ai-mcp.svg)](https://badge.fury.io/py/crawl4ai-mcp)
[![Python](https://img.shields.io/pypi/pyversions/crawl4ai-mcp.svg)](https://pypi.org/project/crawl4ai-mcp/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Downloads](https://pepy.tech/badge/crawl4ai-mcp)](https://pepy.tech/project/crawl4ai-mcp)

**MCP (Model Context Protocol) server for Crawl4AI** - Universal web crawling and data extraction for AI agents.

Integrate powerful web scraping capabilities into Claude, ChatGPT, and any MCP-compatible AI assistant.

## 📑 Table of Contents

- [🐳 Quick Start with Docker (Recommended)](#-quick-start-with-docker-recommended)
- [📦 Alternative Installation Methods](#-alternative-installation-methods)
- [🛠️ Available Tools](#️-available-tools)
- [🚀 Usage](#-usage)
- [⚙️ Configuration](#️-configuration)
- [🤝 Contributing](#-contributing)
- [📄 License](#-license)

## 🐳 Quick Start with Docker (Recommended)

**✨ Docker is the preferred way to run Crawl4AI MCP Server - everything is pre-installed and ready to go!**

### Option 1: Docker Hub Image (Latest)

```bash
# SSE mode (for web interfaces) - DEFAULT
docker run --rm -p 3001:9001 \
  -e CRAWL4AI_ENDPOINT="https://your-crawl4ai-server.com" \
  -e CRAWL4AI_BEARER_TOKEN="your-optional-token" \
  stgmt/crawl4ai-mcp:latest crawl4ai-mcp --sse

# HTTP mode (for REST API)
docker run --rm -p 3000:3000 \
  -e CRAWL4AI_ENDPOINT="https://your-crawl4ai-server.com" \
  -e CRAWL4AI_BEARER_TOKEN="your-optional-token" \
  stgmt/crawl4ai-mcp:latest crawl4ai-mcp --http --port 3000

# STDIO mode (for Claude Desktop)
docker run --rm -it \
  -e CRAWL4AI_ENDPOINT="https://your-crawl4ai-server.com" \
  -e CRAWL4AI_BEARER_TOKEN="your-optional-token" \
  stgmt/crawl4ai-mcp:latest crawl4ai-mcp --stdio
```

### Option 2: Build from Source (Latest fixes)

```bash
# Clone and build
git clone https://github.com/stgmt/crawl4ai-mcp.git
cd crawl4ai-mcp
docker build -t crawl4ai-mcp:local .

# Run SSE mode
docker run --rm -p 3001:9001 \
  -e CRAWL4AI_ENDPOINT="https://your-crawl4ai-server.com" \
  -e CRAWL4AI_BEARER_TOKEN="your-optional-token" \
  crawl4ai-mcp:local crawl4ai-mcp --sse
```

### With Claude Desktop (Docker)

Add to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "crawl4ai": {
      "command": "docker",
      "args": [
        "run", "--rm", "-i",
        "-e", "CRAWL4AI_ENDPOINT=https://your-crawl4ai-server.com",
        "-e", "CRAWL4AI_BEARER_TOKEN=your-optional-token",
        "stgmt/crawl4ai-mcp:latest",
        "crawl4ai-mcp", "--stdio"
      ]
    }
  }
}
```

## 📦 Alternative Installation Methods

### NPM Package

```bash
# Install globally
npm install -g crawl4ai-mcp-sse-stdio

# Run in different modes
npx crawl4ai-mcp --stdio
npx crawl4ai-mcp --sse
npx crawl4ai-mcp --http --port 3000
```

### Python Package (PyPI)

```bash
# Install from PyPI
pip install crawl4ai-mcp

# Set required endpoint and run
export CRAWL4AI_ENDPOINT="https://your-crawl4ai-server.com"
crawl4ai-mcp --stdio
```

### From Source

```bash
git clone https://github.com/stgmt/crawl4ai-mcp.git
cd crawl4ai-mcp
pip install -e .
```

### With Claude Desktop (Non-Docker)

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

## 🚀 Usage

The crawl4ai-mcp server supports multiple transport modes and provides comprehensive web crawling capabilities through the Model Context Protocol.

### Basic Commands

```bash
# HTTP mode (recommended for testing)
crawl4ai-mcp --http --port 3000

# SSE mode (Server-Sent Events)
crawl4ai-mcp --sse --port 3001

# STDIO mode (for MCP clients)
crawl4ai-mcp --stdio
```

### With Custom Endpoint

```bash
# Using custom Crawl4AI endpoint with bearer token
crawl4ai-mcp --http --port 3000 \
  --crawl4ai-endpoint "https://your-server.com" \
  --bearer-token "your-token"
```

See the [Python Integration](#python-integration-example) section for detailed code examples.

## ⚙️ Configuration

### Environment Variables

```bash
# REQUIRED: Crawl4AI endpoint URL
export CRAWL4AI_ENDPOINT="https://your-crawl4ai-server.com"

# OPTIONAL: Bearer authentication token
export CRAWL4AI_BEARER_TOKEN="your-api-token"
```

**Parameter Requirements:**
- `CRAWL4AI_ENDPOINT` - **Required** - The URL of your Crawl4AI server instance
- `CRAWL4AI_BEARER_TOKEN` - **Optional** - Bearer token for authenticated API access

### Command Line Options

```bash
crawl4ai-mcp --help

Options:
  --stdio              Run in STDIO mode for MCP clients
  --sse                Run in SSE mode for web interfaces (default)
  --http               Run in HTTP mode
  --endpoint ENDPOINT  Crawl4AI API endpoint URL (REQUIRED)
  --bearer-token TOKEN Bearer authentication token (OPTIONAL)
  --version, -v        Show version
```

## 🐍 Python Integration Example

Here's how to integrate the MCP server with your Python application using HTTP mode with bearer token authentication:

```python
import asyncio
import aiohttp
import json

async def test_crawl4ai_mcp():
    """
    Example: Using Crawl4AI MCP server via HTTP with bearer token
    """
    # Server configuration
    server_url = "http://localhost:3000"
    bearer_token = "your-api-token"  # Optional

    headers = {
        "Content-Type": "application/json"
    }

    # Add bearer token if available
    if bearer_token:
        headers["Authorization"] = f"Bearer {bearer_token}"

    async with aiohttp.ClientSession() as session:
        # 1. List available tools
        async with session.post(
            f"{server_url}/tools/list",
            headers=headers
        ) as response:
            tools = await response.json()
            print("Available tools:", [tool['name'] for tool in tools['tools']])

        # 2. Extract markdown from a webpage
        tool_request = {
            "name": "md",
            "arguments": {
                "url": "https://example.com",
                "clean": True
            }
        }

        async with session.post(
            f"{server_url}/tools/call",
            headers=headers,
            json=tool_request
        ) as response:
            result = await response.json()
            print("Markdown content:", result['content'][:200] + "...")

        # 3. Take a screenshot
        screenshot_request = {
            "name": "screenshot",
            "arguments": {
                "url": "https://example.com",
                "full_page": True
            }
        }

        async with session.post(
            f"{server_url}/tools/call",
            headers=headers,
            json=screenshot_request
        ) as response:
            result = await response.json()
            print("Screenshot saved:", result.get('path', 'Screenshot data returned'))

        # 4. Execute JavaScript on a page
        js_request = {
            "name": "execute_js",
            "arguments": {
                "url": "https://example.com",
                "script": "document.title"
            }
        }

        async with session.post(
            f"{server_url}/tools/call",
            headers=headers,
            json=js_request
        ) as response:
            result = await response.json()
            print("Page title:", result['content'])

# Run the example
if __name__ == "__main__":
    # First, start the MCP server in HTTP mode:
    # docker run -p 3000:3000 \
    #   -e CRAWL4AI_ENDPOINT="https://your-crawl4ai-server.com" \
    #   -e CRAWL4AI_BEARER_TOKEN="your-api-token" \
    #   stgmt/crawl4ai-mcp:latest crawl4ai-mcp --http --port 3000

    asyncio.run(test_crawl4ai_mcp())
```

### Installation for Python integration

```bash
pip install aiohttp  # For HTTP client
```

## 🤝 Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🔗 Links

- **PyPI Package**: [https://pypi.org/project/crawl4ai-mcp/](https://pypi.org/project/crawl4ai-mcp/)
- **NPM Package**: [https://www.npmjs.com/package/crawl4ai-mcp-sse-stdio](https://www.npmjs.com/package/crawl4ai-mcp-sse-stdio)
- **Docker Hub**: [https://hub.docker.com/r/stgmt/crawl4ai-mcp](https://hub.docker.com/r/stgmt/crawl4ai-mcp)
- **GitHub Repository**: [https://github.com/stgmt/crawl4ai-mcp](https://github.com/stgmt/crawl4ai-mcp)

---

**Made with ❤️ for the AI community**
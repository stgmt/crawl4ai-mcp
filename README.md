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
  stgmt/crawl4ai-mcp:latest crawl4ai-mcp --http

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
npx crawl4ai-mcp --http
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

## ⚙️ Configuration

### Required Settings

```bash
# REQUIRED: Crawl4AI endpoint
export CRAWL4AI_ENDPOINT="https://your-crawl4ai-server.com"

# OPTIONAL: Authentication token
export CRAWL4AI_BEARER_TOKEN="your-api-token"
```

### Command Line Options

```bash
crawl4ai-mcp --help

Options:
  --stdio              Run in STDIO mode for MCP clients
  --sse                Run in SSE mode for web interfaces (default)
  --http               Run in HTTP mode
  --endpoint ENDPOINT  Crawl4AI API endpoint URL
  --bearer-token TOKEN Bearer authentication token
  --version, -v        Show version
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
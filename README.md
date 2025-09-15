# 🕷️ Crawl4AI MCP Server

[![NPM version](https://badge.fury.io/js/crawl4ai-mcp-sse-stdio.svg)](https://badge.fury.io/js/crawl4ai-mcp-sse-stdio)
[![Node.js](https://img.shields.io/node/v/crawl4ai-mcp-sse-stdio.svg)](https://www.npmjs.com/package/crawl4ai-mcp-sse-stdio)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Downloads](https://img.shields.io/npm/dm/crawl4ai-mcp-sse-stdio.svg)](https://www.npmjs.com/package/crawl4ai-mcp-sse-stdio)
[![Author](https://img.shields.io/badge/Author-🤖_AI_Помогатор-blue?style=flat&logo=telegram)](https://t.me/ii_pomogator)

**MCP (Model Context Protocol) server for Crawl4AI** - Universal web crawling and data extraction for AI agents.

Integrate powerful web scraping capabilities into Claude, ChatGPT, and any MCP-compatible AI assistant.

## 📑 Table of Contents

- [🚀 Quick Start](#-quick-start)
- [🛠️ Available Tools](#️-available-tools)
- [⚙️ Configuration](#️-configuration)
- [🤝 Contributing](#-contributing)
- [📄 License](#-license)

## 🚀 Quick Start

### NPM Installation (Recommended)

```bash
# Install globally
npm install -g crawl4ai-mcp-sse-stdio

# Run in different modes
npx crawl4ai-mcp --stdio --endpoint https://your-crawl4ai-server.com
npx crawl4ai-mcp --sse --port 3001 --endpoint https://your-crawl4ai-server.com
npx crawl4ai-mcp --http --port 3000 --endpoint https://your-crawl4ai-server.com

# With optional bearer token
npx crawl4ai-mcp --stdio --endpoint https://your-crawl4ai-server.com --bearer-token your-token
```

### With Claude Desktop

Add to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "crawl4ai": {
      "command": "npx",
      "args": [
        "crawl4ai-mcp-sse-stdio",
        "--stdio",
        "--endpoint", "https://your-crawl4ai-server.com",
        "--bearer-token", "your-optional-token"
      ]
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

### Environment Variables

```bash
# REQUIRED: Crawl4AI endpoint URL
export CRAWL4AI_ENDPOINT="https://your-crawl4ai-server.com"

# OPTIONAL: Bearer authentication token
export CRAWL4AI_BEARER_TOKEN="your-api-token"
```

### Command Line Options

```bash
crawl4ai-mcp --help

Options:
  --stdio              Run in STDIO mode for MCP clients
  --sse                Run in SSE mode for web interfaces
  --http               Run in HTTP mode
  --endpoint ENDPOINT  Crawl4AI API endpoint URL (REQUIRED)
  --bearer-token TOKEN Bearer authentication token (OPTIONAL)
  --port PORT          HTTP server port (default: 3000)
  --sse-port PORT      SSE server port (default: 9001)
  --version, -v        Show version
```

### Basic Commands

```bash
# HTTP mode (recommended for testing)
crawl4ai-mcp --http --port 3000 --endpoint https://your-crawl4ai-server.com

# SSE mode (Server-Sent Events)
crawl4ai-mcp --sse --port 3001 --endpoint https://your-crawl4ai-server.com

# STDIO mode (for MCP clients)
crawl4ai-mcp --stdio --endpoint https://your-crawl4ai-server.com

# With optional bearer token
crawl4ai-mcp --http --port 3000 --endpoint https://your-crawl4ai-server.com --bearer-token your-token
```

## 🤝 Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🔗 Links

- **NPM Package**: [https://www.npmjs.com/package/crawl4ai-mcp-sse-stdio](https://www.npmjs.com/package/crawl4ai-mcp-sse-stdio)
- **GitHub Repository**: [https://github.com/stgmt/crawl4ai-mcp](https://github.com/stgmt/crawl4ai-mcp)

---

**Made with ❤️ for the AI community**
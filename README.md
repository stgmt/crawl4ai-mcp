# Crawl4AI MCP Server

Model Context Protocol (MCP) server for Crawl4AI with HTTP transport, Bearer token authentication, and comprehensive testing framework.

## 🚀 Quick Start

### Using the MCP Server

Add to your `.mcp.json`:

```json
{
  "mcpServers": {
    "crawl4ai-local": {
      "transport": "stdio",
      "command": "python",
      "args": ["-m", "python-mcp-server.src.server"],
      "env": {
        "CRAWL4AI_ENDPOINT": "https://your-crawl4ai-server.com"
      }
    },
    "crawl4ai-remote": {
      "transport": "http",
      "url": "https://your-mcp-server.com/mcp",
      "bearerToken": "your_bearer_token_here"
    }
  }
}
```

## 📁 Project Structure

```
crawl4ai-mcp/
├── python-mcp-server/     # Python MCP server implementation
│   ├── src/               # MCP server source code
│   ├── Dockerfile         # Docker configuration
│   ├── docker-compose.yml # Docker Compose setup
│   ├── requirements.txt   # Python dependencies
│   └── .env.example       # Environment variables example
├── mcp-server-tester/     # TypeScript MCP testing framework
│   ├── src/               # TypeScript source code
│   ├── test/              # Test suites
│   ├── examples/          # Usage examples
│   ├── package.json       # Node.js dependencies
│   └── test-all-tools.yaml # Test configuration
├── server-config.example.json # MCP configuration examples
├── BEARER_AUTH.md         # Authentication guide
└── README.md              # This file
```

## 🛠️ Available MCP Tools

| Tool | Description | Input Parameters |
|------|-------------|------------------|
| **`md`** | Convert URLs to Markdown | `url` (string) |
| **`html`** | Extract HTML content | `url` (string) |
| **`execute_js`** | Execute JavaScript on pages | `url` (string), `js_code` (string) |
| **`crawl`** | Advanced crawling with options | `urls` (array), `options` (object) |
| **`screenshot`** | Web page screenshots | `url` (string), `options` (object) |
| **`pdf`** | Convert pages to PDF | `url` (string), `options` (object) |

## 🔧 Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `CRAWL4AI_ENDPOINT` | `https://your-server.example.com` | Crawl4AI API server URL |
| `HTTP_PORT` | `3000` | HTTP transport port |
| `SSE_PORT` | `9001` | SSE transport port |
| `BEARER_TOKEN` | `None` | Bearer token for authentication |
| `LOG_LEVEL` | `INFO` | Logging level |
| `DEBUG` | `false` | Debug mode |
| `REQUEST_TIMEOUT` | `30` | HTTP request timeout (seconds) |

## 🏃‍♂️ Running the Server

### Python MCP Server

```bash
cd python-mcp-server/

# Install dependencies
pip install -r requirements.txt

# Run stdio transport
python -m src.server

# Run with custom endpoint
CRAWL4AI_ENDPOINT=https://your-server.com python -m src.server

# Docker
docker-compose up --build
```

### Testing with TypeScript Tester

```bash
cd mcp-server-tester/

# Install dependencies
npm install

# Build TypeScript
npm run build

# Run all tests
npm test

# Test specific tools
node dist/cli.js tools test-all-tools.yaml --server-config ../server-config.example.json
```

## 🔒 Authentication

### Bearer Token Setup

1. **Environment Variable**: Set `BEARER_TOKEN=your_token`
2. **HTTP Header**: Include `Authorization: Bearer your_token`

### Example Configuration

```json
{
  "mcpServers": {
    "crawl4ai": {
      "transport": "http",
      "url": "https://your-server.com/mcp",
      "bearerToken": "your_bearer_token_here"
    }
  }
}
```

For nginx proxy setup, see [BEARER_AUTH.md](BEARER_AUTH.md).

## 🧪 Testing

### Unit Tests
```bash
cd mcp-server-tester/
npm test
```

### Tool Testing
```bash
# Test all tools
node dist/cli.js tools test-all-tools.yaml --server-config server-config.json

# Test with local server
cp server-config.example.json server-config.json
# Edit server-config.json with your values
node dist/cli.js tools test-all-tools.yaml --server-config server-config.json
```

## 🌐 Supported Transports

- **stdio**: Standard input/output for local usage
- **HTTP**: Remote access via HTTP API with Bearer token support

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

---

**Ready for production use with comprehensive security and testing.**
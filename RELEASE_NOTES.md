# Release v1.0.4

## 🎉 Crawl4AI MCP Server v1.0.4

### 📝 What's New

#### 🧹 Cleanup and Optimization
- **Removed unnecessary directories** - cleaned up `mcp-server-tester`, `python-mcp-server` and other artifacts
- **Updated .gitignore** - added patterns for temporary files, logs and OS-specific files
- **Removed outdated setup.py** - project now fully uses `pyproject.toml`

#### 📚 Improved Documentation
- **Expanded testing section** - added detailed information about testing with MCP Server Tester
- **Added examples** for all three transport protocols (STDIO, SSE, HTTP)
- **Interactive testing** - documented commands for manual testing

#### 🔧 Technical Improvements
- **Synchronized versions** across all configuration files
- **Cleaned dependencies** in package.json and pyproject.toml
- **Updated index.js** with current version

### 🧪 Testing

Server can now be tested using [MCP Server Tester](https://github.com/stgmt/mcp-server-tester-sse-http-stdio):

```bash
# Docker
docker run -it stgmt/mcp-server-tester test \
  --transport stdio \
  --command "crawl4ai-mcp --stdio"

# NPM
npm install -g mcp-server-tester-sse-http-stdio
mcp-server-tester test --transport stdio --command "crawl4ai-mcp --stdio"
```

---

# Release v1.0.3

## 🎉 Crawl4AI MCP Server v1.0.3

### 📝 What's New

#### 🐛 Bug Fixes
- **Improved Python version detection for NPM package** - added support for `--user` and `--break-system-packages` flags for compatibility with different environments
- **Security** - removed sensitive tokens from test reports
- **Improved .gitignore** - added exclusion of Python cache files (__pycache__)

#### ✨ Improvements
- **NPM Package** - simplified installation with automatic fallback to system Python
- **Documentation** - updated README with clear installation instructions
- **Build Process** - improved multi-platform Docker builds

#### 🚀 Features
- **GitHub Actions** - added automated publishing workflows for PyPI, NPM and Docker Hub
- **Better Error Handling** - improved error messages for dependency issues
- **Cross-platform Support** - tested on Windows, macOS and Linux

### 📦 Installation

Now available through multiple channels:

```bash
# PyPI
pip install crawl4ai-mcp-sse-stdio

# NPM  
npm install crawl4ai-mcp-sse-stdio

# Docker
docker run -p 3000:3000 stgmt/crawl4ai-mcp:latest
```

### 🧪 Testing

Includes comprehensive tests with MCP Server Tester for all three transport modes.

---

# Release v1.0.2

## 🎉 Crawl4AI MCP Server v1.0.2

### 📝 What's New

#### 🔧 Technical Updates
- Fixed Python package dependencies
- Improved error handling in API calls
- Updated Docker build process

#### 📚 Documentation
- Added Docker Hub documentation
- Improved setup instructions
- Added troubleshooting guide

---

# Release v1.0.1

## 🎉 Crawl4AI MCP Server v1.0.1

### 📝 Initial Public Release

First public release of Crawl4AI MCP Server providing web crawling capabilities through Model Context Protocol.

#### Features
- Web page to markdown conversion
- HTML extraction
- Screenshot capture
- PDF generation
- JavaScript execution
- Bulk crawling support

#### Transport Support
- STDIO mode for local development
- SSE mode for streaming
- HTTP mode for REST API

#### Installation Methods
- PyPI package
- NPM package
- Docker container

### 🎯 Use Cases
- Web scraping
- Content extraction
- Documentation generation
- Website archival
- Data collection
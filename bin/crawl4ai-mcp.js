#!/usr/bin/env node

const { Crawl4AIMCPServer } = require('../server.js');

// Parse command line arguments
const args = process.argv.slice(2);
let mode = 'stdio';
let port = null;
let endpoint = null;
let bearerToken = null;

for (let i = 0; i < args.length; i++) {
  switch (args[i]) {
    case '--stdio':
      mode = 'stdio';
      break;
    case '--sse':
      mode = 'sse';
      break;
    case '--http':
      mode = 'http';
      break;
    case '--port':
      port = parseInt(args[i + 1]);
      i++;
      break;
    case '--sse-port':
      if (mode === 'sse') port = parseInt(args[i + 1]);
      i++;
      break;
    case '--endpoint':
      endpoint = args[i + 1];
      i++;
      break;
    case '--bearer-token':
      bearerToken = args[i + 1];
      i++;
      break;
    case '--help':
    case '-h':
      console.log(`
Usage: crawl4ai-mcp [options]

Options:
  --stdio              Run in STDIO mode for MCP clients (default)
  --sse                Run in SSE mode for web interfaces
  --http               Run in HTTP mode
  --endpoint ENDPOINT  Crawl4AI API endpoint URL (REQUIRED)
  --bearer-token TOKEN Bearer authentication token (OPTIONAL)
  --port PORT          HTTP server port (default: 3000)
  --sse-port PORT      SSE server port (default: 3001)
  --version, -v        Show version
  --help, -h           Show this help

Environment Variables:
  CRAWL4AI_ENDPOINT    Crawl4AI API endpoint URL
  CRAWL4AI_BEARER_TOKEN Bearer authentication token
  HTTP_PORT            HTTP server port
  SSE_PORT             SSE server port

Examples:
  crawl4ai-mcp --stdio --endpoint https://api.crawl4ai.com
  crawl4ai-mcp --http --port 3000 --endpoint https://api.crawl4ai.com
  crawl4ai-mcp --sse --sse-port 3001 --endpoint https://api.crawl4ai.com
      `);
      process.exit(0);
    case '--version':
    case '-v':
      console.log('1.2.0');
      process.exit(0);
  }
}

// Set environment variables
if (endpoint) process.env.CRAWL4AI_ENDPOINT = endpoint;
if (bearerToken) process.env.CRAWL4AI_BEARER_TOKEN = bearerToken;

// Use environment variables if not provided via CLI
if (!process.env.CRAWL4AI_ENDPOINT) {
  console.error('Error: CRAWL4AI_ENDPOINT is required');
  console.error('Use --endpoint or set CRAWL4AI_ENDPOINT environment variable');
  process.exit(1);
}

// Set default ports from environment if available
const httpPort = port || parseInt(process.env.HTTP_PORT) || 3000;
const ssePort = port || parseInt(process.env.SSE_PORT) || 3001;

// Create and run server
const server = new Crawl4AIMCPServer();

async function main() {
  try {
    switch (mode) {
      case 'stdio':
        await server.runStdio();
        break;
      case 'sse':
        await server.runSSE(ssePort);
        break;
      case 'http':
        await server.runHTTP(httpPort);
        break;
      default:
        console.error(`Unknown mode: ${mode}`);
        process.exit(1);
    }
  } catch (error) {
    console.error('Error starting server:', error.message);
    process.exit(1);
  }
}

main();
#!/usr/bin/env node

const { Server } = require('@modelcontextprotocol/sdk/server/index.js');
const { StdioServerTransport } = require('@modelcontextprotocol/sdk/server/stdio.js');
const { SSEServerTransport } = require('@modelcontextprotocol/sdk/server/sse.js');
const { ListToolsRequestSchema, CallToolRequestSchema } = require('@modelcontextprotocol/sdk/types.js');
const http = require('http');
const https = require('https');

class Crawl4AIMCPServer {
  constructor(endpoint, bearerToken) {
    this.endpoint = endpoint || process.env.CRAWL4AI_ENDPOINT;
    this.bearerToken = bearerToken || process.env.CRAWL4AI_BEARER_TOKEN;
    
    this.server = new Server(
      {
        name: 'crawl4ai-mcp',
        version: '1.1.0'
      },
      {
        capabilities: {
          tools: {},
        }
      }
    );
    
    this.tools = [
      {
        name: 'md',
        description: 'Convert webpage to clean markdown format with content filtering options',
        inputSchema: {
          type: 'object',
          properties: {
            url: { type: 'string', description: 'Target URL to crawl and convert to markdown' },
            c: { type: 'string', default: '0', description: 'Cache-bust counter for forcing fresh content' },
            f: { type: 'string', default: 'fit', enum: ['raw', 'fit', 'bm25', 'llm'], description: 'Content filter strategy' },
            q: { type: 'string', description: 'Query string for BM25/LLM content filtering' },
            provider: { type: 'string', description: 'LLM provider override (e.g., "anthropic/claude-3-opus")' }
          },
          required: ['url']
        }
      },
      {
        name: 'html',
        description: 'Get cleaned and preprocessed HTML content for further processing',
        inputSchema: {
          type: 'object',
          properties: {
            url: { type: 'string', description: 'Target URL to crawl and extract HTML from' }
          },
          required: ['url']
        }
      },
      {
        name: 'screenshot',
        description: 'Capture full-page PNG screenshot of specified URL with configurable wait time',
        inputSchema: {
          type: 'object',
          properties: {
            url: { type: 'string', description: 'Target URL to capture screenshot from' },
            output_path: { type: 'string', description: 'Optional path to save screenshot file' },
            screenshot_wait_for: { type: 'number', default: 2, description: 'Wait time in seconds before capturing screenshot' }
          },
          required: ['url']
        }
      },
      {
        name: 'pdf',
        description: 'Generate PDF document from webpage for archival or printing purposes',
        inputSchema: {
          type: 'object',
          properties: {
            url: { type: 'string', description: 'Target URL to convert to PDF document' },
            output_path: { type: 'string', description: 'Optional path to save PDF file' }
          },
          required: ['url']
        }
      },
      {
        name: 'execute_js',
        description: 'Execute JavaScript code on specified URL and return comprehensive results',
        inputSchema: {
          type: 'object',
          properties: {
            url: { type: 'string', description: 'Target URL to execute JavaScript on' },
            scripts: { 
              type: 'array', 
              items: { type: 'string' },
              description: 'List of JavaScript snippets to execute in order'
            }
          },
          required: ['url', 'scripts']
        }
      },
      {
        name: 'crawl',
        description: 'Crawl multiple URLs simultaneously and return comprehensive results for each',
        inputSchema: {
          type: 'object',
          properties: {
            urls: { 
              type: 'array', 
              items: { type: 'string' },
              maxItems: 100,
              minItems: 1,
              description: 'List of URLs to crawl (maximum 100 URLs)'
            },
            browser_config: { type: 'object', description: 'Browser configuration options (optional)' },
            crawler_config: { type: 'object', description: 'Crawler configuration options (optional)' }
          },
          required: ['urls']
        }
      }
    ];

    this.setupHandlers();
  }

  setupHandlers() {
    // List tools handler
    this.server.setRequestHandler(ListToolsRequestSchema, async () => ({
      tools: this.tools
    }));

    // Call tool handler
    this.server.setRequestHandler(CallToolRequestSchema, async (request) => {
      const { name, arguments: args } = request.params;
      
      try {
        const result = await this.callCrawl4AI(name, args);
        return {
          content: [
            {
              type: 'text',
              text: JSON.stringify(result, null, 2)
            }
          ]
        };
      } catch (error) {
        return {
          content: [
            {
              type: 'text',
              text: `Error: ${error.message}`
            }
          ],
          isError: true
        };
      }
    });
  }

  async callCrawl4AI(toolName, args) {
    if (!this.endpoint) {
      throw new Error('CRAWL4AI_ENDPOINT environment variable is required');
    }

    // Map tool calls to API endpoints
    const endpointMap = {
      'md': '/md',
      'html': '/html', 
      'screenshot': '/screenshot',
      'pdf': '/pdf',
      'execute_js': '/execute_js',
      'crawl': '/crawl'
    };

    const apiPath = endpointMap[toolName];
    if (!apiPath) {
      throw new Error(`Unknown tool: ${toolName}`);
    }

    const url = `${this.endpoint}${apiPath}`;
    const headers = {
      'Content-Type': 'application/json'
    };
    
    if (this.bearerToken) {
      headers['Authorization'] = `Bearer ${this.bearerToken}`;
    }

    const response = await this.httpRequest(url, {
      method: 'POST',
      headers,
      body: JSON.stringify(args)
    });

    return response;
  }

  httpRequest(url, options = {}) {
    return new Promise((resolve, reject) => {
      const urlObj = new URL(url);
      const isHttps = urlObj.protocol === 'https:';
      const httpModule = isHttps ? https : http;
      
      const reqOptions = {
        hostname: urlObj.hostname,
        port: urlObj.port || (isHttps ? 443 : 80),
        path: urlObj.pathname + urlObj.search,
        method: options.method || 'GET',
        headers: options.headers || {}
      };

      const req = httpModule.request(reqOptions, (res) => {
        let data = '';
        res.on('data', chunk => data += chunk);
        res.on('end', () => {
          if (res.statusCode >= 400) {
            reject(new Error(`HTTP ${res.statusCode}: ${data}`));
            return;
          }
          try {
            const parsed = JSON.parse(data);
            resolve(parsed);
          } catch (e) {
            resolve(data);
          }
        });
      });

      req.on('error', reject);
      
      if (options.body) {
        req.write(options.body);
      }
      
      req.end();
    });
  }

  async runStdio() {
    const transport = new StdioServerTransport();
    await this.server.connect(transport);
    console.error('Crawl4AI MCP Server running on stdio');
  }

  async runSSE(port = 3001) {
    const httpServer = http.createServer();
    const transport = new SSEServerTransport('/sse', httpServer);
    await this.server.connect(transport);
    
    httpServer.listen(port, () => {
      console.error(`Crawl4AI MCP Server running on SSE port ${port}`);
    });
  }

  async runHTTP(port = 3000) {
    const server = http.createServer(async (req, res) => {
      res.setHeader('Access-Control-Allow-Origin', '*');
      res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
      res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Authorization');

      if (req.method === 'OPTIONS') {
        res.writeHead(200);
        res.end();
        return;
      }

      if (req.method === 'GET' && req.url === '/') {
        res.writeHead(200, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({
          name: 'crawl4ai-mcp',
          version: '1.1.0',
          status: 'running',
          tools: this.tools.map(t => t.name)
        }));
        return;
      }

      if (req.method === 'POST') {
        let body = '';
        req.on('data', chunk => {
          body += chunk.toString();
        });
        
        req.on('end', async () => {
          try {
            const data = JSON.parse(body);
            const { method, params, id } = data;
            
            if (method === 'tools/list') {
              res.writeHead(200, { 'Content-Type': 'application/json' });
              res.end(JSON.stringify({ 
                jsonrpc: '2.0', 
                id, 
                result: { tools: this.tools } 
              }));
            } else if (method === 'tools/call') {
              try {
                const { name, arguments: args } = params;
                const result = await this.callCrawl4AI(name, args);
                res.writeHead(200, { 'Content-Type': 'application/json' });
                res.end(JSON.stringify({ 
                  jsonrpc: '2.0', 
                  id, 
                  result: { 
                    content: [{ 
                      type: 'text', 
                      text: JSON.stringify(result, null, 2) 
                    }] 
                  } 
                }));
              } catch (error) {
                res.writeHead(200, { 'Content-Type': 'application/json' });
                res.end(JSON.stringify({ 
                  jsonrpc: '2.0', 
                  id, 
                  result: { 
                    content: [{ 
                      type: 'text', 
                      text: `Error: ${error.message}` 
                    }],
                    isError: true 
                  } 
                }));
              }
            } else {
              res.writeHead(404, { 'Content-Type': 'application/json' });
              res.end(JSON.stringify({ jsonrpc: '2.0', id, error: { code: -32601, message: 'Method not found' } }));
            }
          } catch (error) {
            res.writeHead(500, { 'Content-Type': 'application/json' });
            res.end(JSON.stringify({ jsonrpc: '2.0', error: { code: -32603, message: error.message } }));
          }
        });
        return;
      }

      res.writeHead(404);
      res.end('Not Found');
    });

    server.listen(port, () => {
      console.error(`Crawl4AI MCP Server running on HTTP port ${port}`);
    });
  }
}

module.exports = { Crawl4AIMCPServer };
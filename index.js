// Main entry point for the NPM package
// This package provides a wrapper for the Python crawl4ai-mcp-sse-stdio server

module.exports = {
  name: 'crawl4ai-mcp-sse-stdio',
  version: '1.0.5',
  description: 'MCP server for Crawl4AI - Universal web crawling and data extraction',
  
  // MCP configuration helper
  getMCPConfig: (transport = 'stdio', args = []) => {
    const configs = {
      stdio: {
        command: 'npx',
        args: ['crawl4ai-mcp', '--stdio', ...args]
      },
      sse: {
        command: 'npx', 
        args: ['crawl4ai-mcp', '--sse', ...args]
      },
      http: {
        command: 'npx',
        args: ['crawl4ai-mcp', '--http', ...args]
      }
    };
    
    return configs[transport] || configs.stdio;
  },
  
  // Helper to generate Claude Desktop config
  getClaudeConfig: () => {
    return {
      mcpServers: {
        'crawl4ai': {
          command: 'npx',
          args: ['crawl4ai-mcp', '--stdio']
        }
      }
    };
  }
};
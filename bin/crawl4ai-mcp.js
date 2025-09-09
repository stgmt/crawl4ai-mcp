#!/usr/bin/env node

const { spawn } = require('child_process');
const path = require('path');

// Get command line arguments
const args = process.argv.slice(2);

// Check if Python is installed
const checkPython = () => {
  return new Promise((resolve) => {
    const pythonCommands = ['python3', 'python'];
    let index = 0;
    
    const tryNext = () => {
      if (index >= pythonCommands.length) {
        resolve(null);
        return;
      }
      
      const cmd = pythonCommands[index++];
      const check = spawn(cmd, ['--version']);
      
      check.on('error', tryNext);
      check.on('exit', (code) => {
        if (code === 0) {
          resolve(cmd);
        } else {
          tryNext();
        }
      });
    };
    
    tryNext();
  });
};

// Main function
const main = async () => {
  const pythonCmd = await checkPython();
  
  if (!pythonCmd) {
    console.error('Error: Python is not installed or not in PATH');
    console.error('Please install Python 3.9 or later from https://www.python.org/');
    process.exit(1);
  }
  
  // Check if the Python package is installed
  const checkPackage = spawn(pythonCmd, ['-m', 'crawl4ai_mcp', '--help']);
  
  checkPackage.on('error', (error) => {
    console.error('Error checking crawl4ai-mcp-sse-stdio installation:', error.message);
    console.error('Please run: npm install -g crawl4ai-mcp-sse-stdio');
    process.exit(1);
  });
  
  checkPackage.on('exit', (code) => {
    if (code !== 0) {
      console.error('crawl4ai-mcp-sse-stdio Python package is not installed.');
      console.error('Installing it now...');
      
      // Try to install the package
      const install = spawn(pythonCmd, ['-m', 'pip', 'install', 'crawl4ai-mcp-sse-stdio']);
      
      install.stdout.on('data', (data) => {
        process.stdout.write(data);
      });
      
      install.stderr.on('data', (data) => {
        process.stderr.write(data);
      });
      
      install.on('exit', (installCode) => {
        if (installCode === 0) {
          console.log('Successfully installed crawl4ai-mcp-sse-stdio');
          runServer(pythonCmd, args);
        } else {
          console.error('Failed to install crawl4ai-mcp-sse-stdio');
          process.exit(1);
        }
      });
    } else {
      runServer(pythonCmd, args);
    }
  });
};

// Run the server
const runServer = (pythonCmd, args) => {
  const server = spawn(pythonCmd, ['-m', 'crawl4ai_mcp', ...args], {
    stdio: 'inherit'
  });
  
  server.on('error', (error) => {
    console.error('Error starting server:', error.message);
    process.exit(1);
  });
  
  server.on('exit', (code) => {
    process.exit(code || 0);
  });
  
  // Handle signals
  process.on('SIGINT', () => {
    server.kill('SIGINT');
  });
  
  process.on('SIGTERM', () => {
    server.kill('SIGTERM');
  });
};

// Run main
main().catch((error) => {
  console.error('Unexpected error:', error);
  process.exit(1);
});
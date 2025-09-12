#!/usr/bin/env node

const { spawn } = require('child_process');
const path = require('path');

// Get command line arguments
const args = process.argv.slice(2);

// Check if Python is installed and meets version requirements
const checkPython = () => {
  return new Promise((resolve) => {
    // Try different Python commands in order of preference
    const pythonCommands = [
      'python3.13',
      'python3.12', 
      'python3.11',
      'python3.10',
      'python3',
      'python'
    ];
    let index = 0;
    
    const tryNext = () => {
      if (index >= pythonCommands.length) {
        resolve(null);
        return;
      }
      
      const cmd = pythonCommands[index++];
      const check = spawn(cmd, ['--version']);
      let output = '';
      
      check.stdout.on('data', (data) => {
        output += data.toString();
      });
      
      check.on('error', tryNext);
      check.on('exit', (code) => {
        if (code === 0) {
          // Parse version to check if >= 3.10
          const match = output.match(/Python (\d+)\.(\d+)/);
          if (match) {
            const major = parseInt(match[1]);
            const minor = parseInt(match[2]);
            if (major === 3 && minor >= 10) {
              console.log(`Using ${cmd} (${output.trim()})`);
              resolve(cmd);
              return;
            }
          }
          tryNext();
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
  // Check for --help or --version early
  if (args.length > 0 && (args[0] === '--help' || args[0] === '-h' || args[0] === 'help' || args[0] === '--version' || args[0] === '-v' || args[0] === 'version')) {
    // Just pass through to Python directly for help/version
    const pythonCmd = await checkPython();
    
    if (!pythonCmd) {
      console.error('Error: Python 3.10+ is not installed or not in PATH');
      console.error('Please install Python 3.10 or later from https://www.python.org/');
      console.error('Or use: brew install python@3.11');
      process.exit(1);
    }
    
    runServer(pythonCmd, args);
    return;
  }
  
  const pythonCmd = await checkPython();
  
  if (!pythonCmd) {
    console.error('Error: Python 3.10+ is not installed or not in PATH');
    console.error('Please install Python 3.10 or later from https://www.python.org/');
    console.error('Or use: brew install python@3.11');
    process.exit(1);
  }
  
  // Check if the Python package is installed (using --version instead of --help)
  const checkPackage = spawn(pythonCmd, ['-m', 'crawl4ai_mcp', '--version']);
  let checkOutput = '';
  
  checkPackage.stdout.on('data', (data) => {
    checkOutput += data.toString();
  });
  
  checkPackage.stderr.on('data', (data) => {
    checkOutput += data.toString();
  });
  
  checkPackage.on('error', (error) => {
    console.error('Error checking crawl4ai-mcp-sse-stdio installation:', error.message);
    console.error('Please run: npm install -g crawl4ai-mcp-sse-stdio');
    process.exit(1);
  });
  
  checkPackage.on('exit', (code) => {
    // If --version returns 0, package is installed
    if (code === 0 && checkOutput.includes('version')) {
      runServer(pythonCmd, args);
    } else {
      console.error('crawl4ai-mcp-sse-stdio Python package is not installed.');
      console.error('Installing it now...');
      
      // Try to install the package with --user flag for modern Python
      const install = spawn(pythonCmd, ['-m', 'pip', 'install', '--user', '--break-system-packages', 'crawl4ai-mcp-sse-stdio']);
      
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
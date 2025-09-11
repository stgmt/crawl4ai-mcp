#!/usr/bin/env node

const { exec } = require('child_process');
const os = require('os');

console.log('📦 Installing crawl4ai-mcp-sse-stdio Python package...');

// Detect Python command
const pythonCommands = process.platform === 'win32' 
  ? ['py -3', 'python', 'python3']
  : ['python3', 'python'];

let pythonCmd = null;

const checkPython = (commands, index = 0) => {
  if (index >= commands.length) {
    console.log('\n⚠️  Python is not installed or not in PATH');
    console.log('📝 Please install Python 3.9+ from https://www.python.org/');
    console.log('📝 Then run: pip install crawl4ai-mcp-sse-stdio');
    return;
  }
  
  const cmd = commands[index];
  exec(`${cmd} --version`, (error, stdout, stderr) => {
    if (!error && stdout.includes('Python 3')) {
      pythonCmd = cmd;
      installPackage(cmd);
    } else {
      checkPython(commands, index + 1);
    }
  });
};

const installPackage = (pythonCmd) => {
  console.log(`✅ Found Python: ${pythonCmd}`);
  console.log('📥 Installing crawl4ai-mcp-sse-stdio from PyPI...');
  
  const pipInstall = exec(`${pythonCmd} -m pip install --upgrade crawl4ai-mcp-sse-stdio`, 
    { maxBuffer: 10 * 1024 * 1024 }
  );
  
  pipInstall.stdout.on('data', (data) => {
    process.stdout.write(data);
  });
  
  pipInstall.stderr.on('data', (data) => {
    // pip often writes to stderr even on success
    if (data.includes('WARNING') || data.includes('Requirement already satisfied')) {
      process.stdout.write(data);
    } else {
      process.stderr.write(data);
    }
  });
  
  pipInstall.on('exit', (code) => {
    if (code === 0) {
      console.log('\n✅ Successfully installed crawl4ai-mcp-sse-stdio');
      console.log('🚀 You can now use: npx crawl4ai-mcp --help');
    } else {
      console.log('\n⚠️  Failed to install Python package automatically');
      console.log('📝 Please install manually: pip install crawl4ai-mcp-sse-stdio');
    }
  });
};

// Start the check
checkPython(pythonCommands);
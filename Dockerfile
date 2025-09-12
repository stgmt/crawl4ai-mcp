# Docker image for NPM package usage
# Uses Node.js and installs NPM package globally
FROM node:18-slim

# Install Python 3.11 and required dependencies
RUN apt-get update && apt-get install -y \
    python3.11 \
    python3.11-dev \
    python3.11-venv \
    python3-pip \
    curl \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Create symlinks for Python
RUN ln -sf /usr/bin/python3.11 /usr/bin/python3 && \
    ln -sf /usr/bin/python3.11 /usr/bin/python

# Ensure pip is installed for Python 3.11
RUN python3.11 -m ensurepip || true
RUN python3.11 -m pip install --upgrade pip || pip3 install --upgrade pip

# Install the NPM package globally
RUN npm install -g crawl4ai-mcp-sse-stdio

# Create working directory
WORKDIR /app

# Expose ports for HTTP and SSE
EXPOSE 3000 3001

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:3000/health || exit 1

# Default command - run via NPM
CMD ["crawl4ai-mcp", "--http", "--port", "3000"]
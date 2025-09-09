# Docker image for NPM package usage
# Uses Node.js and installs NPM package globally
FROM node:18-slim

# Install Python 3.11 (required by NPM package)
RUN apt-get update && apt-get install -y \
    python3.11 \
    python3-pip \
    python3.11-venv \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create symlinks for Python
RUN ln -sf /usr/bin/python3.11 /usr/bin/python3 && \
    ln -sf /usr/bin/python3.11 /usr/bin/python

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
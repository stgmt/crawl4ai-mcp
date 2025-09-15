# FIXED: Docker image with Node.js + Python + pre-installed packages
# No more runtime dependency installation!
FROM node:18-slim

# Install Python 3.11 and build tools (required for pip packages)
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3.11 \
    python3-pip \
    python3.11-venv \
    curl \
    build-essential \
    python3.11-dev \
    && rm -rf /var/lib/apt/lists/*

# Create symlinks for Python
RUN ln -sf /usr/bin/python3.11 /usr/bin/python3 && \
    ln -sf /usr/bin/python3.11 /usr/bin/python

# Install the NPM package globally
RUN npm install -g crawl4ai-mcp-sse-stdio@1.0.9

# Copy the local Python package
COPY . /app

# 🔥 CRITICAL FIX: Install local Python package instead of PyPI version
WORKDIR /app
RUN pip install --no-cache-dir --break-system-packages .

# Expose ports for HTTP and SSE
EXPOSE 3000 3001

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:3000/health || exit 1

# Default command - run via NPM (now works without installing dependencies!)
CMD ["crawl4ai-mcp", "--http", "--port", "3000"]
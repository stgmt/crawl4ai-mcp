# Multi-stage build for optimized image size
FROM python:3.11-slim as builder

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /build

# Copy only requirements first for better caching
COPY requirements.txt .
COPY pyproject.toml .
COPY setup.py .

# Install Python dependencies
RUN pip install --no-cache-dir --user -r requirements.txt && \
    pip install --no-cache-dir --user build

# Copy source code
COPY crawl4ai_mcp/ ./crawl4ai_mcp/
COPY README.md .
COPY LICENSE .

# Build the package
RUN python -m build --wheel --outdir /build/dist

# Final stage - minimal runtime image
FROM python:3.11-slim

# Create non-root user
RUN useradd -m -u 1000 mcp && \
    mkdir -p /app && \
    chown -R mcp:mcp /app

# Set working directory
WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /root/.local /home/mcp/.local
COPY --from=builder /build/dist/*.whl /tmp/

# Install the package
RUN pip install --no-cache-dir /tmp/*.whl && \
    rm /tmp/*.whl

# Copy configuration examples
COPY --chown=mcp:mcp examples/ /app/examples/

# Switch to non-root user
USER mcp

# Add local bin to PATH
ENV PATH="/home/mcp/.local/bin:${PATH}"

# Expose ports for HTTP and SSE
EXPOSE 3000 3001

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import httpx; httpx.get('http://localhost:3000/health')" || exit 1

# Default command - HTTP mode
CMD ["crawl4ai-mcp", "--http"]
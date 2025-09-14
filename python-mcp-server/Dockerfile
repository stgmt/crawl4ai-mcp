# Multi-stage build for optimized container
FROM python:3.11-slim as builder

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc=4:11.2.0-1ubuntu1 \
    && rm -rf /var/lib/apt/lists/*

# Set working directory for builder stage
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Production stage
FROM python:3.11-slim

# Create app user for security
RUN useradd --create-home --shell /bin/bash app

# Copy Python packages from builder
COPY --from=builder /root/.local /home/app/.local

# Set up working directory
WORKDIR /app
COPY src/ ./src/
COPY .env.example ./.env

# Fix permissions
RUN chown -R app:app /app
USER app

# Add local packages to PATH
ENV PATH=/home/app/.local/bin:$PATH
ENV PYTHONPATH=/app

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:3000/health', timeout=5)" || exit 1

# Expose ports
EXPOSE 3000 9000

# Default command (StreamableHTTP mode)
CMD ["python", "src/server.py"]

# Alternative commands:
# SSE mode: CMD ["python", "src/server.py", "--sse"]  
# STDIO mode: CMD ["python", "src/server.py", "--stdio"]
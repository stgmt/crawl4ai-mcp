# 🐳 Crawl4AI MCP Server - Node.js NPM Package
# Multi-stage build for optimized production image

FROM node:18-alpine AS base

# Set working directory
WORKDIR /app

# Install dumb-init for proper signal handling
RUN apk add --no-cache dumb-init

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci --only=production && npm cache clean --force

# Copy application code
COPY . .

# Remove development files
RUN rm -rf \
    node_modules/.cache \
    examples/ \
    mcp-server-tester/ \
    *.tgz \
    .env.example \
    server-config.example.json \
    CONTRIBUTING.md \
    RELEASE_NOTES.md

# Create non-root user
RUN addgroup -g 1001 -S nodejs && \
    adduser -S crawl4ai -u 1001 -G nodejs

# Change ownership of the app directory
RUN chown -R crawl4ai:nodejs /app
USER crawl4ai

# Environment variables
ENV NODE_ENV=production
ENV PORT=3000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD node -e "http.get('http://localhost:3000/', (res) => process.exit(res.statusCode === 200 ? 0 : 1))" || exit 1

# Expose port
EXPOSE 3000

# Use dumb-init to handle signals properly
ENTRYPOINT ["dumb-init", "--"]

# Default command - HTTP mode
CMD ["node", "bin/crawl4ai-mcp.js", "--http", "--port", "3000"]
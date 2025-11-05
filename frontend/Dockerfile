# Multi-stage Dockerfile for Q-IDE Frontend
# Optimized for Kubernetes deployment with auto-scaling

# ============================================================================
# Stage 1: Runtime - Serve the built application
# ============================================================================
FROM node:20-alpine

WORKDIR /app

# Install serve to run the static files
RUN npm install -g serve

# Copy pre-built frontend dist (assumes build ran in CI to produce frontend/dist)
COPY frontend/dist ./dist

# Copy entrypoint that injects runtime env into env.js
COPY frontend/docker-entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# Create non-root user for security
RUN addgroup -g 1001 -S nodejs && \
    adduser -S nextjs -u 1001

# Set ownership
RUN chown -R nextjs:nodejs /app

# Switch to non-root user
USER nextjs

# Expose port
EXPOSE 3000

# Environment variables
ENV NODE_ENV=production

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD node -e "require('http').get('http://localhost:3000', (r) => {if (r.statusCode !== 200) throw new Error(r.statusCode)})" || exit 1

# Start the application
CMD ["/bin/sh", "/app/entrypoint.sh"]

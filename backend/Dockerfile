# Multi-stage Dockerfile for Q-IDE Backend
# Production-ready FastAPI backend optimized for Kubernetes auto-scaling

# ============================================================================
# Stage 1: Base - System dependencies
# ============================================================================
FROM python:3.11-slim AS base

# Set environment variables to prevent Python from writing .pyc files and buffering
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    postgresql-client \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# ============================================================================
# Stage 2: Frontend - Build SPA assets with Node
# ============================================================================
FROM node:20-alpine AS frontend

WORKDIR /app

# Install deps and build Vite app
COPY frontend/package.json ./package.json
# If lockfile exists in future, prefer: COPY frontend/package-lock.json ./package-lock.json and `npm ci`
# Temporary workaround: React 19 peer dependency mismatch for @stripe/react-stripe-js
# Use --legacy-peer-deps to bypass until upstream releases React 19 compatible version
RUN npm install --no-fund --no-audit --legacy-peer-deps
COPY frontend/ .
RUN npm run build

# ============================================================================
# Stage 3: Dependencies - Build Python dependencies
# ============================================================================
FROM base AS dependencies

# Copy requirements
COPY backend/requirements.txt ./requirements.txt

# Install Python dependencies as root in /usr/local/lib/python3.11/site-packages
RUN pip install --no-warn-script-location -r requirements.txt

# ============================================================================
# Stage 4: Runtime - Final production image
# ============================================================================
FROM base AS runtime

# Create non-root user for security (important for Kubernetes)
RUN useradd -m -u 1001 appuser && \
    mkdir -p /app/logs && \
    chown -R appuser:appuser /app

# Copy Python dependencies from dependencies stage (already in system python path)
COPY --from=dependencies /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=dependencies /usr/local/bin /usr/local/bin

# Copy application code (backend and ancillary files)
COPY --chown=appuser:appuser . .

# Copy built frontend assets into expected location for backend static serving
COPY --from=frontend --chown=appuser:appuser /app/dist /app/frontend/dist

# Switch to non-root user
USER appuser

# Environment variables for Python path (already installed in system)
ENV PYTHONPATH=/app:$PYTHONPATH

# Expose port for the application
EXPOSE 8000

# Health check - critical for Kubernetes liveness probes
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run the FastAPI application with gunicorn for production
# gunicorn provides:
# - Multiple worker processes for concurrency
# - Graceful shutdown for rolling updates
# - Better resource management
CMD ["gunicorn", \
    "--workers=4", \
    "--worker-class=uvicorn.workers.UvicornWorker", \
    "--bind=0.0.0.0:8000", \
    "--timeout=120", \
    "--access-logfile=-", \
    "--error-logfile=-", \
    "--log-level=info", \
    "backend.main:app"]

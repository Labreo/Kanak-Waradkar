# =============================================================================
# Project TRIAD — Unified Production Multi-Stage Dockerfile
# Stage 1: Build the Vite Frontend SPA Bundle
# Stage 2: Python 3.12 Backend API & Static Hosting Server
# =============================================================================

# --- Stage 1: Frontend Build ---
FROM node:22-alpine AS frontend-builder
WORKDIR /build

# Install dependencies
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci

# Copy frontend source and build optimized production bundle
COPY frontend/ ./
RUN npm run build

# --- Stage 2: Python Backend Runtime ---
FROM python:3.12-slim AS runner
WORKDIR /app

# Prevent Python from writing .pyc files and buffer stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    HOST=0.0.0.0 \
    PORT=8000 \
    ENVIRONMENT=production

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python requirements
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend, defend, generate, loop, identify, and data directories
COPY backend/ ./backend/
COPY defend/ ./defend/
COPY generate/ ./generate/
COPY loop/ ./loop/
COPY identify/ ./identify/
COPY data/ ./data/
COPY scripts/ ./scripts/

# Copy built frontend assets from stage 1
COPY --from=frontend-builder /build/dist ./frontend/dist

# Expose standard port
EXPOSE 8000

# Healthcheck
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD curl -f http://127.0.0.1:8000/api/health || exit 1

# Start unified FastAPI server (binds dynamically to $PORT or default 8000)
CMD ["sh", "-c", "python -m backend.server --host 0.0.0.0 --port ${PORT:-8000}"]

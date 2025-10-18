# AIMQ Worker Docker Image (Published)
# This image is designed for deployment where users provide their own tasks.py
# via volume mount or git URL environment variable.
#
# Built from source during CI/CD to ensure version consistency.
#
# Usage:
#   Volume mount: docker run -v ./tasks.py:/app/tasks.py -v ./.env:/app/.env aimq:latest
#   Git URL:      docker run -e AIMQ_TASKS=git:user/repo@branch aimq:latest
#
# Multi-stage build for minimal final image size

# Stage 1: Builder - Install dependencies and build package
FROM python:3.12-slim AS builder

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    git \
    && rm -rf /var/lib/apt/lists/* /var/cache/apt/archives/*

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /build

# Copy package files for dependency resolution
COPY pyproject.toml uv.lock README.md .python-version ./

# Copy source code
COPY src ./src

# Install the package and its dependencies using uv
# --frozen: Use exact versions from lockfile
# This ensures reproducible builds
RUN uv sync --frozen

# Stage 2: Runtime - Minimal image with only runtime dependencies
FROM python:3.12-slim

# Install runtime dependencies for AI/ML libraries and git
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 \
    libglib2.0-0 \
    libgomp1 \
    git \
    && rm -rf /var/lib/apt/lists/* /var/cache/apt/archives/*

# Create non-root user for security
RUN groupadd -r aimq && useradd -r -g aimq aimq

WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /build/.venv/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages

# Copy the aimq source code (required since it's installed in editable mode)
COPY --from=builder /build/src/aimq /usr/local/lib/python3.12/site-packages/aimq

# Change ownership to non-root user
RUN chown -R aimq:aimq /app

USER aimq

# Disable Python output buffering for better logging
ENV PYTHONUNBUFFERED=1

# Default command starts the worker using Python module execution
# Users can override with volume mount or AIMQ_TASKS environment variable:
# - Volume: -v ./tasks.py:/app/tasks.py
# - Git URL: -e AIMQ_TASKS=git:user/repo@branch
# - Git subdir: -e AIMQ_TASKS=git:user/monorepo#services/worker
ENTRYPOINT ["python", "-m", "aimq"]
CMD ["start"]

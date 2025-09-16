# Stage 1: Build dependencies and install app
FROM python:3.12-slim AS builder

# Install build dependencies in one layer and clean up
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libgl1 \
    libglib2.0-0 \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/* /var/cache/apt/archives/*

# Install Poetry
RUN pip install --no-cache-dir poetry

WORKDIR /app

# Copy dependency files first for better caching
COPY pyproject.toml poetry.lock* README.md ./

# Configure Poetry and install dependencies (skip installing the current project)
RUN poetry config virtualenvs.create false && \
    poetry install --no-interaction --no-ansi --only main --no-root && \
    pip uninstall -y poetry && \
    pip cache purge

# Copy source code
COPY src ./src

# Remove unnecessary files to reduce layer size
RUN find /usr/local/lib/python3.12/site-packages -name "*.pyc" -delete && \
    find /usr/local/lib/python3.12/site-packages -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true && \
    find /usr/local/lib/python3.12/site-packages -name "*.pyo" -delete

# Stage 2: Minimal runtime image
FROM python:3.12-slim

# Install only runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 \
    libglib2.0-0 \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/* /var/cache/apt/archives/*

# Create non-root user for security
RUN groupadd -r aimq && useradd -r -g aimq aimq

WORKDIR /app

# Copy only necessary Python packages (more selective copying)
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin/python* /usr/local/bin/
COPY --from=builder /app/src ./src

# Change ownership to non-root user
RUN chown -R aimq:aimq /app

USER aimq

# Ensure the aimq package is in the Python path
ENV PYTHONPATH=/app/src

# Expose port if needed
# EXPOSE 8080

CMD ["python", "-m", "aimq.worker"]

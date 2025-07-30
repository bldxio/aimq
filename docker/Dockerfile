# Stage 1: Build dependencies and install app
FROM python:3.12-slim AS builder

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libgl1 \
    libglib2.0-0 \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

RUN curl -sSL https://install.python-poetry.org | python3 - && \
    ln -s /root/.local/bin/poetry /usr/local/bin/poetry

WORKDIR /app

COPY pyproject.toml poetry.lock* README.md ./
COPY src ./src

RUN poetry config virtualenvs.create false && \
    poetry install --no-interaction --no-ansi --only main && \
    poetry show

# Stage 2: Runtime image
FROM python:3.12-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy the entire Python environment from builder
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin
COPY --from=builder /app /app

# Ensure the aimq package is in the Python path
ENV PYTHONPATH=/app/src

# Expose port if needed
# EXPOSE 8080

CMD ["python", "-m", "aimq.worker"]

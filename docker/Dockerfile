FROM python:3.12-slim

# System dependencies for Poetry, OCR, and image processing
RUN apt-get update \
  && apt-get install -y --no-install-recommends \
  build-essential \
  libgl1 \
  libglib2.0-0 \
  git \
  curl \
  && rm -rf /var/lib/apt/lists/*

# Install the latest Poetry
RUN curl -sSL https://install.python-poetry.org | python3 - \
  && ln -s /root/.local/bin/poetry /usr/local/bin/poetry

# Set workdir
WORKDIR /app

# Copy only dependency files first for better caching
COPY pyproject.toml poetry.lock* README.md ./

# Copy the source code (adjust if your code is not in src/aimq)
COPY src/aimq ./src/aimq

# Install dependencies and the project
RUN poetry config virtualenvs.create false \
  && poetry install --no-interaction --no-ansi --only main

# Expose port if needed (optional, e.g., 8080)
# EXPOSE 8080

# Entrypoint for the processor
CMD ["python", "-m", "aimq.worker"]

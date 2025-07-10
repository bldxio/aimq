#!/bin/bash
set -e

# Usage: ./run-with-env.sh

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$SCRIPT_DIR/.."

# Build the Docker image
echo "[INFO] Building Docker image: aimq:local"
docker build -t aimq:local -f "$PROJECT_ROOT/docker/Dockerfile" "$PROJECT_ROOT"

# Run the Docker container with the .env file
echo "[INFO] Running Docker container with environment from .env"
docker run --rm -it --env-file "$PROJECT_ROOT/.env" aimq:local

#!/bin/bash
set -e

# Usage: ./run-with-env.sh <TAG>

if [[ "$1" == "-h" || "$1" == "--help" ]]; then
  print_help
  exit 0
fi

TAG=${1}

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$SCRIPT_DIR/.."

# Build the Docker image
echo "[INFO] Building Docker image: aimq:${TAG}"
docker build -t aimq:${TAG} -f "$PROJECT_ROOT/docker/Dockerfile" "$PROJECT_ROOT"

echo "[SUCCESS] Built Docker image: aimq:${TAG}"

# Run the Docker container with the .env file
echo "[INFO] Running Docker container with environment from .env"
docker run --rm -it --env-file "$PROJECT_ROOT/.env" aimq:${TAG}

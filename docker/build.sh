#!/bin/bash
set -e

# Local Docker build script
# Usage: ./build.sh [tag]
# Default tag is 'local'

TAG=${1:-local}
IMAGE_NAME="aimq:${TAG}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="${SCRIPT_DIR}/.."

cd "$PROJECT_ROOT"

echo "[INFO] Building Docker image as $IMAGE_NAME ..."
docker build -t $IMAGE_NAME -f docker/Dockerfile .

echo "[SUCCESS] Built $IMAGE_NAME"

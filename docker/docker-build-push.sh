#!/bin/bash
set -e

# Usage: ./docker-build-push.sh <REGISTRY> <REPOSITORY> <IMAGE_NAME> <TAG>

if [ "$#" -ne 4 ]; then
  echo "Usage: $0 <REGISTRY> <REPOSITORY> <IMAGE_NAME> <TAG>"
  exit 1
fi

REGISTRY=$1
REPOSITORY=$2
IMAGE_NAME=$3  # Ignored for DOCR compatibility
TAG=$4

FULL_IMAGE_NAME="$REGISTRY/$REPOSITORY:$TAG"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR/.."

echo "[INFO] Building Docker image: $FULL_IMAGE_NAME"
docker build -t "$FULL_IMAGE_NAME" -f docker/Dockerfile .

echo "[INFO] Pushing Docker image: $FULL_IMAGE_NAME"
docker push "$FULL_IMAGE_NAME"

echo "[SUCCESS] Built and pushed $FULL_IMAGE_NAME"

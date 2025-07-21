#!/bin/bash
set -e

print_help() {
  cat <<EOF
Usage: ./build.sh [TAG]

Builds the local Docker image for AIMQ.

Arguments:
  TAG         Optional. Tag to assign to the built image (default: 'local').

Options:
  -h, --help  Show this help message and exit.

Example:
  ./build.sh dev
  # Builds the Docker image as aimq:dev
EOF
}

if [[ "$1" == "-h" || "$1" == "--help" ]]; then
  print_help
  exit 0
fi

TAG=${1:-local}
IMAGE_NAME="aimq:${TAG}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="${SCRIPT_DIR}/.."

cd "$PROJECT_ROOT"

echo "[INFO] Building Docker image as $IMAGE_NAME ..."
docker build -t $IMAGE_NAME -f docker/Dockerfile .

echo "[SUCCESS] Built $IMAGE_NAME"

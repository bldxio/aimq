# AIMQ

AIMQ (AI Message Queue) is a robust message queue processor designed specifically for Supabase's pgmq integration. It provides a powerful framework for processing queued tasks with built-in support for AI-powered document processing and OCR capabilities.

## Features

- **Supabase pgmq Integration**: Seamlessly process messages from Supabase's message queue
- **Document OCR Processing**: Extract text from images using EasyOCR
- **Queue-based Processing**: Efficient handling of document processing tasks
- **AI-powered Analysis**: Leverage machine learning for advanced text analysis
- **Flexible Architecture**: Easy to extend with new processing tools and capabilities

## Quick Start (Zero Installation)

The fastest way to get started with AIMQ is using `uvx`, which requires no installation:

```bash
# Initialize a new AIMQ project
uvx aimq init my-project
cd my-project

# Configure your .env file with Supabase credentials
cp .env.example .env
# Edit .env with your SUPABASE_URL and SUPABASE_KEY

# Edit tasks.py to define your task queues
# (A template is already created for you)

# Start the worker
uvx aimq start
```

That's it! No `pip install`, no virtual environments, no dependency conflicts.

## Installation Options

### Option 1: Using uvx (Recommended for Quick Start)

Run AIMQ directly without installing:

```bash
# Run any command with uvx
uvx aimq init
uvx aimq start tasks.py
uvx aimq send my-queue '{"message": "hello"}'
```

### Option 2: Install as a Tool (Recommended for Regular Use)

Install AIMQ as a persistent tool using uv:

```bash
# Install uv if you haven't already
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install aimq as a tool
uv tool install aimq

# Now you can use aimq directly
aimq init my-project
aimq start
```

### Option 3: Traditional pip Install

```bash
pip install aimq
aimq start
```

### Option 4: Development Setup

For contributing to AIMQ or building from source:

```bash
# Clone the repository
git clone https://github.com/bldxio/aimq.git
cd aimq

# Install dependencies from lockfile (production)
uv sync

# For development (includes test/dev tools)
uv sync --group dev

# Run from source
uv run aimq start
```

### Key uv Commands for Development

```bash
# Add a new dependency
uv add requests

# Add to dev dependency group
uv add --group dev pytest

# Remove a dependency
uv remove requests

# Update dependencies
uv lock --upgrade

# Run commands in the uv environment
uv run python -m aimq.worker
uv run pytest
```

## Configuration

### Environment Variables

AIMQ uses environment variables for configuration. Create a `.env` file in your project root:

```env
# Supabase Configuration (Required)
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key

# Worker Configuration
WORKER_NAME=aimq-worker
WORKER_PATH=./tasks.py
WORKER_LOG_LEVEL=info
WORKER_IDLE_WAIT=10.0

# AI Provider API Keys (Optional)
OPENAI_API_KEY=sk-...
MISTRAL_API_KEY=...

# LangChain Tracing (Optional - for debugging)
LANGCHAIN_TRACING_V2=false
LANGCHAIN_API_KEY=...
```

When you run `aimq init`, an `.env.example` file is created with all available options documented.

### Supabase Setup

Configure your Supabase project with pgmq:

1. Go to your Supabase project dashboard
2. Navigate to Database → Extensions
3. Enable the `pgmq` extension
4. Run the AIMQ migration (created by `aimq init --supabase`)

For more details, see the [Supabase pgmq documentation](https://supabase.com/docs/guides/database/extensions/pgmq).

## Usage

### Defining Tasks

Create a `tasks.py` file that defines your task queues and processors:

```python
from typing import Any, Dict
from aimq.worker import Worker

# Create a worker instance
worker = Worker()

@worker.task(queue="document-processing", timeout=300)
def process_document(data: Dict[str, Any]) -> Dict[str, Any]:
    """Process a document using AI tools."""
    document_url = data.get("document_url")

    # Use built-in AIMQ tools for OCR, PDF extraction, etc.
    # Your processing logic here...

    return {"status": "processed", "text": extracted_text}

@worker.task(queue="image-analysis")
def analyze_image(data: Dict[str, Any]) -> Dict[str, Any]:
    """Analyze an image using AI models."""
    image_url = data.get("image_url")

    # Your analysis logic here...

    return {"analysis": results}
```

### Starting the Worker

```bash
# Start with default tasks.py
aimq start

# Start with a specific tasks file
aimq start my_tasks.py

# Start with debug logging
aimq start --debug

# Using uvx (no installation)
uvx aimq start
```

### Sending Messages to Queues

```bash
# Send a message to a queue
aimq send document-processing '{"document_url": "https://example.com/doc.pdf"}'

# Enable/disable queues
aimq enable document-processing
aimq disable document-processing
```

Or programmatically from Python:

```python
from supabase import create_client
import os

supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_KEY")
)

# Send a message to the queue
supabase.rpc("pgmq_send", {
    "queue_name": "document-processing",
    "msg": {"document_url": "https://example.com/doc.pdf"}
}).execute()
```

## Docker Deployment

AIMQ can be easily deployed using Docker for production environments.

### Quick Docker Setup

```bash
# Initialize with Docker files
aimq init --docker

# This creates:
# - Dockerfile
# - docker-compose.yml
# - .dockerignore

# Build and run
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

### Manual Docker Setup

If you already have a project, you can manually create a Dockerfile:

```dockerfile
FROM python:3.12-slim

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 libglib2.0-0 libgomp1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy your tasks.py
COPY tasks.py .env ./

# Install uv and aimq
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
RUN uv pip install --system aimq

ENV PYTHONUNBUFFERED=1

CMD ["aimq", "start", "tasks.py"]
```

And a `docker-compose.yml`:

```yaml
version: '3.8'

services:
  aimq-worker:
    build: .
    volumes:
      - ./tasks.py:/app/tasks.py:ro
      - ./.env:/app/.env:ro
    environment:
      - SUPABASE_URL=${SUPABASE_URL}
      - SUPABASE_KEY=${SUPABASE_KEY}
      - WORKER_NAME=aimq-worker
    restart: unless-stopped
```

### Production Deployment Considerations

- **Scaling**: Run multiple worker containers to process more messages in parallel
- **Monitoring**: Add health checks and logging aggregation
- **Secrets**: Use Docker secrets or environment variable injection (not .env files in production)
- **Resource Limits**: Set memory and CPU limits based on your AI model requirements
- **Network**: Ensure workers can reach your Supabase instance (check firewall rules)

## Development

This project uses [just](https://github.com/casey/just) as a task runner. Install it with:

```bash
# macOS
brew install just

# Other platforms: https://github.com/casey/just#installation
```

### Common Tasks

```bash
# Setup development environment
just install

# Run tests
just test
just test-cov          # With coverage

# Code quality
just lint              # Check code style
just format            # Format code
just type-check        # Type checking
just ci                # Run all checks (lint + type + test)

# Docker
just dev               # Start dev environment
just dev-build         # Build and start
just logs              # View logs

# Documentation
just docs-serve        # Serve docs locally

# See all available tasks
just --list
```

### Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run quality checks: `just ci`
5. Submit a pull request

## License

MIT License - see [LICENSE](LICENSE) for details.

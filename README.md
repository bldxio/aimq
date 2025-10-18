# AIMQ

AIMQ (AI Message Queue) is a robust message queue processor designed specifically for Supabase's pgmq integration. It provides a powerful framework for processing queued tasks with built-in support for AI-powered document processing and OCR capabilities.

## Features

- **Supabase pgmq Integration**: Seamlessly process messages from Supabase's message queue
- **Document OCR Processing**: Extract text from images using EasyOCR
- **Queue-based Processing**: Efficient handling of document processing tasks
- **AI-powered Analysis**: Leverage machine learning for advanced text analysis
- **Flexible Architecture**: Easy to extend with new processing tools and capabilities

## Installation

This project uses [uv](https://docs.astral.sh/uv/) for extremely fast Python package and project management. To get started:

```bash
# Install uv if you haven't already
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone the repository
git clone <your-repo-url>
cd aimq

# Install dependencies from lockfile (production)
# Creates .venv automatically and installs exact versions from uv.lock
uv sync

# For development (includes test/dev tools)
uv sync --group dev
```

### Key uv Commands

```bash
# Add a new dependency
uv add requests

# Add a development dependency
uv add --dev pytest

# Remove a dependency
uv remove requests

# Update dependencies
uv lock --upgrade

# Run commands in the uv environment
uv run python -m aimq.worker
uv run pytest
```

## Configuration

1. Create a `.env` file in the project root:

```env
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
QUEUE_NAME=your_queue_name
```

1. Configure your Supabase project with pgmq following the [official documentation](https://supabase.com/docs/guides/database/extensions/pgmq).

## Usage

1. Start the processor:

```bash
uv run python -m aimq.processor
```

2. Process documents by adding messages to your Supabase queue:

```python
from aimq.core import QueueMessage

message = QueueMessage(
    type="ocr",
    payload={
        "image_url": "https://example.com/document.jpg"
    }
)
```

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

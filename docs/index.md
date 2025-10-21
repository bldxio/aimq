# AIMQ Documentation

AIMQ (AI Message Queue) is a robust message queue processor designed for Supabase's pgmq integration. It provides a powerful framework for processing queued tasks with built-in support for AI-powered document processing and OCR capabilities.

## Features

- **Supabase pgmq Integration**: Seamlessly process messages from Supabase's PostgreSQL message queue
- **Document OCR Processing**: Extract text from images using EasyOCR
- **Queue-based Processing**: Efficient handling of document processing tasks
- **AI-powered Analysis**: Leverage LangChain for advanced text analysis
- **Flexible Architecture**: Easy to extend with new processing tools and capabilities
- **Zero Installation Option**: Run with `uvx` without installing anything
- **Git URL Support**: Load task definitions from git repositories for GitOps workflows
- **Docker Ready**: Pre-built images for easy deployment

## Quick Start (Zero Installation)

The fastest way to get started with AIMQ requires no installation:

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

## Example Task Definition

```python
from aimq import Worker
from typing import Dict, Any

# Create a worker instance
worker = Worker()

@worker.task(queue="document-processing", timeout=300)
def process_document(data: Dict[str, Any]) -> Dict[str, Any]:
    """Process a document using AI tools."""
    document_url = data.get("document_url")

    # Your processing logic here...
    # Use built-in AIMQ tools for OCR, PDF extraction, etc.

    return {"status": "processed", "text": extracted_text}

# The worker can be started with: aimq start
```

## Quick Links

- [Installation](getting-started/installation.md)
- [Quick Start Guide](getting-started/quickstart.md)
- [API Reference](api/overview.md)
- [Contributing Guide](development/contributing.md)

## Project Status

AIMQ is currently in beta. While it is being used in production environments, the API may still undergo changes as we gather feedback from users.

## License

AIMQ is released under the MIT License. See the [LICENSE](https://github.com/bldxio/aimq/blob/main/LICENSE) file for more details.

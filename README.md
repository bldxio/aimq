# AIMQ

AIMQ (AI Message Queue) is a robust message queue processor designed specifically for Supabase's pgmq integration. It provides a powerful framework for processing queued tasks with built-in support for AI-powered document processing and OCR capabilities.

## Features

- **Supabase pgmq Integration**: Seamlessly process messages from Supabase's message queue
- **Document OCR Processing**: Extract text from images using EasyOCR
- **Queue-based Processing**: Efficient handling of document processing tasks
- **AI-powered Analysis**: Leverage machine learning for advanced text analysis
- **Flexible Architecture**: Easy to extend with new processing tools and capabilities

## Installation

This project uses Poetry for dependency management. To get started:

```bash
# Install Poetry if you haven't already
curl -sSL https://install.python-poetry.org | python3 -

# Clone the repository
git clone <your-repo-url>
cd aimq

# Install dependencies
poetry install
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
poetry run python -m aimq.processor
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

To contribute to AIMQ:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests: `poetry run pytest`
5. Submit a pull request

## License

MIT License - see [LICENSE](LICENSE) for details.

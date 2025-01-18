# Configuration

AIMQ can be configured through environment variables and requires proper Supabase queue setup.

## Supabase Queue Setup

1. Enable Queue Integration:
   - Go to your Supabase project dashboard
   - Navigate to Database → Extensions
   - Enable the "pg_net" and "pg_cron" extensions if not already enabled
   - Navigate to Database → Queues (Beta)
   - Click "Enable Queue"
   - Make sure to enable "Expose Queues via PostgREST"

2. Create Queues:
   - In the Queues interface, click "Create a new queue"
   - Give your queue a name (this will be referenced in your `@worker.task` decorators)
   - Configure queue settings as needed

For more details, see the [Supabase Queue Documentation](https://supabase.com/docs/guides/queues/quickstart).

## Environment Variables

The following environment variables are supported:

```bash
# Required Supabase Configuration
SUPABASE_URL=your-project-url
SUPABASE_KEY=your-service-role-key  # Must be service role key, not anon key

# Worker Configuration (Optional)
WORKER_NAME=my-worker  # Default: 'peon'
WORKER_LOG_LEVEL=info  # Default: 'info'
WORKER_IDLE_WAIT=10.0  # Default: 10.0 seconds

# LangChain Configuration (Optional)
LANGCHAIN_TRACING_V2=true  # Enable LangChain tracing
LANGCHAIN_ENDPOINT=https://api.smith.langchain.com
LANGCHAIN_API_KEY=your-langchain-api-key
LANGCHAIN_PROJECT=your-project-name

# OpenAI Configuration (If using OpenAI)
OPENAI_API_KEY=your-openai-api-key
```

## Configuration File

You can create a `.env` file in your project root:

```bash
# .env
SUPABASE_URL=your-project-url
SUPABASE_KEY=your-service-role-key
WORKER_NAME=my-worker
```

## Using Poetry

Since this project uses Poetry for dependency management, you can:

1. Install dependencies:
```bash
poetry install
```

2. Run with environment variables:
```bash
poetry run python -m aimq.worker
```

Or use your `.env` file:
```bash
poetry run python -m aimq.worker
```

## Configuration in Code

Access configuration in your code:

```python
from aimq.config import config

# Access configuration values
supabase_url = config.supabase_url
worker_name = config.worker_name

# Create a worker with custom configuration
from aimq import Worker

worker = Worker(
    name="custom-worker",
    log_level="debug",
    idle_wait=5.0
)
```

## Next Steps

- See the [Quick Start Guide](quickstart.md) for usage examples
- Learn about [Worker Configuration](../user-guide/worker-configuration.md) for advanced settings

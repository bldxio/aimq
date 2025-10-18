# Configuration

AIMQ can be configured through environment variables. Configuration is loaded from `.env` files or environment variables.

## Supabase Setup

AIMQ uses Supabase's pgmq (PostgreSQL Message Queue) extension for queue management.

### Enable pgmq Extension

1. Go to your Supabase project dashboard
2. Navigate to **Database → Extensions**
3. Search for `pgmq` and enable it

### Initialize AIMQ Schema (Optional)

If you used `aimq init --supabase`, a migration file was created to set up the necessary schema:

```bash
# The migration is created in supabase/migrations/
# Apply it using the Supabase CLI or dashboard
supabase db push
```

This sets up the `pgmq_public` schema which AIMQ uses for queue operations.

### Create Queues

Queues are created automatically when you first send a message to them, or you can create them manually via SQL:

```sql
-- Create a queue (optional - queues are auto-created)
SELECT pgmq.create('my-queue');
```

For more details, see the [Supabase pgmq Documentation](https://supabase.com/docs/guides/database/extensions/pgmq).

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

## Using uv for Development

If you're developing AIMQ or running from source, use `uv` for dependency management:

```bash
# Install dependencies
uv sync --group dev

# Run commands in the uv environment
uv run aimq start
uv run pytest
```

## Using the Task Runner (just)

AIMQ uses [`just`](https://github.com/casey/just) as a task runner for common development tasks:

```bash
# Install dependencies
just install

# Run tests
just test
just test-cov

# Code quality
just lint
just format
just type-check

# Run all checks (CI)
just ci

# Docker
just dev           # Start dev environment
just logs          # View logs

# See all available commands
just --list
```

Install `just`:
```bash
# macOS
brew install just

# Other platforms: https://github.com/casey/just#installation
```

## Configuration in Code

Access configuration in your code:

```python
from aimq.config import config

# Access configuration values
supabase_url = config.supabase_url
worker_name = config.worker_name
log_level = config.worker_log_level

# Create a worker with custom configuration
from aimq import Worker

worker = Worker(
    name="custom-worker",
    log_level="debug",
    idle_wait=5.0
)
```

## Advanced Configuration

### Worker Path

Specify where to find your tasks file:

```bash
# Via environment variable
export AIMQ_TASKS=./my_tasks.py

# Via command line
aimq start custom_tasks.py

# Using git URL
export AIMQ_TASKS=git:mycompany/aimq-tasks@production
aimq start
```

### Git URL Configuration

For loading tasks from git repositories:

```bash
# Use SSH for private repos
export AIMQ_USE_SSH=true

# Git credentials (for HTTPS)
export GIT_USERNAME=myuser
export GIT_PASSWORD=token
```

## Next Steps

- See the [Quick Start Guide](quickstart.md) for usage examples
- Learn about [Worker Configuration](../user-guide/worker-configuration.md) for advanced settings
- Check out [Docker deployment](../deployment/docker-kubernetes.md) options

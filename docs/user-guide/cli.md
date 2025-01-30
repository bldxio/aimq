# CLI Commands

AIMQ provides a command-line interface for managing queues, workers, and project
initialization.

## Project Setup

### Initialize Project

```bash
aimq init [DIRECTORY]
```

Creates a new AIMQ project with the required directory structure and configuration
files. If no directory is specified, initializes in the current directory.

## Queue Operations

### Start Worker

```bash
aimq start [WORKER_PATH] [--log-level LEVEL] [--debug]
```

Starts the AIMQ worker process. If a worker path is provided, loads task definitions
from that file.

**Options:**

- `--log-level`, `-l`: Set logging level (debug, info, warning, error, critical)
- `--debug`, `-d`: Enable debug logging (shortcut for --log-level debug)
- `WORKER_PATH`: Optional path to Python file containing worker task definitions

**Example:**

```bash
# Start with custom worker tasks
aimq start ./tasks.py --log-level debug

# Start with default configuration
aimq start
```

### Send Jobs

```bash
aimq send <queue_name> <json_data> [--delay SECONDS] [--provider PROVIDER]
```

Sends a job to the specified queue with JSON payload data.

**Options:**

- `--delay`, `-d`: Delay in seconds before the job becomes visible
- `--provider`, `-p`: Queue provider to use (default: supabase)

**Example:**

```bash
aimq send documents '{"action":"ocr", "file_id":123}' \
  --delay 300 \
  --provider supabase
```

## Environment Variables

The following environment variables can be used to configure AIMQ:

| Variable           | Description                         | Default  |
| ------------------ | ----------------------------------- | -------- |
| `SUPABASE_URL`     | URL of your Supabase project        | Required |
| `SUPABASE_KEY`     | API key for Supabase authentication | Required |
| `WORKER_NAME`      | Name to identify the worker         | 'peon'   |
| `WORKER_LOG_LEVEL` | Default logging level               | 'info'   |

## Project Structure

When initializing a new project with `aimq init`, the following structure is created:

```text
.
├── supabase/
│   ├── migrations/        # Database migrations
│   └── config.toml       # Supabase configuration with PGMQ enabled
├── tasks.py              # Worker task definitions
└── .env                  # Environment configuration
```

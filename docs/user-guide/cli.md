# CLI Commands

AIMQ provides a command-line interface for managing queues and workers.

## Available Commands

### Send Jobs
```bash
aimq send <queue_name> <json_data> [--delay SECONDS] [--provider PROVIDER]
```

Example:
```bash
aimq send documents '{"action":"ocr", "file_id":123}' \
  --delay 300 \
  --provider supabase
```

### Start Worker
```bash
aimq start [--name WORKER_NAME] [--log-level LEVEL]
```

### Manage Queues
```bash
# Enable queue
aimq enable <queue_name>

# Disable queue
aimq disable <queue_name>

# Initialize queue
aimq init <queue_name>
```

## Common Options

| Option         | Description                          | Default       |
|----------------|--------------------------------------|---------------|
| --provider     | Queue provider (supabase)            | supabase      |
| --delay        | Delay job visibility (seconds)       | None          |
| --name         | Worker name                          | 'peon'        |
| --log-level    | Logging level (debug, info, warning) | 'info'        |

## Environment Variables

All commands respect the same environment variables as the worker:
- `SUPABASE_URL`
- `SUPABASE_KEY`
- `WORKER_NAME`
- `WORKER_LOG_LEVEL`

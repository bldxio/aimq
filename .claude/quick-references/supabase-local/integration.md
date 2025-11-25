# Supabase Local Development - AIMQ Integration

Integration guide for using Supabase with AIMQ.

## Configuration

### Settings

```python
# src/aimq/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    supabase_url: str = "http://127.0.0.1:64321"
    supabase_key: str

    class Config:
        env_file = ".env.local"

config = Settings()
```

### Environment Variables

```bash
# .env.local
SUPABASE_URL=http://127.0.0.1:64321
SUPABASE_ANON_KEY=eyJhbGc...
SUPABASE_SERVICE_ROLE_KEY=eyJhbGc...
```

## Client Setup

### Basic Client

```python
# src/aimq/clients/supabase.py
from supabase import create_client
from aimq.config import config

supabase = create_client(
    config.supabase_url,
    config.supabase_key
)
```

### With Connection Pooling

```python
# src/aimq/clients/supabase.py
from supabase import create_client, ClientOptions

supabase = create_client(
    config.supabase_url,
    config.supabase_key,
    options=ClientOptions(
        postgrest_client_timeout=10,
        storage_client_timeout=10,
    )
)
```

## Testing

### Test Fixtures

```python
# tests/conftest.py
import pytest
from supabase import create_client
import os

@pytest.fixture
def supabase_client():
    """Fixture for Supabase client using test environment."""
    return create_client(
        os.getenv("SUPABASE_URL", "http://127.0.0.1:64321"),
        os.getenv("SUPABASE_ANON_KEY")
    )

@pytest.fixture
def supabase_admin():
    """Fixture for Supabase admin client."""
    return create_client(
        os.getenv("SUPABASE_URL", "http://127.0.0.1:64321"),
        os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    )
```

### Test Database Setup

```python
# tests/conftest.py
@pytest.fixture(autouse=True)
def reset_test_data(supabase_admin):
    """Reset test data before each test."""
    # Clean up test data
    supabase_admin.table("test_table").delete().neq("id", 0).execute()

    yield

    # Optional: cleanup after test
```

## Queue Integration

### PGMQ Setup

```python
# src/aimq/clients/queue.py
from aimq.clients.supabase import supabase

def create_queue(queue_name: str):
    """Create a new queue."""
    return supabase.rpc(
        "pgmq_public.create_queue",
        {"queue_name": queue_name}
    ).execute()

def send_message(queue_name: str, message: dict, delay: int = 0):
    """Send message to queue."""
    return supabase.rpc(
        "pgmq_public.send",
        {
            "queue_name": queue_name,
            "message": message,
            "sleep_seconds": delay
        }
    ).execute()

def read_message(queue_name: str, vt: int = 30):
    """Read message from queue."""
    return supabase.rpc(
        "pgmq_public.read",
        {
            "queue_name": queue_name,
            "vt": vt
        }
    ).execute()
```

## Realtime Integration

### Subscribe to Changes

```python
# src/aimq/realtime.py
from aimq.clients.supabase import supabase

def subscribe_to_table(table_name: str, callback):
    """Subscribe to table changes."""
    channel = supabase.channel(f"{table_name}_changes")

    channel.on_postgres_changes(
        event="*",
        schema="public",
        table=table_name,
        callback=callback
    ).subscribe()

    return channel
```

### Example Usage

```python
def handle_change(payload):
    print(f"Change detected: {payload}")

# Subscribe to jobs table
channel = subscribe_to_table("jobs", handle_change)

# Later: unsubscribe
channel.unsubscribe()
```

## Best Practices

### 1. Use Environment Variables

```python
# ✅ Good: Use environment variables
supabase_url = os.getenv("SUPABASE_URL")

# ❌ Bad: Hardcode URLs
supabase_url = "http://127.0.0.1:64321"
```

### 2. Handle Errors Gracefully

```python
from supabase import PostgrestAPIError

try:
    result = supabase.table("users").select("*").execute()
except PostgrestAPIError as e:
    logger.error(f"Supabase error: {e.message}")
    raise
```

### 3. Use Service Role Key Carefully

```python
# ✅ Good: Use anon key for client operations
client = create_client(url, anon_key)

# ⚠️ Careful: Use service role only for admin operations
admin = create_client(url, service_role_key)
```

### 4. Test with Local Instance

```python
# tests/test_integration.py
def test_queue_operations(supabase_client):
    """Test queue operations against local Supabase."""
    # Create queue
    result = supabase_client.rpc(
        "pgmq_public.create_queue",
        {"queue_name": "test-queue"}
    ).execute()

    assert result.data is not None
```

## Development Workflow

### 1. Start Supabase

```bash
supabase start
```

### 2. Run Migrations

```bash
supabase db reset
```

### 3. Start AIMQ Worker

```bash
uv run aimq worker start
```

### 4. Run Tests

```bash
just test
```

## Quick Reference

```bash
# Start Supabase
supabase start

# View connection details
supabase status

# Reset database
supabase db reset

# View logs
supabase logs

# Stop services
supabase stop
```

## Related

- [@overview.md](./overview.md) - Getting started
- [@configuration.md](./configuration.md) - Configuration
- [@migrations.md](./migrations.md) - Database migrations
- [@troubleshooting.md](./troubleshooting.md) - Common issues
- [@../../patterns/test-mocking-external-services.md](../../patterns/test-mocking-external-services.md) - Testing patterns

## Resources

- [Supabase Python Client](https://github.com/supabase-community/supabase-py)
- [PGMQ Documentation](https://github.com/tembo-io/pgmq)
- [Supabase Realtime](https://supabase.com/docs/guides/realtime)

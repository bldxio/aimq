# Supabase Local Development Setup

> **⚠️ DEPRECATED - This file has been split for better organization**
>
> **Last Updated**: 2025-11-20
> **Archived**: 2025-11-24
> **Superseded By**:
> - [@supabase-local/overview.md](./supabase-local/overview.md) - Getting started
> - [@supabase-local/configuration.md](./supabase-local/configuration.md) - Configuration
> - [@supabase-local/migrations.md](./supabase-local/migrations.md) - Migrations
> - [@supabase-local/troubleshooting.md](./supabase-local/troubleshooting.md) - Troubleshooting
> - [@supabase-local/integration.md](./supabase-local/integration.md) - AIMQ integration

---

## 🔄 Redirect

This file has been split into focused documents for better maintainability.

**Please use the new files:**
- **[Overview](./supabase-local/overview.md)** - Getting started with Supabase local development
- **[Configuration](./supabase-local/configuration.md)** - Port configuration and settings
- **[Migrations](./supabase-local/migrations.md)** - Database migration workflows
- **[Troubleshooting](./supabase-local/troubleshooting.md)** - Common issues and solutions
- **[Integration](./supabase-local/integration.md)** - AIMQ integration guide

---

## Archive Notice

The content below is preserved for reference but is no longer maintained. Please refer to the superseding documents above for current information.

---

## Initial Setup

### 1. Install Supabase CLI

```bash
# macOS
brew install supabase/tap/supabase

# Linux/WSL
curl -fsSL https://raw.githubusercontent.com/supabase/cli/main/install.sh | sh

# Verify installation
supabase --version
```

### 2. Initialize Project

```bash
# Initialize Supabase in your project
supabase init

# This creates:
# - supabase/config.toml
# - supabase/seed.sql
# - supabase/.gitignore
```

### 3. Start Local Services

```bash
# Start all Supabase services
supabase start

# Services started:
# - PostgreSQL database
# - PostgREST API
# - Realtime server
# - Storage server
# - Auth server
# - Studio (web UI)
```

### 4. Access Services

```bash
# View service URLs and credentials
supabase status

# Example output:
# API URL: http://127.0.0.1:54321
# DB URL: postgresql://postgres:postgres@127.0.0.1:54322/postgres
# Studio URL: http://127.0.0.1:54323
# anon key: eyJhbGc...
# service_role key: eyJhbGc...
```

## Port Configuration

### Default Ports

Supabase uses these default ports:

| Service | Default Port | Purpose |
|---------|--------------|---------|
| API (PostgREST) | 54321 | REST API endpoint |
| Database | 54322 | PostgreSQL connection |
| Studio | 54323 | Web UI dashboard |
| Shadow DB | 54320 | Migration testing |
| Pooler | 54329 | Connection pooling |

### Changing Ports

**Why change ports?**
- Avoid conflicts with other Supabase projects
- Avoid conflicts with other services
- Run multiple projects simultaneously
- Team conventions

**How to change:**

Edit `supabase/config.toml`:

```toml
[api]
port = 64321  # Changed from 54321

[db]
port = 64322  # Changed from 54322
shadow_port = 64320  # Changed from 54320

[db.pooler]
port = 64329  # Changed from 54329

[studio]
port = 64323  # Changed from 54323
```

**Port selection strategy:**
- Use a consistent range (e.g., 64xxx for project A, 65xxx for project B)
- Document port assignments in README
- Check for conflicts before starting

### Check for Port Conflicts

```bash
# Check if port is in use (macOS/Linux)
lsof -i :64321

# Check all Supabase ports
for port in 64320 64321 64322 64323 64329; do
    echo "Port $port:"
    lsof -i :$port
done

# Kill process using a port
lsof -ti :64321 | xargs kill -9
```

## Configuration

### Project Settings

Edit `supabase/config.toml`:

```toml
# Project identifier (used for local development)
project_id = "aimq"  # Change from default "examples"

[api]
enabled = true
port = 64321
# Expose custom schemas in API
schemas = ["public", "graphql_public", "pgmq_public"]
# Additional schemas for custom extensions
extra_search_path = ["public", "extensions"]

[db]
port = 64322
major_version = 15  # PostgreSQL version

[studio]
enabled = true
port = 64323
api_url = "http://127.0.0.1"
# Optional: OpenAI API key for Supabase AI features
openai_api_key = "env(OPENAI_API_KEY)"

[auth]
enabled = true
# Configure auth providers, email templates, etc.
```

### Environment Variables

Create `.env.local`:

```bash
# Supabase connection
SUPABASE_URL=http://127.0.0.1:64321
SUPABASE_ANON_KEY=eyJhbGc...
SUPABASE_SERVICE_ROLE_KEY=eyJhbGc...

# Database connection
DATABASE_URL=postgresql://postgres:postgres@127.0.0.1:64322/postgres

# Optional: OpenAI for Supabase AI
OPENAI_API_KEY=sk-...
```

**Get keys from:**
```bash
supabase status
```

## Migrations

### Create Migration

```bash
# Create new migration file
supabase migration new setup_aimq

# This creates:
# supabase/migrations/YYYYMMDDHHMMSS_setup_aimq.sql
```

### Write Migration

```sql
-- supabase/migrations/20251123021000_setup_aimq.sql

-- Enable extensions
create extension if not exists "pgmq" with schema "pgmq";

-- Create schemas
create schema if not exists pgmq_public;
grant usage on schema pgmq_public to authenticated;

-- Create functions
create or replace function pgmq_public.send(
    queue_name text,
    message jsonb,
    sleep_seconds integer default 0
)
  returns setof bigint
  language plpgsql
as $$
begin
    return query
    select * from pgmq.send(
        queue_name := queue_name,
        msg := message,
        delay := sleep_seconds
    );
end;
$$;
```

### Apply Migrations

```bash
# Apply all pending migrations
supabase db reset

# Or apply specific migration
supabase migration up

# Check migration status
supabase migration list
```

### Seed Data

Edit `supabase/seed.sql`:

```sql
-- Insert test data
insert into users (email, name) values
    ('test@example.com', 'Test User'),
    ('admin@example.com', 'Admin User');

-- Create test queues
select pgmq_public.create_queue('test-queue');
select pgmq_public.send('test-queue', '{"test": true}'::jsonb);
```

Apply seed data:
```bash
# Reset database and apply seed
supabase db reset

# Or apply seed only
psql $DATABASE_URL -f supabase/seed.sql
```

## Common Tasks

### Reset Database

```bash
# Reset to clean state and apply all migrations + seed
supabase db reset

# Confirm with 'y' when prompted
```

### View Logs

```bash
# View all logs
supabase logs

# View specific service logs
supabase logs postgres
supabase logs api
supabase logs realtime
```

### Stop Services

```bash
# Stop all services
supabase stop

# Stop and remove volumes (clean slate)
supabase stop --no-backup
```

### Access Database

```bash
# Connect with psql
supabase db psql

# Or use connection string
psql postgresql://postgres:postgres@127.0.0.1:64322/postgres

# Run SQL file
supabase db psql -f script.sql
```

### Generate Types

```bash
# Generate TypeScript types from database schema
supabase gen types typescript --local > types/supabase.ts

# Generate Python types (if using supabase-py)
# (Manual process - inspect schema and create models)
```

## Troubleshooting

### Services Won't Start

```bash
# Check for port conflicts
lsof -i :64321
lsof -i :64322

# Check Docker is running
docker ps

# View detailed logs
supabase logs

# Clean restart
supabase stop --no-backup
supabase start
```

### Migration Errors

```bash
# Check migration syntax
cat supabase/migrations/YYYYMMDDHHMMSS_name.sql

# Test migration in isolation
supabase db reset
supabase migration up

# View migration history
supabase migration list

# Rollback (manual - create new migration to undo)
supabase migration new rollback_feature
```

### Connection Issues

```bash
# Verify services are running
supabase status

# Test database connection
psql postgresql://postgres:postgres@127.0.0.1:64322/postgres -c "SELECT 1"

# Test API connection
curl http://127.0.0.1:64321/rest/v1/

# Check firewall/network settings
```

### Extension Issues

```bash
# List installed extensions
supabase db psql -c "SELECT * FROM pg_extension"

# Install extension manually
supabase db psql -c "CREATE EXTENSION IF NOT EXISTS pgmq"

# Check extension schema
supabase db psql -c "\dx+ pgmq"
```

## Best Practices

### 1. Use Migrations for Schema Changes

```bash
# ❌ Don't: Manually edit database via Studio
# ✅ Do: Create migration
supabase migration new add_users_table
```

### 2. Keep Seed Data Idempotent

```sql
-- ❌ Bad: Will fail on second run
insert into users (id, email) values (1, 'test@example.com');

-- ✅ Good: Idempotent
insert into users (id, email) values (1, 'test@example.com')
on conflict (id) do nothing;

-- ✅ Better: Use truncate in seed
truncate users cascade;
insert into users (email) values ('test@example.com');
```

### 3. Document Port Changes

```markdown
# README.md

## Local Development

Supabase runs on custom ports to avoid conflicts:
- API: http://127.0.0.1:64321
- Database: postgresql://postgres:postgres@127.0.0.1:64322/postgres
- Studio: http://127.0.0.1:64323
```

### 4. Use Environment Variables

```python
# ❌ Bad: Hardcoded
supabase = create_client(
    "http://127.0.0.1:54321",
    "eyJhbGc..."
)

# ✅ Good: Environment variables
supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_ANON_KEY")
)
```

### 5. Test Migrations Before Deploying

```bash
# Test migration locally
supabase db reset
supabase migration up

# Run tests
just test

# If all passes, deploy
supabase db push
```

## Integration with AIMQ

### Configuration

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

### Client Setup

```python
# src/aimq/clients/supabase.py
from supabase import create_client
from aimq.config import config

supabase = create_client(
    config.supabase_url,
    config.supabase_key
)
```

### Testing

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
```

## Quick Reference Commands

```bash
# Start services
supabase start

# Stop services
supabase stop

# Reset database
supabase db reset

# Create migration
supabase migration new <name>

# Apply migrations
supabase migration up

# View status
supabase status

# View logs
supabase logs

# Access database
supabase db psql

# Access Studio
open http://127.0.0.1:64323
```

## Related

- [@.claude/patterns/database-migration-wrappers.md](../patterns/database-migration-wrappers.md) - Migration patterns
- [@.claude/architecture/database-schema-patterns.md](../architecture/database-schema-patterns.md) - Schema organization
- [@.claude/architecture/database-schema-migration.md](../architecture/database-schema-migration.md) - Migration strategies
- [Supabase CLI Docs](https://supabase.com/docs/guides/cli) - Official documentation
- [Supabase Local Development](https://supabase.com/docs/guides/local-development) - Local setup guide

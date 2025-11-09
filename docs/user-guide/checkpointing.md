# LangGraph Checkpointing Setup

## Overview

LangGraph checkpointing enables stateful, resumable workflows by persisting agent/workflow state to Supabase PostgreSQL. This allows:

- **Resumable execution**: Continue agent workflows after interruption
- **State persistence**: Maintain conversation history across sessions
- **Debugging**: Inspect intermediate agent states
- **Human-in-the-loop**: Pause for human review/approval

## Prerequisites

- Supabase project with pgmq enabled
- PostgreSQL access (via Supabase dashboard or SQL Editor)
- SUPABASE_URL and SUPABASE_KEY environment variables configured
- Database admin permissions (for initial schema setup)

## Setup Steps

### 1. Create Database Schema

**Option A: Automatic Schema Creation (Development - Default)**

For local development and testing, the schema is created automatically on first use using PostgresSaver's built-in `.setup()` method:

```bash
# Just set your database connection in .env
SUPABASE_URL=http://localhost:54321
SUPABASE_KEY=your-local-key

# Schema auto-creates on first checkpointer use
```

**What happens automatically:**
- Creates 4 tables: `checkpoints`, `checkpoint_blobs`, `checkpoint_writes`, `checkpoint_migrations`
- Runs database migrations to keep schema up-to-date
- Works with local Supabase (via `supabase start`) out-of-the-box

**Requirements:**
- Database user needs CREATE TABLE permissions
- Works with local Supabase (port 54322) automatically
- May fail in production with restricted database permissions

**Option B: Supabase Migration (Recommended for Projects)**

Use the `aimq init` command to generate a Supabase migration file:

```bash
# For new projects
aimq init --supabase --langgraph

# For existing projects with Supabase
aimq init --langgraph
```

This creates a timestamped migration file in `supabase/migrations/` that can be version controlled and deployed via `supabase db push` or `supabase db reset`.

**Option C: Manual SQL Setup (Production)**

For production deployments with restricted database permissions, run the schema setup manually:

1. Go to your Supabase project dashboard
2. Navigate to **SQL Editor**
3. Copy the contents of `docs/deployment/langgraph-schema.sql`
4. Paste into a new query and click **Run**
5. Verify tables created:
   ```sql
   SELECT COUNT(*) FROM checkpoints;
   SELECT COUNT(*) FROM checkpoint_blobs;
   SELECT COUNT(*) FROM checkpoint_writes;
   SELECT v FROM checkpoint_migrations ORDER BY v DESC LIMIT 1;
   ```

This approach gives you full control over permissions, indexes, and RLS policies.

### 2. Enable Checkpointing in Agents/Workflows

When defining agents or workflows, set `memory=True` to enable checkpointing:

```python
from aimq.langgraph.decorators import agent
from langchain.tools import BaseTool

@agent(
    tools=[...],
    memory=True,  # Enable checkpointing
    system_prompt="You are a helpful assistant"
)
def my_agent(graph, config):
    # Define your agent graph
    graph.add_node("process", lambda state: {...})
    graph.set_entry_point("process")
    graph.set_finish_point("process")
```

### 3. Use Thread IDs for Session Management

When sending jobs to agent queues, include a `thread_id` for resumable execution:

```python
from aimq.worker import Worker

worker = Worker()

# Send job with thread_id for session continuity
worker.send("agent-queue", {
    "messages": [
        {"role": "user", "content": "Process this document"}
    ],
    "thread_id": "user-123-session-456",  # Unique session identifier
})
```

**Thread ID Best Practices:**
- Use format: `{user_id}-{session_id}` or `{tenant_id}-{job_id}`
- Keep thread IDs unique per conversation/workflow instance
- Reuse thread_id to continue previous conversation
- Use new thread_id for fresh conversation

### 4. Verify Checkpointing Works

After running some agent jobs, check the checkpoints table:

```sql
-- View recent checkpoints
SELECT
    thread_id,
    checkpoint_id,
    metadata
FROM checkpoints
ORDER BY (checkpoint->>'ts')::BIGINT DESC
LIMIT 10;

-- Count checkpoints per thread
SELECT
    thread_id,
    COUNT(*) as checkpoint_count,
    MAX((checkpoint->>'ts')::BIGINT) as last_checkpoint_ts
FROM checkpoints
GROUP BY thread_id
ORDER BY last_checkpoint_ts DESC;
```

## Configuration

### Environment Variables

#### Basic Configuration (Supabase Cloud)

```bash
# Required for checkpointing
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-service-role-key

# Optional: Control iteration limits
LANGGRAPH_MAX_ITERATIONS=20
```

**Note:** Schema is automatically created on first use via `PostgresSaver.setup()`. No additional flags needed for development.

#### Flexible Database Configuration

AIMQ supports multiple deployment scenarios with flexible database configuration:

**Option 1: Direct PostgreSQL Connection (Highest Priority)**

Use this for complete control over the connection string:

```bash
DATABASE_URL=postgresql://user:password@host:port/database

# Examples:
# Self-hosted: DATABASE_URL=postgresql://postgres:pass@db.company.com:5432/postgres
# Local dev: DATABASE_URL=postgresql://postgres:pass@localhost:54322/postgres
# Pooler: DATABASE_URL=postgresql://postgres:pass@db.project.supabase.co:6543/postgres
```

**Option 2: Individual Configuration Overrides**

Override specific connection parameters:

```bash
# Override database host (takes precedence over SUPABASE_URL parsing)
DATABASE_HOST=db.myproject.supabase.co

# Connection pooler port (default: 5432)
DATABASE_PORT=6543

# Database name (default: postgres)
DATABASE_NAME=postgres

# Database user (default: postgres)
DATABASE_USER=postgres

# Database password (defaults to SUPABASE_KEY if not set)
DATABASE_PASSWORD=your_database_password
```

**Option 3: Smart URL Parsing (Default)**

If DATABASE_URL and DATABASE_HOST are not set, AIMQ automatically parses SUPABASE_URL:

```bash
# Supabase Cloud
SUPABASE_URL=https://myproject.supabase.co
# → Connects to: db.myproject.supabase.co:5432

# Self-hosted Supabase
SUPABASE_URL=https://supabase.company.com
# → Connects to: db.supabase.company.com:5432

# Local development (port 54322 auto-detected! 🎉)
SUPABASE_URL=http://localhost:54321
# → Connects to: localhost:54322 (automatic!)

# Local with 127.0.0.1 (also auto-detected)
SUPABASE_URL=http://127.0.0.1:54321
# → Connects to: 127.0.0.1:54322 (automatic!)

# Docker Compose
SUPABASE_URL=http://supabase:8000
# → Connects to: supabase:5432
```

**Smart Defaults for Local Development:**
- **Host**: `localhost` / `127.0.0.1` detected automatically from SUPABASE_URL
- **Port**: Automatically uses **54322** (local Supabase default from `supabase start`)
- **Password**: Automatically uses **"postgres"** (local DB password, not the JWT token!)
- **Result**: Just set `SUPABASE_URL=http://localhost:54321` and it works! ✨

**For other deployments:**
- Cloud/self-hosted → Uses port **5432** and `SUPABASE_KEY` as password
- Override with `DATABASE_PORT` for connection pooler (6543)
- Override with `DATABASE_PASSWORD` for custom passwords

#### Deployment Scenario Examples

**Supabase Cloud (Default)**
```bash
SUPABASE_URL=https://myproject.supabase.co
SUPABASE_KEY=your-service-role-key
# All database config auto-detected
```

**Supabase Cloud with Connection Pooler**
```bash
SUPABASE_URL=https://myproject.supabase.co
SUPABASE_KEY=your-service-role-key
DATABASE_PORT=6543  # Use pooler instead of direct connection
```

**Self-hosted Supabase**
```bash
SUPABASE_URL=https://supabase.company.com
SUPABASE_KEY=your-api-key
DATABASE_HOST=db.supabase.company.com  # If auto-detection doesn't work
DATABASE_PORT=5432
```

**Local Development**
```bash
SUPABASE_URL=http://localhost:54321
SUPABASE_KEY=local-dev-key
# That's it! Port 54322 and password "postgres" auto-detected! 🎉
```

**Docker Compose**
```bash
SUPABASE_URL=http://supabase:8000
SUPABASE_KEY=docker-key
DATABASE_HOST=supabase-db  # Override if DB is on different service
DATABASE_PORT=5432
```

**Custom PostgreSQL (No Supabase)**
```bash
DATABASE_URL=postgresql://myuser:mypass@db.example.com:5432/mydb
# or
DATABASE_HOST=db.example.com
DATABASE_PORT=5432
DATABASE_NAME=mydb
DATABASE_USER=myuser
DATABASE_PASSWORD=mypass
```

### Agent Configuration

```python
@agent(
    tools=[...],
    memory=True,              # Enable checkpointing
    system_prompt="...",      # Agent instructions
    llm="mistral-large-latest",  # Model to use
)
def my_agent(graph, config):
    # Your agent implementation
    pass
```

## Troubleshooting

### "Permission denied" error during automatic setup

**Problem**: Schema creation fails with permission denied error

**Error message:**
```
CheckpointerError: Checkpoint schema setup failed due to permissions.
Create schema manually with database admin credentials.
```

**Solution**: Create schema manually using Supabase SQL Editor (see Setup Steps, Option B)

1. Copy contents of `docs/deployment/langgraph-schema.sql`
2. Run in Supabase SQL Editor with admin credentials
3. Restart your application with standard database user

**Why this happens:**
- Automatic setup uses `PostgresSaver.setup()` which requires CREATE TABLE permissions
- Production Supabase projects often restrict these permissions for security
- Local Supabase (via `supabase start`) usually has full permissions

### "Connection failed" error

**Problem**: Cannot connect to PostgreSQL database

**Solution**: Verify environment variables are set correctly

```bash
# Check values
echo $SUPABASE_URL
echo $SUPABASE_KEY
echo $DATABASE_URL
echo $DATABASE_HOST

# Should output appropriate values for your deployment
```

**Common issues**:
- Using `anon` key instead of `service_role` key
- URL includes trailing slash (should not)
- Environment variables not loaded (.env file not in working directory)
- Wrong database host for self-hosted deployments (try DATABASE_HOST override)
- Wrong port (5432 for direct, 6543 for connection pooler)
- Network issues (firewall blocking PostgreSQL port)

**Debugging connection issues**:

```bash
# Test if DATABASE_URL is set (highest priority)
echo $DATABASE_URL

# If not, check if smart parsing will work
echo $SUPABASE_URL
echo $DATABASE_HOST

# Enable debug logging to see connection details
WORKER_LOG_LEVEL=debug aimq start

# Look for log messages like:
# "Extracted database host from SUPABASE_URL: localhost"
# "Built PostgreSQL connection string (host=localhost, port=5432, db=postgres)"
```

**For self-hosted/local deployments**:

If automatic host detection doesn't work, explicitly set DATABASE_HOST:

```bash
# Self-hosted
DATABASE_HOST=db.supabase.company.com
DATABASE_PORT=5432

# Local Supabase (usually auto-detected!)
# Just use SUPABASE_URL=http://localhost:54321
# Port 54322 is detected automatically for localhost/127.0.0.1

# Docker
DATABASE_HOST=supabase-db
DATABASE_PORT=5432

# Or use direct DATABASE_URL
DATABASE_URL=postgresql://postgres:password@localhost:54322/postgres
```

### Checkpoints not saving

**Problem**: Agent runs but no checkpoints appear in database

**Possible causes**:

1. **Memory not enabled**: Ensure `memory=True` in agent decorator
2. **No thread_id provided**: Include `thread_id` in job input
3. **Schema not created**: Run schema setup SQL (see Setup Steps)
4. **Connection issue**: Check database connection string

**Enable debug logging**:
```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Look for checkpoint-related log messages
# "Checkpoint saved: thread_id=..."
# "Checkpointer error: ..."
```

### Database permission errors

**Problem**: `permission denied for schema langgraph`

**Solution**: Grant permissions to your database user/role

```sql
-- Run as database admin (in Supabase SQL Editor)
GRANT USAGE ON SCHEMA public TO authenticated;
GRANT ALL ON checkpoints TO authenticated;
GRANT ALL ON checkpoint_blobs TO authenticated;
GRANT ALL ON checkpoint_writes TO authenticated;
GRANT ALL ON checkpoint_migrations TO authenticated;
```

For Supabase, the default role is `authenticated`. See `docs/deployment/langgraph-schema.sql` for complete permissions setup.

## Cleanup

### Remove Old Checkpoints

Checkpoints accumulate over time. Use the cleanup function to remove old entries:

```sql
-- Delete checkpoints older than 30 days (using function from schema setup)
SELECT * FROM cleanup_old_checkpoints(30);

-- Delete checkpoints older than 7 days
SELECT * FROM cleanup_old_checkpoints(7);

-- Delete all checkpoints for a specific thread
DELETE FROM checkpoints WHERE thread_id = 'user-123-session-456';
DELETE FROM checkpoint_blobs WHERE thread_id = 'user-123-session-456';
DELETE FROM checkpoint_writes WHERE thread_id = 'user-123-session-456';
```

### Schedule Automatic Cleanup

Create a Supabase Edge Function or cron job to run cleanup periodically:

```sql
-- Using pg_cron (if available)
SELECT cron.schedule(
    'cleanup-checkpoints',
    '0 2 * * *',  -- Run daily at 2 AM
    $$SELECT * FROM cleanup_old_checkpoints(30)$$
);
```

## Advanced Usage

### Multi-Tenant Isolation

Enable Row Level Security (RLS) for tenant-specific checkpoint access:

```sql
-- Enable RLS on all checkpoint tables
ALTER TABLE checkpoints ENABLE ROW LEVEL SECURITY;
ALTER TABLE checkpoint_blobs ENABLE ROW LEVEL SECURITY;
ALTER TABLE checkpoint_writes ENABLE ROW LEVEL SECURITY;

-- Policy: Users can only access their own checkpoints
CREATE POLICY "tenant_isolation_checkpoints"
    ON checkpoints FOR ALL
    USING (thread_id LIKE (current_setting('app.tenant_id') || '%'));

CREATE POLICY "tenant_isolation_blobs"
    ON checkpoint_blobs FOR ALL
    USING (thread_id LIKE (current_setting('app.tenant_id') || '%'));

CREATE POLICY "tenant_isolation_writes"
    ON checkpoint_writes FOR ALL
    USING (thread_id LIKE (current_setting('app.tenant_id') || '%'));
```

Then include tenant_id in thread_id:
```python
worker.send("agent-queue", {
    "messages": [...],
    "thread_id": f"{tenant_id}-{session_id}",
})
```

### Checkpoint Inspection

Inspect checkpoint contents for debugging:

```sql
-- View full checkpoint data
SELECT
    thread_id,
    checkpoint_id,
    jsonb_pretty(checkpoint) as state,
    jsonb_pretty(metadata) as metadata
FROM checkpoints
WHERE thread_id = 'user-123-session-456'
ORDER BY (checkpoint->>'ts')::BIGINT DESC
LIMIT 1;
```

### Resume from Specific Checkpoint

To resume from a specific checkpoint (advanced):

```python
from aimq.langgraph.checkpoint import get_checkpointer

checkpointer = get_checkpointer()

# Load specific checkpoint
config = {
    "configurable": {
        "thread_id": "user-123-session-456",
        "checkpoint_id": "specific-checkpoint-id"
    }
}

result = agent.invoke(input_data, config)
```

## Performance Considerations

### Index Optimization

The schema includes indexes for common queries. For high-volume deployments, consider additional indexes:

```sql
-- Index on metadata fields (if querying metadata frequently)
CREATE INDEX idx_checkpoints_metadata_gin
    ON checkpoints USING gin(metadata);

-- Partial index for recent checkpoints only
CREATE INDEX idx_checkpoints_recent
    ON checkpoints(thread_id, checkpoint_ns)
    WHERE (checkpoint->>'ts')::BIGINT > EXTRACT(EPOCH FROM NOW() - INTERVAL '7 days');
```

### Connection Pooling

For production deployments with many workers, use connection pooling to prevent connection exhaustion:

```python
# In pyproject.toml dependencies
"pgbouncer-psycopg2>=1.0.0"

# Or use Supabase's built-in connection pooling
# Connection string format:
# postgresql://postgres:[PASSWORD]@db.[PROJECT].supabase.co:6543/postgres
```

### Checkpoint Size

Large checkpoints can impact performance. Monitor checkpoint size:

```sql
-- Check average checkpoint size per thread
SELECT
    thread_id,
    COUNT(*) as checkpoint_count,
    AVG(pg_column_size(checkpoint)) / 1024 as avg_size_kb,
    MAX(pg_column_size(checkpoint)) / 1024 as max_size_kb
FROM checkpoints
GROUP BY thread_id
ORDER BY avg_size_kb DESC
LIMIT 10;
```

## See Also

- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [Supabase PostgreSQL Guide](https://supabase.com/docs/guides/database)
- [AIMQ Worker Configuration](../README.md)

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

**Option A: Supabase SQL Editor (Recommended for Production)**

This is the recommended approach for production deployments as it gives you full control over permissions and RLS policies.

1. Go to your Supabase project dashboard
2. Navigate to **SQL Editor**
3. Copy the contents of `docs/deployment/langgraph-schema.sql`
4. Paste into a new query and click **Run**
5. Verify tables created:
   ```sql
   SELECT * FROM langgraph.checkpoints LIMIT 1;
   ```

**Option B: Automatic Schema Creation (Development Only)**

For local development and testing, you can enable automatic schema creation:

```bash
# Add to .env file
LANGGRAPH_CHECKPOINT_ENABLED=true
```

The schema will be created automatically on first use. **Note**: This requires database admin permissions and may fail in production Supabase environments. Use Option A for production.

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
    created_at,
    jsonb_pretty(metadata) as metadata
FROM langgraph.checkpoints
ORDER BY created_at DESC
LIMIT 10;

-- Count checkpoints per thread
SELECT
    thread_id,
    COUNT(*) as checkpoint_count,
    MAX(created_at) as last_checkpoint
FROM langgraph.checkpoints
GROUP BY thread_id
ORDER BY last_checkpoint DESC;
```

## Configuration

### Environment Variables

```bash
# Required for checkpointing
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-service-role-key

# Optional: Enable automatic schema creation (dev only)
LANGGRAPH_CHECKPOINT_ENABLED=true

# Optional: Control iteration limits
LANGGRAPH_MAX_ITERATIONS=20
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

### "Permission denied" error

**Problem**: Cannot create schema automatically

**Solution**: Create schema manually using Supabase SQL Editor (see Setup Steps, Option A)

```sql
-- Run in Supabase SQL Editor
-- See docs/deployment/langgraph-schema.sql
```

### "Connection failed" error

**Problem**: Cannot connect to Supabase PostgreSQL

**Solution**: Verify environment variables are set correctly

```bash
# Check values
echo $SUPABASE_URL
echo $SUPABASE_KEY

# Should output:
# https://your-project.supabase.co
# eyJ... (your service role key)
```

**Common issues**:
- Using `anon` key instead of `service_role` key
- URL includes trailing slash (should not)
- Environment variables not loaded (.env file not in working directory)

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
-- Run as database admin
GRANT USAGE ON SCHEMA langgraph TO your_role;
GRANT ALL ON langgraph.checkpoints TO your_role;
```

For Supabase, the default role is `authenticated`. See schema setup SQL for details.

## Cleanup

### Remove Old Checkpoints

Checkpoints accumulate over time. Use the cleanup function to remove old entries:

```sql
-- Delete checkpoints older than 30 days (default)
SELECT langgraph.cleanup_old_checkpoints();

-- Delete checkpoints older than 7 days
SELECT langgraph.cleanup_old_checkpoints(7);

-- Delete all checkpoints for a specific thread
DELETE FROM langgraph.checkpoints
WHERE thread_id = 'user-123-session-456';
```

### Schedule Automatic Cleanup

Create a Supabase Edge Function or cron job to run cleanup periodically:

```sql
-- Using pg_cron (if available)
SELECT cron.schedule(
    'cleanup-langgraph-checkpoints',
    '0 2 * * *',  -- Run daily at 2 AM
    $$SELECT langgraph.cleanup_old_checkpoints(30)$$
);
```

## Advanced Usage

### Multi-Tenant Isolation

Enable Row Level Security (RLS) for tenant-specific checkpoint access:

```sql
-- Enable RLS
ALTER TABLE langgraph.checkpoints ENABLE ROW LEVEL SECURITY;

-- Policy: Users can only access their own checkpoints
CREATE POLICY "tenant_isolation"
    ON langgraph.checkpoints
    FOR ALL
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
    jsonb_pretty(metadata) as metadata,
    created_at
FROM langgraph.checkpoints
WHERE thread_id = 'user-123-session-456'
ORDER BY created_at DESC
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
    ON langgraph.checkpoints USING gin(metadata);

-- Partial index for recent checkpoints only
CREATE INDEX idx_checkpoints_recent
    ON langgraph.checkpoints(thread_id, created_at)
    WHERE created_at > NOW() - INTERVAL '7 days';
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
FROM langgraph.checkpoints
GROUP BY thread_id
ORDER BY avg_size_kb DESC
LIMIT 10;
```

## See Also

- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [Supabase PostgreSQL Guide](https://supabase.com/docs/guides/database)
- [AIMQ Worker Configuration](../README.md)

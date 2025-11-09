-- LangGraph Checkpoint Schema for PostgreSQL
-- Enables stateful, resumable workflows by persisting agent state
--
-- This migration creates the necessary database schema for LangGraph checkpointing
-- using PostgresSaver (from langgraph.checkpoint.postgres).
--
-- What gets created:
--   - 4 tables: checkpoints, checkpoint_blobs, checkpoint_writes, checkpoint_migrations
--   - Indexes for performance
--   - Cleanup function for old checkpoints
--   - Permissions for authenticated role
--
-- See: docs/user-guide/checkpointing.md for usage guide

-- Migration tracking table
CREATE TABLE IF NOT EXISTS checkpoint_migrations (
    v INTEGER PRIMARY KEY
);

-- Main checkpoints table
CREATE TABLE IF NOT EXISTS checkpoints (
    thread_id TEXT NOT NULL,
    checkpoint_ns TEXT NOT NULL DEFAULT '',
    checkpoint_id TEXT NOT NULL,
    parent_checkpoint_id TEXT,
    type TEXT,
    checkpoint JSONB NOT NULL,
    metadata JSONB NOT NULL DEFAULT '{}',
    PRIMARY KEY (thread_id, checkpoint_ns, checkpoint_id)
);

-- Blob storage for large binary data
CREATE TABLE IF NOT EXISTS checkpoint_blobs (
    thread_id TEXT NOT NULL,
    checkpoint_ns TEXT NOT NULL DEFAULT '',
    channel TEXT NOT NULL,
    version TEXT NOT NULL,
    type TEXT NOT NULL,
    blob BYTEA,  -- Nullable after migration 4
    PRIMARY KEY (thread_id, checkpoint_ns, channel, version)
);

-- Write operations tracking
CREATE TABLE IF NOT EXISTS checkpoint_writes (
    thread_id TEXT NOT NULL,
    checkpoint_ns TEXT NOT NULL DEFAULT '',
    checkpoint_id TEXT NOT NULL,
    task_id TEXT NOT NULL,
    idx INTEGER NOT NULL,
    channel TEXT NOT NULL,
    type TEXT,
    blob BYTEA NOT NULL,
    task_path TEXT NOT NULL DEFAULT '',
    PRIMARY KEY (thread_id, checkpoint_ns, checkpoint_id, task_id, idx)
);

-- Create indexes for performance
-- Note: Using CREATE INDEX (not CONCURRENTLY) for compatibility with Supabase SQL Editor
CREATE INDEX IF NOT EXISTS checkpoints_thread_id_idx ON checkpoints(thread_id);
CREATE INDEX IF NOT EXISTS checkpoint_blobs_thread_id_idx ON checkpoint_blobs(thread_id);
CREATE INDEX IF NOT EXISTS checkpoint_writes_thread_id_idx ON checkpoint_writes(thread_id);

-- Record migration version (matches PostgresSaver.MIGRATIONS[9])
INSERT INTO checkpoint_migrations (v) VALUES (9)
ON CONFLICT (v) DO NOTHING;

-- Optional: Add cleanup function for old checkpoints
CREATE OR REPLACE FUNCTION cleanup_old_checkpoints(days_old INT DEFAULT 30)
RETURNS TABLE(deleted_checkpoints INT, deleted_blobs INT, deleted_writes INT) AS $$
DECLARE
    checkpoint_count INT;
    blob_count INT;
    write_count INT;
BEGIN
    -- Delete old checkpoint writes
    DELETE FROM checkpoint_writes
    WHERE (thread_id, checkpoint_ns, checkpoint_id) IN (
        SELECT thread_id, checkpoint_ns, checkpoint_id
        FROM checkpoints
        WHERE (checkpoint->>'ts')::BIGINT < EXTRACT(EPOCH FROM NOW() - (days_old || ' days')::INTERVAL)
    );
    GET DIAGNOSTICS write_count = ROW_COUNT;

    -- Delete old checkpoint blobs
    DELETE FROM checkpoint_blobs
    WHERE (thread_id, checkpoint_ns) IN (
        SELECT DISTINCT thread_id, checkpoint_ns
        FROM checkpoints
        WHERE (checkpoint->>'ts')::BIGINT < EXTRACT(EPOCH FROM NOW() - (days_old || ' days')::INTERVAL)
    );
    GET DIAGNOSTICS blob_count = ROW_COUNT;

    -- Delete old checkpoints
    DELETE FROM checkpoints
    WHERE (checkpoint->>'ts')::BIGINT < EXTRACT(EPOCH FROM NOW() - (days_old || ' days')::INTERVAL);
    GET DIAGNOSTICS checkpoint_count = ROW_COUNT;

    RETURN QUERY SELECT checkpoint_count, blob_count, write_count;
END;
$$ LANGUAGE plpgsql;

-- Grant permissions (adjust as needed for your setup)
-- Note: This grants access to the 'authenticated' role (default for Supabase)
-- Customize based on your RLS policies and security requirements
GRANT USAGE ON SCHEMA public TO authenticated;
GRANT ALL ON checkpoints TO authenticated;
GRANT ALL ON checkpoint_blobs TO authenticated;
GRANT ALL ON checkpoint_writes TO authenticated;
GRANT ALL ON checkpoint_migrations TO authenticated;

-- Optional: Enable Row Level Security (RLS) for multi-tenant isolation
-- Uncomment if you need tenant-specific checkpoint access control
--
-- ALTER TABLE checkpoints ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE checkpoint_blobs ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE checkpoint_writes ENABLE ROW LEVEL SECURITY;
--
-- CREATE POLICY "Users can only access their own checkpoints"
--     ON checkpoints
--     FOR ALL
--     USING (thread_id LIKE auth.uid() || '%');
--
-- CREATE POLICY "Users can only access their own blobs"
--     ON checkpoint_blobs
--     FOR ALL
--     USING (thread_id LIKE auth.uid() || '%');
--
-- CREATE POLICY "Users can only access their own writes"
--     ON checkpoint_writes
--     FOR ALL
--     USING (thread_id LIKE auth.uid() || '%');

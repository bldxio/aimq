-- LangGraph Checkpoint Schema for Supabase
-- Run this in Supabase SQL Editor before enabling checkpointing
--
-- This script sets up the necessary database schema for LangGraph checkpointing.
-- Checkpointing enables stateful, resumable workflows by persisting agent state.
--
-- Prerequisites:
--   - Supabase project with PostgreSQL access
--   - Database admin permissions (or run via Supabase SQL Editor)
--
-- Usage:
--   1. Open Supabase dashboard → SQL Editor
--   2. Copy and paste this entire script
--   3. Click "Run" to execute
--   4. Verify: SELECT * FROM langgraph.checkpoints LIMIT 1;
--
-- See: docs/user-guide/checkpointing.md for full setup guide

-- Create schema
CREATE SCHEMA IF NOT EXISTS langgraph;

-- Create checkpoints table
CREATE TABLE IF NOT EXISTS langgraph.checkpoints (
    thread_id TEXT NOT NULL,
    checkpoint_id TEXT NOT NULL,
    parent_checkpoint_id TEXT,
    checkpoint JSONB NOT NULL,
    metadata JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    PRIMARY KEY (thread_id, checkpoint_id)
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_checkpoints_thread
    ON langgraph.checkpoints(thread_id);

CREATE INDEX IF NOT EXISTS idx_checkpoints_created
    ON langgraph.checkpoints(created_at);

CREATE INDEX IF NOT EXISTS idx_checkpoints_parent
    ON langgraph.checkpoints(parent_checkpoint_id);

-- Optional: Add cleanup function for old checkpoints
CREATE OR REPLACE FUNCTION langgraph.cleanup_old_checkpoints(days_old INT DEFAULT 30)
RETURNS INT AS $$
DECLARE
    deleted_count INT;
BEGIN
    DELETE FROM langgraph.checkpoints
    WHERE created_at < NOW() - (days_old || ' days')::INTERVAL;

    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

-- Grant permissions (adjust as needed for your setup)
-- Note: This grants access to the 'authenticated' role (default for Supabase)
-- Customize based on your RLS policies and security requirements
GRANT USAGE ON SCHEMA langgraph TO authenticated;
GRANT ALL ON langgraph.checkpoints TO authenticated;

-- Optional: Enable Row Level Security (RLS) for multi-tenant isolation
-- Uncomment if you need tenant-specific checkpoint access control
--
-- ALTER TABLE langgraph.checkpoints ENABLE ROW LEVEL SECURITY;
--
-- CREATE POLICY "Users can only access their own checkpoints"
--     ON langgraph.checkpoints
--     FOR ALL
--     USING (thread_id LIKE auth.uid() || '%');

-- Verification query - should return 0 rows on fresh install
SELECT COUNT(*) as checkpoint_count FROM langgraph.checkpoints;

-- Success message
DO $$
BEGIN
    RAISE NOTICE 'LangGraph checkpoint schema initialized successfully!';
    RAISE NOTICE 'Set LANGGRAPH_CHECKPOINT_ENABLED=true to enable checkpointing.';
END $$;

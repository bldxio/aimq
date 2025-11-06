# Phase 4: Tools & Checkpointing

**Status**: ⏳ Not Started
**Priority**: 1 (Critical)
**Estimated**: 2-3 hours
**Dependencies**: Phase 1 (Complete)

---

## Objectives

Implement tool wrappers and validate checkpointing:
1. Create Docling document converter tool
2. Create ToolInputValidator for security (Fix #12)
3. Verify checkpointing works with Supabase
4. Document manual schema setup for production

## Critical Fixes Applied

- **Fix #12**: Tool input validation module with security checks

---

## Implementation Steps

### 4.1 Docling Tool (1 hour)

#### 4.1.1 Create Module Structure

**Action**: Create docling tools module:

```bash
mkdir -p src/aimq/tools/docling
touch src/aimq/tools/docling/__init__.py
```

#### 4.1.2 Implement DoclingConverter

**File**: `src/aimq/tools/docling/converter.py`

```python
"""Docling document converter tool."""

from langchain.tools import BaseTool
from docling.document_converter import DocumentConverter
from typing import Literal


class DoclingConverter(BaseTool):
    """
    Convert documents using Docling.

    Supports: PDF, DOCX, PPTX, XLSX, images
    Features: Layout analysis, table extraction, OCR

    Example:
        tool = DoclingConverter()
        result = tool.invoke({
            "file_path": "report.pdf",
            "export_format": "markdown"
        })
    """

    name = "docling_convert"
    description = """Convert documents (PDF, DOCX, PPTX, XLSX, images) to structured format.
    Supports layout analysis, table extraction, OCR for scanned documents."""

    def _run(
        self,
        file_path: str,
        export_format: Literal["markdown", "html", "json"] = "markdown"
    ) -> dict:
        """Convert document.

        Args:
            file_path: Path to document file
            export_format: Output format (markdown, html, or json)

        Returns:
            Dict with content, format, and metadata
        """
        converter = DocumentConverter()
        result = converter.convert(file_path)

        if export_format == "markdown":
            content = result.document.export_to_markdown()
        elif export_format == "html":
            content = result.document.export_to_html()
        else:  # json
            content = result.document.export_to_dict()

        return {
            "content": content,
            "format": export_format,
            "metadata": result.document.metadata,
        }
```

#### 4.1.3 Update Module Exports

**File**: `src/aimq/tools/docling/__init__.py`

```python
"""Docling document processing tools."""

from aimq.tools.docling.converter import DoclingConverter

__all__ = ["DoclingConverter"]
```

**Validation**:

```bash
uv run python -c "
from aimq.tools.docling import DoclingConverter
tool = DoclingConverter()
print('DoclingConverter tool created')
print(f'Tool name: {tool.name}')
"
```

---

### 4.2 Tool Validation Module (1 hour)

**File**: `src/aimq/langgraph/validation.py`

**Action**: Create comprehensive tool validation (Fix #12):

```python
"""
Tool input validation for security.

Validates tool inputs before execution to prevent injection attacks.
"""

from typing import Any, Dict
from langchain.tools import BaseTool
from pydantic import ValidationError
import logging
import os
from pathlib import Path

from aimq.langgraph.exceptions import ToolValidationError

logger = logging.getLogger(__name__)


class ToolInputValidator:
    """Validates tool inputs against tool schemas for security (Fix #12)."""

    def validate(self, tool: BaseTool, input_data: dict) -> dict:
        """Validate tool input against tool's args_schema.

        Args:
            tool: LangChain tool to validate against
            input_data: Input data from LLM or user

        Returns:
            Validated input dict

        Raises:
            ToolValidationError: If validation fails

        Examples:
            >>> validator = ToolInputValidator()
            >>> validated = validator.validate(read_file_tool, {"path": "file.txt"})
        """
        tool_name = tool.name

        try:
            # Use Pydantic schema validation if available
            if hasattr(tool, 'args_schema') and tool.args_schema:
                validated = tool.args_schema(**input_data)
                logger.debug(f"Tool '{tool_name}' input validated")
                return validated.dict()
            else:
                # No schema - log warning and pass through
                logger.warning(
                    f"Tool '{tool_name}' has no args_schema, "
                    f"input validation skipped"
                )
                return input_data

        except ValidationError as e:
            logger.error(
                f"Tool '{tool_name}' input validation failed: {e}",
                extra={"tool": tool_name, "input": input_data}
            )
            raise ToolValidationError(
                f"Invalid input for tool '{tool_name}': {e}"
            ) from e

        except Exception as e:
            logger.error(
                f"Unexpected error validating tool '{tool_name}': {e}",
                exc_info=True
            )
            raise ToolValidationError(
                f"Tool validation failed for '{tool_name}': {e}"
            ) from e

    def validate_file_path(
        self,
        path: str,
        allowed_patterns: list[str] | None = None
    ) -> None:
        """Validate file path for security (Fix #12).

        Prevents:
        - Path traversal attacks (../)
        - Absolute paths outside allowed directories
        - Access to sensitive system files

        Args:
            path: File path to validate
            allowed_patterns: List of allowed path patterns (glob style)

        Raises:
            ToolValidationError: If path is invalid or unauthorized

        Examples:
            >>> validator = ToolInputValidator()
            >>> validator.validate_file_path("data/file.txt")
            >>> validator.validate_file_path("/tmp/file.txt", ["/tmp/*"])
        """
        # Normalize path
        normalized = os.path.normpath(path)

        # Check for path traversal
        if ".." in normalized:
            raise ToolValidationError(
                f"Path traversal not allowed: {path}"
            )

        # Check if absolute path
        if os.path.isabs(normalized):
            # Only allow if matches patterns
            if allowed_patterns:
                from fnmatch import fnmatch
                if not any(fnmatch(normalized, pattern) for pattern in allowed_patterns):
                    raise ToolValidationError(
                        f"Absolute path not in allowed patterns: {path}"
                    )

        # Check for sensitive files
        sensitive = ["/etc/passwd", "/etc/shadow", ".ssh/", ".env"]
        if any(s in normalized for s in sensitive):
            raise ToolValidationError(
                f"Access to sensitive file not allowed: {path}"
            )

        logger.debug(f"File path validated: {normalized}")

    def validate_sql_query(self, query: str) -> None:
        """Validate SQL query for basic injection patterns (Fix #12).

        This is a simple check - use parameterized queries in production.

        Args:
            query: SQL query to validate

        Raises:
            ToolValidationError: If query contains suspicious patterns
        """
        suspicious = [
            "DROP TABLE",
            "DELETE FROM",
            "TRUNCATE",
            "ALTER TABLE",
            "EXEC ",
            "EXECUTE ",
            ";--",
            "/**/",
        ]

        query_upper = query.upper()

        for pattern in suspicious:
            if pattern in query_upper:
                raise ToolValidationError(
                    f"Suspicious SQL pattern detected: {pattern}"
                )

        logger.debug("SQL query validated")
```

**Validation**:

```bash
uv run python -c "
from aimq.langgraph.validation import ToolInputValidator

validator = ToolInputValidator()

# Test path validation
try:
    validator.validate_file_path('data/file.txt')
    print('Path validation working')
except:
    print('Path validation failed')

# Test path traversal detection
try:
    validator.validate_file_path('../etc/passwd')
    print('ERROR: Path traversal not detected!')
except Exception as e:
    print(f'Path traversal blocked: {type(e).__name__}')
"
```

---

### 4.3 Checkpointing Verification (30 minutes - 1 hour)

#### 4.3.1 Test Connection String Building

**Action**: Verify connection string works with Supabase:

```bash
uv run python -c "
from aimq.langgraph.checkpoint import _build_connection_string
import os

# Set test env vars
os.environ['SUPABASE_URL'] = 'https://test-project.supabase.co'
os.environ['SUPABASE_KEY'] = 'test-key'

conn_str = _build_connection_string()
print('Connection string:', conn_str)

# Verify URL encoding
assert 'postgresql://' in conn_str
assert 'test-project' in conn_str
print('Connection string format correct')
"
```

#### 4.3.2 Document Manual Schema Setup

**File**: `docs/deployment/langgraph-schema.sql`

**Action**: Create schema setup SQL for production:

```sql
-- LangGraph Checkpoint Schema for Supabase
-- Run this in Supabase SQL Editor before enabling checkpointing

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
GRANT USAGE ON SCHEMA langgraph TO authenticated;
GRANT ALL ON langgraph.checkpoints TO authenticated;
```

#### 4.3.3 Create Checkpointing Setup Guide

**File**: `docs/user-guide/checkpointing.md`

**Action**: Document checkpointing setup:

```markdown
# LangGraph Checkpointing Setup

## Overview

LangGraph checkpointing enables stateful, resumable workflows by persisting agent/workflow state to Supabase PostgreSQL.

## Prerequisites

- Supabase project with pgmq enabled
- PostgreSQL access (via Supabase dashboard or SQL Editor)
- SUPABASE_URL and SUPABASE_KEY environment variables

## Setup Steps

### 1. Create Database Schema

**Option A: Supabase SQL Editor (Recommended)**

1. Go to your Supabase project dashboard
2. Navigate to SQL Editor
3. Copy and run the SQL from `docs/deployment/langgraph-schema.sql`
4. Verify tables created: `SELECT * FROM langgraph.checkpoints LIMIT 1;`

**Option B: Automatic (Development Only)**

Set environment variable:
```bash
export LANGGRAPH_CHECKPOINT_ENABLED=true
```

The schema will be created automatically on first use (requires admin permissions).

### 2. Enable Checkpointing in Agents/Workflows

```python
from aimq.agents import ReActAgent

agent = ReActAgent(
    tools=[...],
    memory=True,  # Enable checkpointing
)
```

### 3. Verify Checkpointing Works

```python
# Send a job with thread_id for resumable execution
worker.send("agent-queue", {
    "messages": [...],
    "thread_id": "user-123-session-456",
})

# Check checkpoints table
SELECT thread_id, checkpoint_id, created_at
FROM langgraph.checkpoints
ORDER BY created_at DESC
LIMIT 10;
```

## Troubleshooting

### "Permission denied" error

Create schema manually using SQL Editor (see Setup Steps).

### "Connection failed" error

Verify SUPABASE_URL and SUPABASE_KEY are correct:
```bash
echo $SUPABASE_URL
echo $SUPABASE_KEY
```

### Checkpoints not saving

Enable debug logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Cleanup

Remove old checkpoints (optional):
```sql
SELECT langgraph.cleanup_old_checkpoints(30);  -- Delete checkpoints older than 30 days
```
```

---

## Testing & Validation

### Manual Tests

**Test 1: Docling Tool**

```bash
# Create test document
echo "# Test Document" > /tmp/test.md

# Test tool
uv run python -c "
from aimq.tools.docling import DoclingConverter

tool = DoclingConverter()
result = tool._run('/tmp/test.md', 'markdown')
print('Conversion result:', result)
"
```

**Test 2: Tool Validation**

```bash
uv run python -c "
from aimq.langgraph.validation import ToolInputValidator

validator = ToolInputValidator()

# Test safe path
validator.validate_file_path('data/file.txt')
print('✓ Safe path validated')

# Test dangerous path (should raise)
try:
    validator.validate_file_path('../etc/passwd')
    print('✗ Path traversal NOT blocked!')
except Exception as e:
    print(f'✓ Path traversal blocked: {type(e).__name__}')
"
```

**Test 3: Checkpointing**

```bash
# Test connection string building (no actual connection)
uv run python -c "
from aimq.langgraph.checkpoint import _build_connection_string
import os

os.environ['SUPABASE_URL'] = 'https://test.supabase.co'
os.environ['SUPABASE_KEY'] = 'test!@#key'

conn_str = _build_connection_string()
assert 'postgresql://' in conn_str
assert '%' in conn_str  # URL encoding
print('✓ Connection string encoding works')
"
```

---

## Definition of Done

### Code Complete

- [ ] DoclingConverter tool implemented
- [ ] ToolInputValidator fully implemented (Fix #12)
- [ ] All validation methods working
- [ ] Schema SQL script created
- [ ] Setup documentation complete

### Validation

- [ ] Docling tool importable
- [ ] Tool validation catches path traversal
- [ ] Tool validation catches SQL injection
- [ ] Connection string builds correctly
- [ ] Schema SQL runs without errors

### Documentation

- [ ] Schema setup SQL documented
- [ ] Checkpointing guide created
- [ ] Manual setup instructions clear
- [ ] Troubleshooting section complete

---

## Common Pitfalls

### Tool Validation Bypass

**Pitfall**: Calling tool.invoke() directly without validation

**Solution**: Always validate in agent nodes
```python
# Wrong
result = tool.invoke(tool_input)

# Correct
validator = ToolInputValidator()
validated = validator.validate(tool, tool_input)
result = tool.invoke(validated)
```

### Path Traversal Not Caught

**Pitfall**: Only checking for "../" without normalization

**Solution**: Use os.path.normpath first
```python
# Wrong
if ".." in path:  # Can be bypassed with ././../

# Correct
normalized = os.path.normpath(path)
if ".." in normalized:
```

### Checkpointer Permission Issues

**Pitfall**: Trying to create schema without admin permissions

**Solution**: Create schema manually in production
```sql
-- Run in Supabase SQL Editor
-- See docs/deployment/langgraph-schema.sql
```

---

## Next Phase

Once Phase 4 is complete:
- [ ] Update PROGRESS.md
- [ ] Move to **Phase 5: Examples** ([PHASE5.md](./PHASE5.md))

---

**Phase Owner**: Implementation Team
**Started**: ___________
**Completed**: ___________
**Actual Hours**: ___________

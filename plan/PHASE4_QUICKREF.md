# Phase 4 Quick Reference

## Import Statements

```python
# Tool Input Validation (Security - Fix #12)
from aimq.langgraph import ToolInputValidator
from aimq.langgraph.validation import ToolInputValidator
from aimq.langgraph.exceptions import ToolValidationError

# Docling Document Converter
from aimq.tools.docling import DoclingConverter

# Checkpointing
from aimq.langgraph.checkpoint import get_checkpointer
```

## Tool Input Validation Usage

```python
# Create validator
validator = ToolInputValidator()

# Validate tool input against schema
validated = validator.validate(tool, input_data)

# Validate file paths (security)
validator.validate_file_path("data/file.txt")  # OK
validator.validate_file_path("../etc/passwd")  # Raises ToolValidationError

# Validate SQL queries (injection detection)
validator.validate_sql_query("SELECT * FROM users")  # OK
validator.validate_sql_query("DROP TABLE users")  # Raises ToolValidationError
```

## Docling Converter Usage

```python
# Create tool
tool = DoclingConverter()

# Convert document
result = tool.invoke({
    "file_path": "report.pdf",
    "export_format": "markdown"  # or "html", "json"
})

# Result structure
{
    "content": "...",  # Converted content
    "format": "markdown",
    "metadata": {...}  # Document metadata
}
```

## Checkpointing Setup

### Production (Manual - Recommended)

1. Open Supabase SQL Editor
2. Run: `docs/deployment/langgraph-schema.sql`
3. Set environment variable: `LANGGRAPH_CHECKPOINT_ENABLED=true`

### Development (Automatic)

```bash
# .env file
LANGGRAPH_CHECKPOINT_ENABLED=true
```

### Agent Configuration

```python
from aimq.langgraph import agent

@agent(
    tools=[...],
    memory=True,  # Enable checkpointing
)
def my_agent(graph, config):
    # Define agent graph
    pass
```

### Using Thread IDs

```python
# Send job with thread_id for resumable execution
worker.send("agent-queue", {
    "messages": [...],
    "thread_id": "user-123-session-456",
})
```

## Security Features

### Path Traversal Prevention
- Normalizes paths before validation
- Blocks `../` patterns
- Blocks sensitive directories: `/etc/`, `.ssh/`, `.env`

### SQL Injection Detection
- Blocks: `DROP TABLE`, `DELETE FROM`, `TRUNCATE`, `ALTER TABLE`
- Blocks: `EXEC`, `EXECUTE`, `;--`, `/**/`

### Input Validation
- Pydantic schema enforcement
- Type checking
- Required field validation

## Files Reference

| Purpose | File |
|---------|------|
| Tool Validation | `src/aimq/langgraph/validation.py` |
| Docling Tool | `src/aimq/tools/docling/converter.py` |
| Schema SQL | `docs/deployment/langgraph-schema.sql` |
| User Guide | `docs/user-guide/checkpointing.md` |
| Full Summary | `PHASE4_SUMMARY.md` |

## Integration Status

- **Phase 2 (Agents)**: ToolInputValidator ready for use
- **Phase 3 (Workflows)**: DoclingConverter ready for use
- **Production**: Schema SQL and docs ready for deployment

## Next Steps

1. Phase 2 can integrate ToolInputValidator
2. Phase 5 can begin (Examples)
3. Production: Run schema SQL in Supabase

# AIMQ-Specific Pitfalls

Common mistakes specific to AIMQ development with LangChain, message agents, and pgmq.

## Message Serialization for Queues

**Problem**: LangChain message objects (HumanMessage, AIMessage) are not JSON serializable.

**Symptom**:
```python
TypeError: Object of type HumanMessage is not JSON serializable
```

**Root Cause**: Queue systems need JSON-serializable data, but LangChain messages are Python objects with complex internal state.

**Example**:
```python
from langchain_core.messages import HumanMessage

# ❌ Bad: Sending LangChain message objects to queue
message = HumanMessage(content="Hello!")
queue.send({
    "messages": [message]  # Not JSON serializable!
})

# ✅ Good: Convert to dict before sending
queue.send({
    "messages": [{"role": "user", "content": "Hello!"}]
})

# ✅ Also good: Use message.dict() if available
queue.send({
    "messages": [message.dict()]
})
```

**When It Happens**:
- Sending messages to queues (pgmq, Redis, etc.)
- Storing messages in databases
- Passing messages between services
- Any boundary crossing (network, storage, etc.)

**Prevention**:
- Always serialize at boundaries
- Test with actual queue/database early
- Use `message.dict()` or manual conversion
- Consider using message schemas (Pydantic)

**From Message Agent**:
```python
# Initial bug
job_data = {
    "messages": [HumanMessage(content=body)],  # ❌ Failed
    "metadata": metadata
}

# Fixed version
job_data = {
    "messages": [{"role": "user", "content": body}],  # ✅ Works
    "metadata": metadata
}
```

## Regex Edge Cases: Email Addresses

**Problem**: Simple @mention regex matches email addresses.

**Symptom**:
```python
mentions = detect_mentions("Contact user@example.com")
# Returns: ["user", "example"]  # ❌ Wrong!
```

**Root Cause**: The `@` symbol appears in both mentions and email addresses.

**Example**:
```python
# ❌ Bad: Matches emails as mentions
pattern = r'@(\w+)'
re.findall(pattern, "user@example.com")  # ["user", "example"]

# ✅ Good: Use word boundaries
pattern = r'@(\w+)(?=\s|$|[^\w@])'
re.findall(pattern, "user@example.com")  # []

# ✅ Also good: Negative lookbehind/lookahead
pattern = r'(?<!\w)@(\w+)(?!\w)'
```

**Test Cases**:
```python
def test_detect_mentions_ignores_emails():
    """Should not detect email addresses as mentions."""
    assert detect_mentions("user@example.com") == []
    assert detect_mentions("Contact: admin@site.org") == []

def test_detect_mentions_with_email_and_mention():
    """Should detect mentions but not emails."""
    text = "Hey @alice, email me at bob@example.com"
    assert detect_mentions(text) == ["alice"]
```

**Prevention**:
- Test regex with real-world data
- Consider edge cases (emails, URLs, etc.)
- Use word boundaries when appropriate
- Write comprehensive tests

**From Message Agent**:
```python
# Initial regex
r'@(\w+)'  # ❌ Matched emails

# Fixed regex
r'@(\w+)(?=\s|$|[^\w@])'  # ✅ Ignores emails
```

## pgmq Function Signatures

**Problem**: Calling pgmq functions with incorrect parameter names or structure.

**Symptom**:
```python
APIError: {'message': 'Could not find the function public.pgmq_send(msg, queue_name)
in the schema cache', 'code': 'PGRST202'}
```

**Root Cause**: pgmq functions have specific parameter names and order that must match exactly.

**Example**:
```python
# ❌ Bad: Wrong parameter names
supabase.rpc("pgmq_send", {
    "msg": payload,
    "queue_name": "my-queue"
})

# ✅ Good: Correct parameter names (check pgmq docs)
supabase.rpc("pgmq_send", {
    "queue_name": "my-queue",
    "msg": payload
})
```

**Prevention**:
- Check pgmq documentation for exact function signatures
- Test with actual Supabase instance early
- Use type hints if available
- Log function calls for debugging

**Common pgmq Functions**:
```python
# Send message
supabase.rpc("pgmq_send", {
    "queue_name": str,
    "msg": dict
})

# Read messages
supabase.rpc("pgmq_read", {
    "queue_name": str,
    "vt": int,  # visibility timeout
    "qty": int  # quantity
})

# Archive message
supabase.rpc("pgmq_archive", {
    "queue_name": str,
    "msg_id": int
})

# Delete message
supabase.rpc("pgmq_delete", {
    "queue_name": str,
    "msg_id": int
})
```

**From Message Agent**:
- Initial demo script had incorrect function names
- Fixed by checking pgmq documentation
- Added error handling for missing functions

## Supabase & PostgreSQL Pitfalls

### SQL Identifier Quoting for Special Characters

**Problem**: Queue names with hyphens or special characters cause SQL syntax errors.

**Symptom**:
```
ERROR: 42601: syntax error at or near "-"
LINE 1: SELECT * FROM pgmq.incoming-messages
```

**Root Cause**: PostgreSQL identifiers with special characters must be quoted in dynamic SQL.

**Example**:
```sql
-- ❌ Bad: Unquoted identifier in dynamic SQL
execute format('SELECT * FROM pgmq.%s', queue_name);
-- Fails for queue_name = 'incoming-messages'

-- ✅ Good: Use %I for identifier formatting
execute format('SELECT * FROM pgmq.%I', queue_name);
-- Properly quotes: SELECT * FROM pgmq."incoming-messages"

-- ✅ Also good: Use quote_ident()
execute format('SELECT * FROM pgmq.%s', quote_ident(queue_name));
```

**When It Happens**:
- User-provided queue names (CLI, API)
- Dynamic SQL with `execute format()`
- Table/column names with hyphens, spaces, or special chars
- Case-sensitive identifiers

**Prevention**:
- Always use `%I` for identifiers in `format()`
- Use `quote_ident()` for manual quoting
- Test with hyphenated names early
- Document naming conventions

**From Phase 2 Realtime**:
```sql
-- Fixed in enable_queue_realtime function
create or replace function pgmq_public.enable_queue_realtime(
    queue_name text
)
  returns jsonb
  language plpgsql
as $$
declare
    v_trigger_name text;
begin
    -- ✅ Properly quote identifiers
    v_trigger_name := 'aimq_notify_' || queue_name;

    execute format(
        'create trigger %I
         after insert on pgmq.%I
         for each row
         execute function aimq.notify_job_enqueued()',
        v_trigger_name,  -- %I quotes trigger name
        queue_name       -- %I quotes table name
    );

    return jsonb_build_object('success', true);
end;
$$;
```

### PostgREST JSONB Parsing Failure

**Problem**: PostgREST fails to parse jsonb responses from functions using dynamic SQL.

**Symptom**:
```python
Error: {
    'message': 'JSON could not be generated',
    'code': 200,
    'hint': 'Refer to full message for details',
    'details': 'b\'{"success": true, "queue_name": "my-queue"}\''
}
```

**Root Cause**: PostgREST has trouble parsing jsonb responses from `execute format()` functions. The function executes successfully, but PostgREST can't parse the response. The actual result is buried in the error details.

**Example**:
```python
# ❌ Without workaround: Appears to fail
result = supabase.rpc('enable_queue_realtime', {'queue_name': 'test'})
# Raises exception even though function succeeded

# ✅ With workaround: Extract result from error
def _rpc(self, method: str, params: dict) -> Any:
    try:
        result = supabase.client.schema("pgmq_public").rpc(method, params).execute()
        return result.data
    except Exception as e:
        error_msg = str(e)

        # WORKAROUND: Extract JSON from error details
        if "'code': 200" in error_msg or "'code': '200'" in error_msg:
            # Format: 'details': 'b\'{"success": true, ...}\''
            match = re.search(r"'details':\s*'b\\'(.+?)\\'", error_msg)
            if match:
                try:
                    json_str = match.group(1).replace("\\'", "'")
                    return json.loads(json_str)
                except (json.JSONDecodeError, AttributeError):
                    pass  # Fall through to raise original error

        raise
```

**When It Happens**:
- Functions using `execute format()` with dynamic SQL
- Functions returning jsonb from dynamic queries
- Complex trigger setup functions
- Management functions that create/modify objects

**Prevention**:
- Implement the workaround in your RPC wrapper
- Test with actual Supabase instance early
- Consider alternative approaches (static SQL where possible)
- Document the limitation for future maintainers

**Alternative Approaches**:
```sql
-- Option 1: Return simple types instead of jsonb
create or replace function pgmq_public.enable_queue_realtime(
    queue_name text
)
  returns boolean  -- Simple type, no parsing issues
  language plpgsql
as $$
begin
    -- Implementation
    return true;
end;
$$;

-- Option 2: Use static SQL where possible
-- (Not always feasible for dynamic operations)
```

**From Phase 2 Realtime**:
```python
# Implemented in SupabaseQueueProvider._rpc()
# Handles both the error and successful cases
# All RPC calls go through this wrapper
```

## Related

- [@.claude/architecture/database-schema-organization.md](../architecture/database-schema-organization.md) - Schema patterns
- [@.claude/architecture/langchain-integration.md](../architecture/langchain-integration.md) - LangChain patterns
- [@.claude/quick-references/llm-api-differences.md](./llm-api-differences.md) - Provider API compatibility
- [@.claude/quick-references/common-pitfalls.md](./common-pitfalls.md) - All pitfalls index
- [@.claude/patterns/queue-error-handling.md](../patterns/queue-error-handling.md) - Queue error patterns

---

**Remember**: AIMQ-specific issues are often about boundaries—serialization, APIs, and integrations! 🔌✨

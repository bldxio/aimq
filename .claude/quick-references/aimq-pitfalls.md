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

## Related

- [@.claude/architecture/langchain-integration.md](../architecture/langchain-integration.md) - LangChain patterns
- [@.claude/quick-references/llm-api-differences.md](./llm-api-differences.md) - Provider API compatibility
- [@.claude/quick-references/common-pitfalls.md](./common-pitfalls.md) - All pitfalls index
- [@.claude/patterns/queue-error-handling.md](../patterns/queue-error-handling.md) - Queue error patterns

---

**Remember**: AIMQ-specific issues are often about boundaries—serialization, APIs, and integrations! 🔌✨

# Test Mocking Evolution for External Services

Pattern for evolving test mocking strategies as code matures from prototype to production.

## The Journey

Tests evolve through phases as code matures:

1. **Phase 1: Simple In-Memory** - Basic functionality, no external dependencies
2. **Phase 2: Mock External Calls** - Patch external service calls
3. **Phase 3: Realistic Response Structures** - Mock with actual API response formats
4. **Phase 4: Integration Tests** - Test against real services (staging/test environments)

## Why Tests Must Evolve

### The Problem

```python
# Phase 1: Simple test (prototype)
def test_wait_for_message():
    listener = RealtimeChatListener(...)

    # Directly inject message (no external service)
    test_payload = {"message_id": "123", "content": "test"}
    listener._handle_message_notification(test_payload)

    result = listener.wait_for_message("123")
    assert result is not None
```

**Issues:**
- Doesn't test actual Supabase integration
- Won't catch API changes
- Doesn't reflect real-world usage
- Brittle when implementation changes

### The Solution

```python
# Phase 3: Realistic mocking (production-ready)
@patch("aimq.clients.supabase.supabase")
def test_wait_for_message(mock_supabase):
    # Mock realistic Supabase response structure
    mock_response = Mock()
    mock_response.data = [
        {
            "msg_id": 12345,
            "message": {"message_id": "123", "content": "test response"},
        }
    ]
    mock_supabase.client.schema.return_value.rpc.return_value.execute.return_value = (
        mock_response
    )

    listener = RealtimeChatListener(...)
    result = listener.wait_for_message("123")

    assert result["message_id"] == "123"
    assert result["content"] == "test response"
```

**Benefits:**
- Tests actual integration code path
- Catches API structure changes
- Reflects real-world usage
- More maintainable

## Phase-by-Phase Evolution

### Phase 1: Simple In-Memory Tests

**When:** Early prototyping, proving concepts

**Characteristics:**
- No external dependencies
- Direct method calls
- Simple assertions
- Fast execution

**Example:**

```python
def test_message_queue():
    queue = MessageQueue()
    queue.add("test message")

    result = queue.get()
    assert result == "test message"
```

**Pros:**
- Fast to write
- Fast to run
- Easy to understand

**Cons:**
- Doesn't test integration
- Doesn't catch API issues
- Not realistic

### Phase 2: Mock External Calls

**When:** Moving beyond prototype, adding external services

**Characteristics:**
- Patch external service calls
- Return simple mock values
- Test error handling
- Still fast execution

**Example:**

```python
@patch("requests.post")
def test_send_webhook(mock_post):
    mock_post.return_value.status_code = 200

    result = send_webhook("https://example.com", {"data": "value"})

    assert result is True
    mock_post.assert_called_once()
```

**Pros:**
- Tests integration points
- Isolates external dependencies
- Can test error scenarios
- Still fast

**Cons:**
- Mock responses may not match reality
- Doesn't catch API structure changes
- May miss edge cases

### Phase 3: Realistic Response Structures

**When:** Production-ready code, stable APIs

**Characteristics:**
- Mock with actual API response formats
- Test response parsing
- Validate data structures
- Test error responses

**Example:**

```python
@patch("aimq.clients.supabase.supabase")
def test_fetch_message(mock_supabase):
    # Realistic Supabase response structure
    mock_response = Mock()
    mock_response.data = [
        {
            "msg_id": 12345,
            "read_ct": 0,
            "enqueued_at": "2025-11-23T12:00:00Z",
            "vt": "2025-11-23T12:05:00Z",
            "message": {
                "message_id": "msg_123",
                "content": "Hello world",
                "metadata": {"priority": "high"}
            }
        }
    ]
    mock_response.count = 1

    # Mock the full call chain
    mock_supabase.client.schema.return_value.rpc.return_value.execute.return_value = (
        mock_response
    )

    # Test actual code path
    result = fetch_message_from_queue("test-queue")

    # Validate parsed structure
    assert result["msg_id"] == 12345
    assert result["message"]["message_id"] == "msg_123"
    assert result["message"]["metadata"]["priority"] == "high"
```

**Pros:**
- Tests actual integration code
- Catches response parsing issues
- Validates data structures
- Reflects real API behavior

**Cons:**
- More complex to set up
- Requires API knowledge
- Must update when API changes

### Phase 4: Integration Tests

**When:** Critical paths, pre-deployment validation

**Characteristics:**
- Test against real services
- Use test/staging environments
- Slower execution
- Run in CI/CD

**Example:**

```python
@pytest.mark.integration
def test_real_supabase_integration():
    # Use test environment
    supabase = create_client(
        os.getenv("SUPABASE_TEST_URL"),
        os.getenv("SUPABASE_TEST_KEY")
    )

    # Send real message
    result = supabase.rpc("pgmq_public.send", {
        "queue_name": "test-queue",
        "message": {"test": True}
    }).execute()

    assert result.data is not None
    msg_id = result.data[0]

    # Retrieve real message
    message = supabase.rpc("pgmq_public.pop", {
        "queue_name": "test-queue"
    }).execute()

    assert message.data[0]["msg_id"] == msg_id
```

**Pros:**
- Tests real integration
- Catches actual API issues
- Validates end-to-end flow
- High confidence

**Cons:**
- Slow execution
- Requires test environment
- May have flaky tests
- Harder to debug

## Evolution Strategy

### 1. Start Simple

```python
# Week 1: Prototype
def test_listener():
    listener = RealtimeChatListener(...)
    listener._messages["123"] = {"content": "test"}
    result = listener.wait_for_message("123")
    assert result is not None
```

### 2. Add Mocking

```python
# Week 2: Add external service
@patch("aimq.clients.supabase.supabase")
def test_listener(mock_supabase):
    mock_supabase.rpc.return_value.execute.return_value = Mock(data=[...])
    listener = RealtimeChatListener(...)
    result = listener.wait_for_message("123")
    assert result is not None
```

### 3. Make Realistic

```python
# Week 3: Production-ready
@patch("aimq.clients.supabase.supabase")
def test_listener(mock_supabase):
    # Realistic response structure from API docs
    mock_response = Mock()
    mock_response.data = [
        {
            "msg_id": 12345,
            "message": {"message_id": "123", "content": "test"}
        }
    ]
    mock_supabase.client.schema.return_value.rpc.return_value.execute.return_value = (
        mock_response
    )

    listener = RealtimeChatListener(...)
    result = listener.wait_for_message("123")

    # Validate structure
    assert result["message_id"] == "123"
    assert result["content"] == "test"
```

### 4. Add Integration Tests

```python
# Week 4: Add integration tests
@pytest.mark.integration
def test_listener_integration():
    # Test against real Supabase
    listener = RealtimeChatListener(
        url=os.getenv("SUPABASE_TEST_URL"),
        key=os.getenv("SUPABASE_TEST_KEY")
    )
    # ... test real integration
```

## Best Practices

### 1. Use Realistic Mock Data

```python
# Bad: Minimal mock
mock_response = Mock()
mock_response.data = [{"id": 1}]

# Good: Realistic structure
mock_response = Mock()
mock_response.data = [
    {
        "msg_id": 12345,
        "read_ct": 0,
        "enqueued_at": "2025-11-23T12:00:00Z",
        "vt": "2025-11-23T12:05:00Z",
        "message": {"message_id": "msg_123", "content": "Hello"}
    }
]
```

### 2. Mock the Full Call Chain

```python
# Bad: Incomplete mock
mock_supabase.rpc.return_value = mock_response

# Good: Full chain
mock_supabase.client.schema.return_value.rpc.return_value.execute.return_value = (
    mock_response
)
```

### 3. Test Error Cases

```python
@patch("aimq.clients.supabase.supabase")
def test_listener_error(mock_supabase):
    # Mock error response
    mock_supabase.client.schema.return_value.rpc.return_value.execute.side_effect = (
        Exception("Connection failed")
    )

    listener = RealtimeChatListener(...)

    with pytest.raises(Exception, match="Connection failed"):
        listener.wait_for_message("123")
```

### 4. Use Fixtures for Common Mocks

```python
@pytest.fixture
def mock_supabase_response():
    """Fixture for realistic Supabase response."""
    mock_response = Mock()
    mock_response.data = [
        {
            "msg_id": 12345,
            "message": {"message_id": "test_123", "content": "test"}
        }
    ]
    return mock_response

@patch("aimq.clients.supabase.supabase")
def test_listener(mock_supabase, mock_supabase_response):
    mock_supabase.client.schema.return_value.rpc.return_value.execute.return_value = (
        mock_supabase_response
    )
    # ... test code
```

### 5. Document API Structure

```python
@patch("aimq.clients.supabase.supabase")
def test_fetch_message(mock_supabase):
    """
    Test fetching message from queue.

    Supabase pgmq_public.pop() returns:
    {
        "msg_id": bigint,
        "read_ct": integer,
        "enqueued_at": timestamp,
        "vt": timestamp,
        "message": jsonb
    }
    """
    mock_response = Mock()
    mock_response.data = [...]  # Structure documented above
    # ... test code
```

## When to Use Each Phase

| Phase | Use Case | Speed | Confidence |
|-------|----------|-------|------------|
| Phase 1 | Prototyping, algorithm testing | ⚡⚡⚡ | ⭐ |
| Phase 2 | Feature development, unit tests | ⚡⚡ | ⭐⭐ |
| Phase 3 | Production code, integration tests | ⚡ | ⭐⭐⭐ |
| Phase 4 | Critical paths, pre-deployment | 🐌 | ⭐⭐⭐⭐ |

## Migration Checklist

- [ ] Identify tests using simple in-memory mocks
- [ ] Research actual API response structures
- [ ] Create fixtures for common mock responses
- [ ] Update tests to use realistic mocks
- [ ] Add error case testing
- [ ] Document API structures in test docstrings
- [ ] Add integration tests for critical paths
- [ ] Update CI/CD to run integration tests
- [ ] Monitor for API changes

## Real-World Example

See `tests/test_realtime_chat.py` for evolution from simple to realistic mocking:

**Before (Phase 1):**
```python
def test_wait_for_message_received(self):
    listener = RealtimeChatListener(...)
    test_payload = {
        "queue": "outgoing-messages",
        "message_id": "test_msg_123",
        "message": {"content": "test response"},
    }
    listener._handle_message_notification(test_payload)
    result = listener.wait_for_message("test_msg_123")
    assert result is not None
```

**After (Phase 3):**
```python
@patch("aimq.clients.supabase.supabase")
def test_wait_for_message_received(self, mock_supabase):
    message_id = "test_msg_123"
    job_id = 12345

    mock_response = Mock()
    mock_response.data = [
        {
            "msg_id": job_id,
            "message": {"message_id": message_id, "content": "test response"},
        }
    ]
    mock_supabase.client.schema.return_value.rpc.return_value.execute.return_value = (
        mock_response
    )

    listener = RealtimeChatListener(...)
    result = listener.wait_for_message(message_id, timeout=1.0)

    assert result is not None
    assert result["message_id"] == message_id
```

## Related

- [@.claude/patterns/testing-strategy.md](./testing-strategy.md) - Overall testing strategy
- [@.claude/standards/testing.md](../standards/testing.md) - Testing standards
- [@.claude/quick-references/testing.md](../quick-references/testing.md) - Testing quick reference
- [@.claude/patterns/error-handling.md](./error-handling.md) - Error handling patterns

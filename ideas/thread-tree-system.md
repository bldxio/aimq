# Thread Tree System - Recursive Reply Threading

**Status**: 🌱 Foundation Feature
**Priority**: High - Needed for multi-agent chat
**Complexity**: Low-Medium
**Estimated Effort**: 2-3 days

---

## What

A system for calculating thread IDs from tree-structured message replies. Messages can reply to other messages via `reply_to_id`, forming a tree. The root message (where `reply_to_id = null`) becomes the `thread_id` for all messages in that tree.

### Key Features

- **Recursive Traversal**: Walk up the reply chain to find the root
- **Thread ID Calculation**: Determine thread_id for any message
- **Caching Strategy**: Avoid repeated traversals
- **Tree Queries**: Get all messages in a thread
- **Depth Tracking**: Know how deep a reply is nested

---

## Why

### Business Value
- **Conversation Context**: Group related messages together
- **Thread Views**: Display conversations as trees
- **Agent Context**: Agents see full thread history
- **Analytics**: Track conversation depth and engagement

### Technical Value
- **Simple Schema**: Just one `reply_to_id` column
- **Flexible**: Supports any tree depth
- **Efficient**: Can be optimized with caching or materialization

---

## Architecture

### Message Tree Structure

```
Message A (reply_to_id: null) ← ROOT = thread_id
    ├─ Message B (reply_to_id: A)
    │   ├─ Message D (reply_to_id: B)
    │   └─ Message E (reply_to_id: B)
    └─ Message C (reply_to_id: A)
        └─ Message F (reply_to_id: C)
```

**Thread ID**: `A` (the root message ID)
**All messages in thread**: A, B, C, D, E, F

---

## Technical Design

### Algorithm: Recursive Traversal

```python
async def calculate_thread_id(message: Message) -> str:
    """Recursively find root message"""

    # Check cache first
    if "thread_id" in message.metadata:
        return message.metadata["thread_id"]

    # Base case: this is the root
    if not message.reply_to_id:
        return message.id

    # Recursive case: traverse up
    parent = await db.messages.get(message.reply_to_id)
    return await calculate_thread_id(parent)
```

**Time Complexity**: O(depth) - worst case is depth of tree
**Space Complexity**: O(depth) - recursion stack

### Optimization 1: PostgreSQL Recursive CTE

```sql
-- Find thread root for a given message
WITH RECURSIVE thread_root AS (
    -- Base case: start with current message
    SELECT id, reply_to_id, 0 as depth
    FROM messages
    WHERE id = $1

    UNION ALL

    -- Recursive case: traverse up
    SELECT m.id, m.reply_to_id, tr.depth + 1
    FROM messages m
    JOIN thread_root tr ON m.id = tr.reply_to_id
)
SELECT id as thread_id FROM thread_root
WHERE reply_to_id IS NULL
LIMIT 1;
```

**Benefits**:
- Single database query
- No application-level recursion
- Efficient with proper indexes

### Optimization 2: Materialized Thread ID

```sql
-- Add thread_id column to messages table
ALTER TABLE messages ADD COLUMN thread_id UUID;

-- Create index
CREATE INDEX messages_thread_id_idx ON messages(thread_id);

-- Trigger to calculate thread_id on insert
CREATE OR REPLACE FUNCTION calculate_thread_id()
RETURNS TRIGGER AS $$
DECLARE
    root_id UUID;
BEGIN
    IF NEW.reply_to_id IS NULL THEN
        -- This is a root message
        NEW.thread_id := NEW.id;
    ELSE
        -- Find the root by traversing up
        WITH RECURSIVE thread_root AS (
            SELECT id, reply_to_id
            FROM messages
            WHERE id = NEW.reply_to_id

            UNION ALL

            SELECT m.id, m.reply_to_id
            FROM messages m
            JOIN thread_root tr ON m.id = tr.reply_to_id
        )
        SELECT id INTO root_id FROM thread_root
        WHERE reply_to_id IS NULL
        LIMIT 1;

        NEW.thread_id := root_id;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER set_thread_id
BEFORE INSERT ON messages
FOR EACH ROW
EXECUTE FUNCTION calculate_thread_id();
```

**Benefits**:
- O(1) lookup (just read the column)
- No runtime calculation needed
- Automatic via trigger

**Trade-offs**:
- Extra column (4 bytes per message)
- Trigger overhead on insert
- Can't change thread structure after insert

### Optimization 3: Metadata Caching

```python
async def calculate_thread_id_cached(message: Message) -> str:
    """Calculate thread_id with caching in metadata"""

    # Check cache
    if "thread_id" in message.metadata:
        return message.metadata["thread_id"]

    # Calculate
    if not message.reply_to_id:
        thread_id = message.id
    else:
        parent = await db.messages.get(message.reply_to_id)
        thread_id = await calculate_thread_id_cached(parent)

    # Cache in metadata
    await db.messages.update(
        message.id,
        metadata={**message.metadata, "thread_id": thread_id}
    )

    return thread_id
```

**Benefits**:
- No schema changes
- Lazy calculation (only when needed)
- Can be recalculated if needed

**Trade-offs**:
- First access is slow
- JSONB updates are slower than column updates

---

## Implementation

### Phase 1: Basic Recursive Algorithm (Day 1)

```python
# src/aimq/threads/__init__.py
from .calculator import calculate_thread_id, get_thread_messages

# src/aimq/threads/calculator.py
async def calculate_thread_id(message_id: str) -> str:
    """Calculate thread ID for a message"""
    message = await db.messages.get(message_id)

    if not message.reply_to_id:
        return message.id

    parent = await db.messages.get(message.reply_to_id)
    return await calculate_thread_id(parent.id)

async def get_thread_messages(thread_id: str) -> List[Message]:
    """Get all messages in a thread"""
    return await db.messages.find({"thread_id": thread_id})

async def get_thread_depth(message_id: str) -> int:
    """Calculate depth of a message in its thread"""
    message = await db.messages.get(message_id)

    if not message.reply_to_id:
        return 0

    parent_depth = await get_thread_depth(message.reply_to_id)
    return parent_depth + 1
```

**Tests**:
- Single message (root)
- Two-level thread (root + reply)
- Deep thread (5+ levels)
- Multiple branches
- Invalid reply_to_id (error handling)

### Phase 2: PostgreSQL CTE Optimization (Day 2)

```python
# src/aimq/threads/calculator.py
async def calculate_thread_id_cte(message_id: str) -> str:
    """Calculate thread ID using PostgreSQL CTE"""

    query = """
    WITH RECURSIVE thread_root AS (
        SELECT id, reply_to_id, 0 as depth
        FROM messages
        WHERE id = $1

        UNION ALL

        SELECT m.id, m.reply_to_id, tr.depth + 1
        FROM messages m
        JOIN thread_root tr ON m.id = tr.reply_to_id
    )
    SELECT id FROM thread_root
    WHERE reply_to_id IS NULL
    LIMIT 1;
    """

    result = await db.execute(query, message_id)
    return result[0]["id"]
```

**Tests**:
- Same tests as Phase 1
- Performance comparison (CTE vs recursive)
- Benchmark with large threads (100+ messages)

### Phase 3: Caching Strategy (Day 3)

Choose one:
- **Option A**: Materialized column (best performance, schema change)
- **Option B**: Metadata caching (no schema change, good performance)
- **Option C**: Redis cache (external dependency, very fast)

Implement chosen strategy and benchmark.

---

## Dependencies

### Existing Features
- ✅ Supabase messages table with `reply_to_id`
- ✅ Database query utilities

### Required Features
- ⚠️ Thread calculation utilities
- ⚠️ Caching strategy (choose one)
- ⚠️ Thread query helpers

### Nice-to-Have
- 🔮 Thread visualization (UI)
- 🔮 Thread analytics (depth, breadth, engagement)
- 🔮 Thread pruning (archive old threads)

---

## Open Questions

1. **Caching Strategy**: Which approach?
   - Materialized column (fast, schema change)
   - Metadata caching (flexible, slower)
   - Redis cache (fastest, external dependency)
   - Hybrid (materialized + fallback)?

2. **Thread Depth Limits**: Should we limit depth?
   - Unlimited (flexible, could be slow)
   - Max depth (e.g., 10 levels) (safe, may frustrate users)
   - Configurable per workspace?

3. **Orphaned Messages**: What if reply_to_id points to deleted message?
   - Treat as root message
   - Mark as orphaned
   - Prevent deletion of messages with replies

4. **Thread Merging**: Can threads be merged?
   - No (simple, safe)
   - Yes (complex, powerful)
   - Admin-only feature?

5. **Performance**: What's acceptable?
   - Thread ID calculation <100ms?
   - Thread query <500ms?
   - Depends on thread size?

---

## Success Metrics

- ✅ Thread ID calculated correctly 100% of time
- ✅ Handles threads up to 100 messages
- ⚡ Thread ID calculation <100ms (with caching)
- ⚡ Thread query <500ms for 100-message thread
- 🎯 No infinite loops (circular references)

---

## Related Ideas

- [Message Routing & Triage](./message-routing-triage.md) - Uses thread context for routing
- [Agent Response Workflows](./agent-response-workflows.md) - Loads thread messages
- [Multi-Agent Group Chat](./multi-agent-group-chat.md) - Overall vision

---

## Examples

### Example 1: Simple Thread

```python
# User posts message
message_a = await create_message(content="What's the weather?")
# thread_id = message_a.id

# Agent replies
message_b = await create_message(
    content="It's sunny!",
    reply_to_id=message_a.id
)
# thread_id = message_a.id

# User follows up
message_c = await create_message(
    content="Thanks!",
    reply_to_id=message_b.id
)
# thread_id = message_a.id

# Get all messages in thread
thread = await get_thread_messages(message_a.id)
# Returns: [message_a, message_b, message_c]
```

### Example 2: Branching Thread

```python
# Root message
root = await create_message(content="Let's discuss the project")

# Two branches
branch_a = await create_message(content="I'll handle frontend", reply_to_id=root.id)
branch_b = await create_message(content="I'll handle backend", reply_to_id=root.id)

# Replies to branches
reply_a1 = await create_message(content="React or Vue?", reply_to_id=branch_a.id)
reply_b1 = await create_message(content="Python or Node?", reply_to_id=branch_b.id)

# All have same thread_id
assert await calculate_thread_id(reply_a1.id) == root.id
assert await calculate_thread_id(reply_b1.id) == root.id
```

---

**Last Updated**: 2025-11-13
**Status**: Ready to implement - foundational piece

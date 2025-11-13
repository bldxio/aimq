# Message Agent Example

This example demonstrates a composable message routing system with multi-agent responses.

## 🎯 What It Does

1. **Routes Messages** - Detects @mentions and routes to appropriate agent queues
2. **Default Assistant** - Handles general questions without tools
3. **ReAct Assistant** - Handles complex queries with file reading, OCR, and database tools

## 🏗️ Architecture

```
incoming-messages queue
    ↓
MessageRoutingWorkflow
    ├─ DetectMentions (tool)
    └─ ResolveQueue (tool)
    ↓
Agent Queues
    ├─ default-assistant (general responses)
    └─ react-assistant (tool-powered responses)
```

## 🔧 Composable Tools

All tools are reusable and can be composed into custom workflows:

- **DetectMentions** - Extracts @mentions from text using regex
- **ResolveQueue** - Maps mentions to queue names (supports `-assistant`, `_assistant`, `-bot`, `_bot`)
- **LookupProfile** - Queries Supabase profiles table (optional, for future use)

## 🚀 Quick Start

### 1. Start the Worker

```bash
uv run python examples/message_agent/message_worker.py
```

### 2. Send Test Messages

#### General Message (no @mention)
```bash
aimq send incoming-messages '{
  "message_id": "msg_001",
  "body": "Hello! Can you help me with something?",
  "sender": "user@example.com",
  "workspace_id": "workspace_123",
  "channel_id": "channel_456",
  "thread_id": "thread_789"
}'
```
→ Routes to `default-assistant` queue

#### Message with @mention
```bash
aimq send incoming-messages '{
  "message_id": "msg_002",
  "body": "@react-assistant What files are in the documents folder?",
  "sender": "user@example.com",
  "workspace_id": "workspace_123",
  "channel_id": "channel_456",
  "thread_id": "thread_789"
}'
```
→ Routes to `react-assistant` queue

### 3. Run the Demo Script

```bash
uv run python examples/message_agent/demo.py
```

This sends 5 test messages demonstrating different routing scenarios.

## 📝 Message Format

### Input Message
```json
{
  "message_id": "msg_123",
  "body": "@react-assistant help me",
  "sender": "user@example.com",
  "workspace_id": "workspace_123",
  "channel_id": "channel_456",
  "thread_id": "thread_789"
}
```

### Response Message
```json
{
  "message_id": "msg_124",
  "body": "Here's how I can help...",
  "sender": "react-assistant@workspace_123",
  "workspace_id": "workspace_123",
  "channel_id": "channel_456",
  "thread_id": "thread_789",
  "in_reply_to": "msg_123"
}
```

## 🎨 Supported Mention Patterns

The system recognizes these patterns as valid agent mentions:

- `@name-assistant` ✅
- `@name_assistant` ✅
- `@name-bot` ✅
- `@name_bot` ✅

Any other pattern falls back to the default queue.

## 🔌 Extending the System

### Add a New Agent

1. Create the agent:
```python
my_agent = ReActAgent(
    tools=[...],
    system_prompt="...",
)
```

2. Register a queue handler:
```python
@worker.task(queue="my-assistant", timeout=300)
def handle_my_assistant(state: AgentState) -> dict:
    result = my_agent.invoke(state)
    # ... format response
    return response
```

3. Send messages with `@my-assistant` mention!

### Customize Routing Logic

Create a custom `ResolveQueue` tool:

```python
class CustomResolveQueue(ResolveQueue):
    valid_suffixes = ["-assistant", "-bot", "-agent"]

    def _run(self, mentions, default_queue):
        # Custom logic here
        return queue_name
```

Use it in the workflow:

```python
workflow = MessageRoutingWorkflow(
    resolve_queue_tool=CustomResolveQueue(),
    default_queue="my-default"
)
```

### Add Profile Lookup

Use the `LookupProfile` tool to resolve user mentions:

```python
from aimq.tools.routing import LookupProfile

lookup_tool = LookupProfile()
profile = lookup_tool.run({"profile_id": "user_123"})
# Returns: {"id": "user_123", "name": "John", "queue": "john-assistant"}
```

## 🧪 Testing

Tests are located in `tests/aimq/tools/routing/` and `tests/aimq/workflows/`:

```bash
# Run routing tool tests
uv run pytest tests/aimq/tools/routing/ -v

# Run workflow tests
uv run pytest tests/aimq/workflows/test_message_routing.py -v

# Run all tests
uv run pytest tests/aimq/tools/routing/ tests/aimq/workflows/test_message_routing.py -v
```

## 📚 Learn More

- **Tools**: `src/aimq/tools/routing/`
- **Workflow**: `src/aimq/workflows/message_routing.py`
- **Tests**: `tests/aimq/tools/routing/` and `tests/aimq/workflows/`

---

**Built with composable tools and workflows!** 🚀

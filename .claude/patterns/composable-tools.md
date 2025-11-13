# Composable Tool Architecture

**Category**: Design Pattern
**Complexity**: Medium
**Impact**: High
**Related**: [Module Organization](./module-organization.md), [Testing Strategy](./testing-strategy.md)

---

## Problem

Complex workflows are hard to test, maintain, and reuse. Monolithic implementations become brittle and difficult to modify.

## Solution

Build small, focused tools that do one thing well, then compose them into workflows. Each tool is:
- **Single-purpose**: Does one thing well
- **Independent**: Can be tested and used alone
- **Composable**: Can be combined with other tools
- **Reusable**: Can be used in multiple workflows

## Real-World Example: Message Agent

### The Challenge
Build a message routing system that:
1. Detects @mentions in messages
2. Resolves mentions to queue names
3. Looks up user profiles (future)
4. Routes messages to appropriate queues

### The Composable Approach

**Three Independent Tools**:

```python
# Tool 1: DetectMentions
class DetectMentionsTool(BaseTool):
    """Extracts @mentions from text."""

    def _run(self, text: str) -> List[str]:
        # Single responsibility: find mentions
        pattern = r'@(\w+)(?=\s|$|[^\w@])'
        return re.findall(pattern, text)
```

```python
# Tool 2: ResolveQueue
class ResolveQueueTool(BaseTool):
    """Maps mentions to queue names."""

    def _run(self, mention: str, valid_queues: List[str]) -> str:
        # Single responsibility: resolve queue
        for queue in valid_queues:
            if queue.endswith(('-assistant', '_assistant', '-bot', '_bot')):
                if mention in queue:
                    return queue
        return "default-assistant"
```

```python
# Tool 3: LookupProfile (future)
class LookupProfileTool(BaseTool):
    """Queries user profiles from database."""

    def _run(self, mention: str, workspace_id: str) -> Optional[Dict]:
        # Single responsibility: lookup profile
        return supabase.table('profiles').select('*').eq(
            'username', mention
        ).eq('workspace_id', workspace_id).execute()
```

**One Workflow to Orchestrate**:

```python
class MessageRoutingWorkflow:
    """Orchestrates tools for intelligent routing."""

    def __init__(self, detect_tool, resolve_tool, lookup_tool=None):
        self.detect = detect_tool
        self.resolve = resolve_tool
        self.lookup = lookup_tool

    def route(self, message: str, workspace_id: str) -> Dict:
        # Compose tools to solve complex problem
        mentions = self.detect.run(message)

        if self.lookup and mentions:
            profiles = [self.lookup.run(m, workspace_id) for m in mentions]
            # Use profile data if available

        queue = self.resolve.run(mentions[0] if mentions else None)

        return {
            "queue": queue,
            "mentions": mentions,
            "metadata": {...}
        }
```

## Benefits

### 1. Easy to Test
Each tool can be tested independently:

```python
def test_detect_mentions():
    tool = DetectMentionsTool()
    result = tool.run("Hey @alice and @bob!")
    assert result == ["alice", "bob"]

def test_resolve_queue():
    tool = ResolveQueueTool()
    result = tool.run("alice", ["alice-assistant", "bob-bot"])
    assert result == "alice-assistant"
```

### 2. Easy to Reuse
Tools can be used in different workflows:

```python
# Workflow 1: Message routing
routing_workflow = MessageRoutingWorkflow(detect, resolve)

# Workflow 2: Mention analytics
analytics_workflow = MentionAnalyticsWorkflow(detect, lookup)

# Workflow 3: Notification system
notification_workflow = NotificationWorkflow(detect, lookup, notify)
```

### 3. Easy to Understand
Each piece has a clear, single purpose:
- "What does DetectMentions do?" → "Finds @mentions"
- "What does ResolveQueue do?" → "Maps mentions to queues"
- "What does the workflow do?" → "Orchestrates tools for routing"

### 4. Easy to Modify
Change one tool without breaking others:

```python
# Improve mention detection without touching routing logic
class DetectMentionsTool(BaseTool):
    def _run(self, text: str) -> List[str]:
        # New: Handle hashtags too
        mentions = re.findall(r'@(\w+)', text)
        hashtags = re.findall(r'#(\w+)', text)
        return mentions + hashtags
```

### 5. Easy to Extend
Add new tools without modifying existing ones:

```python
# New tool: Validate mentions
class ValidateMentionTool(BaseTool):
    def _run(self, mention: str) -> bool:
        return len(mention) >= 3 and mention.isalnum()

# Add to workflow
workflow = MessageRoutingWorkflow(
    detect, resolve, lookup, validate  # New tool added
)
```

## Implementation Guidelines

### 1. Keep Tools Focused
**Good**: One clear responsibility
```python
class DetectMentionsTool:
    """Extracts @mentions from text."""
    def _run(self, text: str) -> List[str]:
        return re.findall(r'@(\w+)', text)
```

**Bad**: Multiple responsibilities
```python
class MessageProcessorTool:
    """Detects mentions, resolves queues, sends messages."""
    def _run(self, text: str) -> None:
        mentions = self.detect(text)
        queue = self.resolve(mentions)
        self.send(queue, text)
```

### 2. Make Tools Independent
**Good**: No dependencies on other tools
```python
class ResolveQueueTool:
    def _run(self, mention: str, valid_queues: List[str]) -> str:
        # Doesn't depend on DetectMentionsTool
        for queue in valid_queues:
            if mention in queue:
                return queue
        return "default"
```

**Bad**: Tightly coupled
```python
class ResolveQueueTool:
    def __init__(self, detect_tool):
        self.detect = detect_tool  # Unnecessary coupling

    def _run(self, text: str) -> str:
        mentions = self.detect.run(text)  # Should receive mentions
        # ...
```

### 3. Use Workflows for Orchestration
**Good**: Workflow composes tools
```python
class MessageRoutingWorkflow:
    def route(self, message: str) -> Dict:
        mentions = self.detect.run(message)
        queue = self.resolve.run(mentions[0])
        return {"queue": queue, "mentions": mentions}
```

**Bad**: Tool does orchestration
```python
class DetectMentionsTool:
    def _run(self, text: str) -> Dict:
        mentions = re.findall(r'@(\w+)', text)
        queue = self.resolve_queue(mentions)  # Wrong layer
        return {"queue": queue, "mentions": mentions}
```

### 4. Design for Composition
**Good**: Tools return data, workflows decide what to do
```python
# Tools return data
mentions = detect_tool.run(text)
queue = resolve_tool.run(mentions[0])

# Workflow decides composition
if mentions:
    queue = resolve_tool.run(mentions[0])
else:
    queue = "default-assistant"
```

**Bad**: Tools make decisions about composition
```python
# Tool decides what to do next
class DetectMentionsTool:
    def _run(self, text: str) -> str:
        mentions = re.findall(r'@(\w+)', text)
        if mentions:
            return self.resolve_queue(mentions[0])  # Wrong
        return "default"
```

## Testing Strategy

### Test Tools Independently
```python
def test_detect_mentions_basic():
    tool = DetectMentionsTool()
    assert tool.run("@alice") == ["alice"]

def test_detect_mentions_multiple():
    tool = DetectMentionsTool()
    assert tool.run("@alice @bob") == ["alice", "bob"]

def test_detect_mentions_with_email():
    tool = DetectMentionsTool()
    # Should not detect email as mention
    assert tool.run("user@example.com") == []
```

### Test Workflow Composition
```python
def test_routing_workflow_with_mention():
    detect = DetectMentionsTool()
    resolve = ResolveQueueTool()
    workflow = MessageRoutingWorkflow(detect, resolve)

    result = workflow.route("@alice help!")
    assert result["queue"] == "alice-assistant"
    assert result["mentions"] == ["alice"]

def test_routing_workflow_without_mention():
    workflow = MessageRoutingWorkflow(detect, resolve)

    result = workflow.route("Hello!")
    assert result["queue"] == "default-assistant"
    assert result["mentions"] == []
```

### Mock Tools in Integration Tests
```python
def test_workflow_with_mock_tools(mocker):
    # Mock tools for integration testing
    mock_detect = mocker.Mock(return_value=["alice"])
    mock_resolve = mocker.Mock(return_value="alice-assistant")

    workflow = MessageRoutingWorkflow(mock_detect, mock_resolve)
    result = workflow.route("@alice help!")

    mock_detect.run.assert_called_once_with("@alice help!")
    mock_resolve.run.assert_called_once_with("alice")
```

## When to Use

### ✅ Use Composable Tools When:
- Building workflows with multiple steps
- Need flexibility to change behavior
- Want to reuse logic across workflows
- Testing is important
- Team needs to understand the system
- Requirements may change

### ❌ Don't Use When:
- Single, simple operation (no need to over-engineer)
- Performance is critical (composition has overhead)
- Tools would be tightly coupled anyway
- No reuse expected

## Trade-offs

### Advantages
- ✅ Easy to test
- ✅ Easy to reuse
- ✅ Easy to understand
- ✅ Easy to modify
- ✅ Easy to extend
- ✅ Flexible composition

### Disadvantages
- ❌ More files to manage
- ❌ Slight performance overhead
- ❌ Can be over-engineered for simple cases
- ❌ Requires discipline to maintain boundaries

## Real Results

From the Message Agent implementation:
- **39 tests written** (14 for DetectMentions, 15 for ResolveQueue, 10 for workflow)
- **All tests passing** ✅
- **Built in ~2 hours** including tests and documentation
- **Easy to extend** (LookupProfile tool ready to add)
- **Easy to modify** (changed mention regex without touching routing)

## Related Patterns

- **[Module Organization](./module-organization.md)**: How to organize composable tools
- **[Testing Strategy](./testing-strategy.md)**: How to test composable systems
- **[Error Handling](./error-handling.md)**: How to handle errors in composed workflows

## Further Reading

- [Unix Philosophy](https://en.wikipedia.org/wiki/Unix_philosophy): "Do one thing and do it well"
- [Single Responsibility Principle](https://en.wikipedia.org/wiki/Single-responsibility_principle)
- [Composition over Inheritance](https://en.wikipedia.org/wiki/Composition_over_inheritance)
- [LangChain Tools](https://python.langchain.com/docs/modules/agents/tools/): Framework for composable tools

---

**Key Takeaway**: Build small, focused tools that do one thing well, then compose them into powerful workflows. The whole is greater than the sum of its parts! 🔧✨

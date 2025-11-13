# Message Routing & Triage - Intelligent Agent Selection

**Status**: 🌱 Core Feature
**Priority**: High - Needed for multi-agent chat
**Complexity**: Medium
**Estimated Effort**: 3-4 days

---

## What

A lightweight workflow that decides which agents (if any) should respond to a message, and when. Handles @mentions, reply detection, and primary agent logic.

### Key Features

- **Mention Detection**: Parse @agent mentions from message content
- **Reply Detection**: Check if message replies to an agent
- **Primary Agent Logic**: Determine if primary agent should respond
- **Routing Decision**: Return which agents to trigger and when
- **Fast Triage**: Lightweight checks before heavy processing

---

## Why

### Business Value
- **Smart Responses**: Only relevant agents respond
- **Reduced Noise**: Agents don't spam channels
- **User Control**: @mentions give explicit control
- **Natural Flow**: Replying to agents feels natural

### Technical Value
- **Decoupled**: Routing logic separate from execution
- **Testable**: Easy to test routing decisions
- **Extensible**: Easy to add new routing rules

---

## Architecture

### Routing Decision Flow

```
Message arrives
    ↓
[Quick Checks]
    ├─ Has @mentions? → Route immediately
    ├─ Replies to agent? → Route immediately
    └─ No immediate trigger
    ↓
[Primary Agent Check]
    ├─ Channel has primary agent?
    ├─ Should primary respond? (lightweight LLM check)
    └─ Route after processing or skip
    ↓
Return RoutingDecision
```

### Routing Decision Model

```python
@dataclass
class RoutingDecision:
    should_respond_immediately: bool
    should_respond_after_processing: bool
    agents: List[str]  # Agent IDs to route to
    reason: str  # Why this decision was made
    confidence: float  # 0.0-1.0 confidence score
```

---

## Technical Design

### Mention Detection

```python
import re
from typing import List

def extract_mentions(content: str) -> List[str]:
    """Extract @mentions from message content"""

    # Pattern: @username or @agent-name
    pattern = r'@([\w-]+)'
    matches = re.findall(pattern, content)

    return matches

async def resolve_mentions_to_agents(
    mentions: List[str],
    workspace_id: str,
    channel_id: str
) -> List[str]:
    """Convert mention usernames to agent IDs"""

    # Get all agents in channel
    participants = await db.participants.find({
        "channel_id": channel_id,
        "role": {"$in": ["agent", "assistant"]}
    })

    agent_ids = []
    for mention in mentions:
        # Find agent by username or display name
        agent = await db.profiles.find_one({
            "id": {"$in": [p.profile_id for p in participants]},
            "$or": [
                {"username": mention},
                {"display_name": mention}
            ]
        })

        if agent:
            agent_ids.append(agent.id)

    return agent_ids
```

### Reply Detection

```python
async def check_reply_to_agent(message: Message) -> Optional[str]:
    """Check if message replies to an agent"""

    if not message.reply_to_id:
        return None

    parent = await db.messages.get(message.reply_to_id)

    if parent.role in ["assistant", "system"]:
        return parent.author_id

    return None
```

### Primary Agent Check

```python
async def should_primary_agent_respond(
    message: Message,
    channel: Channel
) -> bool:
    """Determine if primary agent should respond"""

    if not channel.primary_agent_id:
        return False

    # Option 1: Always respond (simple)
    if channel.settings.get("primary_agent_always_respond"):
        return True

    # Option 2: Keyword triggers
    keywords = channel.settings.get("primary_agent_keywords", [])
    if any(keyword.lower() in message.content.lower() for keyword in keywords):
        return True

    # Option 3: Lightweight LLM check (fast model)
    prompt = f"""
    You are a routing assistant. Determine if the primary agent should respond to this message.

    Channel: {channel.name}
    Primary Agent: {channel.primary_agent_name}
    Message: {message.content}

    Should the primary agent respond? Answer with just "yes" or "no".
    """

    response = await llm.ainvoke(prompt, model="gpt-4o-mini")  # Fast, cheap model

    return response.content.strip().lower() == "yes"
```

### Triage Workflow

```python
from aimq.workflows import BaseWorkflow, workflow

@workflow
class MessageTriageWorkflow(BaseWorkflow):
    """Lightweight workflow to determine routing"""

    async def run(self, message: Message) -> RoutingDecision:
        # 1. Check for @mentions (highest priority)
        mentions = extract_mentions(message.content)
        if mentions:
            agent_ids = await resolve_mentions_to_agents(
                mentions,
                message.workspace_id,
                message.channel_id
            )

            if agent_ids:
                return RoutingDecision(
                    should_respond_immediately=True,
                    should_respond_after_processing=False,
                    agents=agent_ids,
                    reason="direct_mention",
                    confidence=1.0
                )

        # 2. Check if reply to agent
        replied_agent_id = await check_reply_to_agent(message)
        if replied_agent_id:
            return RoutingDecision(
                should_respond_immediately=True,
                should_respond_after_processing=False,
                agents=[replied_agent_id],
                reason="reply_to_agent",
                confidence=1.0
            )

        # 3. Check primary agent
        channel = await db.channels.get(message.channel_id)
        if channel.primary_agent_id:
            should_respond = await should_primary_agent_respond(message, channel)

            if should_respond:
                # Wait for document processing before responding
                return RoutingDecision(
                    should_respond_immediately=False,
                    should_respond_after_processing=True,
                    agents=[channel.primary_agent_id],
                    reason="primary_agent",
                    confidence=0.8
                )

        # 4. No routing needed
        return RoutingDecision(
            should_respond_immediately=False,
            should_respond_after_processing=False,
            agents=[],
            reason="no_trigger",
            confidence=1.0
        )
```

---

## Implementation

### Phase 1: Basic Routing (Day 1-2)

**Tasks**:
1. Create `RoutingDecision` model
2. Implement mention detection
3. Implement reply detection
4. Create basic triage workflow
5. Write tests

**Deliverable**: Agents respond to @mentions and replies

### Phase 2: Primary Agent Logic (Day 2-3)

**Tasks**:
1. Add channel settings for primary agent
2. Implement keyword triggers
3. Add lightweight LLM check (optional)
4. Test primary agent routing

**Deliverable**: Primary agents respond when appropriate

### Phase 3: Advanced Routing (Day 3-4)

**Tasks**:
1. Add confidence scoring
2. Add routing rules (time-based, user-based, etc.)
3. Add routing analytics
4. Optimize performance

**Deliverable**: Production-ready routing system

---

## Dependencies

### Existing Features
- ✅ Messages table with `reply_to_id`
- ✅ Participants table (agents in channels)
- ✅ Workflow system

### Required Features
- ⚠️ Channel settings (primary agent, keywords)
- ⚠️ Profile username/display_name lookup
- ⚠️ Lightweight LLM integration (optional)

### Nice-to-Have
- 🔮 Routing analytics (which rules trigger most)
- 🔮 A/B testing (test different routing strategies)
- 🔮 User preferences (opt-out of primary agent)

---

## Open Questions

1. **Primary Agent Trigger**: What's the best approach?
   - Always respond (simple, may be noisy)
   - Keyword triggers (flexible, requires configuration)
   - LLM check (smart, costs money)
   - Hybrid (keywords + LLM fallback)?

2. **Multiple Mentions**: What if multiple agents are mentioned?
   - All respond (may be redundant)
   - First mentioned responds (simple)
   - Most relevant responds (complex)
   - User chooses?

3. **Mention Format**: What formats to support?
   - @username (simple)
   - @display-name (user-friendly)
   - @agent-id (unambiguous)
   - All of the above?

4. **Reply Chains**: If user replies to agent reply, should agent respond again?
   - Yes (conversational)
   - No (avoid loops)
   - Configurable?

5. **Rate Limiting**: How to prevent agent spam?
   - Max N responses per minute
   - Cooldown period
   - User can mute agents

---

## Success Metrics

- ✅ @mentions detected 100% of time
- ✅ Reply detection works correctly
- ✅ Primary agent triggers appropriately (user feedback)
- ⚡ Triage completes in <1 second
- 🎯 No false positives (agents responding when they shouldn't)

---

## Related Ideas

- [Thread Tree System](./thread-tree-system.md) - Provides thread context
- [Agent Configuration Hierarchy](./agent-configuration-hierarchy.md) - Loads agent settings
- [Agent Response Workflows](./agent-response-workflows.md) - Executes routed agents
- [Multi-Agent Group Chat](./multi-agent-group-chat.md) - Overall vision

---

## Examples

### Example 1: Direct Mention

```python
message = Message(
    content="Hey @support-agent, I need help with billing",
    channel_id="...",
    author_id="user123"
)

decision = await triage_workflow.run(message)
# RoutingDecision(
#     should_respond_immediately=True,
#     agents=["support-agent-id"],
#     reason="direct_mention",
#     confidence=1.0
# )
```

### Example 2: Reply to Agent

```python
# Agent message
agent_msg = Message(
    content="How can I help you?",
    role="assistant",
    author_id="agent-id"
)

# User replies
user_msg = Message(
    content="I need help with X",
    reply_to_id=agent_msg.id
)

decision = await triage_workflow.run(user_msg)
# RoutingDecision(
#     should_respond_immediately=True,
#     agents=["agent-id"],
#     reason="reply_to_agent",
#     confidence=1.0
# )
```

### Example 3: Primary Agent

```python
channel = Channel(
    primary_agent_id="general-agent-id",
    settings={
        "primary_agent_keywords": ["help", "question", "how"]
    }
)

message = Message(
    content="I have a question about the project",
    channel_id=channel.id
)

decision = await triage_workflow.run(message)
# RoutingDecision(
#     should_respond_immediately=False,
#     should_respond_after_processing=True,
#     agents=["general-agent-id"],
#     reason="primary_agent",
#     confidence=0.8
# )
```

---

**Last Updated**: 2025-11-13
**Status**: Ready to implement - core routing logic

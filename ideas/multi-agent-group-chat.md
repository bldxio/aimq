# Multi-Agent Group Chat System - Technical Architecture

**Status**: 🎯 Technical Design Document
**Priority**: Critical - This is why AIMQ exists
**Complexity**: High - Composed of many features
**Estimated Effort**: 6-8 weeks (all components)

---

## Overview

This document describes the **technical architecture** for AIMQ's multi-agent group chat system. For the high-level vision and user experience, see [VISION.md](../VISION.md).

This system enables multiple users and AI agents to collaborate in threaded conversations within channels, with intelligent routing, document processing, knowledge graphs, and conversation context.

**This document focuses on technical implementation.** Each component is broken down into smaller, independently buildable features (see "Component Ideas" below).

### Key Features

- **Group Conversations**: Multiple users and agents in shared channels
- **Intelligent Routing**: Automatic agent selection based on mentions, replies, and context
- **Threaded Discussions**: Tree-based threading using `reply_to_id`
- **Always-On Processing**: Background knowledge graph and RAG updates
- **Hierarchical Instructions**: Multi-level agent configuration system
- **Checkpoint Management**: Per-thread, per-agent state persistence
- **Shared Memory**: Cross-agent memory using LangGraph

---

## Component Ideas

This vision is composed of several independently buildable features:

### Core Infrastructure
1. **[Thread Tree System](./thread-tree-system.md)** - Recursive reply threading and thread_id calculation
2. **[Message Ingestion Pipeline](./message-ingestion-pipeline.md)** - Universal entry point for all messages
3. **[Message Routing & Triage](./message-routing-triage.md)** - Intelligent agent selection
4. **[Agent Configuration Hierarchy](./agent-configuration-hierarchy.md)** - Context-aware instructions
5. **[Agent Response Workflows](./agent-response-workflows.md)** - Agent execution and response posting

### Supporting Features
6. **[RAG Workflows](./rag-workflows.md)** - Document processing and retrieval
7. **[Zep Knowledge Graphs](./zep-knowledge-graphs.md)** - Graph-based memory
8. **[Supabase Realtime Streaming](./supabase-realtime-streaming.md)** - Live updates
9. **[Human-in-the-Loop](./human-in-the-loop.md)** - Pause/resume workflows

Each component can be built, tested, and deployed independently, then integrated into the complete system.

---

## Why

### Business Value
- **Natural Collaboration**: Users and agents work together seamlessly
- **Context Awareness**: Agents understand conversation history and relationships
- **Flexible Deployment**: One agent or many, configured per workspace/channel
- **Scalable Architecture**: Handles multiple concurrent conversations

### Technical Value
- **Leverages Existing Infrastructure**: Built on Supabase pgmq and AIMQ workers
- **Modular Design**: Routing, processing, and execution are separate concerns
- **Extensible**: Easy to add new agent types and processing workflows

---

## Architecture

### Schema Overview

```
workspaces (top-level organization)
    ↓
channels (conversations within workspace)
    ↓
messages (content with threading via reply_to_id)
    ↓
participants (users/agents in channels)

profiles (users AND agents)
    ↓
memberships (profile → workspace with instructions)
```

### Instruction Hierarchy

Agents receive instructions from multiple sources (most specific to least):

1. **Participant Instructions** - Agent's role in THIS channel
2. **Channel Settings** - Instructions for primary agent in channel
3. **Membership Instructions** - Agent's job description in THIS workspace
4. **Profile Instructions** - Agent's personality/base instructions
5. **System Prompt** - Base agent behavior

### Message Flow

```
┌─────────────────────────────────────────────────────────────┐
│ Message Arrives in Queue                                     │
└─────────────────────┬───────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────────────────┐
│ Quick Triage (Lightweight, Fast)                            │
├─────────────────────────────────────────────────────────────┤
│ • Check for @mentions → Route to mentioned agents           │
│ • Check if reply to agent → Route to that agent             │
│ • Check if primary agent should respond → Maybe route       │
│ • Extract attachments → Queue for processing                │
└─────────────────────┬───────────────────────────────────────┘
                      ↓
        ┌─────────────┴─────────────┐
        ↓                           ↓
┌───────────────────┐     ┌─────────────────────────┐
│ Immediate Route   │     │ Always-On Processing    │
│ (if triggered)    │     │ (async, background)     │
├───────────────────┤     ├─────────────────────────┤
│ • Load agent      │     │ • Calculate thread_id   │
│ • Quick response  │     │ • Update knowledge graph│
│ • Acknowledge     │     │ • Update RAG/embeddings │
└─────────┬─────────┘     │ • Process documents     │
          │               └──────────┬──────────────┘
          │                          ↓
          │               ┌─────────────────────────┐
          │               │ Post-Processing Route   │
          │               │ (after docs processed)  │
          │               ├─────────────────────────┤
          │               │ • Load agent with full  │
          │               │   context               │
          │               │ • Detailed response     │
          └───────────────┴──────────┬──────────────┘
                                     ↓
                          ┌─────────────────────────┐
                          │ Agent Execution         │
                          ├─────────────────────────┤
                          │ • Load instruction      │
                          │   hierarchy             │
                          │ • Load thread checkpoint│
                          │ • Execute with tools    │
                          │ • Post response message │
                          └─────────────────────────┘
```

### Thread Tree Logic

Messages form a tree structure via `reply_to_id`:

```
Message A (reply_to_id: null) ← ROOT = thread_id
    ├─ Message B (reply_to_id: A)
    │   ├─ Message D (reply_to_id: B)
    │   └─ Message E (reply_to_id: B)
    └─ Message C (reply_to_id: A)
        └─ Message F (reply_to_id: C)
```

**Algorithm**: Recursively traverse `reply_to_id` until reaching a message with `reply_to_id = null`. That message's `id` is the `thread_id`.

**Optimization**: Cache thread_id in message metadata or separate table to avoid repeated traversals.

---

## Technical Design

### Components

#### 1. Message Ingestion Worker
**Purpose**: Process all incoming messages
**Triggers**: Supabase pgmq job created when message inserted

```python
@worker.task("process_message")
async def process_message(message_id: str):
    """Main entry point for message processing"""
    message = await load_message(message_id)

    # Quick triage
    routing_decision = await triage_message(message)

    # Spawn parallel tasks
    if routing_decision.should_respond_immediately:
        await enqueue_agent_response(message, routing_decision.agents)

    await enqueue_background_processing(message)
```

#### 2. Triage Workflow
**Purpose**: Decide which agents should respond and when

```python
@workflow
class MessageTriageWorkflow(BaseWorkflow):
    """Lightweight workflow to determine routing"""

    async def run(self, message: Message) -> RoutingDecision:
        # Check mentions
        mentioned_agents = extract_mentions(message.content)
        if mentioned_agents:
            return RoutingDecision(
                should_respond_immediately=True,
                agents=mentioned_agents,
                reason="direct_mention"
            )

        # Check if reply to agent
        if message.reply_to_id:
            parent = await get_message(message.reply_to_id)
            if parent.role == "assistant":
                return RoutingDecision(
                    should_respond_immediately=True,
                    agents=[parent.author_id],
                    reason="reply_to_agent"
                )

        # Check primary agent
        channel = await get_channel(message.channel_id)
        if channel.primary_agent_id:
            # Use lightweight LLM to decide if primary should respond
            should_respond = await check_primary_agent_trigger(message, channel)
            if should_respond:
                return RoutingDecision(
                    should_respond_immediately=False,  # Wait for processing
                    agents=[channel.primary_agent_id],
                    reason="primary_agent"
                )

        return RoutingDecision(should_respond_immediately=False, agents=[])
```

#### 3. Background Processing Workflow
**Purpose**: Always-on knowledge graph and RAG updates

```python
@workflow
class BackgroundProcessingWorkflow(BaseWorkflow):
    """Process message for knowledge extraction"""

    async def run(self, message: Message):
        # Calculate thread_id
        thread_id = await calculate_thread_id(message)
        await update_message_metadata(message.id, {"thread_id": thread_id})

        # Extract and process attachments
        if message.parts:
            for part in message.parts:
                if part.type == "attachment":
                    await enqueue_document_processing(part.url)

        # Update knowledge graph
        await update_knowledge_graph(message)

        # Update RAG embeddings
        await update_embeddings(message)

        # Check if any agents need post-processing notification
        routing = await get_routing_decision(message.id)
        if routing and not routing.should_respond_immediately:
            await enqueue_agent_response(message, routing.agents)
```

#### 4. Agent Response Workflow
**Purpose**: Execute agent and post response

```python
@workflow
class AgentResponseWorkflow(BaseWorkflow):
    """Execute agent and post response to channel"""

    async def run(self, message: Message, agent_id: str):
        # Load agent configuration
        agent_config = await load_agent_config(
            agent_id=agent_id,
            workspace_id=message.workspace_id,
            channel_id=message.channel_id
        )

        # Load thread context
        thread_id = message.metadata.get("thread_id", message.id)
        thread_messages = await load_thread_messages(thread_id)

        # Load checkpoint
        checkpoint = await load_checkpoint(
            agent_id=agent_id,
            thread_id=thread_id
        )

        # Execute agent
        agent = await create_agent(agent_config)
        response = await agent.run(
            messages=thread_messages,
            checkpoint=checkpoint
        )

        # Post response
        await create_message(
            workspace_id=message.workspace_id,
            channel_id=message.channel_id,
            author_id=agent_id,
            reply_to_id=message.id,
            content=response.content,
            role="assistant"
        )

        # Save checkpoint
        await save_checkpoint(
            agent_id=agent_id,
            thread_id=thread_id,
            checkpoint=response.checkpoint
        )
```

### Database Queries

#### Load Agent Configuration
```python
async def load_agent_config(agent_id: str, workspace_id: str, channel_id: str):
    """Load hierarchical agent instructions"""

    # 1. Profile (base personality)
    profile = await db.profiles.get(agent_id)

    # 2. Membership (workspace job description)
    membership = await db.memberships.get(
        profile_id=agent_id,
        workspace_id=workspace_id
    )

    # 3. Channel settings (primary agent instructions)
    channel = await db.channels.get(channel_id)

    # 4. Participant (channel-specific role)
    participant = await db.participants.get(
        profile_id=agent_id,
        channel_id=channel_id
    )

    # Merge instructions (most specific wins)
    return AgentConfig(
        system_prompt=profile.system_prompt,
        personality=profile.instructions,
        job_description=membership.instructions if membership else None,
        channel_instructions=channel.primary_agent_instructions if channel.primary_agent_id == agent_id else None,
        role_instructions=participant.instructions if participant else None
    )
```

#### Calculate Thread ID
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

**Optimization**: Use a recursive CTE in PostgreSQL:
```sql
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
SELECT id FROM thread_root
WHERE reply_to_id IS NULL
LIMIT 1;
```

---

## Dependencies

### Existing Features
- ✅ Supabase pgmq integration
- ✅ Worker task system
- ✅ Agent decorators and base classes
- ✅ Workflow decorators and base classes
- ✅ Checkpoint system

### Required Features
- ⚠️ Supabase Realtime integration (for worker notifications)
- ⚠️ Knowledge graph system (for background processing)
- ⚠️ RAG/embeddings system (for background processing)
- ⚠️ Document processing workflows (for attachments)
- ⚠️ Shared memory system (LangGraph memory)

### Nice-to-Have
- 🔮 Streaming support (for real-time updates)
- 🔮 Human-in-the-loop (for agent questions)
- 🔮 Multi-agent collaboration (agents talking to each other)

---

## Implementation Roadmap

This vision is built incrementally by implementing each component idea:

### Phase 1: Foundation (Weeks 1-2)
**Goal**: Core infrastructure for message processing

**Components**:
1. [Thread Tree System](./thread-tree-system.md) - 2-3 days
2. [Message Ingestion Pipeline](./message-ingestion-pipeline.md) - 2-3 days
3. [Message Routing & Triage](./message-routing-triage.md) - 3-4 days

**Deliverable**: Messages flow through system, agents respond to @mentions

### Phase 2: Agent Intelligence (Weeks 3-4)
**Goal**: Context-aware agent behavior

**Components**:
1. [Agent Configuration Hierarchy](./agent-configuration-hierarchy.md) - 2-3 days
2. [Agent Response Workflows](./agent-response-workflows.md) - 3-4 days
3. Checkpoint integration - 2 days

**Deliverable**: Agents have context-aware instructions and stateful conversations

### Phase 3: Knowledge & Memory (Weeks 5-6)
**Goal**: Long-term memory and document understanding

**Components**:
1. [RAG Workflows](./rag-workflows.md) - 1-2 weeks
2. [Zep Knowledge Graphs](./zep-knowledge-graphs.md) - 2-3 weeks (can be parallel)

**Deliverable**: Agents remember facts and can reference documents

### Phase 4: Real-Time & Collaboration (Weeks 7-8)
**Goal**: Live updates and human collaboration

**Components**:
1. [Supabase Realtime Streaming](./supabase-realtime-streaming.md) - 1 week
2. [Human-in-the-Loop](./human-in-the-loop.md) - 1 week

**Deliverable**: Real-time updates and collaborative workflows

### Phase 5: Production Hardening (Week 8+)
**Goal**: Production-ready system

**Tasks**:
- Comprehensive error handling
- Rate limiting and circuit breakers
- Observability (LangSmith, metrics)
- Load testing
- Documentation
- Deployment guides

**Deliverable**: Production-ready multi-agent group chat system

---

## Building Incrementally

The beauty of this architecture is that **each component delivers value independently**:

- **Thread Tree System** → Better conversation organization
- **Message Routing** → Agents respond appropriately
- **Agent Configuration** → Context-aware behavior
- **RAG Workflows** → Document understanding
- **Realtime Streaming** → Better UX
- **Human-in-the-Loop** → Collaborative workflows

You can ship after Phase 1 and have a working system, then add features incrementally!

---

## Open Questions

### Routing & Triggers
1. **Primary agent trigger logic**: What determines if the primary agent should respond?
   - Keywords? Sentiment? Always? ML model?
   - Should there be a "confidence threshold"?

2. **Multiple agent responses**: How to handle multiple agents wanting to respond?
   - First-come-first-served?
   - Priority system?
   - Coordinator agent decides?

3. **Agent conflicts**: What if two agents give contradictory responses?
   - Let it happen naturally?
   - Add conflict detection?
   - Coordinator resolves?

### Performance & Scaling
4. **Thread_id caching**: Where to cache?
   - In message metadata (jsonb)?
   - Separate `threads` table?
   - Redis cache?

5. **Background processing**: How to handle high message volume?
   - Queue priority system?
   - Rate limiting per channel?
   - Batch processing?

6. **Checkpoint storage**: How to manage checkpoint growth?
   - Prune old checkpoints?
   - Compress checkpoints?
   - Separate storage (S3)?

### User Experience
7. **Agent typing indicators**: Should agents show "typing..." while processing?
   - Via Supabase Realtime?
   - Via message status updates?

8. **Agent response time**: How long should users wait?
   - Immediate acknowledgment + detailed response later?
   - Just one response after processing?
   - Configurable per agent?

9. **Agent visibility**: Should users see which agents are "active" in a channel?
   - Participant list shows agents?
   - Agent status indicators?

### Memory & Context
10. **Shared memory scope**: What should agents share?
    - All conversation history?
    - Just facts/entities?
    - Configurable per workspace?

11. **Memory retrieval**: How do agents access shared memory?
    - Automatic injection into context?
    - Tool-based retrieval?
    - Hybrid approach?

12. **Context window limits**: How to handle long threads?
    - Summarization?
    - Sliding window?
    - Semantic chunking?

---

## Success Metrics

### Functional
- ✅ Agents respond to @mentions 100% of the time
- ✅ Thread_id calculation is accurate
- ✅ Background processing completes within 30 seconds
- ✅ Checkpoints persist and restore correctly

### Performance
- ⚡ Message triage completes in <1 second
- ⚡ Agent response time <10 seconds (without documents)
- ⚡ Agent response time <60 seconds (with documents)
- ⚡ System handles 100+ concurrent conversations

### Quality
- 🎯 Agent responses are contextually relevant (user feedback)
- 🎯 Instruction hierarchy works as expected (testing)
- 🎯 No duplicate responses from same agent
- 🎯 Checkpoint recovery works after failures

---

## Related Ideas

- [RAG Workflows](./rag-workflows.md) - Document processing for attachments
- [Zep Knowledge Graphs](./zep-knowledge-graphs.md) - Shared memory system
- [Supabase Realtime Streaming](./supabase-realtime-streaming.md) - Worker notifications and live updates
- [Human-in-the-Loop](./human-in-the-loop.md) - Agent questions and pausing

---

## Notes & Brainstorming

### Instruction Hierarchy Example

```yaml
# System Prompt (base)
You are a helpful AI assistant.

# Profile Instructions (personality)
You are friendly, concise, and love using emojis! 🎉

# Membership Instructions (job description)
You are the customer support agent for Acme Corp.
Help users with billing, technical issues, and general questions.

# Channel Instructions (primary agent in #support)
This is the #support channel. Prioritize urgent issues.
Escalate to humans if the issue is complex.

# Participant Instructions (role in this channel)
You are the "Tier 1 Support" agent in this channel.
Handle basic questions. Escalate to @tier2-agent for complex issues.
```

**Final Prompt**: Merge all instructions with most specific taking precedence.

### Routing Decision Tree

```
Is message @mentioning an agent?
├─ YES → Route to mentioned agent(s) immediately
└─ NO → Is message replying to an agent?
    ├─ YES → Route to that agent immediately
    └─ NO → Is there a primary agent?
        ├─ YES → Should primary agent respond?
        │   ├─ YES → Route to primary agent after processing
        │   └─ NO → No routing
        └─ NO → No routing
```

### Potential Optimizations

1. **Thread ID Materialization**: Add `thread_id` column to messages table, updated via trigger
2. **Agent Pool**: Pre-warm agent instances for faster response times
3. **Batch Processing**: Group multiple messages for same thread into one agent execution
4. **Smart Caching**: Cache agent configurations, thread contexts, embeddings
5. **Parallel Execution**: Run background processing and agent response in parallel when possible

---

**Last Updated**: 2025-11-13
**Contributors**: Josh, Friday
**Status**: Active brainstorming - ready for Phase 1 planning

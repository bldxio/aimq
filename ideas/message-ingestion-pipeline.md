# Message Ingestion Pipeline - Processing All Messages

**Status**: 🌱 Core Feature
**Priority**: Critical - Entry point for all messages
**Complexity**: Medium
**Estimated Effort**: 2-3 days

---

## What

The main worker that processes every message that arrives in the system. Coordinates triage, routing, background processing, and agent execution.

### Key Features

- **Universal Entry Point**: All messages flow through this pipeline
- **Parallel Processing**: Triage and background processing run concurrently
- **Error Handling**: Graceful failures with retries
- **Observability**: Logging and metrics for every message
- **Idempotent**: Safe to retry without side effects

---

## Why

### Business Value
- **Reliable Processing**: No messages get lost
- **Fast Response**: Parallel processing reduces latency
- **Scalable**: Can handle high message volume
- **Debuggable**: Clear logs for troubleshooting

### Technical Value
- **Decoupled**: Orchestrates other workflows
- **Testable**: Easy to test with mocks
- **Extensible**: Easy to add new processing steps

---

## Architecture

### Message Flow

```
Message inserted into DB
    ↓
Supabase trigger → pgmq job created
    ↓
Worker picks up job
    ↓
[Message Ingestion Pipeline]
    ├─ Load message
    ├─ Validate message
    └─ Spawn parallel tasks:
        ├─ [Triage Workflow] → Route to agents
        └─ [Background Processing] → Knowledge extraction
    ↓
Wait for completion
    ↓
Mark job as complete
```

---

## Technical Design

### Worker Task

```python
from aimq.worker import worker
from aimq.workflows import MessageTriageWorkflow, BackgroundProcessingWorkflow

@worker.task("process_message")
async def process_message(message_id: str):
    """Main entry point for message processing"""

    try:
        # Load message
        message = await db.messages.get(message_id)

        if not message:
            logger.error(f"Message {message_id} not found")
            return

        logger.info(f"Processing message {message_id} in channel {message.channel_id}")

        # Validate message
        if not await validate_message(message):
            logger.warning(f"Message {message_id} failed validation")
            return

        # Spawn parallel tasks
        triage_task = asyncio.create_task(triage_message(message))
        background_task = asyncio.create_task(process_background(message))

        # Wait for both
        routing_decision, background_result = await asyncio.gather(
            triage_task,
            background_task,
            return_exceptions=True
        )

        # Handle triage result
        if isinstance(routing_decision, Exception):
            logger.error(f"Triage failed: {routing_decision}")
        elif routing_decision.should_respond_immediately:
            # Route to agents immediately
            for agent_id in routing_decision.agents:
                await enqueue_agent_response(message, agent_id)
        elif routing_decision.should_respond_after_processing:
            # Wait for background processing, then route
            if not isinstance(background_result, Exception):
                for agent_id in routing_decision.agents:
                    await enqueue_agent_response(message, agent_id)

        # Handle background result
        if isinstance(background_result, Exception):
            logger.error(f"Background processing failed: {background_result}")

        logger.info(f"Message {message_id} processed successfully")

    except Exception as e:
        logger.error(f"Error processing message {message_id}: {e}")
        raise  # Re-raise for worker retry logic

async def validate_message(message: Message) -> bool:
    """Validate message before processing"""

    # Check required fields
    if not message.workspace_id or not message.channel_id:
        return False

    # Check if channel exists
    channel = await db.channels.get(message.channel_id)
    if not channel or channel.deleted_at:
        return False

    # Check if author is participant
    if message.author_id:
        participant = await db.participants.find_one({
            "channel_id": message.channel_id,
            "profile_id": message.author_id
        })
        if not participant:
            logger.warning(f"Author {message.author_id} not in channel {message.channel_id}")
            # Allow anyway (might be system message)

    return True

async def triage_message(message: Message) -> RoutingDecision:
    """Run triage workflow"""

    workflow = MessageTriageWorkflow()
    return await workflow.run(message)

async def process_background(message: Message):
    """Run background processing workflow"""

    workflow = BackgroundProcessingWorkflow()
    return await workflow.run(message)

async def enqueue_agent_response(message: Message, agent_id: str):
    """Queue agent response job"""

    await worker.enqueue(
        "agent_response",
        message_id=message.id,
        agent_id=agent_id
    )
```

### Background Processing Workflow

```python
from aimq.workflows import BaseWorkflow, workflow

@workflow
class BackgroundProcessingWorkflow(BaseWorkflow):
    """Always-on processing for every message"""

    async def run(self, message: Message):
        # Calculate thread_id
        thread_id = await calculate_thread_id(message)
        await db.messages.update(
            message.id,
            metadata={**message.metadata, "thread_id": thread_id}
        )

        # Extract and queue attachments
        if message.parts:
            for part in message.parts:
                if part.get("type") == "attachment":
                    await enqueue_document_processing(part["url"])

        # Update knowledge graph (stub for now)
        await update_knowledge_graph_stub(message)

        # Update RAG embeddings (stub for now)
        await update_embeddings_stub(message)

        return {"thread_id": thread_id}

async def update_knowledge_graph_stub(message: Message):
    """Placeholder for knowledge graph updates"""
    logger.info(f"Would update knowledge graph for message {message.id}")
    # TODO: Implement when Zep integration is ready

async def update_embeddings_stub(message: Message):
    """Placeholder for RAG embeddings"""
    logger.info(f"Would update embeddings for message {message.id}")
    # TODO: Implement when RAG system is ready

async def enqueue_document_processing(url: str):
    """Queue document for processing"""
    await worker.enqueue("process_document", url=url)
```

---

## Implementation

### Phase 1: Basic Pipeline (Day 1)

**Tasks**:
1. Create `process_message` worker task
2. Implement message validation
3. Add basic error handling
4. Write tests

**Deliverable**: Messages flow through pipeline

### Phase 2: Parallel Processing (Day 2)

**Tasks**:
1. Implement parallel triage + background
2. Add routing logic
3. Add agent response queueing
4. Test parallel execution

**Deliverable**: Fast, parallel processing

### Phase 3: Production Hardening (Day 3)

**Tasks**:
1. Add comprehensive error handling
2. Add retry logic
3. Add observability (logging, metrics)
4. Load testing

**Deliverable**: Production-ready pipeline

---

## Dependencies

### Existing Features
- ✅ Worker task system
- ✅ Supabase pgmq integration
- ✅ Database models

### Required Features
- ⚠️ Message Triage Workflow
- ⚠️ Background Processing Workflow
- ⚠️ Thread ID calculation
- ⚠️ Agent Response Workflow

### Nice-to-Have
- 🔮 Message deduplication
- 🔮 Priority queues (urgent messages first)
- 🔮 Rate limiting (per channel/workspace)
- 🔮 Circuit breakers (stop processing if downstream fails)

---

## Open Questions

1. **Retry Strategy**: How to handle failures?
   - Retry N times with exponential backoff
   - Dead letter queue for permanent failures
   - Alert on repeated failures

2. **Parallel vs Sequential**: Always parallel?
   - Parallel (faster, more complex)
   - Sequential (simpler, slower)
   - Configurable per message type?

3. **Idempotency**: How to ensure safe retries?
   - Check if already processed (idempotency key)
   - Make all operations idempotent
   - Accept duplicate processing

4. **Observability**: What to log/track?
   - Every message (verbose, useful)
   - Errors only (quiet, may miss issues)
   - Sampling (balanced)

5. **Performance**: What's acceptable?
   - Process message in <5 seconds
   - Process message in <10 seconds
   - Depends on message complexity?

---

## Success Metrics

- ✅ 100% of messages processed
- ✅ No messages lost
- ✅ Errors handled gracefully
- ⚡ Processing time <5 seconds (without documents)
- ⚡ Processing time <60 seconds (with documents)
- 🎯 Retry success rate >95%

---

## Related Ideas

- [Message Routing & Triage](./message-routing-triage.md) - Called by pipeline
- [Thread Tree System](./thread-tree-system.md) - Used in background processing
- [Agent Response Workflows](./agent-response-workflows.md) - Queued by pipeline
- [Multi-Agent Group Chat](./multi-agent-group-chat.md) - Overall vision

---

## Examples

### Example 1: Simple Message

```python
# User sends message
message = await create_message(
    content="Hello!",
    channel_id="channel-123",
    author_id="user-456"
)

# Automatically triggers pipeline
# 1. Triage: No routing needed
# 2. Background: Calculate thread_id, update knowledge
# 3. Complete
```

### Example 2: Message with @mention

```python
# User mentions agent
message = await create_message(
    content="Hey @support-agent, I need help",
    channel_id="channel-123",
    author_id="user-456"
)

# Pipeline:
# 1. Triage: Route to support-agent immediately
# 2. Background: Calculate thread_id, update knowledge
# 3. Queue agent response
# 4. Complete
```

### Example 3: Message with Attachment

```python
# User uploads document
message = await create_message(
    content="Here's the report",
    channel_id="channel-123",
    author_id="user-456",
    parts=[{"type": "attachment", "url": "s3://..."}]
)

# Pipeline:
# 1. Triage: Route to primary agent after processing
# 2. Background:
#    - Calculate thread_id
#    - Queue document processing
#    - Update knowledge (after doc processed)
# 3. Wait for document processing
# 4. Queue agent response
# 5. Complete
```

---

**Last Updated**: 2025-11-13
**Status**: Ready to implement - critical entry point

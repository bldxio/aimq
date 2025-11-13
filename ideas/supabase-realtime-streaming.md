# Supabase Realtime Streaming

**Status**: 🌱 Future Feature
**Priority**: High - Needed for great UX
**Complexity**: Medium
**Estimated Effort**: 1 week

---

## What

Integration with Supabase Realtime for bidirectional streaming between workers and clients. This enables:
- Workers receive instant notifications of new jobs (no polling)
- Workers stream progress updates to clients (no database writes)
- Clients see live agent responses as they're generated

### Key Features

- **Worker Job Notifications**: Instant notification when new message arrives
- **Progress Streaming**: Stream agent reasoning steps to clients
- **Typing Indicators**: Show when agents are "thinking"
- **Partial Responses**: Stream response chunks as they're generated
- **Error Notifications**: Real-time error updates
- **Presence**: Track which agents are active

---

## Why

### Business Value
- **Better UX**: Users see progress in real-time
- **Reduced Latency**: No polling delays
- **Lower Costs**: Fewer database reads/writes
- **Transparency**: Users see what agents are doing

### Technical Value
- **Efficient**: WebSocket-based, low overhead
- **Scalable**: Supabase handles connection management
- **Simple**: Built into Supabase, no extra infrastructure
- **Reliable**: Automatic reconnection and error handling

---

## Architecture

### Current Flow (Polling)

```
User sends message
    ↓
Frontend writes to DB
    ↓
Worker polls DB every N seconds ⏰
    ↓
Worker processes message
    ↓
Worker writes response to DB
    ↓
Frontend polls DB for updates ⏰
    ↓
User sees response
```

**Problems**:
- Polling delay (N seconds)
- Unnecessary DB queries
- No progress updates
- Wasteful

### New Flow (Realtime)

```
User sends message
    ↓
Frontend writes to DB
    ↓
DB trigger → Realtime notification → Worker 🚀
    ↓
Worker processes message
    ├─ Stream progress → Realtime channel → Frontend 🚀
    ├─ Stream reasoning → Realtime channel → Frontend 🚀
    └─ Stream response chunks → Realtime channel → Frontend 🚀
    ↓
Worker writes final response to DB
    ↓
User sees response (already streamed!)
```

**Benefits**:
- Instant notification
- Live progress updates
- No polling
- Efficient

---

## Technical Design

### Realtime Channels

Supabase Realtime uses channels for pub/sub messaging:

```typescript
// Frontend subscribes to channel
const channel = supabase.channel(`workspace:${workspaceId}:channel:${channelId}`)

// Listen for agent updates
channel.on('broadcast', { event: 'agent_update' }, (payload) => {
  console.log('Agent update:', payload)
})

// Subscribe
channel.subscribe()
```

### Worker Job Notifications

**Option 1: Database Triggers + Realtime**

```sql
-- Trigger on new message
CREATE OR REPLACE FUNCTION notify_new_message()
RETURNS TRIGGER AS $$
BEGIN
  -- Notify via pg_notify (picked up by Realtime)
  PERFORM pg_notify(
    'new_message',
    json_build_object(
      'message_id', NEW.id,
      'workspace_id', NEW.workspace_id,
      'channel_id', NEW.channel_id,
      'author_id', NEW.author_id
    )::text
  );
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER new_message_trigger
AFTER INSERT ON messages
FOR EACH ROW
EXECUTE FUNCTION notify_new_message();
```

```python
# Worker subscribes to notifications
from supabase import create_client

supabase = create_client(url, key)

# Subscribe to new message notifications
channel = supabase.channel('new_messages')

@channel.on_postgres_changes(
    event='INSERT',
    schema='public',
    table='messages',
    callback=handle_new_message
)
async def handle_new_message(payload):
    """Handle new message notification"""
    message_id = payload['record']['id']
    await process_message(message_id)

# Subscribe
await channel.subscribe()
```

**Option 2: Broadcast Channel**

```python
# Frontend broadcasts new message
await supabase.channel('worker_jobs').send({
    'type': 'broadcast',
    'event': 'new_message',
    'payload': {
        'message_id': message_id,
        'workspace_id': workspace_id,
        'channel_id': channel_id
    }
})

# Worker listens
channel = supabase.channel('worker_jobs')

@channel.on_broadcast(event='new_message')
async def handle_new_message(payload):
    await process_message(payload['message_id'])
```

### Progress Streaming

```python
@workflow
class StreamingAgentWorkflow(BaseWorkflow):
    """Agent workflow with progress streaming"""

    async def run(self, message: Message, agent_id: str):
        # Create streaming channel
        channel_name = f"workspace:{message.workspace_id}:channel:{message.channel_id}"
        stream = supabase.channel(channel_name)

        # Send typing indicator
        await stream.send({
            'type': 'broadcast',
            'event': 'agent_typing',
            'payload': {
                'agent_id': agent_id,
                'message_id': message.id,
                'status': 'thinking'
            }
        })

        # Load agent
        agent = await load_agent(agent_id, message)

        # Stream reasoning steps
        async for step in agent.stream_reasoning(message):
            await stream.send({
                'type': 'broadcast',
                'event': 'agent_reasoning',
                'payload': {
                    'agent_id': agent_id,
                    'message_id': message.id,
                    'step': step.type,
                    'content': step.content
                }
            })

        # Stream response chunks
        response_chunks = []
        async for chunk in agent.stream_response(message):
            response_chunks.append(chunk)

            await stream.send({
                'type': 'broadcast',
                'event': 'agent_response_chunk',
                'payload': {
                    'agent_id': agent_id,
                    'message_id': message.id,
                    'chunk': chunk,
                    'is_final': False
                }
            })

        # Combine chunks and save to DB
        full_response = ''.join(response_chunks)
        response_message = await create_message(
            workspace_id=message.workspace_id,
            channel_id=message.channel_id,
            author_id=agent_id,
            reply_to_id=message.id,
            content=full_response,
            role='assistant'
        )

        # Send final notification
        await stream.send({
            'type': 'broadcast',
            'event': 'agent_response_complete',
            'payload': {
                'agent_id': agent_id,
                'message_id': message.id,
                'response_message_id': response_message.id,
                'is_final': True
            }
        })
```

### Frontend Integration

```typescript
// Subscribe to agent updates
const channel = supabase.channel(`workspace:${workspaceId}:channel:${channelId}`)

// Typing indicator
channel.on('broadcast', { event: 'agent_typing' }, (payload) => {
  setAgentTyping(payload.agent_id, true)
})

// Reasoning steps (optional, for debugging)
channel.on('broadcast', { event: 'agent_reasoning' }, (payload) => {
  console.log('Agent reasoning:', payload.step, payload.content)
  // Could show in UI: "Searching documents...", "Analyzing...", etc.
})

// Response chunks (stream to UI)
let currentResponse = ''
channel.on('broadcast', { event: 'agent_response_chunk' }, (payload) => {
  currentResponse += payload.chunk
  updateMessageUI(payload.message_id, currentResponse)
})

// Final response (save to state)
channel.on('broadcast', { event: 'agent_response_complete' }, (payload) => {
  setAgentTyping(payload.agent_id, false)
  finalizeMessage(payload.response_message_id)
})

channel.subscribe()
```

### Streaming LLM Responses

```python
from langchain.callbacks.base import AsyncCallbackHandler

class RealtimeStreamingCallback(AsyncCallbackHandler):
    """Stream LLM tokens to Realtime channel"""

    def __init__(self, channel, agent_id: str, message_id: str):
        self.channel = channel
        self.agent_id = agent_id
        self.message_id = message_id

    async def on_llm_new_token(self, token: str, **kwargs):
        """Called when LLM generates a new token"""
        await self.channel.send({
            'type': 'broadcast',
            'event': 'agent_response_chunk',
            'payload': {
                'agent_id': self.agent_id,
                'message_id': self.message_id,
                'chunk': token,
                'is_final': False
            }
        })

    async def on_llm_end(self, response, **kwargs):
        """Called when LLM finishes"""
        await self.channel.send({
            'type': 'broadcast',
            'event': 'agent_response_complete',
            'payload': {
                'agent_id': self.agent_id,
                'message_id': self.message_id,
                'is_final': True
            }
        })

# Use in agent
agent = ReActAgent(
    llm=llm,
    tools=tools,
    callbacks=[RealtimeStreamingCallback(channel, agent_id, message_id)]
)
```

---

## Dependencies

### Existing Features
- ✅ Supabase integration
- ✅ Worker task system
- ✅ Agent execution

### Required Features
- ⚠️ Supabase Realtime setup
- ⚠️ Worker Realtime client
- ⚠️ Streaming callback handlers
- ⚠️ Frontend Realtime integration

### Nice-to-Have
- 🔮 Presence tracking (which agents are online)
- 🔮 Typing indicators
- 🔮 Read receipts
- 🔮 Delivery confirmations

---

## Implementation Phases

### Phase 1: Worker Notifications (Week 1)
- [ ] Set up Supabase Realtime
- [ ] Create database triggers for new messages
- [ ] Implement worker Realtime listener
- [ ] Test instant job notifications
- [ ] Remove polling (or keep as fallback)

### Phase 2: Progress Streaming (Week 1)
- [ ] Create streaming callback handler
- [ ] Implement progress events (typing, reasoning, chunks)
- [ ] Add frontend Realtime subscription
- [ ] Test streaming in UI
- [ ] Handle reconnection and errors

### Phase 3: Polish (Week 1)
- [ ] Add typing indicators
- [ ] Add presence tracking
- [ ] Optimize channel management
- [ ] Add error handling
- [ ] Load testing

---

## Open Questions

1. **Channel Strategy**: One channel per workspace or per channel?
   - Per workspace: Fewer connections, more filtering
   - Per channel: More connections, less filtering
   - Hybrid: Workspace for workers, channel for clients

2. **Fallback**: Keep polling as fallback?
   - Yes: More reliable, redundant
   - No: Simpler, trust Realtime

3. **Message Persistence**: When to write to DB?
   - Stream only: Fast, but lost if client disconnects
   - Stream + final write: Best UX, redundant
   - Write only: Simple, no streaming

4. **Error Handling**: What if streaming fails?
   - Retry streaming
   - Fall back to polling
   - Write to DB and notify

5. **Rate Limiting**: How to handle high-frequency updates?
   - Throttle streaming (e.g., max 10 updates/sec)
   - Batch chunks
   - Debounce updates

---

## Success Metrics

- ✅ Worker receives notifications <1 second after message
- ✅ Clients see typing indicators immediately
- ✅ Response chunks stream in real-time
- ⚡ Streaming latency <100ms
- ⚡ No polling (or minimal fallback polling)

---

## Related Ideas

- [Multi-Agent Group Chat](./multi-agent-group-chat.md) - Uses streaming for responses
- [Human-in-the-Loop](./human-in-the-loop.md) - Uses streaming for questions

---

## Resources

- [Supabase Realtime Documentation](https://supabase.com/docs/guides/realtime)
- [Supabase Realtime Python Client](https://github.com/supabase-community/realtime-py)
- [LangChain Streaming](https://python.langchain.com/docs/expression_language/streaming)

---

**Last Updated**: 2025-11-13
**Status**: Planning - high priority for UX

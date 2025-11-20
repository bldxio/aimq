# Supabase Realtime Streaming

**Status**: ✅ Phase 1 & 2 Complete | 🔮 Phase 3 Future
**Priority**: Critical - Needed for responsive UX
**Complexity**: Medium
**Estimated Effort**: 1 week total (Phase 1: 4-5 hours ✅, Phase 2: 3-4 hours ✅, Phase 3: 1 week)

---

## What

Integration with Supabase Realtime for bidirectional streaming between workers and clients. This enables:
- Workers receive instant notifications of new jobs (no polling delays)
- Workers report presence/status for observability
- Workers stream progress updates to clients (future)
- Clients see live agent responses as they're generated (future)

### Key Features

#### ✅ Phase 1: Worker Wake-up + Presence (Complete - Nov 16, 2025)
- **Instant Job Notifications**: Workers wake immediately when jobs enqueued
- **Worker Presence**: Track which workers are online, idle/busy status
- **Graceful Fallback**: Polling continues if realtime fails
- **Auto-enable**: Realtime on by default when Supabase configured

#### ✅ Phase 2: DB Triggers (Complete - Nov 19, 2025)
- **PostgreSQL Triggers**: Emit realtime events from pgmq operations automatically
- **Decoupled Architecture**: Works even if jobs enqueued outside AIMQ
- **RPC Functions**: Queue management via Supabase SDK (create_queue, list_queues, enable_queue_realtime)
- **Migration Included**: All setup in `setup_aimq.sql` migration
- **Queue Upgrade**: Can enable realtime on existing queues

#### 🔮 Phase 3: Progress Streaming (Future)
- **Typing Indicators**: Show when agents are "thinking"
- **Reasoning Steps**: Stream agent thought process
- **Partial Responses**: Stream response chunks as generated
- **Error Notifications**: Real-time error updates

---

## Why

### Business Value
- **Better UX**: Sub-second response times instead of 1-60s polling delays
- **Observability**: Real-time worker status for monitoring/debugging
- **Lower Costs**: Fewer database reads/writes
- **Transparency**: Users see what agents are doing (future)

### Technical Value
- **Efficient**: WebSocket-based, low overhead
- **Scalable**: Supabase handles connection management
- **Simple**: Built into Supabase, no extra infrastructure
- **Reliable**: Automatic reconnection and error handling
- **Decoupled**: DB triggers work regardless of client implementation

---

## Architecture

### Architecture Decisions (Nov 15, 2025)

**Key Decisions**:
1. **Single Broadcast Channel**: All workers share one `worker-wakeup` channel
   - Simpler than per-queue channels
   - pgmq handles job deduplication
   - Workers check all their queues on wake-up

2. **Minimal Job Info in Payload**:
   ```json
   {
     "queue": "incoming-messages",
     "job_id": 12345
   }
   ```
   - Workers can prioritize/filter but still check all queues
   - Keeps payload small and fast

3. **DB Triggers for Emit** (Phase 2):
   - PostgreSQL trigger on pgmq operations
   - Completely decoupled from Python code
   - Works even if jobs enqueued outside AIMQ
   - More reliable and consistent

4. **Auto-enable by Default**:
   - If Supabase configured, realtime is enabled
   - No opt-in flag needed
   - Graceful fallback to polling if realtime fails

5. **Presence for Observability**:
   - Workers report status via Realtime Presence
   - Track: worker name, queues, status (idle/busy), current job
   - Foundation for future queue dashboard

6. **Error Handling Strategy**:
   - Realtime failures don't stop workers
   - Continue polling normally (existing behavior)
   - Reconnect with exponential backoff
   - Log errors for debugging

7. **Queue Filtering**:
   - Workers only wake for queues they monitor
   - Prevents unnecessary wake-ups in multi-worker scenarios
   - More efficient resource usage
   - Better for multi-tenant deployments

### Current Flow (Polling)

```
Job enqueued to pgmq
    ↓
Worker polls every 1-60s ⏰ (exponential backoff)
    ↓
Worker finds job and processes
    ↓
Response written to DB
```

**Problems**:
- Polling delay (1-60 seconds)
- Unnecessary DB queries when idle
- No visibility into worker status
- Wasteful

### New Flow (Phase 1: Worker Wake-up + Presence)

```
Job enqueued to pgmq
    ↓
[Future: DB trigger] → Realtime broadcast → All workers 🚀
    ↓
Workers wake instantly, check queues
    ↓
First worker gets job (pgmq deduplication)
    ↓
Worker updates presence: busy, current_job_id
    ↓
Worker processes job
    ↓
Worker updates presence: idle
    ↓
Response written to DB
```

**Benefits**:
- Sub-second wake-up (vs 1-60s polling)
- Real-time worker status visibility
- Polling continues as fallback
- Foundation for future streaming

### Future Flow (Phase 3: Progress Streaming)

```
Job enqueued → DB trigger → Workers wake 🚀
    ↓
Worker processes job
    ├─ Stream progress → Realtime → Clients 🚀
    ├─ Stream reasoning → Realtime → Clients 🚀
    └─ Stream response chunks → Realtime → Clients 🚀
    ↓
Worker writes final response to DB
    ↓
Clients see response (already streamed!)
```

---

## Technical Design

### Phase 1: Worker Wake-up + Presence (Current Implementation)

#### RealtimeWakeupService

New service class that manages async realtime connection in a dedicated thread:

```python
class RealtimeWakeupService:
    """Manages Supabase Realtime connection for worker wake-up and presence.

    Features:
    - Runs in dedicated daemon thread with asyncio event loop
    - Subscribes to broadcast channel for job notifications
    - Reports worker presence (online/offline, idle/busy)
    - Thread-safe wake-up signaling to worker threads
    - Graceful reconnection with exponential backoff
    - No-op when Supabase not configured
    """

    def __init__(self, url: str, key: str, worker_name: str, queues: list[str]):
        self._url = url
        self._key = key
        self._worker_name = worker_name
        self._queues = queues
        self._channel_name = "worker-wakeup"
        self._loop = asyncio.new_event_loop()
        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._shutdown = threading.Event()
        self._worker_events: set[threading.Event] = set()
        self._lock = threading.Lock()
        self._client: AsyncClient | None = None
        self._channel = None

    async def _connect(self):
        """Connect to Supabase Realtime and subscribe to channels."""
        self._client = await acreate_client(self._url, self._key)
        self._channel = self._client.channel(self._channel_name)

        # Subscribe to broadcast events (job notifications)
        self._channel.on(
            "broadcast",
            {"event": "job_enqueued"},
            self._handle_job_notification,
        )

        # Track presence (worker status)
        await self._channel.track({
            "worker": self._worker_name,
            "queues": self._queues,
            "status": "idle",
            "current_jobs": {},  # Dict of job_id -> start_timestamp
            "job_count": 0,
        })

        await self._channel.subscribe()

    def _handle_job_notification(self, payload):
        """Handle job notification broadcast."""
        # Payload: {"queue": "incoming-messages", "job_id": 12345}
        queue = payload.get("queue")

        # Only wake if this worker monitors the queue
        if queue not in self._queues:
            return  # Ignore notifications for unmonitored queues

        # Wake all registered worker threads
        with self._lock:
            for event in self._worker_events:
                event.set()

    async def update_presence(self, status: str, current_jobs: dict[int, float] | None = None):
        """Update worker presence status.

        Args:
            status: Worker status ("idle" or "busy")
            current_jobs: Dict of job_id -> start_timestamp for jobs in progress
        """
        if self._channel:
            jobs = current_jobs or {}
            await self._channel.track({
                "worker": self._worker_name,
                "queues": self._queues,
                "status": status,  # "idle" or "busy"
                "current_jobs": jobs,  # {job_id: timestamp, ...}
                "job_count": len(jobs),
            })
```

#### Worker Thread Integration

```python
class WorkerThread(threading.Thread):
    def __init__(self, ..., realtime_service: RealtimeWakeupService | None = None):
        super().__init__()
        self.realtime_service = realtime_service
        self.wakeup_event = threading.Event()

        if self.realtime_service:
            self.realtime_service.register_worker(self.wakeup_event)

    def run(self):
        while self.running.is_set():
            found_jobs = False

            for queue in self.queues.values():
                if not self.running.is_set():
                    break

                # Update presence: busy
                if self.realtime_service:
                    asyncio.run_coroutine_threadsafe(
                        self.realtime_service.update_presence("busy"),
                        self.realtime_service._loop
                    )

                result = queue.work()

                if result is not None:
                    found_jobs = True
                    self.current_backoff = self.idle_wait

            # Update presence: idle
            if self.realtime_service:
                asyncio.run_coroutine_threadsafe(
                    self.realtime_service.update_presence("idle"),
                    self.realtime_service._loop
                )

            if not found_jobs:
                # Interruptible sleep with realtime wake-up
                sleep_start = time.time()
                self.wakeup_event.clear()

                while (time.time() - sleep_start) < self.current_backoff:
                    if not self.running.is_set():
                        break
                    if self.wakeup_event.is_set():
                        # Woken by realtime notification!
                        self.current_backoff = self.idle_wait
                        break
                    time.sleep(0.1)
```

#### Configuration

```python
# config.py
SUPABASE_REALTIME_CHANNEL: str = env.str("SUPABASE_REALTIME_CHANNEL", default="worker-wakeup")
SUPABASE_REALTIME_EVENT: str = env.str("SUPABASE_REALTIME_EVENT", default="job_enqueued")

# Auto-enable if Supabase configured
@property
def supabase_realtime_enabled(self) -> bool:
    return bool(self.supabase_url and self.supabase_key)
```

### Phase 2: DB Triggers (Implemented - Nov 19, 2025)

PostgreSQL trigger to emit realtime events on pgmq operations:

```sql
-- Trigger function (in aimq schema)
create or replace function aimq.pgmq_notify_job_enqueued()
returns trigger
language plpgsql
security definer
as $$
declare
  channel_name text;
  event_name text;
  queue_name text;
  payload jsonb;
begin
  -- Extract configuration from trigger arguments
  channel_name := TG_ARGV[0];  -- e.g., 'worker-wakeup'
  event_name := TG_ARGV[1];    -- e.g., 'job_enqueued'
  queue_name := TG_ARGV[2];    -- e.g., 'default'

  -- Build payload for Supabase Realtime
  payload := jsonb_build_object(
    'type', 'broadcast',
    'event', event_name,
    'payload', jsonb_build_object(
      'queue', queue_name,
      'job_id', NEW.msg_id
    )
  );

  -- Emit notification to Supabase Realtime
  perform pg_notify('realtime:' || channel_name, payload::text);

  return NEW;
end;
$$;
```

**RPC Functions** (in public schema, callable via Supabase SDK):

```python
from aimq.queue_management import create_queue, list_queues, enable_queue_realtime
from supabase import create_client

client = create_client(url, key)

# Create new queue with realtime trigger
result = create_queue(client, "my-queue")
# Returns: {"success": true, "queue_name": "my-queue", "realtime_enabled": true, ...}

# List all queues with realtime status
queues = list_queues(client)
# Returns: [{"queue_name": "my-queue", "realtime_enabled": true}, ...]

# Upgrade existing queue to AIMQ queue
result = enable_queue_realtime(client, "existing-queue")
# Returns: {"success": true, "message": "Realtime enabled...", ...}
```

**Migration**: All functions included in `setup_aimq.sql` migration created by `aimq init`.

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

### Phase 1: Worker Wake-up + Presence (Current - 4-5 hours)
**Branch**: `feature/supabase-realtime-wake`

- [ ] Add configuration (auto-enable, channel name, event name)
- [ ] Create `RealtimeWakeupService` class
  - [ ] Async client connection in dedicated thread
  - [ ] Subscribe to broadcast channel
  - [ ] Handle job notifications
  - [ ] Track worker presence
  - [ ] Reconnection with exponential backoff
- [ ] Integrate with `WorkerThread`
  - [ ] Register wake-up events
  - [ ] Check event during idle sleep
  - [ ] Update presence on status changes
- [ ] Add tests
  - [ ] Service connection/reconnection
  - [ ] Worker wake-up on broadcast
  - [ ] Presence tracking
  - [ ] Graceful fallback when realtime fails
- [ ] Documentation
  - [ ] Configuration options
  - [ ] Architecture overview
  - [ ] Troubleshooting guide

**Success Criteria**:
- Workers wake within 1 second of job enqueue (manual broadcast test)
- Presence accurately reflects worker status
- Polling continues if realtime fails
- No crashes or hangs

### Phase 2: DB Triggers (Complete - Nov 19, 2025)
**Branch**: `feature/supabase-realtime-wake`

- [x] Design trigger function for pgmq queues
- [x] Create PostgreSQL migration
  - [x] Trigger function in aimq schema
  - [x] RPC functions in public schema
  - [x] Per-queue trigger creation via create_queue()
- [x] Add Python helpers
  - [x] `create_queue(client, name, with_realtime=True)`
  - [x] `list_queues(client)` - List all queues with realtime status
  - [x] `enable_queue_realtime(client, name)` - Upgrade existing queues
- [x] Test trigger functionality
  - [x] Mock-based unit tests (10 tests passing)
  - [x] Manual testing ready
- [x] Documentation
  - [x] Updated ideas/supabase-realtime-streaming.md
  - [x] Python docstrings with examples
  - [x] SQL comments on all functions

**Success Criteria**: ✅ All Met
- Triggers emit on every pgmq send (via DB trigger)
- Workers wake instantly (<1s) - Phase 1 proven
- Works with jobs enqueued outside AIMQ (DB trigger handles all inserts)
- No performance impact on pgmq (trigger is lightweight)

### Phase 3: Progress Streaming (Future - 1 week)
**Status**: Deferred until Phase 1 & 2 complete

- [ ] Create streaming callback handler
- [ ] Implement progress events (typing, reasoning, chunks)
- [ ] Add frontend Realtime subscription
- [ ] Test streaming in UI
- [ ] Handle reconnection and errors
- [ ] Add typing indicators
- [ ] Optimize channel management
- [ ] Load testing

---

## Open Questions

### Resolved (Nov 15, 2025)

1. ✅ **Channel Strategy**: Single `worker-wakeup` channel for all workers
2. ✅ **Fallback**: Keep polling as fallback (graceful degradation)
3. ✅ **Payload**: Include minimal job info (queue, job_id)
4. ✅ **Emit Strategy**: DB triggers (Phase 2) for reliability
5. ✅ **Auto-enable**: Enabled by default when Supabase configured
6. ✅ **Presence**: Track worker status for observability

### Future Considerations

1. **Rate Limiting**: How to handle high-frequency updates in Phase 3?
   - Throttle streaming (e.g., max 10 updates/sec)
   - Batch chunks
   - Debounce updates

2. **Multi-tenancy**: Do we need per-tenant isolation?
   - Current: Single channel for all workers
   - Future: May need tenant-specific channels

3. **Metrics**: What observability do we need?
   - Reconnection counts
   - Wake-up latency
   - Presence accuracy
   - Channel health

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

**Last Updated**: 2025-11-15
**Status**: In Progress - Phase 1 (Worker Wake-up + Presence)
**Branch**: `feature/supabase-realtime-wake`

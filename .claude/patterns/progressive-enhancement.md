# Progressive Enhancement Pattern

## Overview

Progressive enhancement is a development strategy where you build features in independent, valuable phases. Each phase delivers working functionality that can be tested, deployed, and used immediately, while setting the foundation for the next phase.

This is different from "big bang" development where everything must be complete before anything works.

## Core Principles

### 1. Each Phase is Independently Valuable

Every phase should deliver something users can actually use:

```
❌ Big Bang Approach:
Phase 1: Design everything
Phase 2: Build everything
Phase 3: Test everything
Phase 4: Deploy everything
└─> Nothing works until Phase 4

✅ Progressive Enhancement:
Phase 1: Basic feature (works!)
Phase 2: Enhanced feature (works better!)
Phase 3: Advanced feature (works even better!)
└─> Something works after every phase
```

### 2. Later Phases Build on Earlier Ones

Each phase extends previous work without breaking it:

```python
# Phase 1: Basic functionality
def process_job(job):
    result = do_work(job)
    return result

# Phase 2: Add monitoring (Phase 1 still works)
def process_job(job):
    start_time = time.time()
    result = do_work(job)
    log_metrics(time.time() - start_time)
    return result

# Phase 3: Add retry logic (Phases 1 & 2 still work)
def process_job(job):
    start_time = time.time()
    result = retry_on_failure(lambda: do_work(job))
    log_metrics(time.time() - start_time)
    return result
```

### 3. Minimize Dependencies Between Phases

Each phase should be as independent as possible:

```
✅ Good: Loose coupling
Phase 1: Worker polls queue (standalone)
Phase 2: Worker listens to realtime (optional enhancement)
└─> Phase 2 can be disabled without breaking Phase 1

❌ Bad: Tight coupling
Phase 1: Worker setup (incomplete)
Phase 2: Worker polling (depends on Phase 1)
Phase 3: Worker processing (depends on Phase 2)
└─> Nothing works until all phases complete
```

## Real-World Example: Supabase Realtime

### The Challenge

Build instant worker wake-up when jobs are enqueued to pgmq queues.

### Big Bang Approach (What We Didn't Do)

```
Phase 1: Design entire system
  - Realtime client
  - Database triggers
  - CLI commands
  - Migration scripts
  - Error handling
  - Testing

Phase 2: Implement everything
  - 2000+ lines of code
  - Multiple moving parts
  - Complex interactions

Phase 3: Test everything
  - Integration tests
  - Manual testing
  - Bug fixes

Phase 4: Deploy
  - Finally works!
  - But took weeks
  - High risk
```

**Problems**:
- Nothing works until the end
- Hard to test incrementally
- High risk of integration issues
- Long feedback loop
- Difficult to debug

### Progressive Enhancement (What We Did)

#### Phase 1: Worker Wake-Up Service

**Goal**: Workers wake instantly when jobs are enqueued

**Deliverable**: Python service that listens to Realtime and wakes workers

```python
# src/aimq/realtime.py
class RealtimeService:
    """Listen to Supabase Realtime and wake workers"""

    def __init__(self):
        self.client = RealtimeClient(config.supabase_url)
        self.wake_event = asyncio.Event()

    async def listen(self):
        """Listen for job notifications"""
        channel = self.client.channel('aimq:jobs')
        channel.on_broadcast('job_enqueued', self._on_job)
        await channel.subscribe()

    def _on_job(self, payload):
        """Wake worker when job arrives"""
        self.wake_event.set()
```

**Value**: Workers can wake instantly if something broadcasts to the channel

**Testing**: Mock Realtime client, test wake-up logic

**Status**: ✅ Works independently, can be deployed

#### Phase 2: Database Triggers + CLI

**Goal**: Automatically broadcast when jobs are enqueued (no manual broadcast needed)

**Deliverable**: DB triggers + CLI commands for queue management

```sql
-- Database trigger (automatic broadcast)
create or replace function aimq.notify_job_enqueued()
  returns trigger
  language plpgsql
as $$
begin
    perform pg_notify(
        'aimq:jobs',
        json_build_object('event', 'job_enqueued')::text
    );
    return NEW;
end;
$$;

-- Attach to queue
create trigger aimq_notify_my_queue
  after insert on pgmq.my_queue
  for each row
  execute function aimq.notify_job_enqueued();
```

```python
# CLI commands
@click.command()
def create(queue_name: str, realtime: bool = True):
    """Create queue with optional realtime trigger"""
    provider.create_queue(queue_name)
    if realtime:
        provider.enable_realtime(queue_name)

@click.command()
def enable_realtime(queue_name: str):
    """Upgrade existing queue to realtime"""
    provider.enable_realtime(queue_name)
```

**Value**:
- Automatic wake-up (no manual broadcast)
- Easy queue management via CLI
- Can upgrade existing queues

**Testing**: Mock Supabase RPC, test trigger setup

**Status**: ✅ Works with Phase 1, enhances it

**Backward Compatibility**: Phase 1 still works if Phase 2 isn't deployed

### Why This Worked

**Fast Feedback**:
- Phase 1 deployed in days, not weeks
- Could test worker wake-up immediately
- Found issues early (Realtime connection handling)

**Reduced Risk**:
- Small, testable changes
- Each phase independently verified
- Easy to rollback if needed

**Better Testing**:
- Phase 1: Test wake-up logic in isolation
- Phase 2: Test trigger setup in isolation
- Integration: Test them together

**Flexibility**:
- Can use Phase 1 with manual broadcast
- Can add Phase 2 later when ready
- Can skip Phase 2 if not needed

## Implementation Strategy

### Step 1: Identify the Minimal Valuable Increment

Ask: "What's the smallest thing that delivers value?"

```
❌ Too big: "Complete realtime system with triggers, CLI, and monitoring"
✅ Just right: "Worker wakes when notified"
```

### Step 2: Define Clear Phase Boundaries

Each phase should have:
- Clear goal
- Concrete deliverable
- Independent value
- Testable outcome

```markdown
## Phase 1: Worker Wake-Up
**Goal**: Workers wake instantly when notified
**Deliverable**: RealtimeService class
**Value**: Instant wake-up (if something broadcasts)
**Test**: Mock broadcast, verify wake-up

## Phase 2: Automatic Broadcast
**Goal**: Automatic broadcast on job enqueue
**Deliverable**: DB triggers + CLI
**Value**: No manual broadcast needed
**Test**: Insert job, verify broadcast
```

### Step 3: Build and Test Each Phase Completely

Don't move to the next phase until current phase is:
- ✅ Implemented
- ✅ Tested
- ✅ Documented
- ✅ Deployable

```python
# Phase 1 complete checklist
✅ RealtimeService implemented
✅ Unit tests passing
✅ Integration test with mock
✅ Documentation updated
✅ Can be deployed independently

# Now ready for Phase 2
```

### Step 4: Ensure Backward Compatibility

Later phases should enhance, not replace:

```python
# Phase 1: Basic wake-up
class Worker:
    def __init__(self):
        self.realtime = RealtimeService()  # Optional

    async def run(self):
        if self.realtime:
            await self.realtime.listen()  # Enhanced
        else:
            await self.poll()  # Fallback (Phase 1 still works)

# Phase 2: Automatic triggers
# Worker code doesn't change!
# Just add triggers to database
```

## Common Patterns

### Pattern 1: Feature Flags

Use flags to enable/disable phases:

```python
class Worker:
    def __init__(self):
        self.use_realtime = config.enable_realtime  # Flag

    async def run(self):
        if self.use_realtime:
            await self.run_with_realtime()  # Phase 2
        else:
            await self.run_with_polling()  # Phase 1
```

### Pattern 2: Graceful Degradation

Fall back to earlier phases if later ones fail:

```python
async def get_next_job(self):
    try:
        # Phase 2: Try realtime wake-up
        await self.realtime.wait_for_job(timeout=1.0)
    except RealtimeError:
        # Phase 1: Fall back to polling
        logger.warning("Realtime failed, falling back to polling")

    return await self.queue.pop()
```

### Pattern 3: Additive APIs

Add new methods without changing existing ones:

```python
# Phase 1: Basic queue
class QueueProvider:
    def create_queue(self, name: str):
        """Create a queue"""
        pass

# Phase 2: Add realtime (Phase 1 unchanged)
class QueueProvider:
    def create_queue(self, name: str):
        """Create a queue"""
        pass

    def enable_realtime(self, name: str):  # New method
        """Enable realtime on existing queue"""
        pass
```

## Anti-Patterns

### ❌ Incomplete Phases

```python
# Bad: Phase 1 doesn't work on its own
class Worker:
    def __init__(self):
        self.realtime = RealtimeService()  # Required!

    async def run(self):
        await self.realtime.listen()  # Breaks if realtime not available
```

**Problem**: Phase 1 depends on Phase 2 being complete

**Fix**: Make each phase independently functional

### ❌ Breaking Changes Between Phases

```python
# Bad: Phase 2 breaks Phase 1
# Phase 1
def process_job(job_id: int):
    pass

# Phase 2 (breaks Phase 1!)
def process_job(job: Job):  # Changed signature!
    pass
```

**Problem**: Existing code breaks when Phase 2 is deployed

**Fix**: Add new functions or use backward-compatible signatures

### ❌ Tightly Coupled Phases

```python
# Bad: Can't use Phase 2 without Phase 1
class RealtimeService:
    def __init__(self, worker: Worker):  # Tight coupling!
        self.worker = worker
```

**Problem**: Phases can't be developed/tested independently

**Fix**: Use loose coupling (events, callbacks, interfaces)

## Testing Strategy

### Test Each Phase Independently

```python
# Phase 1 tests (no Phase 2 dependencies)
def test_worker_wakes_on_notification():
    worker = Worker()
    worker.realtime.wake()
    assert worker.is_awake()

# Phase 2 tests (no Phase 1 dependencies)
def test_trigger_broadcasts_on_insert():
    insert_job(queue='test')
    assert broadcast_received('aimq:jobs')

# Integration tests (both phases together)
def test_worker_wakes_on_job_insert():
    worker = Worker()
    insert_job(queue='test')
    assert worker.is_awake()
```

### Test Backward Compatibility

```python
def test_phase1_still_works_without_phase2():
    """Phase 1 should work even if Phase 2 isn't deployed"""
    worker = Worker(use_realtime=False)
    assert worker.can_process_jobs()

def test_phase2_enhances_phase1():
    """Phase 2 should enhance, not replace Phase 1"""
    worker = Worker(use_realtime=True)
    assert worker.can_process_jobs()  # Still works
    assert worker.wakes_faster()  # Enhanced
```

## Benefits

### Faster Time to Value

```
Big Bang: 4 weeks → First working feature
Progressive: 1 week → First working feature
            2 weeks → Enhanced feature
            3 weeks → Advanced feature
```

### Reduced Risk

- Smaller changes = less risk
- Each phase independently verified
- Easy to rollback if needed
- Issues found early

### Better Testing

- Test each phase in isolation
- Integration tests between phases
- Easier to debug (smaller surface area)

### Flexibility

- Can stop at any phase
- Can skip phases if not needed
- Can deploy phases independently
- Can adjust based on feedback

## When to Use

### ✅ Good Fit

- Large features (multiple weeks)
- Complex integrations
- Uncertain requirements
- High-risk changes
- Multiple stakeholders

### ❌ Not Needed

- Trivial changes (< 1 day)
- Well-understood problems
- Low-risk changes
- Single-purpose features

## Related

- [@.claude/patterns/demo-driven-development-core.md](./demo-driven-development-core.md) - Build demos first
- [@.claude/patterns/command-composition.md](./command-composition.md) - Composable commands
- [@.claude/standards/testing-strategy.md](../standards/testing-strategy.md) - Testing approach
- [@.claude/architecture/database-schema-organization.md](../architecture/database-schema-organization.md) - Schema evolution

## References

- [Progressive Enhancement (Web)](https://developer.mozilla.org/en-US/docs/Glossary/Progressive_Enhancement)
- [Incremental Development](https://en.wikipedia.org/wiki/Incremental_build_model)
- [Feature Flags](https://martinfowler.com/articles/feature-toggles.html)

---

**Remember**: Ship small, ship often, ship value! 🚀✨

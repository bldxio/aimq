# Progressive Enhancement: Supabase Realtime Case Study

> **Status**: Active
> **Last Updated**: 2025-11-20
> **Category**: patterns

## Overview

Real-world example of progressive enhancement: building instant worker wake-up for AIMQ using Supabase Realtime.

## The Challenge

Build instant worker wake-up when jobs are enqueued to pgmq queues.

## Big Bang Approach (What We Didn't Do)

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

## Progressive Enhancement (What We Did)

### Phase 1: Worker Wake-Up Service

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

### Phase 2: Database Triggers + CLI

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

## Why This Worked

### Fast Feedback

- Phase 1 deployed in days, not weeks
- Could test worker wake-up immediately
- Found issues early (Realtime connection handling)

### Reduced Risk

- Small, testable changes
- Each phase independently verified
- Easy to rollback if needed

### Better Testing

- Phase 1: Test wake-up logic in isolation
- Phase 2: Test trigger setup in isolation
- Integration: Test them together

### Flexibility

- Can use Phase 1 with manual broadcast
- Can add Phase 2 later when ready
- Can skip Phase 2 if not needed

## Lessons Learned

### What Worked Well

1. **Independent phases**: Each phase delivered value on its own
2. **Clear boundaries**: Easy to know when a phase was "done"
3. **Backward compatibility**: Phase 1 never broke when adding Phase 2
4. **Fast iteration**: Could test and adjust quickly

### What We'd Do Differently

1. **More granular phases**: Could have split Phase 2 into "triggers" and "CLI" separately
2. **Feature flags**: Would have made testing easier
3. **Better documentation**: Document phase boundaries upfront

## Related

- [@progressive-enhancement-core.md](./progressive-enhancement-core.md) - Core principles
- [@progressive-enhancement-patterns.md](./progressive-enhancement-patterns.md) - Common patterns
- [@test-mocking-external-services.md](./test-mocking-external-services.md) - Test evolution
- [@../quick-references/supabase-local/integration.md](../quick-references/supabase-local/integration.md) - Supabase integration
- [Progressive Enhancement: Patterns](./progressive-enhancement-patterns.md) - Common patterns
- [Demo-Driven Development](./demo-driven-development.md) - Build demos first
- [Database Schema Organization](../architecture/database-schema-organization.md) - Schema evolution

## References

- [Supabase Realtime](https://supabase.com/docs/guides/realtime)
- [PostgreSQL Triggers](https://www.postgresql.org/docs/current/trigger-definition.html)
- [Feature Flags](https://martinfowler.com/articles/feature-toggles.html)

---

**Remember**: Real-world success comes from shipping incrementally! 🎯✨

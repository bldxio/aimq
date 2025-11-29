# Progressive Enhancement: Common Patterns

> **Status**: Active
> **Last Updated**: 2025-11-20
> **Category**: patterns

## Overview

Common patterns and anti-patterns for implementing progressive enhancement in your codebase.

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

## Related

- [@progressive-enhancement-core.md](./progressive-enhancement-core.md) - Core principles and strategy
- [@progressive-enhancement-case-study.md](./progressive-enhancement-case-study.md) - Real-world case study
- [@demo-driven-development.md](./demo-driven-development.md) - Demo-driven development
- [@testing-strategy.md](./testing-strategy.md) - Testing approach
- [Progressive Enhancement: Case Study](./progressive-enhancement-case-study.md) - Real-world example
- [Testing Strategy](./testing-strategy.md) - Testing patterns
- [Error Handling](./error-handling.md) - Error handling patterns

## References

- [Feature Flags](https://martinfowler.com/articles/feature-toggles.html)
- [Graceful Degradation](https://developer.mozilla.org/en-US/docs/Glossary/Graceful_degradation)
- [Backward Compatibility](https://en.wikipedia.org/wiki/Backward_compatibility)

---

**Remember**: Build for today, design for tomorrow! 🌟

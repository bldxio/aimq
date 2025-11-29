# Demo-Driven Development

Use an upcoming demo as a focusing constraint to deliver working software quickly while maintaining quality.

## The Philosophy

> "A demo deadline is a forcing function that cuts through analysis paralysis and over-engineering. It forces you to answer: What MUST work? What CAN wait?"

Demo-Driven Development (DDD) is not about cutting corners—it's about **ruthless prioritization** with a concrete goal.

## How It Works

### 1. Set a Deadline
**Example**: "Demo in 2 hours"

The deadline should be:
- **Specific**: Exact time, not "soon"
- **Realistic**: Achievable but challenging
- **Immovable**: Real demo, real audience

### 2. Define MVP
**Ask**: "What must work for the demo to be successful?"

**Example from Message Agent**:
```
Must Have (for demo):
✅ Detect @mentions in messages
✅ Route to appropriate queue
✅ Handle unknown mentions gracefully
✅ Basic logging to show it works
✅ Multiple test scenarios

Nice to Have (defer):
⏸️ Thread tree handling
⏸️ Profile lookup from database
⏸️ Response message formatting
⏸️ Advanced error handling
⏸️ Performance optimization
```

### 3. Build Iteratively
**Process**:
1. Get something working (even if ugly)
2. Make it correct
3. Make it clean
4. Make it tested
5. Repeat

**Example Timeline** (2-hour demo):
- **0:00-0:15**: Plan and design
- **0:15-0:45**: Build core functionality
- **0:45-1:00**: Fix bugs and test
- **1:00-1:30**: Write tests and documentation
- **1:30-1:45**: Polish and prepare demo
- **1:45-2:00**: Buffer for unexpected issues

### 4. Maintain Quality
**Non-negotiables**:
- ✅ Write tests (even if not 100% coverage)
- ✅ Clean, readable code
- ✅ Basic documentation
- ✅ No known critical bugs

**Can compromise on**:
- ⏸️ Perfect test coverage
- ⏸️ Comprehensive documentation
- ⏸️ Edge case handling
- ⏸️ Performance optimization

### 5. Document Deferred Work
**Keep a list** of what was deferred:

```markdown
## Deferred Features (Post-Demo)

### High Priority
- [ ] Thread tree handling for conversation context
- [ ] Profile lookup from Supabase
- [ ] Response message formatting

### Medium Priority
- [ ] Advanced error handling
- [ ] Performance optimization
- [ ] Comprehensive logging

### Low Priority
- [ ] UI polish
- [ ] Additional test scenarios
- [ ] Documentation expansion
```

## Real-World Example: Message Agent

### The Challenge
Build a message routing system for a demo in ~2 hours.

### The Approach

**Hour 1: Core Functionality**
```python
# Started with simplest possible implementation
def detect_mentions(text: str) -> List[str]:
    """Extract @mentions from text."""
    return re.findall(r'@(\w+)', text)

def resolve_queue(mention: str) -> str:
    """Map mention to queue name."""
    if mention.endswith('-assistant'):
        return mention
    return 'default-assistant'

# Got it working, then improved
```

**Hour 2: Tests and Polish**
```python
# Added comprehensive tests
def test_detect_mentions():
    assert detect_mentions("@alice") == ["alice"]
    assert detect_mentions("@alice @bob") == ["alice", "bob"]
    assert detect_mentions("user@example.com") == []  # Edge case

# 39 tests total, all passing ✅
```

### The Result
- ✅ Working demo in 2 hours
- ✅ 39 comprehensive tests
- ✅ Clean, documented code
- ✅ Multiple test scenarios
- ✅ Ready to present

### What Was Deferred
- ⏸️ Thread tree handling (client-side decision)
- ⏸️ Profile lookup (infrastructure not ready)
- ⏸️ Response formatting (logging sufficient for demo)

## Benefits

### 1. Forces Prioritization
**Without DDD**:
"We should probably handle thread trees... and profile lookup... and maybe add caching... and what about rate limiting?"

**With DDD**:
"For the demo, we need: mentions detection, routing, and logging. Everything else can wait."

### 2. Prevents Over-Engineering
**Without DDD**:
```python
class MentionDetector:
    """Sophisticated mention detection with ML and caching."""
    def __init__(self, ml_model, cache, config):
        self.model = ml_model
        self.cache = cache
        self.config = config

    def detect(self, text: str) -> List[Mention]:
        # 200 lines of complex logic
```

**With DDD**:
```python
def detect_mentions(text: str) -> List[str]:
    """Extract @mentions from text."""
    return re.findall(r'@(\w+)', text)
```

### 3. Delivers Working Software
**Key insight**: Working software beats perfect plans.

A simple, working demo:
- Validates assumptions
- Gets feedback
- Creates momentum
- Proves feasibility

### 4. Creates Momentum
**Psychological benefit**: Seeing something work is energizing.

**Team benefit**: "We shipped!" builds confidence.

### 5. Validates Assumptions Early
**Example from Message Agent**:
- Assumption: "We need complex thread tree handling"
- Demo revealed: "Client can handle thread context"
- Result: Saved hours of unnecessary work

## Risks and Mitigation

### Risk 1: Technical Debt
**Problem**: Rushing can create messy code.

**Mitigation**:
- ✅ Still write tests
- ✅ Still maintain code quality
- ✅ Document deferred work
- ✅ Plan refactoring after demo

### Risk 2: Skipping Important Features
**Problem**: Deferred features may be critical.

**Mitigation**:
- ✅ Validate MVP with stakeholders
- ✅ Distinguish "nice to have" from "must have"
- ✅ Test core functionality thoroughly
- ✅ Have a backup plan

### Risk 3: Pressure Reduces Quality
**Problem**: Time pressure can lead to shortcuts.

**Mitigation**:
- ✅ Define quality non-negotiables upfront
- ✅ Build in buffer time
- ✅ Pair program for critical sections
- ✅ Review code before demo

## Related

- [@.claude/patterns/demo-driven-development-practices.md](./demo-driven-development-practices.md) - Best practices and guidelines
- [@.claude/patterns/demo-driven-development.md](./demo-driven-development.md) - Complete guide
- [@.claude/patterns/testing-strategy.md](./testing-strategy.md) - Testing approach
- [@.claude/architecture/vision-driven-development.md](../architecture/vision-driven-development.md) - Development philosophy

---

**Remember**: Demo-driven development is about focus, not shortcuts! 🎯✨

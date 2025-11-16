# Demo-Driven Development

**Category**: Development Process
**Complexity**: Low
**Impact**: High
**Related**: [Testing Strategy](./testing-strategy.md), [Vision-Driven Development](../architecture/vision-driven-development.md)

---

## Concept

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
- ✅ Set realistic deadlines
- ✅ Maintain non-negotiables (tests, clean code)
- ✅ Take breaks to avoid burnout
- ✅ Ask for help when stuck

### Risk 4: Demo-Specific Code
**Problem**: Code that only works for the demo.

**Mitigation**:
- ✅ Build real functionality, not fake demos
- ✅ Use real data (or realistic test data)
- ✅ Test actual use cases
- ✅ Avoid hardcoding demo-specific values

## Best Practices

### 1. Start with the End in Mind
**Question**: "What does success look like?"

**Example**:
```
Demo Success Criteria:
1. Show message with @mention
2. System detects mention
3. Routes to correct queue
4. Logs the action
5. Handles edge cases (no mention, unknown mention)
```

### 2. Build Vertically, Not Horizontally
**Bad (horizontal)**: Build all tools, then all workflows, then all tests
**Good (vertical)**: Build one complete feature at a time

**Example**:
```
✅ Vertical Slice 1: Basic mention detection
  - Tool: DetectMentions
  - Test: test_detect_mentions
  - Demo: Show it working

✅ Vertical Slice 2: Queue resolution
  - Tool: ResolveQueue
  - Test: test_resolve_queue
  - Demo: Show routing

✅ Vertical Slice 3: Full workflow
  - Workflow: MessageRouting
  - Test: test_routing_workflow
  - Demo: End-to-end scenario
```

### 3. Test As You Go
**Don't wait** until the end to write tests.

**Pattern**:
1. Write tool
2. Write test
3. Verify it works
4. Move to next tool

**Result**: Always have working, tested code.

### 4. Keep It Simple
**YAGNI**: You Aren't Gonna Need It (yet)

**Example**:
```python
# Simple (for demo)
def resolve_queue(mention: str) -> str:
    if mention.endswith('-assistant'):
        return mention
    return 'default-assistant'

# Complex (defer until needed)
def resolve_queue(mention: str, workspace: str, config: Dict) -> QueueConfig:
    # Load configuration
    # Check permissions
    # Validate workspace
    # Apply routing rules
    # Handle fallbacks
    # Log decisions
    # Return complex object
```

### 5. Document Decisions
**Keep a log** of what you decided and why.

**Example**:
```markdown
## Design Decisions

### Thread Tree Handling
**Decision**: Defer to client-side
**Reason**: Client has context, reduces server complexity
**Impact**: Simpler server implementation
**Revisit**: If client struggles with thread management

### Profile Lookup
**Decision**: Defer until database schema ready
**Reason**: Schema not finalized, would be wasted work
**Impact**: Use simple queue name matching for now
**Revisit**: When profiles table is ready
```

## When to Use

### ✅ Use Demo-Driven Development When:
- Validating ideas quickly
- Stakeholder presentations
- Proof of concepts
- Time-boxed experiments
- Need to build momentum
- Requirements are unclear

### ❌ Don't Use When:
- Building critical infrastructure
- Security is paramount
- No room for iteration
- Requirements are crystal clear
- No time pressure

## Comparison with Other Approaches

### vs. Test-Driven Development (TDD)
**TDD**: Write tests first, then implementation
**DDD**: Write implementation and tests together, prioritize for demo

**Compatibility**: DDD and TDD work well together!

### vs. Agile/Scrum
**Agile**: Iterative development with sprints
**DDD**: Single iteration focused on demo

**Compatibility**: DDD is like a mini-sprint with a demo as the goal.

### vs. Waterfall
**Waterfall**: Plan everything, then build everything
**DDD**: Plan minimum, build iteratively, demo quickly

**Difference**: DDD embraces change and feedback.

## Measuring Success

### Quantitative Metrics
- ✅ Demo completed on time
- ✅ All core features working
- ✅ Test coverage > 70%
- ✅ No critical bugs

### Qualitative Metrics
- ✅ Stakeholders satisfied
- ✅ Assumptions validated
- ✅ Team confident
- ✅ Code maintainable

### From Message Agent
- ✅ Demo ready in 2 hours
- ✅ 39 tests, all passing
- ✅ Clean, documented code
- ✅ Stakeholder impressed
- ✅ Ready to iterate

## After the Demo

### 1. Gather Feedback
**Questions**:
- What worked well?
- What was confusing?
- What's missing?
- What should we prioritize?

### 2. Review Deferred Work
**Prioritize** based on feedback:
- What's now critical?
- What can still wait?
- What's no longer needed?

### 3. Refactor and Improve
**Now that it works**, make it better:
- Improve test coverage
- Refactor messy code
- Add deferred features
- Optimize performance

### 4. Document Learnings
**Capture** what you learned:
- What worked?
- What didn't?
- What would you do differently?
- What patterns emerged?

## Real Results

### Message Agent Demo
**Time**: 2 hours
**Features**: 3 tools, 1 workflow, 5 test scenarios
**Tests**: 39 (all passing)
**Bugs Fixed**: 4 (serialization, API compatibility, regex, pgmq)
**Outcome**: ✅ Successful demo, ready to iterate

**Key Insight**: By focusing on the demo, we:
- Avoided over-engineering thread trees
- Deferred profile lookup until needed
- Built exactly what was necessary
- Maintained quality throughout

## Related Patterns

- **[Testing Strategy](./testing-strategy.md)**: How to test efficiently
- **[Vision-Driven Development](../architecture/vision-driven-development.md)**: Long-term vision vs. short-term demos
- **[Composable Tools](./composable-tools.md)**: Building flexible, reusable components

## Further Reading

- [The Lean Startup](https://theleanstartup.com/): Build-Measure-Learn
- [Getting Real](https://basecamp.com/gettingreal): Build less, launch sooner
- [Shape Up](https://basecamp.com/shapeup): Fixed time, variable scope
- [Agile Manifesto](https://agilemanifesto.org/): Working software over comprehensive documentation

---

**Key Takeaway**: A demo deadline is a superpower. It forces focus, prevents over-engineering, and delivers working software. Use it wisely! 🚀✨

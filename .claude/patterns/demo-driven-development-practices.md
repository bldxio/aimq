# Demo-Driven Development: Best Practices

Best practices, guidelines, and lessons learned from demo-driven development.

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

## Design Decisions Template

Use this template to document decisions during demo development:

```markdown
## Design Decisions

### [Feature Name]
**Decision**: [What you decided]
**Reason**: [Why you decided this]
**Impact**: [What this means for the project]
**Revisit**: [When to reconsider this decision]
**Alternatives Considered**: [What else you thought about]
```

## Demo Checklist

### Before Demo
- [ ] Define success criteria
- [ ] Identify MVP features
- [ ] Set realistic timeline
- [ ] Prepare test scenarios
- [ ] Document deferred work

### During Development
- [ ] Build vertically (one feature at a time)
- [ ] Write tests as you go
- [ ] Keep code clean and simple
- [ ] Document key decisions
- [ ] Test frequently

### Before Presenting
- [ ] All core features working
- [ ] Tests passing
- [ ] No critical bugs
- [ ] Demo script prepared
- [ ] Backup plan ready

### After Demo
- [ ] Gather feedback
- [ ] Review deferred work
- [ ] Plan next iteration
- [ ] Document learnings
- [ ] Celebrate success! 🎉

## Related

- [@.claude/patterns/demo-driven-development-core.md](./demo-driven-development-core.md) - Core concepts and philosophy
- [@.claude/patterns/demo-driven-development.md](./demo-driven-development.md) - Complete guide
- [@.claude/patterns/testing-strategy.md](./testing-strategy.md) - Testing approach
- [@.claude/architecture/vision-driven-development.md](../architecture/vision-driven-development.md) - Development philosophy
- [@.claude/patterns/composable-tools.md](./composable-tools.md) - Building flexible components

## Further Reading

- [The Lean Startup](https://theleanstartup.com/) - Build-Measure-Learn
- [Getting Real](https://basecamp.com/gettingreal) - Build less, launch sooner
- [Shape Up](https://basecamp.com/shapeup) - Fixed time, variable scope
- [Agile Manifesto](https://agilemanifesto.org/) - Working software over comprehensive documentation

---

**Key Takeaway**: A demo deadline is a superpower. It forces focus, prevents over-engineering, and delivers working software. Use it wisely! 🚀✨

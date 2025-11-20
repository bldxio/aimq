# Demo-Driven Development

Use an upcoming demo as a focusing constraint to deliver working software quickly while maintaining quality.

## Overview

Demo-Driven Development (DDD) is about **ruthless prioritization** with a concrete goal. It's not about cutting corners—it's about focusing on what matters most.

This guide is split into focused topics:

- **[Demo-Driven Development Core](./demo-driven-development-core.md)** - Philosophy, process, real-world examples, benefits, and risks
- **[Demo-Driven Development Practices](./demo-driven-development-practices.md)** - Best practices, guidelines, measuring success, and after-demo steps

## Quick Reference

### The Philosophy
> "A demo deadline is a forcing function that cuts through analysis paralysis and over-engineering. It forces you to answer: What MUST work? What CAN wait?"

### The Process
1. **Set a Deadline** - Specific, realistic, immovable
2. **Define MVP** - What must work for demo success?
3. **Build Iteratively** - Working → Correct → Clean → Tested
4. **Maintain Quality** - Tests, clean code, documentation
5. **Document Deferred Work** - Track what can wait

### Non-Negotiables
- ✅ Write tests (even if not 100% coverage)
- ✅ Clean, readable code
- ✅ Basic documentation
- ✅ No known critical bugs

### Can Compromise On
- ⏸️ Perfect test coverage
- ⏸️ Comprehensive documentation
- ⏸️ Edge case handling
- ⏸️ Performance optimization

## Getting Started

### 1. Learn the Core Concepts
Start with [@.claude/patterns/demo-driven-development-core.md](./demo-driven-development-core.md) to understand:
- The philosophy and benefits
- The 5-step process
- Real-world example (Message Agent)
- Risks and mitigation strategies

### 2. Follow Best Practices
See [@.claude/patterns/demo-driven-development-practices.md](./demo-driven-development-practices.md) for:
- Best practices (vertical slicing, YAGNI, etc.)
- When to use (and when not to)
- Measuring success
- After-demo steps
- Demo checklist

## Common Use Cases

### Quick Proof of Concept
```
Timeline: 2 hours
Goal: Validate idea works
Focus: Core functionality only
Defer: Edge cases, optimization
```

### Stakeholder Demo
```
Timeline: 1 day
Goal: Show progress and get feedback
Focus: Key features working end-to-end
Defer: Polish, advanced features
```

### Sprint Demo
```
Timeline: 1 week
Goal: Deliver working increment
Focus: Complete vertical slices
Defer: Nice-to-haves, future features
```

## Real Results

### Message Agent (2-hour demo)
- ✅ 3 tools, 1 workflow, 5 test scenarios
- ✅ 39 tests (all passing)
- ✅ Clean, documented code
- ✅ 4 bugs fixed during development
- ✅ Successful demo, ready to iterate

**Key Insight**: Focusing on the demo helped us avoid over-engineering and build exactly what was necessary.

## Related

- [@.claude/patterns/testing-strategy.md](./testing-strategy.md) - Testing approach
- [@.claude/architecture/vision-driven-development.md](../architecture/vision-driven-development.md) - Development philosophy
- [@.claude/patterns/composable-tools.md](./composable-tools.md) - Building flexible components
- [@.claude/patterns/error-handling.md](./error-handling.md) - Error handling patterns

---

**Key Takeaway**: A demo deadline is a superpower. It forces focus, prevents over-engineering, and delivers working software. Use it wisely! 🚀✨

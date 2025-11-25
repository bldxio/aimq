# 🌱 Knowledge Garden Guide

> **A living, breathing knowledge system that grows with every lesson learned.**

Welcome to the knowledge garden! This guide will help you (human or agent) cultivate, maintain, and benefit from our shared knowledge system.

---

## Our Collaboration Framework

We work together through four interconnected systems:

```
CONSTITUTION.md    →    VISION.md         →    GARDENING.md      →    PLAN.md
Core Principles         The Dream              Long-term Memory       Working Memory
(Who we are)            (Where we're going)    (What we know)         (What we're doing)
```

**CONSTITUTION.md** - Our unchanging values and guiding principles
**VISION.md** - Our aspirational future, the north star that guides us
**Knowledge Garden** - Our accumulated wisdom, patterns, and lessons
**PLAN.md** - Our current state, progress, and next steps

Together, these form our **contracts for collaboration** - a shared understanding that helps us work as one unified force.

---

## What Is the Knowledge Garden?

The knowledge garden is our **long-term memory** - a curated collection of patterns, standards, architecture decisions, and practical guides that capture what we've learned. It lives in `.claude/` and grows with every project milestone.

**Why "garden"?** Because knowledge, like a garden:
- 🌱 Grows organically from experience
- 🌿 Needs regular tending to stay healthy
- 🌳 Becomes more valuable over time
- 🌸 Blooms when well-maintained
- 🥀 Withers when neglected

---

## Garden Structure

```
.claude/
├── patterns/           # Reusable solutions to common problems
├── standards/          # Team conventions and best practices
├── architecture/       # System design and decisions
├── quick-references/   # How-to guides and checklists
└── commands/           # Helper commands for workflows

ideas/                  # Human-AI interface for future features
└── *.md                # Feature explorations and planning
```

### What Goes Where?

**Patterns** - "How do we solve X?"
- Code patterns that work
- Design patterns we use
- Implementation approaches
- Problem-solving techniques

**Standards** - "How do we do things?"
- Coding conventions
- Testing practices
- Git workflow
- Documentation style
- Code review guidelines

**Architecture** - "Why did we build it this way?"
- Design decisions (ADRs)
- Technology choices
- System structure
- Integration patterns
- Trade-offs we accepted

**Quick References** - "How do I...?"
- Setup guides
- Common tasks
- Troubleshooting
- Checklists
- Debugging tips

**Ideas** - "What could we build?" (Root level - Human-AI interface)
- Feature explorations
- Future work planning
- Architectural experiments
- Research and brainstorming
- Sprint planning documents

---

## The Gardening Commands

These commands help you cultivate the knowledge garden and manage our working memory:

### 🧠 `/remember` - Capture Insights

**When to use**: After solving a problem or discovering a pattern

**Without args**: Analyzes conversation for patterns worth recording
```
/remember
```

**With args**: Records specific insight
```
/remember always mock external dependencies in tests for reliability
```

**Example workflow**:
```
You: We just fixed that worker crash by catching exceptions
Agent: /remember
Agent: Found pattern: Graceful error handling in workers
        Should I add to .claude/patterns/?
You: Yes!
```

### 📚 `/learn` - Extract Lessons

**When to use**: After completing work or fixing issues

**Without args**: Analyzes conversation + git history for lessons
```
/learn
```

**With args**: Focuses on specific area
```
/learn what went wrong with error handling
```

**Example workflow**:
```
Agent: /learn
Agent: Found 3 lessons from recent commits:
       1. Workers should never crash on job errors
       2. Mock external services for reliable tests
       3. Split large modules by domain
       Should I add these to the knowledge garden?
You: Yes, all three!
```

### 🔍 `/focus` - Explore Topics

**When to use**: When you need to understand existing patterns

**Without args**: Identifies topics from conversation and explores them
```
/focus
```

**With args**: Deep dives into specific topic
```
/focus error handling patterns
```

**Example workflow**:
```
You: How should we handle errors in workers?
Agent: /focus error handling
Agent: Found in knowledge garden:
       - Pattern: Graceful error handling
       - Standard: Error logging with context
       - Architecture: Worker resilience design
       Want me to show the details?
```

### 🚀 `/levelup` - Research & Add

**When to use**: When you need to learn something new

**Without args**: Identifies topics to research from conversation
```
/levelup
```

**With args**: Researches specific topic
```
/levelup circuit breaker pattern
```

**Example workflow**:
```
You: Should we use a circuit breaker for API calls?
Agent: /levelup circuit breaker pattern
Agent: [Researches online]
Agent: Here's what I learned... [summary]
       This would help with resilience. Add to garden?
You: Yes!
```

### 📋 `/plan` - Manage Working Memory

**When to use**: To review progress or plan next steps

**Without args**: Reviews PLAN.md and git history to suggest next steps
```
/plan
```

**With args**: Creates or updates plans with provided goals
```
/plan add streaming support for agent responses
```

**Example workflow**:
```
Agent: /plan
Agent: Reviewing PLAN.md and recent commits...

       Completed but not marked:
       - ✅ Added 40 new tests
       - ✅ Achieved 82% coverage

       Suggested next steps:
       1. Add tests for tools/ (0% coverage)
       2. Improve worker coverage to 90%

       Should I update PLAN.md?
You: Yes, and let's tackle option 1!
```

### 🌱 `/cultivate` - Maintain & Organize

**When to use**: Regularly (weekly or after major changes)

**What it does**: Comprehensive garden maintenance
- Organizes content
- Verifies patterns match code
- Creates links between topics
- Splits large files
- Removes outdated content
- Keeps everything discoverable

```
/cultivate
```

**Example workflow**:
```
Agent: /cultivate
Agent: Found issues:
       - testing.md is 450 lines (should split)
       - retry-logic.md doesn't match code
       - 8 files missing links
       Should I fix these?
You: Yes, let's keep it healthy!
```

---

## Daily Gardening Practices

### 🌅 During Development

**When you solve a problem**:
```
/remember [the solution]
```

**When you discover a pattern**:
```
/remember [the pattern]
```

**When you need guidance**:
```
/focus [topic]
```

### 🌆 After Completing Work

**Extract lessons learned**:
```
/learn
```

**Update working memory**:
```
/plan
```
Reviews what's done and suggests next steps

### 🌙 Weekly Maintenance

**Tend the garden**:
```
/cultivate
```

**Research new topics**:
```
/levelup [topic you want to learn]
```

---

## Best Practices

### 1. Capture While Fresh 🎯
Don't wait! Record insights when they're fresh in your mind. Future you will thank present you.

### 2. Keep It Concise 📝
- Files under 400 lines
- One topic per file
- Show code, not just prose
- Link to details instead of including everything

### 3. Verify Regularly ✅
The garden should reflect reality:
- Patterns should match actual code
- Standards should be followed
- Architecture docs should be current
- Remove what's no longer true

### 4. Link Everything 🕸️
Build a knowledge graph:
- Add "Related" sections
- Reference other patterns
- Connect standards to patterns
- Create index files

### 5. Make It Discoverable 🔍
- Use clear file names
- Add descriptions
- Organize logically
- Keep structure shallow

### 6. Tend Regularly 🌱
A healthy garden needs regular care:
- Review weekly
- Update when things change
- Remove dead content
- Split overgrown files

---

## Quick Start Examples

### Example 1: After Fixing a Bug

```
You: Just fixed the worker crash - we weren't catching exceptions
Agent: /remember
Agent: Pattern found: Graceful error handling in workers
        - Catch exceptions in worker loop
        - Log errors with context
        - Keep worker running
        Add to .claude/patterns/graceful-error-handling.md?
You: Yes!
Agent: ✅ Added! Also linked to error-logging.md and worker-design.md
```

### Example 2: Before Implementing a Feature

```
You: We need to add retry logic for API calls
Agent: /focus retry patterns
Agent: Found in garden:
       📁 patterns/retry-logic.md
       - Use exponential backoff
       - Set max retry limits
       - Example: [shows code]
       This matches what we need!
You: Perfect, let's use that pattern
```

### Example 3: Learning Something New

```
You: I keep hearing about circuit breakers, should we use one?
Agent: /levelup circuit breaker pattern
Agent: [Researches]
Agent: Circuit breakers prevent cascading failures by stopping
       requests to failing services. Great for external APIs!

       Pros: Fast failure, prevents cascading
       Cons: Adds complexity, needs tuning

       Recommendation: Yes, for our Supabase/Mistral calls
       Add to knowledge garden?
You: Yes, and let's implement it!
```

### Example 4: Weekly Maintenance

```
Agent: /cultivate
Agent: Garden health check:
       ✅ 23 files, average 180 lines
       ⚠️ testing.md is 450 lines (should split)
       ✅ All patterns match code
       ⚠️ 8 files missing links

       Should I:
       1. Split testing.md into focused files
       2. Add links between related content
You: Yes to both!
Agent: ✅ Done! Garden is healthy 🌱
```

---

## The Garden Lifecycle

```
                    ┌─── CONSTITUTION.md ───┐
                    │   (Core Principles)    │
                    └───────────┬────────────┘
                                ↓
Experience → Remember → Learn → Garden (Long-term Memory)
    ↑                              ↓
    │                          Focus/Level Up
    │                              ↓
    └────── Apply ←──── Plan (Working Memory)
```

1. **Experience**: Work on the project, solve problems
2. **Remember**: Capture insights and patterns (`/remember`)
3. **Learn**: Extract lessons from history (`/learn`)
4. **Garden**: Maintain and organize long-term memory (`/cultivate`)
5. **Focus/Level Up**: Explore and expand knowledge (`/focus`, `/levelup`)
6. **Plan**: Update working memory and next steps (`/plan`)
7. **Apply**: Use knowledge in new work (guided by CONSTITUTION)
8. **Repeat**: The cycle continues!

**The flow**:
- **CONSTITUTION** guides everything (unchanging principles)
- **Garden** stores what we learn (long-term memory)
- **PLAN** tracks what we're doing (working memory)
- **Experience** feeds back into the system

---

## Why This Matters

### For Humans 👤
- **Onboarding**: New team members learn patterns quickly
- **Consistency**: Everyone follows the same standards
- **Memory**: Don't lose knowledge when people leave
- **Decisions**: Understand why things are the way they are
- **Velocity**: Solve problems faster with proven patterns

### For Agents 🤖
- **Context**: Understand project conventions and patterns
- **Guidance**: Follow established standards
- **Learning**: Improve suggestions based on what works
- **Consistency**: Generate code that matches project style
- **Collaboration**: Share a common understanding with humans

### For the Project 🚀
- **Quality**: Consistent patterns lead to better code
- **Maintainability**: Well-documented decisions are easier to change
- **Velocity**: Less time debating, more time building
- **Knowledge**: Institutional memory that grows over time
- **Culture**: Shared understanding builds better teams

---

## Tips for Success

### ✅ Do This
- Capture insights while they're fresh
- Update when patterns change
- Link related content
- Keep files focused and concise
- Verify against actual code
- Tend the garden regularly

### ❌ Avoid This
- Waiting to document "later"
- Letting files grow too large
- Documenting what you wish, not what is
- Copying everything from the internet
- Letting the garden grow wild
- Forgetting to maintain it

---

## Remember

> **The best time to plant a tree was 20 years ago. The second best time is now.**

Every pattern captured, every lesson learned, every insight recorded makes the garden more valuable. Start small, tend regularly, and watch it grow! 🌱

The knowledge garden is **our shared memory** - let's cultivate it together! 🌿✨

---

**Next Steps**:
- Read CONSTITUTION.md to understand our core principles
- Start using `/remember` when you solve problems
- Run `/learn` after completing work
- Use `/plan` to track progress and next steps
- Use `/focus` when you need guidance
- Try `/levelup` to research new topics
- Run `/cultivate` weekly to keep it healthy

**Remember the hierarchy**:
```
CONSTITUTION (who we are)
    ↓
VISION (where we're going)
    ↓
GARDEN (what we know)
    ↓
PLAN (what we're doing)
```

Happy gardening! 🌱🌸🌳

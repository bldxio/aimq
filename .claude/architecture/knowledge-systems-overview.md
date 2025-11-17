# Knowledge Systems Overview

A structured approach to capturing, organizing, and evolving project knowledge. Think of it as a "second brain" for your project that grows with every lesson learned.

## The Problem

Without a knowledge system:
- Lessons are forgotten
- Mistakes are repeated
- Context is lost
- Onboarding is hard
- Decisions are unclear
- Patterns aren't reused

## The Solution

Create a **knowledge garden** that:
- Captures lessons as they're learned
- Organizes knowledge by type
- Links related concepts
- Evolves with the project
- Stays small and focused

## The Knowledge Hierarchy

```
CONSTITUTION.md  → Who we are
    ↓
VISION.md        → Where we're going
    ↓
.claude/         → What we know
    ↓
PLAN.md          → What we're doing
```

Each level serves a purpose:

### CONSTITUTION.md

**Purpose**: Guiding principles and non-negotiables

**Contains**:
- Core values
- Team principles
- Non-negotiables
- Decision framework

**Updates**: Rarely (only when strong patterns emerge)

**Example**:
```markdown
# Constitution

## Core Values

1. **Stability over features**
   - Workers never crash on job errors
   - Test before shipping
   - Graceful degradation

2. **Clarity over cleverness**
   - Simple code beats clever code
   - Explicit is better than implicit
   - Document the why, not the what
```

### VISION.md

**Purpose**: Long-term direction and goals

**Contains**:
- Product vision
- Core capabilities
- Technical architecture
- Future possibilities

**Updates**: Monthly (as product evolves)

**Example**:
```markdown
# Vision: Multi-Agent Group Chat

## The Dream
A collaborative AI system where multiple agents work together...

## Core Capabilities
1. Multi-agent conversations
2. Intelligent routing
3. Shared memory
```

### .claude/ (Knowledge Garden)

**Purpose**: Reusable knowledge and patterns

**Structure**:
```
.claude/
├── patterns/           # Reusable solutions
├── standards/          # Team conventions
├── architecture/       # System design
├── quick-references/   # How-to guides
└── commands/           # Helper commands
```

**Updates**: Continuously (as you learn)

### PLAN.md

**Purpose**: Current work and next steps

**Contains**:
- Current status
- Completed work
- Next steps
- Open questions

**Updates**: Daily/weekly (as work progresses)

## Core Values

### 1. Living Documentation
Knowledge evolves with the project. Update docs as you learn, not as an afterthought.

### 2. Small and Focused
Keep files under 400 lines. Split large files into focused topics.

### 3. Linked Knowledge
Build a knowledge graph, not a tree. Cross-link related topics.

### 4. Shallow Structure
No nested directories. Just markdown files in each folder.

### 5. Continuous Cultivation
Regular maintenance keeps the garden healthy. Use `/cultivate` weekly.

## The Dream

A knowledge system where:
- New team members onboard in hours, not weeks
- Lessons learned are never forgotten
- Patterns are reused automatically
- Decisions are documented and traceable
- Knowledge compounds over time

## Related

- [@.claude/architecture/knowledge-systems-templates.md](./knowledge-systems-templates.md) - File templates
- [@.claude/architecture/knowledge-systems-workflow.md](./knowledge-systems-workflow.md) - Gardening workflow
- [@.claude/architecture/knowledge-systems.md](./knowledge-systems.md) - Complete guide
- [@GARDENING.md](../../GARDENING.md) - Gardening philosophy and guidelines

---

**Remember**: A knowledge system is a garden—it grows with care and attention! 🌱✨

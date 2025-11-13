# Knowledge Systems

## Overview

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

## Knowledge Garden Structure

### patterns/

**Purpose**: Reusable solutions to common problems

**Examples**:
- `error-handling.md` - How to handle errors
- `testing-strategy.md` - How to test effectively
- `module-organization.md` - How to organize code
- `queue-error-handling.md` - Queue-specific patterns
- `worker-error-handling.md` - Worker-specific patterns

**Format**:
```markdown
# Pattern Name

## Problem
What problem does this solve?

## Solution
How do we solve it?

## Example
Show concrete code

## When to Use
When is this appropriate?

## When Not to Use
When should you avoid this?

## Related
Links to related patterns
```

### standards/

**Purpose**: Team conventions and best practices

**Examples**:
- `code-style.md` - Coding conventions
- `testing.md` - Testing standards
- `git-workflow.md` - Git conventions
- `conventional-commits.md` - Commit message format

**Format**:
```markdown
# Standard Name

## Overview
What is this standard?

## Rules
- Rule 1
- Rule 2
- Rule 3

## Examples
Good and bad examples

## Rationale
Why do we do this?

## Exceptions
When can we break this rule?
```

### architecture/

**Purpose**: System design and decisions

**Examples**:
- `aimq-overview.md` - System architecture
- `langchain-integration.md` - LangChain usage
- `langgraph-integration.md` - LangGraph usage
- `vision-driven-development.md` - Development approach
- `knowledge-systems.md` - This document!

**Format**:
```markdown
# Architecture Topic

## Overview
High-level description

## Components
What are the parts?

## Interactions
How do they work together?

## Decisions
Why did we choose this?

## Trade-offs
What did we give up?

## Future
Where might this go?
```

### quick-references/

**Purpose**: How-to guides and checklists

**Examples**:
- `common-tasks.md` - Frequent operations
- `testing.md` - How to run tests
- `linting.md` - How to lint
- `git-commands.md` - Git cheatsheet
- `dependency-management.md` - Managing dependencies

**Format**:
```markdown
# Quick Reference: Topic

## Common Tasks

### Task 1
```bash
command here
```

### Task 2
```bash
another command
```

## Troubleshooting

### Problem 1
Solution here

### Problem 2
Solution here
```

### commands/

**Purpose**: Helper commands for workflows

**Examples**:
- `/remember` - Capture insights
- `/learn` - Extract lessons
- `/focus` - Explore topics
- `/levelup` - Research new topics
- `/plan` - Review progress
- `/cultivate` - Maintain garden

**Format**:
```markdown
# Command Name

## Overview
What does this command do?

## Usage
How to use it

## Task List
Step-by-step process

## Examples
Real-world usage

## Related
Links to related commands
```

## Gardening Workflow

### 1. Capture (Daily)

As you work, capture insights:

```bash
# After solving a problem
/remember "Workers should catch all exceptions in the main loop"

# After learning something
/remember "Mock external services for reliable tests"

# After making a decision
/remember "Chose exponential backoff for retries because..."
```

### 2. Learn (Weekly)

Extract lessons from recent work:

```bash
# Review recent work
/learn

# Focus on specific area
/learn "focus on testing patterns"

# Learn from failures
/learn "what went wrong and how we fixed it"
```

### 3. Organize (Monthly)

Keep the garden healthy:

```bash
# Review and organize
/cultivate

# Check for duplicates
# Merge related content
# Remove outdated info
# Update links
```

### 4. Explore (As Needed)

Find relevant knowledge:

```bash
# Explore a topic
/focus "error handling"

# Research new topics
/levelup "LangGraph memory"

# Review progress
/plan
```

## Best Practices

### ✅ Do

- **Capture while fresh** - Don't wait
- **Keep files small** - Under 400 lines
- **Link everything** - Build a knowledge graph
- **Use examples** - Show, don't just tell
- **Update regularly** - Knowledge evolves
- **Prune aggressively** - Remove outdated content
- **Make it searchable** - Use clear headings

### ❌ Don't

- Don't wait to document
- Don't write novels (keep it concise)
- Don't duplicate content
- Don't use jargon without explanation
- Don't let it get stale
- Don't hoard outdated info
- Don't bury important info

## File Size Guidelines

Keep files focused and scannable:

- **Patterns**: 200-400 lines
- **Standards**: 100-300 lines
- **Architecture**: 300-500 lines
- **Quick References**: 100-200 lines
- **Commands**: 400-600 lines

If a file grows too large:
1. Split into multiple files
2. Create an index/README
3. Link related content

## Real-World Example

From our project:

**Before Knowledge System**:
- Lessons in chat history
- Patterns in code comments
- Decisions undocumented
- Context lost over time

**After Knowledge System**:
- 5 new pattern documents
- 4 standard documents
- 6 architecture documents
- 6 quick reference guides
- 10 helper commands

**Result**:
- Faster onboarding
- Fewer repeated mistakes
- Better decisions
- Clearer direction
- Shared understanding

## Measuring Success

### Quantitative

- Number of documents
- Lines of documentation
- Links between documents
- Update frequency
- Usage in conversations

### Qualitative

- Easier onboarding?
- Fewer repeated questions?
- Better decisions?
- More consistent code?
- Faster problem solving?

## Evolution

### Phase 1: Bootstrap (Week 1)

Create initial structure:
- CONSTITUTION.md
- VISION.md
- .claude/ folders
- PLAN.md
- README updates

### Phase 2: Populate (Month 1)

Add core knowledge:
- Key patterns
- Essential standards
- Architecture docs
- Quick references

### Phase 3: Refine (Month 2-3)

Improve quality:
- Add examples
- Link content
- Remove duplicates
- Update outdated info

### Phase 4: Maintain (Ongoing)

Keep it healthy:
- Weekly reviews
- Monthly cultivation
- Continuous updates
- Regular pruning

## Tools and Commands

### Helper Commands

Use these to manage the garden:

- `/remember` - Capture insights
- `/learn` - Extract lessons
- `/focus` - Explore topics
- `/levelup` - Research new topics
- `/plan` - Review progress
- `/cultivate` - Maintain garden

### File Operations

```bash
# Find files
fd pattern .claude/

# Search content
rg "search term" .claude/

# Count files
fd . .claude/ | wc -l

# Check file sizes
fd . .claude/ -x wc -l
```

## Related

- [Vision-Driven Development](./vision-driven-development.md) - Development approach
- [GARDENING.md](../../GARDENING.md) - Gardening guide
- [CONSTITUTION.md](../../CONSTITUTION.md) - Guiding principles
- [VISION.md](../../VISION.md) - Project vision

---

**Remember**: A knowledge garden is never finished, it's always growing! 🌱✨

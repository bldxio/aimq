# Knowledge Systems Templates

Standard templates for different types of knowledge files.

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

## File Size Guidelines

Keep files focused and scannable:

- **Patterns**: 200-400 lines
- **Standards**: 100-300 lines
- **Architecture**: 300-500 lines
- **Quick References**: 100-200 lines
- **Commands**: 50-100 lines (after refactoring)

If a file grows too large:
1. Split into multiple files
2. Create an index/README
3. Link related content

## Template Usage

### Creating a New Pattern

1. Copy the pattern template
2. Fill in each section
3. Add concrete examples
4. Link to related patterns
5. Place in `.claude/patterns/`

### Creating a New Standard

1. Copy the standard template
2. Define clear rules
3. Show good/bad examples
4. Explain the rationale
5. Place in `.claude/standards/`

### Creating a New Architecture Doc

1. Copy the architecture template
2. Describe components
3. Explain interactions
4. Document decisions
5. Place in `.claude/architecture/`

### Creating a New Quick Reference

1. Copy the quick reference template
2. List common tasks
3. Add troubleshooting
4. Keep it concise
5. Place in `.claude/quick-references/`

## Related

- [@.claude/architecture/knowledge-systems-overview.md](./knowledge-systems-overview.md) - Philosophy and hierarchy
- [@.claude/architecture/knowledge-systems-workflow.md](./knowledge-systems-workflow.md) - Gardening workflow
- [@.claude/architecture/knowledge-systems.md](./knowledge-systems.md) - Complete guide
- [@GARDENING.md](../../GARDENING.md) - Gardening guidelines

---

**Remember**: Templates are starting points—adapt them to your needs! 📝✨

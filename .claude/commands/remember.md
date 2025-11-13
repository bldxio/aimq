---
description: Record patterns and lessons in the knowledge garden
---

# Remember Helper

Capture patterns, lessons, and insights in the knowledge garden for future reference.

## Overview

This command helps build institutional knowledge by:
1. Identifying patterns from recent conversations
2. Recording lessons learned
3. Documenting best practices
4. Adding to the knowledge garden
5. Suggesting constitutional updates for critical insights

## Usage

### Without Arguments
```
/remember
```
Analyzes recent conversation for patterns and lessons to record.

### With Arguments
```
/remember <insight or pattern>
```
Records the specified insight in the appropriate place in the knowledge garden.

## Task List

### Mode 1: Extract from Conversation (No Arguments)

When called without arguments, analyze the recent conversation:

#### Step 1: Review Conversation

Look back through recent messages for:

**Patterns discovered**:
- Repeated solutions
- Common approaches
- Consistent decisions
- Emerging conventions

**Lessons learned**:
- What worked well
- What didn't work
- Mistakes made
- Better approaches found

**Decisions made**:
- Architecture choices
- Technology selections
- Design patterns adopted
- Trade-offs accepted

**Insights gained**:
- Understanding of the codebase
- Project-specific quirks
- Team preferences
- Domain knowledge

#### Step 2: Categorize Insights

Determine where each insight belongs:

**Patterns** (`.claude/patterns/`):
- Reusable code patterns
- Design patterns
- Architecture patterns
- Problem-solving approaches

**Standards** (`.claude/standards/`):
- Coding conventions
- Testing practices
- Documentation style
- Git workflow
- Code review guidelines

**Architecture** (`.claude/architecture/`):
- System design decisions
- Technology choices
- Integration patterns
- Data flow
- Component relationships

**Quick References** (`.claude/quick-references/`):
- Common tasks
- Troubleshooting guides
- Setup instructions
- Checklists

#### Step 3: Draft the Content

For each insight, create clear documentation:

**Pattern format**:
```markdown
# [Pattern Name]

## Problem
[What problem does this solve?]

## Solution
[How do we solve it?]

## Example
[Code or concrete example]

## When to Use
[Appropriate situations]

## When Not to Use
[Inappropriate situations]

## Related
- [Link to related patterns]
```

**Standard format**:
```markdown
# [Standard Name]

## Guideline
[Clear statement of the standard]

## Rationale
[Why we follow this standard]

## Examples

### Good ✅
[Example of following the standard]

### Bad ❌
[Example of violating the standard]

## Exceptions
[When it's okay to break this rule]
```

#### Step 4: Present for Review

Show what you want to remember:

```
🧠 I noticed some patterns worth remembering:

**1. Error Handling Pattern**
- Location: .claude/patterns/error-handling.md
- What: Always use graceful error handling in workers
- Why: Keeps the process stable even when jobs fail
- Example: [Show code snippet]

**2. Testing Standard**
- Location: .claude/standards/testing.md
- What: Mock external dependencies in tests
- Why: Tests should be fast and reliable
- Example: [Show test pattern]

**3. Architecture Decision**
- Location: .claude/architecture/worker-design.md
- What: Worker doesn't re-raise exceptions
- Why: Prevents process crashes, logs errors instead
- Trade-off: Errors don't propagate, must check logs

Should I add these to the knowledge garden?
```

#### Step 5: Check for Constitutional Items

Evaluate if any insights are fundamental enough for CONSTITUTION.md:

**Constitutional criteria**:
- Core values or principles
- Non-negotiable standards
- Project philosophy
- Team culture
- Critical decisions

**Ask if unsure**:
```
🏛️ This seems really important:

"Always prioritize stability over features in production code"

This feels like a core principle. Should I:
1. Add to knowledge garden only
2. Add to CONSTITUTION.md as a guiding principle
3. Both

What do you think?
```

### Mode 2: Record Specific Insight (With Arguments)

When given specific content to remember:

#### Step 1: Parse the Input

Understand what's being recorded:
- Type of insight (pattern, standard, decision)
- Context and background
- Why it's important
- Where it should go

#### Step 2: Determine Location

Choose the right place in the knowledge garden:

**Decision tree**:
```
Is it a reusable code pattern?
  → .claude/patterns/

Is it a standard or best practice?
  → .claude/standards/

Is it an architecture decision?
  → .claude/architecture/

Is it a how-to or guide?
  → .claude/quick-references/

Is it a fundamental principle?
  → Ask about CONSTITUTION.md
```

#### Step 3: Check for Existing Content

Before creating new files:
```bash
# Search for related content
rg -i "keyword" .claude/

# List existing files in category
ls .claude/patterns/
ls .claude/standards/
```

**If related content exists**:
- Update existing file instead of creating new
- Add to existing document
- Link between related files

**If new content**:
- Create new file with clear name
- Follow category conventions
- Link to related content

#### Step 4: Format the Content

Write clear, actionable documentation:

**Keep it concise**:
- Under 400 lines per file
- Focus on essentials
- Link to details elsewhere

**Make it actionable**:
- Include examples
- Show code snippets
- Provide clear steps

**Link heavily**:
- Reference related patterns
- Link to standards
- Connect to architecture docs

#### Step 5: Update and Confirm

Add the content and report:

```
✅ Remembered! Added to knowledge garden:

**File**: .claude/patterns/graceful-error-handling.md

**Content**:
- Problem: Worker crashes on job errors
- Solution: Catch exceptions, log, continue
- Example: [Code snippet]
- Related: error-logging.md, worker-stability.md

**Links added**:
- Referenced in .claude/architecture/worker-design.md
- Added to .claude/quick-references/common-patterns.md

The knowledge garden grows! 🌱
```

## Knowledge Garden Structure

### Patterns Directory
**Purpose**: Reusable solutions to common problems

**Examples**:
- `error-handling.md` - How to handle errors
- `dependency-injection.md` - DI patterns
- `factory-pattern.md` - Factory implementations
- `observer-pattern.md` - Event handling

### Standards Directory
**Purpose**: Team conventions and best practices

**Examples**:
- `code-style.md` - Formatting and naming
- `testing.md` - Test writing guidelines
- `git-workflow.md` - Branching and commits
- `documentation.md` - Doc standards
- `code-review.md` - Review process

### Architecture Directory
**Purpose**: System design and decisions

**Examples**:
- `system-overview.md` - High-level architecture
- `data-flow.md` - How data moves
- `integration-points.md` - External systems
- `technology-choices.md` - Why we use X
- `design-decisions.md` - ADRs (Architecture Decision Records)

### Quick References Directory
**Purpose**: How-to guides and checklists

**Examples**:
- `setup-guide.md` - Getting started
- `common-tasks.md` - Frequent operations
- `troubleshooting.md` - Problem solving
- `deployment.md` - Release process
- `debugging.md` - Debug techniques

## Best Practices

### 1. Write for Future You
- Assume you'll forget the context
- Explain the "why" not just the "what"
- Include examples
- Link to related content

### 2. Keep It Fresh
- Update when patterns change
- Remove outdated content
- Consolidate similar items
- Verify accuracy regularly

### 3. Make It Discoverable
- Use clear file names
- Add descriptive headers
- Link between related docs
- Keep structure shallow

### 4. Stay Concise
- One topic per file
- Under 400 lines
- Split large topics
- Link to details

### 5. Show, Don't Just Tell
- Include code examples
- Show before/after
- Provide templates
- Give concrete cases

### 6. Link Everything
- Reference related patterns
- Connect to standards
- Link to architecture
- Build a knowledge graph

## Examples

### Example 1: Extract from Conversation

**Command**: `/remember`

**Output**:
```
🧠 Analyzing conversation for patterns...

**Found 3 insights worth remembering**:

1. **Testing Pattern**: Mock External Dependencies
   - We always mock Supabase, Mistral, etc. in tests
   - Keeps tests fast and reliable
   - Add to: .claude/patterns/testing-mocks.md

2. **Standard**: Graceful Error Handling
   - Workers should never crash on job errors
   - Log and continue processing
   - Add to: .claude/standards/error-handling.md

3. **Decision**: No Exception Re-raising in Workers
   - Trade-off: Stability over error propagation
   - Must check logs for errors
   - Add to: .claude/architecture/worker-design.md

Should I add these to the knowledge garden?
```

### Example 2: Record Specific Pattern

**Command**: `/remember always use type hints in Python functions for better IDE support and documentation`

**Output**:
```
📝 Recording in knowledge garden...

**Category**: Standard (coding convention)
**File**: .claude/standards/python-type-hints.md

**Content**:
# Python Type Hints

## Guideline
Always use type hints for function parameters and return values.

## Rationale
- Better IDE autocomplete and error detection
- Self-documenting code
- Catches type errors early
- Enables static analysis with mypy

## Example

### Good ✅
```python
def calculate_total(items: List[Item]) -> Decimal:
    return sum(item.price for item in items)
```

### Bad ❌
```python
def calculate_total(items):
    return sum(item.price for item in items)
```

## Related
- [Python Standards](./python-style.md)
- [Type Checking](../quick-references/mypy-guide.md)

✅ Added to knowledge garden!
```

### Example 3: Constitutional Consideration

**Command**: `/remember`

**Output**:
```
🧠 Found an important principle:

"Always prioritize code stability and reliability over new features"

This came up multiple times:
- Choosing graceful error handling
- Focusing on tests before new features
- Preferring proven patterns over clever solutions

This feels like a core value. Should I:
1. Add to .claude/standards/development-priorities.md
2. Add to CONSTITUTION.md as a guiding principle
3. Both

What do you think? This seems fundamental to how we work.
```

## Error Handling

### Nothing Worth Remembering
**Solution**:
- That's okay! Not every conversation has patterns
- Suggest reviewing later
- Ask if user has something specific

### Unclear Where to Put It
**Solution**:
- Describe the insight
- Explain the options
- Ask user to decide
- Document the decision

### File Already Exists
**Solution**:
- Read existing content
- Merge or update
- Avoid duplication
- Link related content

### Too Much to Remember
**Solution**:
- Prioritize by importance
- Break into multiple files
- Add incrementally
- Don't overwhelm the garden

## Reusability

This command works across:
- Any project with a knowledge garden
- Any programming language
- Any team size
- Any agent or AI assistant

The key is to:
- Identify valuable patterns
- Document clearly
- Organize logically
- Keep it maintainable

---

**Remember**: The knowledge garden grows with every lesson learned! 🌱🧠✨

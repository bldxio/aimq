# Command Composition Pattern

## What Happened

Some commands tried to automatically execute follow-up commands, but this doesn't work in the current interface. Users can't pass arguments after typing `/command`, so chaining breaks down.

**Example problem:**
```markdown
After extracting lessons, automatically run `/commit` to save them.
```

**Why it failed:**
- Can't pass commit message after `/commit`
- User loses control of workflow
- Unclear what's happening
- Breaks when steps need customization

## What We Learned

Suggesting follow-up commands is better than auto-executing them. This gives users control and makes the workflow explicit. Commands should compose through suggestion, not automation.

**Key insight:** Commands are like functions - they should do one thing well and return control to the caller. Composition happens at the user level, not the command level.

## Why It Matters

### User Control
- User decides when to proceed
- Can skip or reorder steps
- Can customize each step
- Clear what's happening at each stage

### Flexibility
- Adapt workflow to situation
- Handle edge cases
- Interrupt and resume
- Branch to different paths

### Reliability
- Works within interface constraints
- No hidden automation
- Predictable behavior
- Easy to debug

## How to Apply

### Suggest, Don't Execute

❌ **Don't:**
```markdown
## 📋 STEPS
1. Extract lessons
2. Add to knowledge garden
3. Automatically run `/commit` to save changes
```

✅ **Do:**
```markdown
## 📋 STEPS
1. Extract lessons
2. Add to knowledge garden
3. Present findings to user

## 🔗 Follow-up Commands
- `/commit` - Commit the new knowledge
- `/cultivate` - Organize the garden
```

### Provide Context for Next Steps

```markdown
## 🔗 Follow-up Commands

- `/commit` - Commit the new knowledge to the garden
- `/test` - Verify no tests were broken
- `/cultivate` - Organize and maintain the garden (weekly)
- `/focus [topic]` - Explore related topics in depth
```

**Why this works:**
- User knows what to do next
- User understands why to do it
- User can choose their path
- Clear relationship between commands

### Create Command Workflows

Document common workflows in project files:

```markdown
# .claude/quick-references/common-workflows.md

## Adding New Knowledge

1. `/learn` - Extract lessons from recent work
2. `/commit` - Commit the new knowledge
3. `/cultivate` - Organize the garden (if needed)

## Fixing Issues

1. `/fix` - Analyze and fix the problem
2. `/test` - Verify the fix works
3. `/commit` - Commit the fix

## Starting New Work

1. `/plan` - Review progress and plan next steps
2. `/focus [topic]` - Research relevant patterns
3. [Do the work]
4. `/learn` - Extract lessons learned
5. `/commit` - Commit everything
```

### Design for Composition

Each command should:
- **Do one thing well** - Clear, focused purpose
- **Return control** - Don't chain automatically
- **Suggest next steps** - Guide the workflow
- **Be self-contained** - Work independently

## Example

### ❌ Before (Auto-Chaining)

```markdown
# 🎯 ACTION: Extract and Document Lessons

## 📋 STEPS
1. Analyze conversation
2. Review git history
3. Extract lessons
4. Add to knowledge garden
5. Run `/commit` to save changes
6. Run `/cultivate` to organize
```

**Problems:**
- Can't customize commit message
- Can't review before committing
- Forced to cultivate even if not needed
- User loses control

### ✅ After (Composition)

```markdown
# 🎯 ACTION: Extract and Document Lessons

Analyze recent conversation and git history to extract patterns,
lessons, and insights for the knowledge garden.

## 📋 STEPS
1. **Analyze conversation** - Review for patterns and insights
2. **Review git history** - Check recent commits
3. **Extract lessons** - Create lesson documents
4. **Add to garden** - Update knowledge files
5. **Present findings** - Show user what was learned

## 🔗 Follow-up Commands

- `/commit` - Commit the new knowledge
- `/cultivate` - Organize and maintain the garden
- `/focus [topic]` - Explore related topics
```

**Benefits:**
- User reviews findings first
- User decides when to commit
- User can customize commit message
- User can skip cultivation if not needed
- Clear workflow, user in control

## Command Relationships

### Sequential Composition
Commands that naturally follow each other:
```
/plan → [work] → /learn → /commit
/fix → /test → /commit
/focus → [work] → /remember
```

### Parallel Composition
Commands that can be used together:
```
/debug + /focus (research while debugging)
/test + /fix (iterate on fixes)
```

### Conditional Composition
Commands based on outcomes:
```
/test → pass? → /commit
      → fail? → /fix → /test
```

### Periodic Composition
Commands on a schedule:
```
Daily: /plan
Weekly: /cultivate
Per feature: /learn
```

## Real-World Workflows

### Knowledge Garden Workflow
```
1. /learn          # Extract lessons
2. Review findings # User validates
3. /commit         # Save to garden
4. /cultivate      # Organize (weekly)
```

### Development Workflow
```
1. /plan           # Review priorities
2. /focus [topic]  # Research approach
3. [Implement]     # Do the work
4. /test           # Verify it works
5. /commit         # Save changes
6. /learn          # Extract lessons
```

### Debugging Workflow
```
1. /debug          # Analyze the problem
2. /focus [topic]  # Research solutions
3. /fix            # Implement fix
4. /test           # Verify fix
5. /commit         # Save fix
```

## Related

- [@.claude/patterns/documentation-as-interface.md](./documentation-as-interface.md) - Command structure
- [@.claude/patterns/portable-commands.md](./portable-commands.md) - Keeping commands generic
- [@.claude/standards/command-structure.md](../standards/command-structure.md) - Standard format
- [@.claude/INDEX.md](../INDEX.md) - All available commands

## Design Principles

### Single Responsibility
Each command does one thing:
- `/learn` - Extract lessons
- `/commit` - Save changes
- `/cultivate` - Organize garden

Not:
- `/learn-and-commit` - Too coupled
- `/do-everything` - Too broad

### Loose Coupling
Commands don't depend on each other:
- Can run `/commit` without `/learn`
- Can run `/learn` without `/commit`
- Can run in any order that makes sense

### High Cohesion
Related commands suggest each other:
- `/learn` suggests `/commit`
- `/fix` suggests `/test`
- `/test` suggests `/commit`

### Clear Boundaries
Each command has clear:
- Input (what it needs)
- Output (what it produces)
- Side effects (what it changes)
- Next steps (what comes after)

## Key Takeaway

**Commands should compose through suggestion, not automation.** Let users orchestrate the workflow. Provide clear next steps, but let them decide when and how to proceed. This respects their agency and works within interface constraints.

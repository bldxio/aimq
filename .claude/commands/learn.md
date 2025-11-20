---
description: Extract lessons from conversation and git history
---

# 🎯 ACTION: Extract and Document Lessons

Analyze recent conversation and git history to extract patterns, lessons, and insights for the knowledge garden.

See @CONSTITUTION.md for project conventions and @.claude/GARDENING.md for knowledge garden structure.

## 📋 STEPS

1. **Analyze conversation** - Review for successful patterns, challenges, insights, and decisions
2. **Review git history** - Run `git log --oneline -20`, `git log --stat -10`, look for fix/refactor/test commits
3. **Identify patterns** - Categorize as technical patterns, process patterns, mistakes/fixes, or best practices
4. **Extract lessons** - For each pattern, create lesson with what happened, what we learned, why it matters
5. **Analyze specific commits** - Dig deeper into interesting commits with `git show <hash>`
6. **Look for anti-patterns** - Identify what didn't work (reverted code, recurring bugs, flaky tests)
7. **Categorize learnings** - Determine if lesson belongs in patterns/, standards/, architecture/, or quick-references/
8. **Present learnings** - Show extracted lessons with suggested file locations
9. **Add to knowledge garden** - Create or update files with examples and cross-links
10. **Suggest follow-up** - Recommend immediate actions or future considerations

## 💡 CONTEXT

**Lesson format:**
```markdown
# [Lesson Title]

## What Happened
[Describe the situation]

## What We Learned
[The key insight or lesson]

## Why It Matters
[Impact and importance]

## How to Apply
[Actionable guidance]

## Example
[Concrete example from code]

## Related
- [Links to related lessons]
```

**Learning strategies:**
- Pattern recognition (repeated solutions)
- Failure analysis (what broke and why)
- Evolution tracking (how code improved)
- Decision archaeology (why choices were made)

**Knowledge garden structure:**
- `.claude/patterns/` - Reusable code solutions
- `.claude/standards/` - Best practices and conventions
- `.claude/architecture/` - Design decisions and system insights
- `.claude/quick-references/` - Troubleshooting and how-to guides

**Learning principles:**
- Learn from both success and failure
- Focus on transferable knowledge (why, not just what)
- Document the journey and reasoning
- Make it actionable with clear guidance
- Connect the dots with cross-links

## 🔗 Follow-up Commands

- `/commit` - Commit the new knowledge
- `/cultivate` - Organize and maintain the garden
- `/focus` - Explore related topics

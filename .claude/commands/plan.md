---
description: Review and update the project plan
---

# 🎯 ACTION: Review and Update Project Plan

Analyze current progress, review @PLAN.md, and suggest or create next steps.

See @CONSTITUTION.md for project-specific planning conventions and @VISION.md for project direction.

## 📋 STEPS

1. **Read @PLAN.md** - Load and parse the current plan to understand status
2. **Check git history** - Review recent commits with `git log --oneline -20` and `git log --stat -10`
3. **Check current branch** - Run `git branch --show-current` and `git status --short`
4. **Compare plan vs reality** - Identify completed work not marked done, new work not documented
5. **Assess current state** - Determine what's blocking progress, if priorities are still valid
6. **Suggest next steps** - Present immediate actions, short-term goals, and long-term vision
7. **Get user input** - Ask which direction to take or if plan needs updating
8. **Update @PLAN.md** - If approved, update with completed work and new plans
9. **Confirm changes** - Show what was added/removed from the plan
10. **Suggest next step** - Recommend starting work or refining the plan further

## 💡 CONTEXT

**Plan structure:**
```markdown
# Project Plan
**Last Updated**: [Date]

## ✅ Completed Work
[Recently completed items]

## 🎯 Current Status
[What's happening now]

## 📋 Recommended Next Steps
[What's coming next]

## 🤔 Open Questions
[Things to decide]
```

**When reviewing:**
- Look for completed work not marked done
- Check if priorities have shifted
- Identify blockers or technical debt
- Consider velocity and progress patterns

**When creating plans:**
- Define clear goal and success criteria
- Break into phases with estimates
- Note dependencies and risks
- Get approval before adding to @PLAN.md

**Planning principles:**
- Keep plans current and realistic
- Stay flexible, adapt to new information
- Focus on high-impact work
- Communicate clearly and specifically

## 🔗 Follow-up Commands

- `/commit` - Commit plan updates
- `/learn` - Extract lessons from recent work
- `/focus` - Explore specific topics before planning

## Related

- [@PLAN.md](../../PLAN.md) - Project plan (working memory)
- [@VISION.md](../../VISION.md) - Project vision
- [@CONSTITUTION.md](../../CONSTITUTION.md) - Guiding principles
- [@.claude/commands/learn.md](./learn.md) - Extract lessons
- [@.claude/commands/commit.md](./commit.md) - Commit changes
- [@.claude/INDEX.md](../INDEX.md) - Command directory

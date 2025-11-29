---
description: Bootstrap a complete knowledge system for human-agent collaboration
---

# 🎯 ACTION: Seed Knowledge System

Set up a complete knowledge system structure for seamless human-agent collaboration, including core documents, knowledge garden, and workflow commands.

See @.claude/GARDENING.md for knowledge garden philosophy and structure.

## 📋 STEPS

1. **Check existing structure** - Verify what already exists to avoid overwriting
2. **Create root documents** - Set up CONSTITUTION.md, VISION.md, PLAN.md, agents.md
3. **Create ideas folder** - Set up ideas/ directory for brainstorming and exploration
4. **Create .claude directory** - Set up .claude/ with subdirectories
5. **Create GARDENING.md** - Document knowledge garden philosophy and guidelines
6. **Create INDEX.md** - Main navigation hub for the knowledge base
7. **Create pattern files** - Add initial patterns (module-organization, error-handling, etc.)
8. **Create standard files** - Add initial standards (conventional-commits, testing, code-style, etc.)
9. **Create architecture files** - Add architecture documentation
10. **Create quick-reference files** - Add quick guides for common tasks
11. **Create command files** - Add workflow commands (/commit, /test, /fix, /plan, etc.)
12. **Create README files** - Add README to each directory explaining purpose
13. **Confirm setup** - Show what was created and suggest next steps

## 💡 CONTEXT

**Root structure:**
```
project/
├── CONSTITUTION.md    # Guiding principles and non-negotiables
├── VISION.md          # Project vision and direction
├── PLAN.md            # Current status and next steps (working memory)
├── agents.md          # Quick reference for AI agents
├── ideas/             # Brainstorming and exploration
│   └── README.md
└── .claude/           # Knowledge garden
    ├── INDEX.md       # Main navigation hub
    ├── GARDENING.md   # Knowledge garden guidelines
    ├── patterns/      # Reusable code patterns
    ├── standards/     # Best practices and conventions
    ├── architecture/  # System design and decisions
    ├── quick-references/  # How-tos and troubleshooting
    └── commands/      # Workflow commands
```

**Core documents:**
- **CONSTITUTION.md** - Your team's guiding principles, values, and non-negotiables
- **VISION.md** - Where the project is going, the north star that guides decisions
- **PLAN.md** - Working memory of current status, completed work, and next steps
- **agents.md** - Quick reference guide for AI agents working on the project
- **ideas/** - Folder for brainstorming, experiments, and exploration

**Knowledge garden (.claude/):**
- **patterns/** - Reusable solutions to common problems
- **standards/** - Team conventions and best practices
- **architecture/** - System design and architectural decisions
- **quick-references/** - How-to guides and troubleshooting checklists
- **commands/** - Workflow commands for development and knowledge management

**Essential commands to include:**
- `/commit` - Stage changes, run checks, create conventional commits
- `/test` - Run test suite and report results
- `/fix` - Identify and fix test failures
- `/debug` - Debug issues systematically
- `/plan` - Review progress and update PLAN.md
- `/remember` - Capture insights and patterns
- `/learn` - Extract lessons from conversation and git history
- `/focus` - Explore topics in the knowledge garden
- `/levelup` - Research new topics and add to garden
- `/cultivate` - Maintain and organize the garden
- `/release` - Prepare and execute releases

**What this enables:**
- Shared knowledge between humans and AI agents
- Consistent patterns and conventions across the codebase
- Living documentation that evolves with the project
- Efficient onboarding for new team members (human or AI)
- Institutional memory that persists across conversations
- Clear vision and principles that guide decisions
- Working memory that tracks progress and next steps

**After setup:**
1. Customize CONSTITUTION.md with your team's principles
2. Define your VISION.md with project goals and direction
3. Initialize PLAN.md with current status and next steps
4. Start using `/remember` to capture patterns as you work
5. Use `/learn` to extract lessons from completed work
6. Use `/plan` regularly to track progress
7. Use `/cultivate` weekly to maintain the garden

## 🔗 Follow-up Commands

- `/plan` - Create initial project plan
- `/remember` - Start capturing patterns
- `/commit` - Commit the knowledge system setup

## Related

- [@.claude/architecture/knowledge-systems.md](../architecture/knowledge-systems.md) - Knowledge systems guide
- [@.claude/architecture/knowledge-systems-templates.md](../architecture/knowledge-systems-templates.md) - File templates
- [@.claude/commands/cultivate.md](./cultivate.md) - Maintain garden
- [@.claude/commands/remember.md](./remember.md) - Capture insights
- [@GARDENING.md](../../GARDENING.md) - Gardening philosophy

# AIMQ Agents Guide

> **You are amazing!** We're building the future together, seamlessly collaborating as one unified force. Every line of code, every refactor, every test—we're making something incredible. Let's keep this momentum going! 🚀✨

## Quick Reference

**AIMQ (AI Message Queue)** processes Supabase `pgmq` jobs with AI-powered document workflows and agent orchestration.

For deep technical details, see `CLAUDE.md`. This guide is your quick reference for architecture, testing, and our collaborative workflow.

---

## Architecture Snapshot

| Module | Purpose |
|--------|---------|
| `src/aimq/agents/` | Agent implementations (ReAct, Plan-Execute), base classes, decorators, validation, state management |
| `src/aimq/workflows/` | Multi-agent & document workflows with decorators and state models |
| `src/aimq/common/` | Shared utilities (LLM adapters, custom exceptions) |
| `src/aimq/memory/` | Checkpoint and memory persistence |
| `src/aimq/clients/` | External service clients (Supabase, Mistral) |
| `src/aimq/providers/` | Queue provider implementations (pgmq) |
| `src/aimq/tools/` | LangChain tools (OCR, PDF, Supabase operations) |
| `src/aimq/worker.py` | Main orchestrator with `@worker.task()` decorator |
| `src/aimq/queue.py` | Queue wrapper for LangChain Runnables |

**Tech Stack**: Python 3.11-3.13, uv, LangChain, LangGraph, Supabase pgmq, pytest

---

## Testing

```bash
# Run all tests (parallel)
just test

# Run with coverage report (target: 79%+)
just test-cov

# Run specific test file
uv run pytest tests/aimq/test_worker.py

# Run tests matching pattern
uv run pytest -k "test_agent"
```

**Config**: `pyproject.toml` → `[tool.pytest.ini_options]` and `[tool.coverage.*]`

---

## Linting & Formatting

```bash
# Lint with flake8
just lint

# Format with black
just format

# Type check with mypy
just type-check

# Run all CI checks (lint + type + test)
just ci
```

**Rules**: `.flake8` → max-line-length=100, ignore E203/W503/E501, max-complexity=10

---

## Working Memory: PLAN.md

`PLAN.md` is our **shared working memory**—a high-level tracker of what's done and what's next.

### Guidelines:
- **Keep it updated**: After completing features or making architectural changes, update PLAN.md
- **Keep it clean**: Remove completed items, consolidate related tasks
- **Keep it concise**: High-level overview only, details go in code/docs
- **Use it as context**: Reference it when planning next steps

Think of it as our team's north star—always pointing to where we're going next.

---

## Knowledge Garden: .claude/

The `.claude/` directory is our **knowledge garden**—a living, breathing knowledge system that grows with every lesson learned. It contains patterns, standards, architecture decisions, and quick references that help us work in perfect sync.

> 🌱 **New to gardening?** See [GARDENING.md](./GARDENING.md) for a complete crash course on cultivating our shared knowledge!

### Structure:

```
.claude/
├── patterns/           # Reusable solutions to common problems
├── standards/          # Team conventions and best practices
├── architecture/       # System design and decisions
├── quick-references/   # How-to guides and checklists
└── commands/           # Helper commands for workflows
```

### Gardening Commands:

Use these commands to cultivate the knowledge garden and manage our working memory:

- **`/remember`** - Capture insights and patterns from conversation
- **`/learn`** - Extract lessons from conversation and git history
- **`/focus`** - Explore topics in the knowledge garden
- **`/levelup`** - Research new topics and add to the garden
- **`/plan`** - Review progress and update PLAN.md (working memory)
- **`/cultivate`** - Maintain and organize the garden (weekly)

See [GARDENING.md](./GARDENING.md) for detailed usage and examples.

**The hierarchy**: `CONSTITUTION` (who we are) → `VISION` (where we're going) → `GARDEN` (what we know) → `PLAN` (what we're doing)

### Quick Gardening Tips:

1. **Capture while fresh**: Use `/remember` when you solve problems
2. **Learn from history**: Run `/learn` after completing work
3. **Explore before building**: Use `/focus` when you need guidance
4. **Research new topics**: Try `/levelup` to expand knowledge
5. **Cultivate regularly**: Run `/cultivate` weekly to keep it healthy
6. **Keep files small**: Under 400 lines per file
7. **Link everything**: Build a knowledge graph with cross-references

---

## VISION.md & CONSTITUTION.md

**VISION.md** - Our **north star**, the living document that describes where we're going. The vision evolves as we learn and grow, always guiding us forward.

**CONSTITUTION.md** - Our **guiding principles and non-negotiables**. This is our shared value system that keeps us aligned.

Review both regularly. The vision shows us where we're going, the constitution keeps us true to who we are.

---

## Quick Workflow

1. **Install**: `just install` (or `uv sync --group dev`)
2. **Code**: Implement in the right module (agents/workflows/common/etc.)
3. **Format**: `just format`
4. **Lint**: `just lint`
5. **Test**: `just test-cov`
6. **Update docs**: Keep VISION.md, PLAN.md, .claude/, and CLAUDE.md current
7. **Commit**: Use conventional commits (feat:, fix:, docs:, refactor:, etc.)

---

## Remember

**We're not just writing code—we're building the future together.** Every commit is a step forward. Every test is confidence. Every refactor is clarity. You're doing amazing work, and together we're unstoppable! 💪✨

Now let's go build something incredible! 🚀

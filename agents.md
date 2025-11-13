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

## Knowledge Base: .claude/

The `.claude/` directory is our **internal knowledge base**—patterns, standards, architecture, and quick references that help us work in perfect sync.

### Structure:

```
.claude/
├── patterns/           # Established patterns for consistency
├── standards/          # Best practices (coding, testing, git, etc.)
├── architecture/       # System design and library references
├── quick-references/   # Common task guidance
└── commands/           # Custom /commands for workflows
```

### Maintenance Guidelines:

1. **Keep files small**: Under 400 lines per file
2. **One topic per file**: Split large topics into multiple files
3. **Use links heavily**: Cross-reference between files to build a knowledge graph
4. **Update as you code**: When you learn something new or establish a pattern, document it
5. **Stay shallow**: No nested directories—just markdown files in each folder
6. **Make it actionable**: Focus on "how-to" over "what is"

### When to Update:

- **After refactoring**: Document new patterns in `patterns/`
- **Establishing conventions**: Add to `standards/`
- **Integrating new libraries**: Update `architecture/`
- **Solving common problems**: Add to `quick-references/`
- **Creating workflows**: Add new commands to `commands/`

---

## CONSTITUTION.md

Our **guiding principles and non-negotiables** live in `CONSTITUTION.md`. This is our shared value system that keeps us aligned.

Review it regularly and suggest updates when you notice strong preferences or patterns emerging.

---

## Quick Workflow

1. **Install**: `just install` (or `uv sync --group dev`)
2. **Code**: Implement in the right module (agents/workflows/common/etc.)
3. **Format**: `just format`
4. **Lint**: `just lint`
5. **Test**: `just test-cov`
6. **Update docs**: Keep PLAN.md, .claude/, and CLAUDE.md current
7. **Commit**: Use conventional commits (feat:, fix:, docs:, refactor:, etc.)

---

## Remember

**We're not just writing code—we're building the future together.** Every commit is a step forward. Every test is confidence. Every refactor is clarity. You're doing amazing work, and together we're unstoppable! 💪✨

Now let's go build something incredible! 🚀

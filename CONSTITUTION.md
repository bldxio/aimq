# AIMQ Constitution

> Our guiding principles and non-negotiables for building together

**This document defines WHO WE ARE.** For where we're going, see [VISION.md](./VISION.md).

## Core Values

### 1. Clarity Over Cleverness
- Write code that's easy to understand, not code that shows off
- Prefer explicit over implicit
- Name things clearly—no abbreviations unless universally understood

### 2. Modularity & Separation of Concerns
- Each module has a clear, single responsibility
- Shared code goes in `common/`, not duplicated
- Agent code stays in `agents/`, workflow code in `workflows/`
- If it's used in multiple places, it belongs in a shared module

### 3. Test Everything That Matters
- Target: 79%+ coverage, but quality over quantity
- Test behavior, not implementation details
- Mock external dependencies (Supabase, AI providers)
- Fast tests enable fast iteration

### 4. Documentation Evolves With Code
- Update docs when you change architecture
- Keep VISION.md aligned with product evolution
- Keep PLAN.md current as our working memory
- Maintain .claude/ knowledge base as we learn
- CLAUDE.md is the deep reference, agents.md is the quick guide

### 5. Conventional Commits = Clear History
- Use `feat:`, `fix:`, `docs:`, `refactor:`, etc.
- Enables automatic CHANGELOG generation
- Makes git history readable and meaningful
- See `.claude/commands/commit.md` for guidance

### 6. Consistency is Key
- Use project conventions everywhere (code, docs, error messages)
- Error messages should reference `uv add`, not `pip install`
- Command examples should use `uv run`, not bare `python`
- Maintain consistency across all touchpoints with users

## Non-Negotiables

### Code Quality
- ✅ **Always use `uv`** for dependency management (never pip/poetry)
- ✅ **Always use `rg`** for searching file contents (never grep)
- ✅ **Always use `fd`** for finding files (never find)
- ✅ **Format with black** before committing
- ✅ **Lint with flake8** before committing
- ✅ **Run tests** before pushing

### Architecture
- ✅ **No circular dependencies** between modules
- ✅ **Config is a singleton** (`from aimq.config import config`)
- ✅ **One module per concern** (agents, workflows, common, memory)
- ✅ **Tools are LangChain-compatible** (inherit from BaseTool)

### Git Workflow
- ✅ **Feature branches** for all work (`feature/`, `fix/`, `docs/`)
- ✅ **Conventional commits** for all commits
- ✅ **Never force push** to main or dev
- ✅ **Always quote filenames** in git commands (`git add "file.py"`)
- ✅ **Never use `git push origin HEAD`** (always explicit branch names)

### Testing
- ✅ **Test files mirror source structure** (`tests/aimq/test_worker.py` tests `src/aimq/worker.py`)
- ✅ **Mock external services** (no real API calls in unit tests)
- ✅ **Use pytest fixtures** for common setup
- ✅ **Test edge cases** (errors, missing data, race conditions)

### Documentation
- ✅ **Keep PLAN.md concise** (high-level only)
- ✅ **Keep .claude/ files under 400 lines** (split if needed)
- ✅ **Update CLAUDE.md** when architecture changes
- ✅ **No nested directories** in .claude/ (stay shallow)
- ✅ **Ideas live at root** (`/ideas/`, not `.claude/ideas/`) - Human-AI interface

## Strong Preferences

### Code Style
- **Prefer explicit types** over implicit (use type hints)
- **Prefer composition** over inheritance
- **Prefer small functions** over large ones (max ~50 lines)
- **Prefer early returns** over nested conditionals

### Naming Conventions
- **Classes**: PascalCase (`WorkerThread`, `QueueProvider`)
- **Functions/methods**: snake_case (`process_job`, `send_message`)
- **Constants**: UPPER_SNAKE_CASE (`MAX_RETRIES`, `DEFAULT_TIMEOUT`)
- **Private attributes**: Leading underscore (`_internal_state`)

### Error Handling
- **Raise specific exceptions** (not generic `Exception`)
- **Use custom exceptions** from `common/exceptions.py`
- **Log errors with context** (include job ID, queue name, etc.)
- **Fail fast** on configuration errors

### Performance
- **Use async where it matters** (I/O-bound operations)
- **Avoid premature optimization** (profile first)
- **Cache expensive operations** (LLM calls, file reads)
- **Use batch operations** when available (send_batch vs send)

## Collaboration Principles

### Human ↔ Agent Partnership
- **We're a team**: Not human vs AI, but human + AI
- **Ask when uncertain**: Better to clarify than assume
- **Suggest improvements**: If you see a better way, speak up
- **Learn together**: Update .claude/ as we discover patterns
- **Celebrate wins**: Every successful feature is a shared victory

### Communication Style
- **Be clear and concise**: No fluff, get to the point
- **Use examples**: Show, don't just tell
- **Provide context**: Explain the "why" behind decisions
- **Stay positive**: We're building something amazing together

### Decision Making
- **Default to action**: When in doubt, try it and iterate
- **Bias toward simplicity**: Simple solutions beat complex ones
- **Measure what matters**: Test coverage, performance, user value
- **Iterate quickly**: Small changes, fast feedback, continuous improvement

## Living Document

This constitution evolves as we work together. When you notice:
- **New strong preferences** emerging → Add them here
- **Patterns becoming established** → Document in `.claude/patterns/`
- **Better ways of working** → Update this document
- **Outdated rules** → Remove or revise them

**Last Updated**: 2025-11-25

---

## The Hierarchy

```
CONSTITUTION (who we are)
    ↓
VISION (where we're going)
    ↓
GARDEN (what we know)
    ↓
PLAN (what we're doing)
```

**This document anchors everything.** Our vision grows from our values. Our knowledge reflects our principles. Our plans execute our vision.

---

> "We're not just writing code—we're building the future together." 🚀

# Conventional Commits Standard

## Overview

AIMQ uses [Conventional Commits](https://www.conventionalcommits.org/) for all commit messages. This enables automatic CHANGELOG generation and makes git history readable and meaningful.

## Format

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

## Commit Types

| Type | Purpose | CHANGELOG Section | Examples |
|------|---------|-------------------|----------|
| `feat` | New features or capabilities | Added | Adding new functions, endpoints, features |
| `fix` | Bug fixes | Fixed | Fixing errors, crashes, incorrect behavior |
| `docs` | Documentation only | Changed | README, guides, comments, docstrings |
| `refactor` | Code restructuring | Changed | Renaming, reorganizing, simplifying |
| `perf` | Performance improvements | Changed | Optimizations, caching, reducing complexity |
| `style` | Code style changes | (Skipped) | Formatting, linting, whitespace |
| `test` | Test changes | (Skipped) | Adding tests, fixing tests |
| `chore` | Maintenance tasks | (Skipped) | Dependency updates, tooling, config |
| `ci` | CI/CD changes | (Skipped) | GitHub Actions, workflows |
| `build` | Build system | (Skipped) | pyproject.toml, build scripts |
| `security` | Security improvements | Security | Fixing vulnerabilities, hardening |
| `deprecate` | Deprecating features | Deprecated | Marking features for removal |
| `remove` | Removing features | Removed | Deleting deprecated features |

## Scope (Optional)

Scope indicates which module or component is affected:

- `agents` - Agent-related changes
- `workflows` - Workflow-related changes
- `memory` - Memory/checkpoint changes
- `tools` - Tool implementations
- `worker` - Worker orchestration
- `queue` - Queue management
- `cli` - CLI commands
- `docs` - Documentation
- `tests` - Test infrastructure

## Examples

### Good Commits

```bash
# Feature with scope
feat(agents): add ReAct agent implementation

# Bug fix with scope
fix(worker): resolve race condition in worker startup

# Documentation
docs: update Docker deployment guide

# Refactoring with scope
refactor(workflows): simplify multi-agent workflow state management

# Performance improvement
perf(queue): optimize batch message processing

# Breaking change (note the !)
feat(agents)!: change agent decorator API to support async

BREAKING CHANGE: Agent decorators now require async functions.
Migrate by adding 'async' keyword to all agent functions.
```

### Bad Commits

```bash
# ❌ Too vague
fix: bug fix

# ❌ Not conventional format
Fixed the worker bug

# ❌ Multiple concerns (should be separate commits)
feat: add ReAct agent and fix worker bug and update docs

# ❌ Wrong type (this is a refactor, not a feature)
feat: rename langgraph module to agents
```

## Breaking Changes

For breaking changes, add `!` after the type/scope and include a `BREAKING CHANGE:` footer:

```bash
feat(agents)!: change agent decorator API

BREAKING CHANGE: Agent decorators now require async functions.
See migration guide in docs/migration/v0.2.0.md
```

## Multi-line Commits

For complex changes, use the body to explain:

```bash
feat(workflows): add document processing workflow

Implements a LangGraph workflow for processing documents with:
- OCR extraction
- Text chunking
- Embedding generation
- Vector storage

Closes #123
```

## Using the /commit Command

The `.claude/commands/commit.md` command helps generate conventional commits:

1. Analyzes your staged changes
2. Suggests appropriate type and scope
3. Generates a descriptive message
4. Gets your approval before committing

**Usage**: Just say "commit" or "create a commit" and the command will guide you.

## CHANGELOG Generation

Commits are automatically converted to CHANGELOG entries:

```bash
# Generate CHANGELOG from commits
just changelog

# Preview what will be generated
just changelog-preview

# Finalize for release
just changelog-finalize 0.2.0
```

## Tips

1. **Commit often**: Small, focused commits are better than large ones
2. **One concern per commit**: If you're using "and" in your message, split it
3. **Use imperative mood**: "add feature" not "added feature" or "adds feature"
4. **Be specific**: "fix worker race condition" not "fix bug"
5. **Reference issues**: Use "Closes #123" or "Fixes #456" in the body

## Related

- See `.claude/commands/commit.md` for the commit helper command
- See `docs/development/conventional-commits.md` for full documentation
- See `CLAUDE.md` for release workflow details

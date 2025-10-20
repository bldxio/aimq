# Conventional Commits Guide

AIMQ uses [Conventional Commits](https://www.conventionalcommits.org/) for automatic CHANGELOG generation. This guide explains how to write commits that will be properly categorized in release notes.

## Why Conventional Commits?

- **Automated CHANGELOG**: Commit messages automatically generate CHANGELOG.md entries
- **Clear History**: Understand what changed at a glance
- **Semantic Versioning**: Easily determine version bumps
- **Better Collaboration**: Consistent format across the team

## Commit Message Format

```
<type>(<scope>): <description>

[optional body]

[optional footer(s)]
```

### Type

The type determines which CHANGELOG section your commit appears in:

| Type | CHANGELOG Section | Description | Example |
|------|-------------------|-------------|---------|
| `feat` | Added | New features | `feat: add user authentication` |
| `fix` | Fixed | Bug fixes | `fix: resolve database connection timeout` |
| `docs` | Changed | Documentation changes | `docs: update API documentation` |
| `refactor` | Changed | Code refactoring | `refactor: simplify worker thread logic` |
| `perf` | Changed | Performance improvements | `perf: optimize queue polling` |
| `style` | Changed | Code style changes | `style: format with black` |
| `test` | *(skipped)* | Test changes | `test: add queue integration tests` |
| `chore` | *(skipped)* | Maintenance tasks | `chore: update dependencies` |
| `ci` | *(skipped)* | CI/CD changes | `ci: add Python 3.13 to test matrix` |
| `build` | *(skipped)* | Build system changes | `build: update uv lock file` |
| `security` | Security | Security improvements | `security: update dependencies` |
| `deprecate` | Deprecated | Feature deprecation | `deprecate: old queue API` |
| `remove` | Removed | Feature removal | `remove: deprecated queue methods` |

### Scope (Optional)

The scope provides additional context about what changed:

```
feat(ocr): add support for PDF documents
fix(worker): prevent duplicate job processing
docs(api): add examples for queue operations
```

Common scopes in AIMQ:
- `worker` - Worker-related changes
- `queue` - Queue operations
- `ocr` - OCR processing
- `api` - API changes
- `cli` - Command-line interface
- `docs` - Documentation
- `tests` - Testing infrastructure

### Description

- Use imperative mood: "add" not "added" or "adds"
- Don't capitalize first letter
- No period at the end
- Keep under 72 characters

**Good:**
```
feat: add batch processing for OCR jobs
fix: prevent memory leak in worker threads
```

**Bad:**
```
feat: Added batch processing for OCR jobs.
fix: Fixes memory leak.
Fixed a bug in the worker
```

### Body (Optional)

Provide additional context about the changes:

```
feat: add batch processing for OCR jobs

Implements a new batch processor that groups multiple OCR
requests into a single operation, reducing API calls and
improving throughput by 3x.

Includes automatic retry logic and progress tracking.
```

### Footer (Optional)

Add metadata like breaking changes or issue references:

```
feat: redesign queue priority system

BREAKING CHANGE: Queue priority now uses a 0-10 scale
instead of low/medium/high. Update all queue configurations.

Fixes #123
Closes #456
```

## Breaking Changes

Mark breaking changes in two ways:

**Option 1: Exclamation mark**
```
feat!: redesign queue API
```

**Option 2: Footer**
```
feat: redesign queue API

BREAKING CHANGE: Queue.add() now returns a Job object
instead of job ID string.
```

## Real Examples from AIMQ

### Features
```
feat: add git URL support for Docker deployments
feat(worker): implement graceful shutdown
feat(ocr): support batch image processing
```

### Fixes
```
fix: resolve race condition in worker startup
fix(queue): prevent job duplication on retry
fix(cli): handle missing config file gracefully
```

### Documentation
```
docs: add Docker deployment guide
docs(api): update Queue class docstrings
docs: fix typos in README
```

### Refactoring
```
refactor: extract queue provider interface
refactor(worker): simplify thread management
refactor: use pathlib instead of os.path
```

### Testing
```
test: add integration tests for worker
test(ocr): increase coverage to 95%
test: mock Supabase client in unit tests
```

### Chores
```
chore: update dependencies
chore: bump version to 0.1.1b2
chore(ci): add caching to GitHub Actions
```

## Multi-line Commits

For complex changes, use multiple lines:

```
feat: implement retry logic with exponential backoff

- Add RetryPolicy class with configurable delays
- Implement exponential backoff with jitter
- Add max retry limit configuration
- Log retry attempts for debugging

This improves reliability when processing jobs that depend
on external services experiencing temporary outages.

Fixes #234
```

## CHANGELOG Generation

The changelog script (`scripts/generate_changelog.py`) parses commits and generates entries:

**Input (git commits):**
```
feat: add user authentication
fix: resolve database timeout
docs: update README
test: add auth tests
```

**Output (CHANGELOG.md):**
```markdown
### Added
- add user authentication

### Fixed
- resolve database timeout

### Changed
- update README
```

Note: `test:` commits are automatically skipped.

## Best Practices

### DO ✅

- **Use present tense**: "add feature" not "added feature"
- **Be specific**: "fix worker timeout" not "fix bug"
- **Reference issues**: Add "Fixes #123" in footer
- **Explain why**: Use body to explain motivation
- **Group related changes**: Make atomic commits

### DON'T ❌

- **Don't combine types**: Keep feat, fix, docs separate
- **Don't be vague**: "update stuff" tells us nothing
- **Don't skip type**: "implement feature" should be "feat: implement feature"
- **Don't write novels**: Keep description concise
- **Don't commit WIP**: Only commit working code

## Generating CHANGELOG

### Automatic Generation

Run during release:
```bash
# Preview what will be generated
just changelog-preview

# Generate and update CHANGELOG.md
just changelog

# Generate from specific version
just changelog-since v0.1.0
```

### Manual CHANGELOG

If you need to manually edit CHANGELOG.md:
1. Generate initial entries: `just changelog`
2. Review and edit the `[Unreleased]` section
3. Add any context the commit messages don't capture
4. Commit: `git add CHANGELOG.md && git commit -m "docs: update changelog"`

## Integration with Release Workflow

The release workflow automatically:
1. Detects last version tag
2. Parses all commits since that version
3. Categorizes commits by type
4. Generates CHANGELOG.md entries
5. Prompts for review before building

**For Beta Releases:**
```bash
just release-beta
# Automatically generates CHANGELOG from commits
# Prompts for review
# Builds and prepares for TestPyPI
```

**For Stable Releases:**
```bash
just release
# Same automatic CHANGELOG generation
# Builds and prepares for PyPI
```

## Commit Tools

### Commitizen

Install commitizen for interactive commit prompts:

```bash
npm install -g commitizen cz-conventional-changelog

# Or with pipx
pipx install commitizen

# Then use instead of git commit
git cz
```

### Pre-commit Hooks

Add commitlint to validate commit messages:

```bash
npm install -g @commitlint/cli @commitlint/config-conventional

# Add to .pre-commit-config.yaml
- repo: https://github.com/alessandrojcm/commitlint-pre-commit-hook
  rev: v9.5.0
  hooks:
    - id: commitlint
      stages: [commit-msg]
```

## Troubleshooting

### No entries generated

**Problem:** `just changelog` says "No meaningful changes found"

**Solutions:**
1. Check if you're using conventional commit format
2. Verify commits have `feat:`, `fix:`, etc. prefixes
3. Use `--debug` flag: `uv run python scripts/generate_changelog.py --debug`

### Wrong category

**Problem:** Commits appear in wrong CHANGELOG section

**Solution:** Use correct type prefix:
- Use `feat:` for new features (→ Added)
- Use `fix:` for bug fixes (→ Fixed)
- Use `docs:` for documentation (→ Changed)

### Commits skipped

**Problem:** Some commits don't appear in CHANGELOG

**Reason:** These types are automatically skipped:
- `test:` - Test changes
- `chore:` - Maintenance tasks
- `ci:` - CI/CD changes
- `build:` - Build system changes
- Merge commits

### Need manual entry

If automatic generation doesn't capture everything:
1. Generate initial: `just changelog`
2. Manually add entries to `[Unreleased]` section
3. Use clear, user-facing language
4. Follow existing format

## Resources

- [Conventional Commits Specification](https://www.conventionalcommits.org/)
- [Semantic Versioning](https://semver.org/)
- [Keep a Changelog](https://keepachangelog.com/)
- [Commitizen](https://commitizen-tools.github.io/commitizen/)
- [Git Commit Best Practices](https://cbea.ms/git-commit/)

## Examples from Other Projects

**Angular:**
```
feat(compiler): add support for standalone components
fix(router): prevent navigation to undefined routes
docs(forms): improve reactive forms guide
```

**Kubernetes:**
```
feat: implement graceful pod shutdown
fix: resolve kubelet memory leak
perf: optimize pod scheduling algorithm
```

**VS Code:**
```
feat: add multi-cursor editing
fix: prevent extension host crash
docs: update debugging guide
```

---

Remember: Good commit messages are a gift to your future self and your team!

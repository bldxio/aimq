# Precommit Workflow Standard

## What Happened

The `/commit` command would often fail because precommit hooks rejected the changes. This required:
1. Attempt commit
2. Precommit hook fails
3. Fix issues
4. Attempt commit again

**Common failures:**
- Linting errors (flake8)
- Formatting issues (black)
- Test failures (pytest)
- Type errors (mypy)

**Result:** Wasted time, frustration, broken flow.

## What We Learned

Running linting, formatting, and tests BEFORE attempting to commit prevents rejection and saves time. Preemptive quality checks catch issues early when they're easier to fix.

**Key insight:** It's faster to check quality before committing than to fix rejected commits. Prevention beats correction.

## Why It Matters

### Time Savings
- Fix issues once, not twice
- No failed commit attempts
- Faster workflow overall
- Less context switching

### Quality Benefits
- Catch issues early
- Better code quality
- Consistent standards
- Fewer bugs

### Developer Experience
- Less frustration
- Smoother workflow
- More confidence
- Better focus

## How to Apply

### Standard Precommit Workflow

```markdown
1. **Format code** - Apply code style
2. **Run linter** - Check code quality
3. **Run tests** - Verify functionality
4. **Update docs** - Keep documentation current
5. **Stage changes** - Add files to commit
6. **Commit** - Save changes
7. **Push** - Share with team
```

### Detailed Steps

#### 1. Format Code
```bash
just format
# or: black src/ tests/
# or: ruff format .
```

**Why first:** Formatting changes are mechanical, fix them before checking quality.

#### 2. Run Linter
```bash
just lint
# or: flake8 src/ tests/
# or: ruff check .
```

**Why second:** Catch style issues after formatting is done.

#### 3. Run Tests
```bash
just test
# or: pytest
# or: npm test
```

**Why third:** Verify functionality before committing.

#### 4. Update Documentation
- Update PLAN.md with progress
- Update relevant docs
- Add/update comments if needed

**Why fourth:** Document what you did while it's fresh.

#### 5. Stage Changes
```bash
git add "file1.py"
git add "file2.py"
```

**Why selective:** Review each file, avoid accidental commits.

#### 6. Commit
```bash
git commit -m "feat: add new feature"
```

**Why conventional:** Clear commit messages help everyone.

#### 7. Push
```bash
git push origin feature-branch
```

**Why explicit:** Know exactly where you're pushing.

### Quick Reference

```bash
# Full precommit workflow
just format && just lint && just test && git add . && git commit -m "message" && git push origin branch
```

### Project-Specific Workflow

See @CONSTITUTION.md for project-specific commands and standards.

## Example

### ❌ Before (Reactive)

```markdown
## 📋 STEPS
1. Stage changes with `git add`
2. Commit with conventional commit message
3. Push to origin
```

**What happens:**
```bash
$ git commit -m "feat: add feature"
Running precommit hooks...
❌ black failed (formatting issues)
❌ flake8 failed (linting errors)
❌ pytest failed (test failures)

$ # Fix issues...
$ git commit -m "feat: add feature"
Running precommit hooks...
✅ All checks passed
```

**Problems:**
- Commit failed
- Had to fix issues
- Had to commit again
- Wasted time

### ✅ After (Proactive)

```markdown
## 📋 STEPS
1. **Format code** - Run formatter
2. **Run linter** - Check code quality
3. **Run tests** - Verify all tests pass
4. **Update PLAN.md** - Document progress
5. **Stage changes** - Add files selectively
6. **Commit** - Use conventional commit message
7. **Push** - Push to feature branch
```

**What happens:**
```bash
$ just format
✅ Formatted 5 files

$ just lint
✅ No linting errors

$ just test
✅ 469 tests passed

$ # Update PLAN.md...

$ git add "src/file.py" "tests/test_file.py" "PLAN.md"
$ git commit -m "feat: add feature"
✅ All checks passed

$ git push origin feature-branch
✅ Pushed to origin
```

**Benefits:**
- No failed commits
- Issues caught early
- One commit attempt
- Smooth workflow

## Common Precommit Checks

### Formatting
- **Python:** black, autopep8, ruff format
- **JavaScript:** prettier, eslint --fix
- **Go:** gofmt, goimports
- **Rust:** rustfmt

### Linting
- **Python:** flake8, pylint, ruff check
- **JavaScript:** eslint
- **Go:** golint, staticcheck
- **Rust:** clippy

### Testing
- **Python:** pytest, unittest
- **JavaScript:** jest, mocha
- **Go:** go test
- **Rust:** cargo test

### Type Checking
- **Python:** mypy, pyright
- **JavaScript:** tsc (TypeScript)
- **Go:** built-in
- **Rust:** built-in

### Documentation
- **Update PLAN.md** - Track progress
- **Update README** - Keep docs current
- **Update CHANGELOG** - Document changes
- **Update comments** - Explain complex code

## Automation Options

### Git Hooks
```bash
# .git/hooks/pre-commit
#!/bin/bash
just format
just lint
just test
```

### Pre-commit Framework
```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: format
        name: Format code
        entry: just format
        language: system
      - id: lint
        name: Lint code
        entry: just lint
        language: system
      - id: test
        name: Run tests
        entry: just test
        language: system
```

### CI/CD
```yaml
# .github/workflows/ci.yml
- name: Format
  run: just format
- name: Lint
  run: just lint
- name: Test
  run: just test
```

## Related

- [@.claude/standards/command-structure.md](./command-structure.md) - Standard command format
- [@.claude/standards/conventional-commits.md](./conventional-commits.md) - Commit message format
- [@.claude/standards/git-workflow.md](./git-workflow.md) - Git best practices
- [@.claude/quick-references/git-commands.md](../quick-references/git-commands.md) - Common git commands
- [@CONSTITUTION.md](../../CONSTITUTION.md) - Project-specific standards

## Troubleshooting

### Formatter Conflicts with Linter
**Problem:** Formatter and linter disagree on style.
**Solution:** Configure linter to ignore formatting rules, let formatter handle style.

### Tests Take Too Long
**Problem:** Full test suite takes 5+ minutes.
**Solution:** Run fast tests locally, full suite in CI. Use `pytest -k` for specific tests.

### Precommit Hook Too Strict
**Problem:** Hook blocks commits for minor issues.
**Solution:** Make hook advisory (warnings) not blocking (errors), or allow bypass with `--no-verify`.

### Forgot to Run Checks
**Problem:** Committed without running checks.
**Solution:** Set up git hooks or use pre-commit framework for automation.

## Key Takeaway

**Prevention beats correction.** Run quality checks before committing, not after. This catches issues early, saves time, and creates a smoother workflow. Make it a habit, or better yet, automate it.

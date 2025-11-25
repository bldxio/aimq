# Pre-commit Hook Troubleshooting

Quick reference for handling common pre-commit hook issues and workflows.

## The Two-Stage Commit Dance

### What Happens

Pre-commit hooks that auto-fix issues (like `end-of-file-fixer`, `trailing-whitespace`) modify files after staging, causing the initial commit to fail.

### The Pattern

```bash
# First attempt - hooks run and may modify files
$ git commit -m "feat: add new feature"
fix end of files.........................................................Failed
- hook id: end-of-file-fixer
- exit code: 1
- files were modified by this hook

Fixing supabase/.branches/_current_branch
Fixing supabase/.temp/cli-latest

# Re-stage the modified files
$ git add supabase/.branches/_current_branch supabase/.temp/cli-latest

# Second attempt - hooks pass, commit succeeds
$ git commit -m "feat: add new feature"
[feature/my-branch abc1234] feat: add new feature
 11 files changed, 731 insertions(+), 235 deletions(-)
```

### Why This Happens

1. You stage files with `git add`
2. Pre-commit hooks run on staged files
3. Auto-fix hooks modify files to meet standards
4. Modified files are now unstaged (working directory changed)
5. Commit fails because staged content differs from working directory
6. You re-stage the fixed files
7. Hooks run again, find no issues, commit succeeds

### Quick Fix

```bash
# If hooks modified files, just re-add and commit again
git add -A
git commit -m "your message"
```

## Common Pre-commit Hook Issues

### 1. End-of-File Fixer

**Issue:** Files missing newline at end

**Fix:** Automatically adds newline, requires re-staging

```bash
# Hook output
fix end of files.........................................................Failed
- files were modified by this hook

# Solution
git add <modified-files>
git commit -m "message"
```

### 2. Trailing Whitespace

**Issue:** Lines have trailing spaces/tabs

**Fix:** Automatically removes whitespace, requires re-staging

```bash
# Hook output
trim trailing whitespace.................................................Failed
- files were modified by this hook

# Solution
git add <modified-files>
git commit -m "message"
```

### 3. Black Formatting

**Issue:** Python code doesn't match Black style

**Fix:** Run Black manually before committing

```bash
# Hook output
black....................................................................Failed

# Solution
just format  # or: uv run black src/ tests/
git add -A
git commit -m "message"
```

### 4. Flake8 Linting

**Issue:** Code has linting errors

**Fix:** Fix the issues manually (hooks don't auto-fix linting)

```bash
# Hook output
flake8...................................................................Failed
src/aimq/commands/chat.py:173:1: C901 'chat' is too complex (15)

# Solution - fix the code
# Then commit
git add <fixed-files>
git commit -m "message"
```

## Pre-existing Issues Don't Block Commits

### The Scenario

```bash
$ just lint
src/aimq/commands/chat.py:173:1: C901 'chat' is too complex (15)
error: Recipe `lint` failed

$ git status
M tests/test_realtime_chat.py  # Only this file is staged
```

### Key Insight

Pre-commit hooks typically only check **staged files**. Linting errors in unchanged files are pre-existing and don't block your commit.

### How to Verify

```bash
# Check what files are staged
git diff --cached --name-only

# If linting errors are in files NOT in this list,
# they're pre-existing and won't block the commit
```

### When to Fix Pre-existing Issues

**Don't fix immediately if:**
- Issues are in unrelated files
- You're in the middle of a feature
- Fixing would expand scope significantly

**Do fix in a separate commit:**
```bash
# Create a dedicated refactoring task
git checkout -b refactor/reduce-complexity
# Fix the issues
git commit -m "refactor: reduce complexity in chat command"
```

## Skipping Hooks (Use Sparingly)

### When It's Acceptable

- Emergency hotfix
- Hooks are broken
- Committing work-in-progress for backup

### How to Skip

```bash
# Skip all hooks
git commit --no-verify -m "message"

# Or use the shorthand
git commit -n -m "message"
```

### Warning

Skipping hooks means:
- Code may not meet standards
- Tests may not have run
- CI/CD might fail
- Team members may be affected

**Only skip hooks when you have a good reason and plan to fix issues later.**

## Debugging Hook Failures

### 1. See What Hooks Are Running

```bash
# List installed hooks
ls -la .git/hooks/

# View pre-commit config
cat .pre-commit-config.yaml
```

### 2. Run Hooks Manually

```bash
# Run all hooks on staged files
pre-commit run

# Run all hooks on all files
pre-commit run --all-files

# Run specific hook
pre-commit run black --all-files
```

### 3. Update Hooks

```bash
# Update to latest versions
pre-commit autoupdate

# Reinstall hooks
pre-commit install
```

### 4. Check Hook Output

```bash
# Verbose output
pre-commit run --verbose

# Show diff of changes
git diff
```

## Best Practices

### 1. Run Checks Before Committing

```bash
# Format code
just format

# Run linting
just lint

# Run tests
just test

# Then commit
git add -A
git commit -m "message"
```

### 2. Stage Selectively

```bash
# Stage specific files
git add src/aimq/realtime.py tests/test_realtime.py

# Avoid staging everything if you have WIP files
# git add -A  # Be careful with this
```

### 3. Review Hook Changes

```bash
# After hooks modify files, review the changes
git diff

# Make sure auto-fixes are correct
# Then stage and commit
```

### 4. Keep Hooks Fast

Slow hooks frustrate developers and encourage skipping:
- Use `--files` flag to only check staged files
- Cache dependencies when possible
- Run expensive checks in CI, not pre-commit

## Troubleshooting Checklist

- [ ] Did hooks modify files? → Re-stage and commit again
- [ ] Are linting errors in staged files? → Fix them
- [ ] Are linting errors in unstaged files? → Pre-existing, can ignore
- [ ] Did Black fail? → Run `just format` first
- [ ] Are tests failing? → Fix tests before committing
- [ ] Need to skip hooks? → Use `--no-verify` (sparingly)
- [ ] Hooks taking too long? → Check `.pre-commit-config.yaml`

## Related

- [@.claude/standards/precommit-workflow.md](../standards/precommit-workflow.md) - Pre-commit workflow
- [@.claude/standards/conventional-commits.md](../standards/conventional-commits.md) - Commit message format
- [@.claude/quick-references/linting.md](./linting.md) - Linting guide
- [@.claude/commands/commit.md](../commands/commit.md) - Commit command

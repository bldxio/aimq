# Git Workflow Standards

## Overview

AIMQ uses a feature branch workflow with conventional commits and automated releases.

## Branch Strategy

### Main Branches
- **main**: Stable releases only (protected)
- **dev**: Development branch for beta releases (protected)

### Feature Branches
- **feature/**: New features (`feature/add-react-agent`)
- **fix/**: Bug fixes (`fix/worker-race-condition`)
- **docs/**: Documentation (`docs/update-readme`)
- **refactor/**: Code refactoring (`refactor/split-langgraph-module`)
- **test/**: Test improvements (`test/add-agent-tests`)

## Workflow

### 1. Create Feature Branch

```bash
# From dev branch
git checkout dev
git pull origin dev

# Create feature branch
git checkout -b feature/my-feature
```

### 2. Make Changes

```bash
# Stage files (quote filenames!)
git add "src/aimq/agents/react.py"
git add "tests/aimq/agents/test_react.py"

# Commit with conventional format
git commit -m "feat(agents): add ReAct agent implementation"

# Push to remote (explicit branch name!)
git push origin feature/my-feature
```

### 3. Create Pull Request

- Create PR from `feature/my-feature` to `dev`
- Add description of changes
- Link related issues
- Request review if needed

### 4. Merge and Cleanup

```bash
# After PR is merged
git checkout dev
git pull origin dev

# Delete local branch
git branch -d feature/my-feature

# Delete remote branch (if not auto-deleted)
git push origin --delete feature/my-feature
```

## Commit Guidelines

### Format
```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

### Examples
```bash
# Feature
git commit -m "feat(agents): add ReAct agent implementation"

# Bug fix
git commit -m "fix(worker): resolve race condition in startup"

# Documentation
git commit -m "docs: update architecture overview"

# Refactoring
git commit -m "refactor(workflows): simplify state management"

# Breaking change
git commit -m "feat(agents)!: change decorator API

BREAKING CHANGE: Decorators now require async functions"
```

See `standards/conventional-commits.md` for full details.

## Non-Negotiables

### ✅ Always Do
- Use feature branches (never commit directly to main/dev)
- Use conventional commit format
- Quote filenames in git commands (`git add "file.py"`)
- Use explicit branch names in push (`git push origin feature/my-feature`)
- Pull before creating new branches
- Keep commits focused (one concern per commit)

### ❌ Never Do
- Force push to main or dev (`git push -f`)
- Use `git push origin HEAD` (always explicit branch names)
- Commit directly to main or dev
- Use interactive commands (`git rebase -i`, `git add -i`)
- Commit without testing (`just ci` first)
- Use vague commit messages ("fix bug", "update code")

## Common Commands

### Status and Diff
```bash
# Check status
git status

# View changes
git diff

# View staged changes
git diff --cached

# View commit history
git log --oneline -10
```

### Staging
```bash
# Stage specific file (quote it!)
git add "src/aimq/worker.py"

# Stage all changes in directory
git add src/aimq/agents/

# Stage all changes (use carefully!)
git add -A

# Unstage file
git restore --staged "file.py"
```

### Committing
```bash
# Commit with message
git commit -m "feat(agents): add new feature"

# Amend last commit (before pushing!)
git commit --amend -m "feat(agents): add new feature with fix"

# Amend without changing message
git commit --amend --no-edit
```

### Branching
```bash
# List branches
git branch

# Create and switch to branch
git checkout -b feature/my-feature

# Switch to existing branch
git checkout dev

# Delete local branch
git branch -d feature/my-feature

# Delete remote branch
git push origin --delete feature/my-feature
```

### Syncing
```bash
# Pull latest changes
git pull origin dev

# Fetch without merging
git fetch origin

# Push to remote (explicit branch!)
git push origin feature/my-feature

# Set upstream for current branch
git push -u origin feature/my-feature
```

### Undoing Changes
```bash
# Discard changes in file
git restore "file.py"

# Discard all changes
git restore .

# Undo last commit (keep changes)
git reset --soft HEAD~1

# Undo last commit (discard changes)
git reset --hard HEAD~1

# Revert a commit (creates new commit)
git revert <commit-hash>
```

## Release Workflow

### Beta Release (dev branch)
```bash
# On dev branch
just release-beta

# Review CHANGELOG.md
# Commit and push
git add -A
git commit -m "chore: release v0.1.1b2"
git push origin dev
```

### Stable Release (main branch)
```bash
# On dev branch
just release

# Create release branch
git checkout -b release/v0.1.1
git push origin release/v0.1.1

# Create PR to main
# After merge, sync back to dev
git checkout main
git pull
git checkout dev
git merge main
git push origin dev
```

See `CLAUDE.md` for detailed release workflow.

## Troubleshooting

### Merge Conflicts
```bash
# Pull latest changes
git pull origin dev

# If conflicts, resolve in editor
# Then stage resolved files
git add "resolved-file.py"

# Continue merge
git commit
```

### Accidentally Committed to Wrong Branch
```bash
# On wrong branch
git reset --soft HEAD~1

# Switch to correct branch
git checkout correct-branch

# Commit changes
git commit -m "feat: my changes"
```

### Need to Update Feature Branch with Latest Dev
```bash
# On feature branch
git fetch origin
git merge origin/dev

# Or rebase (if no conflicts expected)
git rebase origin/dev
```

## Best Practices

1. **Commit often**: Small, focused commits are better than large ones
2. **Pull before push**: Always pull latest changes before pushing
3. **Test before commit**: Run `just ci` before committing
4. **Write good messages**: Use conventional commits format
5. **Keep branches short-lived**: Merge within a few days
6. **Review your changes**: Use `git diff` before committing
7. **Clean up branches**: Delete merged branches

## Related

- [@conventional-commits.md](./conventional-commits.md) - Commit message format
- [@../commands/commit.md](../commands/commit.md) - Commit helper command
- [@precommit-workflow.md](./precommit-workflow.md) - Pre-commit checks
- [@../../CONSTITUTION.md](../../CONSTITUTION.md) - Git non-negotiables

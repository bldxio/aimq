# Git Commands Quick Reference

## Daily Workflow

```bash
# Check status
git status

# Create feature branch
git checkout -b feature/my-feature

# Stage changes (quote filenames!)
git add "src/aimq/worker.py"
git add "tests/aimq/test_worker.py"

# Commit with conventional format
git commit -m "feat(worker): add new feature"

# Push to remote (explicit branch!)
git push origin feature/my-feature

# Pull latest changes
git pull origin dev
```

## Branching

```bash
# List branches
git branch
git branch -a  # Include remote branches

# Create and switch
git checkout -b feature/my-feature

# Switch to existing
git checkout dev

# Delete local branch
git branch -d feature/my-feature

# Delete remote branch
git push origin --delete feature/my-feature

# Rename current branch
git branch -m new-name
```

## Staging

```bash
# Stage specific file (quote it!)
git add "file.py"

# Stage all in directory
git add src/aimq/

# Stage all changes
git add -A

# Unstage file
git restore --staged "file.py"

# Discard changes
git restore "file.py"
```

## Committing

```bash
# Commit with message
git commit -m "feat: add feature"

# Commit all tracked changes
git commit -am "fix: bug fix"

# Amend last commit (before pushing!)
git commit --amend -m "feat: updated message"

# Amend without changing message
git commit --amend --no-edit
```

## Viewing Changes

```bash
# View unstaged changes
git diff

# View staged changes
git diff --cached

# View changes in specific file
git diff "file.py"

# View commit history
git log --oneline -10

# View detailed history
git log -p -2

# View file history
git log --follow "file.py"
```

## Syncing

```bash
# Fetch from remote
git fetch origin

# Pull from remote
git pull origin dev

# Push to remote (explicit branch!)
git push origin feature/my-feature

# Set upstream for current branch
git push -u origin feature/my-feature

# Force push (use carefully!)
git push --force-with-lease origin feature/my-feature
```

## Undoing Changes

```bash
# Discard changes in file
git restore "file.py"

# Discard all changes
git restore .

# Unstage file
git restore --staged "file.py"

# Undo last commit (keep changes)
git reset --soft HEAD~1

# Undo last commit (discard changes)
git reset --hard HEAD~1

# Revert a commit (creates new commit)
git revert <commit-hash>
```

## Stashing

```bash
# Stash changes
git stash

# Stash with message
git stash save "WIP: feature work"

# List stashes
git stash list

# Apply latest stash
git stash apply

# Apply and remove stash
git stash pop

# Apply specific stash
git stash apply stash@{0}

# Drop stash
git stash drop stash@{0}

# Clear all stashes
git stash clear
```

## Merging

```bash
# Merge branch into current
git merge feature/my-feature

# Merge with no fast-forward
git merge --no-ff feature/my-feature

# Abort merge
git merge --abort

# Continue after resolving conflicts
git add "resolved-file.py"
git commit
```

## Rebasing

```bash
# Rebase current branch onto dev
git rebase dev

# Continue after resolving conflicts
git add "resolved-file.py"
git rebase --continue

# Skip current commit
git rebase --skip

# Abort rebase
git rebase --abort
```

## Tagging

```bash
# List tags
git tag

# Create tag
git tag v0.1.0

# Create annotated tag
git tag -a v0.1.0 -m "Release v0.1.0"

# Push tag
git push origin v0.1.0

# Push all tags
git push origin --tags

# Delete local tag
git tag -d v0.1.0

# Delete remote tag
git push origin --delete v0.1.0
```

## Remote Management

```bash
# List remotes
git remote -v

# Add remote
git remote add origin https://github.com/user/repo.git

# Change remote URL
git remote set-url origin https://github.com/user/repo.git

# Remove remote
git remote remove origin
```

## Inspection

```bash
# Show commit details
git show <commit-hash>

# Show file at specific commit
git show <commit-hash>:path/to/file.py

# Show who changed each line
git blame "file.py"

# Search commits
git log --grep="search term"

# Search code
git log -S "function_name"
```

## Cleaning

```bash
# Remove untracked files (dry run)
git clean -n

# Remove untracked files
git clean -f

# Remove untracked files and directories
git clean -fd

# Remove ignored files too
git clean -fdx
```

## Conventional Commits

```bash
# Feature
git commit -m "feat(agents): add ReAct agent"

# Bug fix
git commit -m "fix(worker): resolve race condition"

# Documentation
git commit -m "docs: update README"

# Refactoring
git commit -m "refactor(workflows): simplify state management"

# Breaking change
git commit -m "feat(agents)!: change decorator API

BREAKING CHANGE: Decorators now require async functions"
```

## Troubleshooting

```bash
# Undo accidental commit to wrong branch
git reset --soft HEAD~1
git checkout correct-branch
git commit -m "feat: my changes"

# Update feature branch with latest dev
git checkout feature/my-feature
git merge origin/dev

# Fix merge conflicts
git status  # See conflicted files
# Edit files to resolve conflicts
git add "resolved-file.py"
git commit

# Recover deleted branch
git reflog  # Find commit hash
git checkout -b recovered-branch <commit-hash>

# Undo force push (if you have the commits)
git reflog  # Find commit before force push
git reset --hard <commit-hash>
git push --force-with-lease origin branch-name
```

## Related

- [@../standards/git-workflow.md](../standards/git-workflow.md) - Detailed git workflow
- [@../standards/conventional-commits.md](../standards/conventional-commits.md) - Commit message format
- [@../commands/commit.md](../commands/commit.md) - Commit helper command
- [@common-tasks.md](./common-tasks.md) - Common development tasks

---
description: Guide through the AIMQ release workflow (beta or stable)
---

# Release Workflow Guide

You are helping with an AIMQ release. Follow the Release Workflow documented in CLAUDE.md.

## Your Tasks

1. **Determine Release Type**
   - Check current git branch (`git branch --show-current`)
   - If on `dev` → Beta Release workflow
   - If on `main` or release branch → Stable Release workflow
   - If on other branch → Ask user to switch to appropriate branch

2. **Pre-Release Validation**
   Run these checks before proceeding:
   - [ ] Verify all tests pass: `just ci`
   - [ ] Check for uncommitted changes: `git status`
   - [ ] Verify branch is up to date: `git fetch && git status`
   - [ ] Check current version: `just version`

   If any checks fail, report to user and ask how to proceed.

3. **Auto-Generate CHANGELOG.md**
   - Run `just changelog-preview` to preview generated entries from commits
   - Show the user what will be added
   - If entries look good, automatically update CHANGELOG.md with `just changelog`
   - If no meaningful commits found, **STOP and inform user** they need conventional commits
   - Summarize the changes that will be in the release

4. **Version Bump Strategy**
   Based on the branch and current version, determine the next version:

   **For dev branch (Beta releases):**
   - Current: `0.1.1b1` → Next: `0.1.1b2` (use `just version-beta`)
   - Current: `0.1.1` → Next: `0.1.2b1` (use `just version-beta`)

   **For main/release branch (Stable releases):**
   - Current: `0.1.1b2` → Next: `0.1.1` (use `just version-stable`)
   - Current: `0.1.1rc1` → Next: `0.1.1` (use `just version-stable`)
   - Current: `0.1.1` → Ask user: patch (0.1.2), minor (0.2.0), or major (1.0.0)?

5. **Execute Release Workflow**

   **For Beta Release (dev branch):**
   ```bash
   # Run the guided release workflow
   just release-beta

   # This will:
   # - Run CI checks (lint, type-check, test)
   # - Bump version to next beta
   # - Auto-generate CHANGELOG.md from git commits
   # - Prompt to review CHANGELOG.md (pause for user)
   # - Build the package

   # Then commit and push:
   git add -A
   git commit -m "chore: release v<VERSION>"
   git push origin dev

   # GitHub Actions will automatically publish to TestPyPI
   ```

   **Manual CHANGELOG generation (if needed):**
   ```bash
   # Preview what will be generated
   just changelog-preview

   # Generate CHANGELOG entries from commits
   just changelog

   # Generate from specific commit/tag
   just changelog-since v0.1.0
   ```

   **For Stable Release (main branch):**
   ```bash
   # Run the guided release workflow
   just release

   # Create release branch:
   git add -A
   git commit -m "chore: release v<VERSION>"
   git checkout -b release/v<VERSION>
   git push origin release/v<VERSION>

   # Then create PR to main
   # After merge, GitHub Actions publishes to PyPI
   ```

6. **Post-Release Tasks**
   - Confirm version was bumped correctly
   - Verify CHANGELOG.md was updated with release date
   - For stable releases: Create PR to main
   - For beta releases: Confirm push triggered GitHub Actions
   - Provide TestPyPI/PyPI installation command to user

## Important Reminders

- **CHANGELOG.md is auto-generated** from git commit messages using conventional commit format
- **Use conventional commits** for automatic categorization (feat:, fix:, docs:, etc.)
- **Version numbers must be in sync** between pyproject.toml and __init__.py (the scripts handle this)
- **Beta versions go to TestPyPI**, stable versions go to PyPI
- **Never release from feature branches** - only dev or main
- **Follow CONTRIBUTING.md** for the complete release process

## Conventional Commit Format

For automatic CHANGELOG generation, use these commit prefixes:

- `feat:` → Added section
- `fix:` → Fixed section
- `docs:` → Changed section
- `refactor:` → Changed section
- `perf:` → Changed section
- `test:` → Skipped
- `chore:` → Skipped
- `security:` → Security section

Example:
```
feat: add user authentication
fix: resolve database connection timeout
docs: update API documentation
```

## Error Handling

If tests fail:
- Review the test output
- Ask user if they want to fix issues or abort release

If git is not clean:
- Show uncommitted changes
- Ask user to commit or stash changes first

If version is already published:
- Check PyPI/TestPyPI
- Suggest bumping to next version

## Communication Style

- Be clear and concise
- Show command output when relevant
- Confirm each step before proceeding
- Summarize what will happen before executing commands
- If uncertain, ask the user rather than guessing

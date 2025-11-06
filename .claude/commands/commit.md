---
description: Stage files and create conventional commit with AI-generated message
---

# Commit Helper

Guide the user through creating a conventional commit by analyzing staged changes and generating an appropriate commit message.

## Overview

This command helps create conventional commits by:
1. Staging all changes
2. Analyzing the diff to understand what changed
3. Suggesting an appropriate commit type and scope
4. Generating a descriptive commit message
5. Getting user approval before committing

## Conventional Commit Types

Use these mappings to determine the commit type:

| Type | When to Use | Examples |
|------|-------------|----------|
| `feat` | New features or capabilities | Adding new functions, endpoints, features |
| `fix` | Bug fixes | Fixing errors, crashes, incorrect behavior |
| `docs` | Documentation only | README, guides, comments, docstrings |
| `refactor` | Code restructuring | Renaming, reorganizing, simplifying without changing behavior |
| `perf` | Performance improvements | Optimizations, caching, reducing complexity |
| `style` | Code style changes | Formatting, linting, whitespace |
| `test` | Test changes | Adding tests, fixing tests, test infrastructure |
| `chore` | Maintenance tasks | Dependency updates, tooling, config changes |
| `ci` | CI/CD changes | GitHub Actions, workflows, build pipelines |
| `build` | Build system | Package.json, pyproject.toml, build scripts |
| `security` | Security improvements | Fixing vulnerabilities, hardening |
| `deprecate` | Deprecating features | Marking features for removal |
| `remove` | Removing features | Deleting deprecated features |

## Task List

Follow these steps in order:

### 1. Validate Git Repository

First, verify we're in a git repository:
```bash
git rev-parse --is-inside-work-tree
```

If this fails, inform the user and exit.

### 2. Stage All Changes

Stage all modified, deleted, and new files:
```bash
git add -A
```

### 3. Check for Staged Changes

Verify there are changes to commit:
```bash
git diff --cached --quiet
```

If this returns 0 (no changes), inform the user "No changes to commit" and exit.

### 4. Show What Will Be Committed

Display a summary:
```bash
git status --short
```

And show the diff:
```bash
git diff --cached --stat
```

### 5. Analyze Changes

Use `git diff --cached` to understand:
- Which files changed
- What types of changes (additions, deletions, modifications)
- The nature of changes (new features, fixes, docs, etc.)

**Scope Detection Rules**:
- Extract the primary directory or module being changed
- Common scope patterns:
  - `src/api/` → `api`
  - `docs/` → `docs`
  - `tests/` → `test`
  - `src/cli/` → `cli`
  - `.github/workflows/` → `ci`
  - Root config files → omit scope or use `config`
- If changes span multiple unrelated areas, omit scope
- Keep scope short (1-2 words max)

**Type Detection Logic**:

Analyze the diff content to determine type:

1. **feat**: Look for:
   - New files being added
   - New functions/classes/methods
   - New endpoints or routes
   - New features in existing code

2. **fix**: Look for:
   - Changes to existing logic
   - Error handling additions
   - Bug-related keywords in comments
   - Corrections to behavior

3. **docs**: Look for:
   - Changes only to `.md` files
   - Changes to docstrings/comments
   - README updates
   - Documentation directories

4. **refactor**: Look for:
   - Renaming variables/functions
   - Restructuring code without feature changes
   - Extracting functions
   - Simplifying complex code

5. **test**: Look for:
   - Changes in test directories
   - New test files
   - Test function additions

6. **chore**: Look for:
   - Dependency updates (`package.json`, `pyproject.toml`, `requirements.txt`)
   - Config file changes
   - Tooling updates

7. **ci**: Look for:
   - `.github/workflows/` changes
   - CI configuration files
   - Build pipeline changes

8. **security**: Look for:
   - Security-related updates
   - Vulnerability fixes
   - Security keywords in changes

### 6. Generate Commit Message

Create a commit message following this format:

```
<type>(<scope>): <description>

<optional body>

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
```

**Subject Line Rules** (first line):
- Format: `type(scope): description` or `type: description` if no scope
- Use imperative mood: "add" not "added", "fix" not "fixed"
- No capitalization of first letter
- No period at the end
- Keep under 72 characters
- Be specific and descriptive

**Examples**:
- `feat(api): add user authentication endpoint`
- `fix(ocr): resolve memory leak in image processing`
- `docs: update installation instructions`
- `refactor(cli): simplify command argument parsing`
- `test(worker): add tests for queue processing`
- `chore: update dependencies to latest versions`
- `ci: add automated security scanning`

### 7. Present for Approval

Show the generated commit message and ask the user:

**"I suggest the following commit message:"**

```
[Generated message]
```

**"Would you like to:"**
- Proceed with this message
- Edit the message
- Cancel

If the user wants to edit, get their revised message and validate it.

### 8. Validate Commit Message

Before committing, validate:

1. **Format**: Must match `type(scope): description` or `type: description`
2. **Type**: Must be one of the allowed types (feat, fix, docs, etc.)
3. **Description**:
   - Starts with lowercase
   - Uses imperative mood
   - No trailing period
   - Under 72 characters
4. **Scope** (if present):
   - Lowercase
   - No spaces
   - Use hyphens for multi-word scopes

If validation fails, explain the issue and ask for corrections.

### 9. Execute Commit

Use the HEREDOC format to ensure proper multi-line handling:

```bash
git commit -m "$(cat <<'EOF'
<commit-message-here>

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
EOF
)"
```

**Important**: Replace `<commit-message-here>` with the actual commit message (type, scope, description, and optional body).

### 10. Confirm Success

After committing:
1. Show the commit hash: `git log -1 --oneline`
2. Confirm: "✓ Committed successfully"
3. Remind: "Run `git push` when ready to push to remote"

## Error Handling

### No Git Repository
**Error**: `fatal: not a git repository`
**Solution**: "This directory is not a git repository. Initialize with `git init` first."

### No Changes to Commit
**Error**: No staged changes after `git add -A`
**Solution**: "No changes to commit. The working directory is clean."

### Commit Failed
**Error**: Git commit command fails
**Solution**: Show the error message and suggest:
- Check if there are pre-commit hooks that failed
- Verify git config is set up (user.name, user.email)
- Check if the repository allows commits

### Validation Errors
**Error**: Invalid commit message format
**Solution**: Explain what's wrong and provide examples:
- "Commit type must be one of: feat, fix, docs, refactor, test, chore, ci, build, perf, style, security, deprecate, remove"
- "Description should start with lowercase"
- "Use imperative mood: 'add' not 'added'"
- "Remove trailing period"

## Examples

### Example 1: New Feature
**Changes**: Added new OCR processing functionality
**Generated Message**:
```
feat(ocr): add PDF text extraction support

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
```

### Example 2: Bug Fix
**Changes**: Fixed authentication token expiration handling
**Generated Message**:
```
fix(auth): handle token expiration gracefully

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
```

### Example 3: Documentation
**Changes**: Updated README installation instructions
**Generated Message**:
```
docs: update installation instructions for uv

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
```

### Example 4: Multiple Areas
**Changes**: Refactored code across multiple modules
**Generated Message**:
```
refactor: simplify error handling across codebase

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
```

## Important Notes

- **Do NOT** make assumptions about what the user wants to commit
- **Do** analyze the actual diff content to generate accurate messages
- **Do** ask for approval before committing
- **Do** allow the user to edit the suggested message
- **Do** validate the final message format
- **Do NOT** skip the validation step
- **Do** use the HEREDOC format for commits to handle multi-line messages
- **Do** include the Claude Code attribution footer

## Reusability

This command is designed to work in any git repository and doesn't require project-specific tools or configurations. The only project-specific element is the "Co-Authored-By: Claude" footer, which can be kept or modified when using in other projects.

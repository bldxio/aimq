---
description: Stage files and create conventional commit with AI-generated message
---

# 🎯 ACTION: Create Conventional Commit

Run linting and pre-commit checks, stage changes, generate a conventional commit message, and commit.

See @CONSTITUTION.md for project-specific commit conventions and pre-commit requirements.

## 📋 STEPS

1. **Run linting and formatting** - Execute project's lint and format commands to ensure code quality
2. **Run pre-commit checks** - Execute any pre-commit hooks or validation scripts
3. **Stage all changes** - Run `git add -A` to stage all modified, deleted, and new files
4. **Check for changes** - Verify there are staged changes with `git diff --cached --quiet`
5. **Show what will be committed** - Display `git status --short` and `git diff --cached --stat`
6. **Analyze changes** - Review diff to determine commit type and scope
7. **Generate commit message** - Create conventional commit message following format
8. **Present for approval** - Show message and ask user to proceed, edit, or cancel
9. **Validate message** - Ensure format matches `type(scope): description` or `type: description`
10. **Execute commit** - Use HEREDOC format for multi-line commit
11. **Update PLAN.md** - Ask if @PLAN.md should be updated to reflect these changes
12. **Suggest next step** - Recommend pushing or making additional changes

## 💡 CONTEXT

**Conventional commit types:**
- `feat` - New features or capabilities
- `fix` - Bug fixes
- `docs` - Documentation only
- `refactor` - Code restructuring without behavior change
- `test` - Test changes
- `chore` - Maintenance tasks (dependencies, tooling, config)
- `ci` - CI/CD changes
- `perf` - Performance improvements
- `style` - Code style changes (formatting, linting)
- `build` - Build system changes
- `security` - Security improvements

**Commit message rules:**
- Use imperative mood: "add" not "added"
- Start with lowercase
- No period at the end
- Keep under 72 characters
- Be specific and descriptive

**Scope detection:**
- Extract primary directory or module being changed
- Omit scope if changes span multiple unrelated areas
- Keep scope short (1-2 words max)

**HEREDOC commit format:**
```bash
git commit -m "$(cat <<'EOF'
type(scope): description

🤖 [Your signature and fun comment!]
EOF
)"
```

## 🔗 Follow-up Commands

- `/plan` - Update the project plan
- `/learn` - Extract lessons from the work
- Push changes when ready

## Related

- [@.claude/standards/conventional-commits.md](../standards/conventional-commits.md) - Commit message format
- [@.claude/standards/precommit-workflow.md](../standards/precommit-workflow.md) - Pre-commit checks
- [@.claude/standards/git-workflow.md](../standards/git-workflow.md) - Git workflow
- [@.claude/commands/test.md](./test.md) - Run tests before committing
- [@.claude/commands/plan.md](./plan.md) - Update project plan
- [@.claude/INDEX.md](../INDEX.md) - Command directory

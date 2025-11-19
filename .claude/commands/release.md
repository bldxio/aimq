---
description: Guide through the AIMQ release workflow (beta or stable)
---

# 🎯 ACTION: Execute Release Workflow

Guide through the AIMQ release process for beta or stable releases.

See @CLAUDE.md for complete release workflow documentation and @CONSTITUTION.md for release conventions.

## 📋 STEPS

1. **Validate environment** - Check current branch is `dev`, working directory is clean
2. **Determine release type** - Beta or stable release
3. **Analyze commits** - Review conventional commits since last release
4. **Determine version bump** - Auto-detect or use specified bump (major/minor/patch)
5. **Update version** - Bump version in project files
6. **Update changelog** - Generate or update CHANGELOG.md from commits
7. **Create release branch** - For stable releases, create `release/vX.Y.Z` branch
8. **Run tests** - Ensure all tests pass before release
9. **Create release commit** - Commit version and changelog updates
10. **Tag release** - Create git tag for the version
11. **Push changes** - Push branch and tags to remote
12. **Create PR** - For stable releases, create PR to main branch
13. **Confirm completion** - Show release summary and next steps

## 💡 CONTEXT

**Release types:**
- **Beta** - Quick release to dev branch (e.g., 0.1.1b1 → 0.1.1b2)
- **Stable** - Full release with PR to main (e.g., 0.1.1 → 0.2.0)

**Version bump detection:**
- Auto-detect from conventional commits (recommended)
- `major` - Breaking changes (0.1.1 → 1.0.0)
- `minor` - New features (0.1.1 → 0.2.0)
- `patch` - Bug fixes (0.1.1 → 0.1.2)

**Branch requirements:**
- MUST be on `dev` branch to start release
- Stable releases create `release/vX.Y.Z` branch
- Beta releases stay on `dev` branch

**Release checklist:**
- All tests passing
- Changelog updated
- Version bumped in all files
- Git tag created
- Changes pushed to remote
- PR created (stable only)

## 🔗 Follow-up Commands

- `/tidyup` - Archive old work before release
- `/commit` - If manual changes needed
- `/test` - Run tests before release
- `/plan` - Update plan after release

## Related

- [@.claude/commands/tidyup.md](./tidyup.md) - Archive completed work
- [@.claude/commands/test.md](./test.md) - Run test suite
- [@.claude/commands/commit.md](./commit.md) - Commit changes
- [@.claude/commands/plan.md](./plan.md) - Update project plan
- [@.claude/standards/git-workflow.md](../standards/git-workflow.md) - Git workflow
- [@CLAUDE.md](../../CLAUDE.md) - Release workflow documentation

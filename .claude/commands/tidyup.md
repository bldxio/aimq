---
description: Archive completed work from PLAN.md to CHANGELOG.md
---

# 🎯 ACTION: Tidy Up Planning Documents

Archive completed work from PLAN.md to CHANGELOG.md to keep planning documents focused and manageable.

See @PLAN.md for current planning state and @CHANGELOG.md for release history.

## 📋 STEPS

1. **Review PLAN.md** - Identify completed work sections that are old enough to archive
2. **Determine archive threshold** - Suggest cutoff date (e.g., work older than 2 weeks)
3. **Extract completed items** - Pull out completed work sections with dates
4. **Categorize changes** - Group by Keep a Changelog categories (Added, Changed, Fixed, etc.)
5. **Format for changelog** - Convert to changelog format with proper categories
6. **Update CHANGELOG.md** - Add entries to [Unreleased] section
7. **Update PLAN.md** - Remove archived content, keep recent work
8. **Show changes** - Display what will be archived and what stays
9. **Get approval** - Ask user to proceed, adjust threshold, or cancel
10. **Commit changes** - Create commit with both file updates

## 💡 CONTEXT

**Archive threshold guidelines:**
- Default: Work completed more than 2 weeks ago
- Keep recent work (last 1-2 weeks) in PLAN.md for context
- Keep current priorities and next steps in PLAN.md
- Archive to CHANGELOG.md for historical record

**Keep a Changelog categories:**
- **Added** - New features, capabilities, tools, documentation
- **Changed** - Changes to existing functionality, refactors
- **Deprecated** - Features marked for removal
- **Removed** - Removed features or code
- **Fixed** - Bug fixes
- **Security** - Security improvements or vulnerability fixes

**PLAN.md structure to preserve:**
- Current Status section (always keep)
- Known Issues section (always keep)
- Recommended Next Steps (always keep)
- Recent completed work (last 1-2 weeks)

**CHANGELOG.md format:**
```markdown
## [Unreleased]

### Added
- New feature description
- Another feature

### Changed
- Refactoring description

### Fixed
- Bug fix description
```

**Commit message format:**
```
docs: archive completed work from PLAN.md to CHANGELOG.md

Archive work completed before [date] to keep PLAN.md focused on
current and upcoming work.
```

**Relationship to /release:**
- `/tidyup` - Ongoing maintenance, moves to [Unreleased]
- `/release` - Creates versions, moves [Unreleased] to [vX.Y.Z]

## 🔗 Follow-up Commands

- `/commit` - If manual adjustments needed
- `/plan` - Review updated plan
- `/release` - Create a release when ready

## Related

- [@.claude/commands/release.md](./release.md) - Create releases
- [@.claude/commands/plan.md](./plan.md) - Update project plan
- [@.claude/commands/commit.md](./commit.md) - Commit changes
- [@PLAN.md](../../PLAN.md) - Project planning document
- [@CHANGELOG.md](../../CHANGELOG.md) - Release history
- [@.claude/INDEX.md](../INDEX.md) - Command directory

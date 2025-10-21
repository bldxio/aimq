---
description: Guide through the AIMQ release workflow (beta or stable)
---

# Release Workflow Guide

You are helping with an AIMQ release. Follow the Release Workflow documented in CLAUDE.md.

## Command Arguments

The `/release` command accepts optional arguments to control release type and version bump:

**Usage:**
```bash
/release              # Stable release with auto-detected version bump
/release beta         # Beta release (auto-increment beta number)
/release major        # Stable release with major version bump
/release minor        # Stable release with minor version bump
/release patch        # Stable release with patch version bump
```

**Release Types:**
- **No argument** or **`stable`**: Stable release with auto-detected version bump
- **`beta`**: Beta release (increments beta number: 0.1.1b1 → 0.1.1b2)

**Version Bump Types (stable releases only):**
- **`major`**: Major version bump (0.1.1 → 1.0.0)
- **`minor`**: Minor version bump (0.1.1 → 0.2.0)
- **`patch`**: Patch version bump (0.1.1 → 0.1.2)
- **No argument**: Auto-detect from conventional commits (recommended)

**Examples:**
- `/release` → Analyzes commits, recommends bump type, creates stable release PR
- `/release beta` → Creates beta release, pushes to dev
- `/release minor` → Forces minor bump, creates stable release PR
- `/release major` → Forces major bump, creates stable release PR

## Your Tasks

1. **Parse Command Arguments**
   - Extract argument from user command: `/release`, `/release beta`, `/release major`, etc.
   - Determine release type: `beta` or `stable` (default)
   - Determine version bump: `major`, `minor`, `patch`, or `auto` (default)

2. **Validate Branch and Environment**
   - Check current git branch (`git branch --show-current`)
   - **MUST be on `dev` branch** for both beta and stable releases
   - If on `main` → Error: "Releases must be created from dev branch"
   - If on `release/*` → Error: "Already on release branch. Switch to dev to start new release"
   - If on other branch → Error: "Please switch to dev branch to create a release"
   - Check if `gh` CLI is installed: `gh --version` (required for PR creation)

3. **Pre-Release Validation**
   Run these checks before proceeding:
   - [ ] Verify all tests pass: `just ci`
   - [ ] Check for uncommitted changes: `git status`
   - [ ] Verify branch is up to date: `git fetch && git status`
   - [ ] Check current version: `just version`

   If any checks fail, report to user and ask how to proceed.

4. **Auto-Detect Version Bump (Stable Releases Only)**

   **Skip this step if `/release beta` - beta releases auto-increment**

   If version bump not specified (major/minor/patch), analyze commits to recommend bump type:

   **Detection Algorithm:**
   ```bash
   # Get commits since last tag
   git log --format=%s --no-merges $(git describe --tags --abbrev=0 --match="v*")..HEAD
   ```

   **Analyze commit prefixes:**
   - Look for **BREAKING CHANGES**: `feat!:`, `fix!:`, body contains `BREAKING CHANGE:`
   - Look for **FEATURES**: `feat:`, `feat(`
   - Look for **FIXES**: `fix:`, `docs:`, `refactor:`, `perf:`, `style:`

   **Apply bump priority:**
   1. If BREAKING found → Recommend `major` bump
   2. Else if FEATURE found → Recommend `minor` bump
   3. Else → Recommend `patch` bump

   **Present recommendation to user:**
   ```
   📊 Analyzing commits for version bump...
      Found: 3 feat:, 5 fix:, 2 docs:
      Recommended: MINOR bump (0.1.1 → 0.2.0)

      Continue with minor bump? (y/N/major/minor/patch):
   ```

   **Allow override:**
   - `y` or `yes` → Use recommended bump
   - `major` → Force major bump
   - `minor` → Force minor bump
   - `patch` → Force patch bump
   - `N` or `no` → Abort release

5. **CHANGELOG Preview**
   - Run `just changelog-preview` to show what will be added to `[Unreleased]`
   - If no meaningful commits found, **STOP and inform user** they need conventional commits
   - Summarize the changes that will be in the release

6. **Execute Release Workflow**

   ### BETA RELEASE WORKFLOW (`/release beta`)

   **Branch: dev → Publishes to TestPyPI → No PR**

   1. **Run guided release preparation:**
      ```bash
      just release-beta
      ```
      - Runs CI checks (lint, type-check, test)
      - Auto-increments beta version (0.1.1b1 → 0.1.1b2)
      - Updates CHANGELOG [Unreleased] section from commits
      - Prompts to review CHANGELOG
      - Builds package
      - **NOTE:** [Unreleased] is NOT converted to version section

   2. **Auto-commit changes:**
      ```bash
      NEW_VERSION=$(uv run python -c "import tomllib; print(tomllib.load(open('pyproject.toml', 'rb'))['project']['version'])")
      git add -A
      git commit -m "chore: release v${NEW_VERSION}"
      ```

   3. **Auto-push to dev:**
      ```bash
      git push origin dev
      ```

   4. **Provide installation instructions:**
      ```
      ✅ Beta release v${NEW_VERSION} published to TestPyPI

      📦 Installation:
         # Add to project
         uv add --index https://test.pypi.org/simple/ aimq==${NEW_VERSION}

         # Or run directly
         uvx --from aimq==${NEW_VERSION} --index https://test.pypi.org/simple/ aimq

      ⏭️  Next: Test the beta, then run /release when ready for stable
      ```

   **BETA RELEASES DO NOT:**
   - Create release branches
   - Create PRs to main
   - Create version sections in CHANGELOG
   - Create git tags

   ### STABLE RELEASE WORKFLOW (`/release` or `/release major|minor|patch`)

   **Branch: dev → release/vX.Y.Z → PR to main → Auto-publish**

   1. **Determine version bump (if not specified):**
      - Use auto-detection from step 4 above
      - Or use explicit bump type from command argument

   2. **Run guided release preparation:**
      ```bash
      # Call appropriate version bump based on detection/argument
      # If major: just version-major
      # If minor: just version-minor
      # If patch: just version-patch

      # Then run release workflow
      just release
      ```
      - Runs CI checks (lint, type-check, test)
      - Bumps to stable version
      - Updates CHANGELOG [Unreleased] from commits
      - Prompts to review [Unreleased]
      - **Converts [Unreleased] → [VERSION] - DATE** with git tag link
      - Prompts to review finalized version section
      - Builds package

   3. **Auto-commit release changes:**
      ```bash
      NEW_VERSION=$(uv run python -c "import tomllib; print(tomllib.load(open('pyproject.toml', 'rb'))['project']['version'])")
      git add -A
      git commit -m "chore: release v${NEW_VERSION}"
      ```

   4. **Create and push release branch:**
      ```bash
      git checkout -b "release/v${NEW_VERSION}"
      git push -u origin "release/v${NEW_VERSION}"
      ```

   5. **Extract CHANGELOG section for PR body:**
      ```bash
      # Read CHANGELOG.md and extract the version section
      # Parse from ## [X.Y.Z] - DATE to next ## [ heading
      # Store in variable for PR body
      ```

      **Example extraction:**
      ```markdown
      ## [0.2.0] - 2025-10-21

      [0.2.0]: https://github.com/bldxio/aimq/compare/v0.1.0...v0.2.0

      ### Added
      - New feature X
      - New feature Y

      ### Changed
      - Updated feature Z

      ### Fixed
      - Bug fix A
      ```

   6. **Create PR to main using `gh` CLI:**
      ```bash
      gh pr create \
        --base main \
        --head "release/v${NEW_VERSION}" \
        --title "chore: release v${NEW_VERSION}" \
        --body "$(cat <<EOF
${CHANGELOG_SECTION}

---

**Installation after merge:**
\`\`\`bash
# Add to project
uv add aimq==${NEW_VERSION}

# Or run directly
uvx aimq@${NEW_VERSION}
\`\`\`

**GitHub Actions will automatically:**
- Publish to PyPI
- Create git tag v${NEW_VERSION}
- Generate GitHub release
EOF
)"
      ```

   7. **Provide release summary:**
      ```
      ✅ Stable release v${NEW_VERSION} prepared

      📦 Release branch: release/v${NEW_VERSION}
      🔗 Pull Request: ${PR_URL}

      📋 Next steps:
         1. Review PR: ${PR_URL}
         2. Approve and merge to main
         3. GitHub Actions will publish to PyPI and create git tag v${NEW_VERSION}

      📥 Installation after merge:
         uv add aimq==${NEW_VERSION}
      ```

   **STABLE RELEASES CREATE:**
   - Release branch from dev
   - Version section in CHANGELOG with git tag link
   - PR to main with CHANGELOG content
   - After merge: Git tag + PyPI publish (automated)

7. **Verify Release Completion**

   **For Beta Releases:**
   - ✅ Confirm version bumped (e.g., 0.1.1b1 → 0.1.1b2)
   - ✅ Verify CHANGELOG.md has `[Unreleased]` section updated (NO version section)
   - ✅ Confirm commit created with message `chore: release vX.Y.ZbN`
   - ✅ Confirm pushed to `dev` branch
   - ✅ Wait for GitHub Actions to complete (check workflow run)
   - ✅ Verify published to TestPyPI (check test.pypi.org)
   - 📦 Provide installation command to user

   **For Stable Releases:**
   - ✅ Confirm version bumped to stable (e.g., 0.1.1b2 → 0.2.0)
   - ✅ Verify CHANGELOG.md has `[VERSION] - DATE` section (NOT [Unreleased])
   - ✅ Confirm comparison link exists (e.g., `[0.2.0]: https://...v0.1.0...v0.2.0`)
   - ✅ Confirm commit created with message `chore: release vX.Y.Z`
   - ✅ Confirm release branch created (`release/vX.Y.Z`)
   - ✅ Confirm pushed to remote
   - ✅ Confirm PR created to main branch
   - 🔗 Provide PR URL to user
   - 📋 Remind user to review, approve, and merge PR
   - 📥 Provide post-merge installation command

## CHANGELOG Extraction Helper

For stable releases, extract the version section from CHANGELOG.md to use as PR body:

```bash
# Read CHANGELOG.md
CHANGELOG_CONTENT=$(cat CHANGELOG.md)

# Extract version section using awk/sed
# From: ## [X.Y.Z] - DATE
# To: Next ## [ heading (or end of file)

VERSION="0.2.0"
CHANGELOG_SECTION=$(awk "/## \[${VERSION}\]/,/^## \[/{print; if (/^## \[/ && !/${VERSION}/) exit}" CHANGELOG.md)

# Use in PR body
gh pr create --body "${CHANGELOG_SECTION}..."
```

**Alternative using Python:**
```python
import re

def extract_changelog_section(version: str) -> str:
    """Extract version section from CHANGELOG.md"""
    with open('CHANGELOG.md', 'r') as f:
        content = f.read()

    # Pattern: ## [VERSION] ... until next ## [
    pattern = rf'(## \[{re.escape(version)}\].*?)(?=\n## \[|\Z)'
    match = re.search(pattern, content, re.DOTALL)

    return match.group(1).strip() if match else ""
```

## Enhanced Error Handling

**Branch Validation:**
- ❌ Not on `dev` branch → "Error: Releases must be created from dev branch. Current: {current_branch}"
- ❌ On `release/*` branch → "Error: Already on release branch. Checkout dev to start new release"

**Prerequisite Checks:**
- ❌ `gh` CLI not installed → "Error: GitHub CLI required. Install: brew install gh (macOS) or see https://cli.github.com"
- ❌ Tests failing → "Error: Tests must pass before release. Run: just ci"
- ❌ Uncommitted changes → "Error: Uncommitted changes detected. Commit or stash first"
- ❌ Not up to date → "Error: Branch out of sync. Run: git pull origin dev"

**Release Conflicts:**
- ❌ Release branch exists → "Error: Branch release/v{version} already exists. Delete it or bump version"
- ❌ PR already exists → "Warning: PR already exists: {pr_url}. Using existing PR"
- ❌ Version already published → "Error: Version {version} already on PyPI/TestPyPI. Bump version number"

**No Meaningful Changes:**
- ⚠️ No commits since last release → "Warning: No new commits since last release. Continue anyway? (y/N)"
- ⚠️ Only chore/test commits → "Warning: No user-facing changes (only chore/test commits). Continue? (y/N)"

## Example Workflows

### Example 1: Auto-Detected Stable Release
```
User: /release

Bot: 📊 Analyzing commits for version bump...
     Found: 3 feat:, 5 fix:, 2 docs:
     Recommended: MINOR bump (0.1.1 → 0.2.0)

     Continue with minor bump? (y/N/major/minor/patch): y

     ✅ Running stable release workflow...
     [Executes: just version-minor && just release]
     [Creates PR]

     ✅ Stable release v0.2.0 prepared
     🔗 Pull Request: https://github.com/bldxio/aimq/pull/42

     📋 Next steps:
        1. Review PR: https://github.com/bldxio/aimq/pull/42
        2. Approve and merge to main
        3. GitHub Actions will publish to PyPI

     📥 Installation after merge:
        uv add aimq==0.2.0
```

### Example 2: Beta Release
```
User: /release beta

Bot: ✅ Running beta release workflow...
     Current version: 0.1.1b2
     Next version: 0.1.1b3

     [Executes: just release-beta]
     [Commits and pushes to dev]

     ✅ Beta release v0.1.1b3 published to TestPyPI

     📦 Installation:
        uv add --index https://test.pypi.org/simple/ aimq==0.1.1b3

     ⏭️  Next: Test the beta, then run /release when ready for stable
```

### Example 3: Forced Major Release
```
User: /release major

Bot: ✅ Running stable release workflow with MAJOR bump...
     Current version: 0.2.0
     Next version: 1.0.0

     [Executes: just version-major && just release]
     [Creates PR]

     ✅ Stable release v1.0.0 prepared
     🔗 Pull Request: https://github.com/bldxio/aimq/pull/43

     ⚠️  MAJOR version bump - breaking changes!
     📋 Ensure CHANGELOG documents breaking changes clearly.
```

### Example 4: Error - Not on Dev Branch
```
User: /release

Bot: ❌ Error: Releases must be created from dev branch
     Current branch: feature/new-thing

     Please run:
       git checkout dev
       git pull origin dev

     Then try /release again
```

## Important Reminders

- **CHANGELOG.md is auto-generated** from git commit messages using conventional commit format
- **Use conventional commits** for automatic categorization (feat:, fix:, docs:, etc.)
- **Version numbers must be in sync** between pyproject.toml and __init__.py (the scripts handle this)
- **Beta versions go to TestPyPI**, stable versions go to PyPI
- **Git tags are only created for stable releases** (after merge to main), not for beta releases
- **Tags are created automatically by GitHub Actions** on the merge commit to main
- **CHANGELOG version sections align with git tags:**
  - Beta releases: Changes in `[Unreleased]`, NO version sections
  - Stable releases: `[Unreleased]` converted to `[VERSION]` with tag comparison link
- **Releases MUST be created from `dev` branch** - never from feature branches or main
- **Use native uv commands** - `uv add`, `uvx`, not `uv pip`
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

## Additional Notes

**Manual CHANGELOG commands (if needed):**
```bash
# Preview what will be generated
just changelog-preview

# Generate CHANGELOG entries from commits → [Unreleased]
just changelog

# Generate from specific commit/tag
just changelog-since v0.1.0

# Finalize [Unreleased] → [VERSION] (stable releases only, automatic in workflow)
just changelog-finalize 0.1.1
```

**Manual version bump commands (if needed):**
```bash
# Check current version
just version

# Beta version bump
just version-beta          # 0.1.1b1 → 0.1.1b2

# Stable version bumps
just version-major         # 0.1.1 → 1.0.0
just version-minor         # 0.1.1 → 0.2.0
just version-patch         # 0.1.1 → 0.1.2
```

## Communication Style

- Be clear and concise
- Show command output when relevant
- Confirm each step before proceeding
- Summarize what will happen before executing commands
- If uncertain, ask the user rather than guessing

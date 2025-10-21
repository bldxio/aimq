#!/usr/bin/env python3
"""
Changelog Generator Script

Automatically generates CHANGELOG.md entries from git commit messages
using conventional commit format.

Parses commits since the last release and categorizes them into:
- Added (feat:)
- Changed (refactor:, perf:, style:)
- Fixed (fix:)
- Security (security:)
- Removed (remove:)
- Deprecated (deprecate:)

Usage:
    python scripts/generate_changelog.py [--since TAG] [--dry-run]
    python scripts/generate_changelog.py --since v0.1.0
    python scripts/generate_changelog.py  # Auto-detects last release
"""

import argparse
import logging
import re
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Tuple

# Configure logger
logger = logging.getLogger(__name__)


def get_project_root() -> Path:
    """Get the project root directory."""
    return Path(__file__).parent.parent


def get_last_version_tag() -> str:
    """Get the most recent version tag from git."""
    try:
        result = subprocess.run(
            ["git", "describe", "--tags", "--abbrev=0", "--match=v*"],
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip()
    except Exception as e:
        logger.warning(
            "Failed to get version tag from git: %s. Falling back to CHANGELOG.md parsing.",
            e,
            exc_info=True,
        )

    # Try to get from CHANGELOG.md
    changelog_path = get_project_root() / "CHANGELOG.md"
    if changelog_path.exists():
        content = changelog_path.read_text()
        # Find first version heading (## [X.Y.Z])
        match = re.search(r"## \[(\d+\.\d+\.\d+[^\]]*)\]", content)
        if match:
            return f"v{match.group(1)}"

    return None


def get_commits_since(since_ref: str = None) -> List[str]:
    """Get commit messages since a git reference."""
    # Use a unique delimiter that won't appear in commit messages
    delimiter = "<<<COMMIT_SEPARATOR>>>"
    cmd = ["git", "log", f"--format=%H|||%s|||%b|||%an{delimiter}", "--no-merges"]

    if since_ref:
        cmd.append(f"{since_ref}..HEAD")
    else:
        # Get all commits if no reference
        cmd.append("HEAD")

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        commits = result.stdout.strip().split(delimiter)
        return [c.strip() for c in commits if c.strip()]
    except subprocess.CalledProcessError:
        return []


def parse_commit(commit_line: str) -> Tuple[str, str, str, str]:
    """Parse a commit line into hash, subject, body, author."""
    parts = commit_line.split("|||")
    if len(parts) >= 4:
        return parts[0], parts[1], parts[2], parts[3]
    return "", "", "", ""


def categorize_commit(subject: str, body: str) -> Tuple[str, str]:
    """
    Categorize commit into CHANGELOG section and extract description.

    Returns: (category, description)
    """
    # Conventional commit pattern: type(scope): description
    pattern = r"^(\w+)(?:\([^)]+\))?: (.+)"
    match = re.match(pattern, subject)

    if not match:
        # Try to categorize by keywords if not conventional format
        lower_subject = subject.lower()
        if any(kw in lower_subject for kw in ["add", "new", "feature"]):
            return "Added", subject
        elif any(kw in lower_subject for kw in ["fix", "bug", "resolve"]):
            return "Fixed", subject
        elif any(kw in lower_subject for kw in ["update", "change", "modify"]):
            return "Changed", subject
        elif any(kw in lower_subject for kw in ["remove", "delete"]):
            return "Removed", subject
        elif any(kw in lower_subject for kw in ["deprecate"]):
            return "Deprecated", subject
        elif any(kw in lower_subject for kw in ["security", "cve"]):
            return "Security", subject
        else:
            return "Changed", subject

    commit_type = match.group(1).lower()
    description = match.group(2)

    # Map conventional commit types to CHANGELOG categories
    type_mapping = {
        "feat": "Added",
        "feature": "Added",
        "fix": "Fixed",
        "bugfix": "Fixed",
        "docs": "Changed",
        "doc": "Changed",
        "refactor": "Changed",
        "perf": "Changed",
        "performance": "Changed",
        "style": "Changed",
        "test": None,  # Skip test commits
        "tests": None,
        "chore": None,  # Skip chore commits
        "ci": None,  # Skip CI commits
        "build": None,  # Skip build commits
        "security": "Security",
        "sec": "Security",
        "remove": "Removed",
        "deprecate": "Deprecated",
    }

    category = type_mapping.get(commit_type, "Changed")

    # Check for breaking changes in body
    if "BREAKING CHANGE" in body or "BREAKING-CHANGE" in body:
        category = "Changed"
        description = f"**BREAKING:** {description}"

    return category, description


def generate_changelog_entries(commits: List[str], debug: bool = False) -> Dict[str, List[str]]:
    """Generate categorized changelog entries from commits."""
    categories = {
        "Added": [],
        "Changed": [],
        "Fixed": [],
        "Deprecated": [],
        "Removed": [],
        "Security": [],
    }

    for commit in commits:
        commit_hash, subject, body, author = parse_commit(commit)
        if not subject:
            continue

        # Skip commits that are likely automated or maintenance
        skip_keywords = [
            "merge branch",
            "merge pull request",
            "bump version",
            "update lock file",
            "update uv.lock",
        ]
        should_skip = any(skip in subject.lower() for skip in skip_keywords)
        if debug and should_skip:
            print(f"  [SKIP] {subject[:60]}")
        if should_skip:
            continue

        category, description = categorize_commit(subject, body)
        if debug:
            print(f"  [{category or 'NONE'}] {subject[:60]}")

        if category and category in categories:
            # Clean up description
            description = description.strip()
            # Remove trailing period if present
            if description.endswith("."):
                description = description[:-1]

            # Add to category if not duplicate
            if description not in categories[category]:
                categories[category].append(description)

    return categories


def format_changelog_section(entries: Dict[str, List[str]]) -> str:
    """Format changelog entries into markdown."""
    lines = []

    for category in ["Added", "Changed", "Deprecated", "Removed", "Fixed", "Security"]:
        if entries[category]:
            lines.append(f"### {category}\n")
            for entry in entries[category]:
                lines.append(f"- {entry}")
            lines.append("")  # Empty line between sections

    return "\n".join(lines)


def update_changelog(content: str, dry_run: bool = False) -> str:
    """Update CHANGELOG.md with new entries."""
    changelog_path = get_project_root() / "CHANGELOG.md"

    if not changelog_path.exists():
        print("Error: CHANGELOG.md not found")
        return None

    current_content = changelog_path.read_text()

    # Find the [Unreleased] section
    unreleased_pattern = r"(## \[Unreleased\]\s*\n)(.*?)(\n## \[)"
    match = re.search(unreleased_pattern, current_content, re.DOTALL)

    if not match:
        print("Error: Could not find [Unreleased] section in CHANGELOG.md")
        return None

    # Replace the unreleased content
    new_content = current_content.replace(match.group(2), "\n" + content + "\n")

    if dry_run:
        print("\n" + "=" * 60)
        print("DRY RUN - Would update CHANGELOG.md with:")
        print("=" * 60)
        print(content)
        print("=" * 60)
        return content

    changelog_path.write_text(new_content)
    print("✓ Updated CHANGELOG.md")
    return content


def main():
    parser = argparse.ArgumentParser(description="Generate CHANGELOG entries from git commits")
    parser.add_argument(
        "--since",
        help="Git reference to start from (tag, commit, etc.). Auto-detects last version if not provided.",
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="Show what would be added without updating the file"
    )
    parser.add_argument("--debug", action="store_true", help="Show debug output for each commit")
    args = parser.parse_args()

    # Determine starting point
    since_ref = args.since
    if not since_ref:
        since_ref = get_last_version_tag()
        if since_ref:
            print(f"📍 Generating changelog since last release: {since_ref}")
        else:
            print("⚠️  No previous release found, using all commits")

    # Get commits
    commits = get_commits_since(since_ref)
    if not commits:
        print("No commits found")
        return 0

    print(f"📝 Found {len(commits)} commits to process")

    # Generate entries
    entries = generate_changelog_entries(commits, debug=args.debug)

    # Check if there are any entries
    total_entries = sum(len(items) for items in entries.values())
    if total_entries == 0:
        print("⚠️  No meaningful changes found in commits")
        print("💡 Tip: Use conventional commit format (feat:, fix:, etc.)")
        return 0

    # Format output
    formatted = format_changelog_section(entries)

    # Update changelog
    update_changelog(formatted, dry_run=args.dry_run)

    if not args.dry_run:
        print("\n✅ CHANGELOG.md updated successfully!")
        print("\n💡 Next steps:")
        print("  1. Review the changes: git diff CHANGELOG.md")
        print("  2. Edit manually if needed")
        print("  3. Commit: git add CHANGELOG.md")

    return 0


if __name__ == "__main__":
    sys.exit(main())

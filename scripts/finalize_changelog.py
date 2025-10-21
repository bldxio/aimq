#!/usr/bin/env python3
"""
Changelog Finalization Script

Converts the [Unreleased] section to a versioned release section with git tag links.
This should only be run for stable releases that will have git tags.

Usage:
    python scripts/finalize_changelog.py VERSION [--dry-run]
    python scripts/finalize_changelog.py 0.1.1
    python scripts/finalize_changelog.py 0.1.2 --dry-run
"""

import argparse
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional


def get_project_root() -> Path:
    """Get the project root directory."""
    return Path(__file__).parent.parent


def get_git_remote_url() -> Optional[str]:
    """Get the GitHub repository URL from git remote."""
    try:
        result = subprocess.run(
            ["git", "remote", "get-url", "origin"],
            capture_output=True,
            text=True,
            check=True,
        )
        url = result.stdout.strip()

        # Convert SSH to HTTPS format
        if url.startswith("git@github.com:"):
            url = url.replace("git@github.com:", "https://github.com/")

        # Remove .git suffix if present
        if url.endswith(".git"):
            url = url[:-4]

        return url
    except subprocess.CalledProcessError:
        return None


def get_previous_version(changelog_content: str) -> Optional[str]:
    """Extract the most recent version from CHANGELOG.md."""
    # Find first version after [Unreleased]
    pattern = r"## \[(\d+\.\d+\.\d+[^\]]*)\]"
    matches = re.findall(pattern, changelog_content)

    if matches:
        return matches[0]
    return None


def insert_comparison_link(content: str, comparison_link: str) -> str:
    """Insert comparison link into CHANGELOG content."""
    if not comparison_link:
        return content

    # Find where to insert the link (after other version links or before end of file)
    link_pattern = r"(\[[\d.]+\]: https://.*\n)"
    link_matches = list(re.finditer(link_pattern, content))

    if link_matches:
        # Insert after the last existing link
        last_link = link_matches[-1]
        insert_pos = last_link.end()
        return content[:insert_pos] + comparison_link + content[insert_pos:]
    else:
        # No existing links, add at the end
        return content.rstrip() + "\n\n" + comparison_link

    return content


def finalize_changelog(version: str, dry_run: bool = False) -> bool:
    """
    Finalize the [Unreleased] section to a versioned release.

    Args:
        version: Version number (e.g., "0.1.1")
        dry_run: If True, only show what would be changed

    Returns:
        True if successful, False otherwise
    """
    changelog_path = get_project_root() / "CHANGELOG.md"

    if not changelog_path.exists():
        print("❌ Error: CHANGELOG.md not found")
        return False

    content = changelog_path.read_text()

    # Check if [Unreleased] section exists
    if "## [Unreleased]" not in content:
        print("❌ Error: [Unreleased] section not found in CHANGELOG.md")
        return False

    # Check if version already exists
    version_pattern = rf"## \[{re.escape(version)}\]"
    if re.search(version_pattern, content):
        print(f"⚠️  Warning: Version [{version}] already exists in CHANGELOG.md")
        return False

    # Extract [Unreleased] section content
    unreleased_pattern = r"(## \[Unreleased\]\s*\n)(.*?)(\n## \[|$)"
    match = re.search(unreleased_pattern, content, re.DOTALL)

    if not match:
        print("❌ Error: Could not parse [Unreleased] section")
        return False

    unreleased_content = match.group(2).strip()

    if not unreleased_content:
        print("⚠️  Warning: [Unreleased] section is empty - nothing to finalize")
        return False

    # Get current date
    today = datetime.now().strftime("%Y-%m-%d")

    # Create new version section
    version_section = f"## [{version}] - {today}\n\n{unreleased_content}\n\n"

    # Get previous version for comparison link
    previous_version = get_previous_version(content)
    repo_url = get_git_remote_url()

    # Build comparison link if we have both versions and repo URL
    comparison_link = ""
    if previous_version and repo_url:
        comparison_link = f"[{version}]: {repo_url}/compare/v{previous_version}...v{version}\n"

    # Replace [Unreleased] section with empty version + new version section
    new_unreleased = "## [Unreleased]\n\n"
    new_content = content.replace(match.group(0), new_unreleased + version_section + match.group(3))

    # Add comparison link at the bottom if needed
    new_content = insert_comparison_link(new_content, comparison_link)

    if dry_run:
        print("\n" + "=" * 70)
        print("DRY RUN - Would update CHANGELOG.md with:")
        print("=" * 70)
        print(f"\n{new_unreleased}")
        print(version_section)
        if comparison_link:
            print(f"(And add at bottom: {comparison_link.strip()})")
        print("=" * 70)
        return True

    # Write the updated content
    changelog_path.write_text(new_content)

    print(f"✅ Finalized CHANGELOG.md for version {version}")
    print(f"   - Converted [Unreleased] → [{version}] - {today}")
    if previous_version:
        print(f"   - Added comparison link: v{previous_version}...v{version}")
    print("\n💡 Next steps:")
    print("  1. Review: git diff CHANGELOG.md")
    print("  2. Commit with release changes")

    return True


def main():
    parser = argparse.ArgumentParser(
        description="Finalize CHANGELOG.md [Unreleased] section to a versioned release"
    )
    parser.add_argument(
        "version",
        help="Version number for the release (e.g., 0.1.1)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be changed without updating the file",
    )
    args = parser.parse_args()

    # Validate version format (X.Y.Z)
    version_pattern = r"^\d+\.\d+\.\d+$"
    if not re.match(version_pattern, args.version):
        print(f"❌ Error: Invalid version format '{args.version}'")
        print("   Expected format: X.Y.Z (e.g., 0.1.1)")
        return 1

    success = finalize_changelog(args.version, dry_run=args.dry_run)
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())

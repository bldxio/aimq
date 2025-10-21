#!/usr/bin/env python3
"""
Version Synchronization Script

Keeps version numbers in sync between pyproject.toml and src/aimq/__init__.py
This ensures the package version is consistent across the codebase.

Usage:
    python scripts/sync_version.py <new_version>
    python scripts/sync_version.py 0.1.1b2
"""

import re
import sys
from pathlib import Path

import tomlkit


def get_project_root() -> Path:
    """Get the project root directory."""
    return Path(__file__).parent.parent


def update_pyproject_version(version: str) -> None:
    """Update version in pyproject.toml using proper TOML parsing."""
    pyproject_path = get_project_root() / "pyproject.toml"

    # Parse TOML file
    with open(pyproject_path, "r") as f:
        data = tomlkit.load(f)

    # Ensure [project] section exists
    if "project" not in data:
        data["project"] = {}

    # Update only the [project].version field
    data["project"]["version"] = version

    # Write back preserving formatting
    with open(pyproject_path, "w") as f:
        tomlkit.dump(data, f)

    print(f"✓ Updated pyproject.toml to version {version}")


def update_init_version(version: str) -> None:
    """Update version in src/aimq/__init__.py."""
    init_path = get_project_root() / "src" / "aimq" / "__init__.py"
    content = init_path.read_text()

    # Update __version__ field
    new_content = re.sub(r'__version__\s*=\s*"[^"]+"', f'__version__ = "{version}"', content)

    init_path.write_text(new_content)
    print(f"✓ Updated src/aimq/__init__.py to version {version}")


def get_current_version() -> str:
    """Get the current version from pyproject.toml using proper TOML parsing."""
    pyproject_path = get_project_root() / "pyproject.toml"

    with open(pyproject_path, "r") as f:
        data = tomlkit.load(f)

    if "project" not in data or "version" not in data["project"]:
        raise ValueError("Could not find [project].version in pyproject.toml")

    return data["project"]["version"]


def validate_version(version: str) -> bool:
    """Validate semantic version format with optional pre-release suffix."""
    pattern = r"^\d+\.\d+\.\d+([ab]\d+|rc\d+)?$"
    return bool(re.match(pattern, version))


def main():
    if len(sys.argv) < 2:
        current = get_current_version()
        print(f"Current version: {current}")
        print("\nUsage: python scripts/sync_version.py <new_version>")
        print("Examples:")
        print("  python scripts/sync_version.py 0.1.1b2   # Beta version")
        print("  python scripts/sync_version.py 0.1.1rc1  # Release candidate")
        print("  python scripts/sync_version.py 0.1.1     # Stable release")
        sys.exit(1)

    new_version = sys.argv[1]

    if not validate_version(new_version):
        print(f"Error: Invalid version format: {new_version}")
        print("Expected format: X.Y.Z or X.Y.ZbN or X.Y.ZrcN")
        print("Examples: 0.1.1, 0.1.1b2, 0.1.1rc1")
        sys.exit(1)

    try:
        current = get_current_version()
        print(f"Current version: {current}")
        print(f"New version: {new_version}")
        print()

        update_pyproject_version(new_version)
        update_init_version(new_version)

        print(f"\n✅ Successfully synchronized version to {new_version}")
        print("\nNext steps:")
        print("  1. Update CHANGELOG.md with changes")
        print(
            "  2. Commit: git add -A && git commit -m 'chore: bump version to {}'".format(
                new_version
            )
        )
        print("  3. Push to trigger CI/CD")

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

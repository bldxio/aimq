#!/usr/bin/env python3
"""
Version Synchronization Check Script

Verifies that version numbers are in sync between pyproject.toml and src/aimq/__init__.py
Used as a pre-commit hook to catch version mismatches before commit.

Exit codes:
    0 - Versions are in sync
    1 - Versions are out of sync or error occurred
"""

import re
import sys
from pathlib import Path


def get_project_root() -> Path:
    """Get the project root directory."""
    return Path(__file__).parent.parent


def get_pyproject_version() -> str:
    """Get version from pyproject.toml."""
    pyproject_path = get_project_root() / "pyproject.toml"
    content = pyproject_path.read_text()

    match = re.search(r'version\s*=\s*"([^"]+)"', content)
    if not match:
        raise ValueError("Could not find version in pyproject.toml")

    return match.group(1)


def get_init_version() -> str:
    """Get version from src/aimq/__init__.py."""
    init_path = get_project_root() / "src" / "aimq" / "__init__.py"
    content = init_path.read_text()

    match = re.search(r'__version__\s*=\s*"([^"]+)"', content)
    if not match:
        raise ValueError("Could not find __version__ in src/aimq/__init__.py")

    return match.group(1)


def main():
    try:
        pyproject_version = get_pyproject_version()
        init_version = get_init_version()

        if pyproject_version == init_version:
            print(f"✓ Version sync OK: {pyproject_version}")
            return 0
        else:
            print("✗ Version mismatch detected!")
            print(f"  pyproject.toml: {pyproject_version}")
            print(f"  __init__.py:    {init_version}")
            print()
            print("Fix with: uv run python scripts/sync_version.py <version>")
            return 1

    except Exception as e:
        print(f"Error checking version sync: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())

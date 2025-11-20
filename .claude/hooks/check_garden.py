#!/usr/bin/env python3
"""
Garden Health Check Script

Checks the knowledge garden for:
- Files over the size limit (380 lines)
- Broken links
- Missing cross-references

Usage:
    python .claude/hooks/check_garden.py
    python .claude/hooks/check_garden.py --max-lines 400
    python .claude/hooks/check_garden.py --check-links
"""

import argparse
import pathlib
import re
import sys
from typing import List, Tuple

# Configuration
ROOT = pathlib.Path(__file__).resolve().parents[2]
GARDEN = ROOT / ".claude"
DEFAULT_MAX_LINES = 380


def check_file_sizes(max_lines: int) -> List[Tuple[pathlib.Path, int]]:
    """Check for markdown files exceeding the line limit."""
    oversize = []

    for path in GARDEN.rglob("*.md"):
        if path.name.startswith("."):  # Skip hidden files
            continue

        try:
            lines = path.read_text(encoding="utf-8").splitlines()
            line_count = len(lines)

            if line_count > max_lines:
                oversize.append((path.relative_to(ROOT), line_count))
        except Exception as e:
            print(f"⚠️  Error reading {path.relative_to(ROOT)}: {e}", file=sys.stderr)

    return sorted(oversize, key=lambda x: x[1], reverse=True)


def should_skip_link(link_path: str) -> bool:
    """Check if a link should be skipped during validation."""
    skip_prefixes = ("http://", "https://", "#", "@")
    return link_path.startswith(skip_prefixes)


def resolve_link_target(source_path: pathlib.Path, link_path: str) -> pathlib.Path:
    """Resolve a relative link path to an absolute path."""
    return (source_path.parent / link_path).resolve()


def check_broken_links() -> List[Tuple[pathlib.Path, str, str]]:
    """Check for broken internal links in markdown files."""
    broken = []
    link_pattern = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")

    for path in GARDEN.rglob("*.md"):
        if path.name.startswith("."):
            continue

        try:
            content = path.read_text(encoding="utf-8")

            for match in link_pattern.finditer(content):
                link_text = match.group(1)
                link_path = match.group(2)

                if should_skip_link(link_path):
                    continue

                target = resolve_link_target(path, link_path)

                if not target.exists():
                    broken.append((path.relative_to(ROOT), link_text, link_path))
        except Exception as e:
            print(
                f"⚠️  Error checking links in {path.relative_to(ROOT)}: {e}",
                file=sys.stderr,
            )

    return broken


def count_files() -> dict:
    """Count files in each garden directory."""
    counts = {}

    for subdir in ["patterns", "standards", "architecture", "quick-references", "commands"]:
        dir_path = GARDEN / subdir
        if dir_path.exists():
            md_files = list(dir_path.glob("*.md"))
            counts[subdir] = len(md_files)

    return counts


def main():
    parser = argparse.ArgumentParser(description="Check knowledge garden health")
    parser.add_argument(
        "--max-lines",
        type=int,
        default=DEFAULT_MAX_LINES,
        help=f"Maximum lines per file (default: {DEFAULT_MAX_LINES})",
    )
    parser.add_argument(
        "--check-links", action="store_true", help="Check for broken internal links"
    )
    parser.add_argument("--verbose", action="store_true", help="Show detailed output")

    args = parser.parse_args()

    print("🌱 Checking Knowledge Garden Health...\n")

    # Check file sizes
    print(f"📏 Checking file sizes (max: {args.max_lines} lines)...")
    oversize = check_file_sizes(args.max_lines)

    if oversize:
        print(f"⚠️  Found {len(oversize)} oversize files:\n")
        for path, lines in oversize:
            print(f"  {path} ({lines} lines)")
        print()
    else:
        print("✅ All files within size limit\n")

    # Check broken links (optional)
    if args.check_links:
        print("🔗 Checking for broken links...")
        broken = check_broken_links()

        if broken:
            print(f"⚠️  Found {len(broken)} broken links:\n")
            for path, text, link in broken:
                print(f"  {path}")
                print(f"    Link: [{text}]({link})")
            print()
        else:
            print("✅ No broken links found\n")

    # Show file counts
    if args.verbose:
        print("📊 File counts by directory:")
        counts = count_files()
        total = 0
        for subdir, count in sorted(counts.items()):
            print(f"  {subdir}: {count} files")
            total += count
        print(f"  Total: {total} files\n")

    # Exit with error if issues found
    if oversize or (args.check_links and broken):
        print("❌ Garden health check failed")
        sys.exit(1)
    else:
        print("✅ Garden is healthy!")
        sys.exit(0)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Generate INDEX.md from the knowledge garden structure.

This script scans the .claude/ directory and generates a comprehensive
index of all documentation files, organized by category.
"""

import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple


def extract_metadata(file_path: Path) -> Tuple[str, str, str]:
    """Extract title, status, and first line description from a markdown file."""
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Extract title (first # heading)
    title_match = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
    title = title_match.group(1) if title_match else file_path.stem

    # Extract status from metadata block
    status_match = re.search(r">\s*\*\*Status\*\*:\s*(\w+)", content)
    status = status_match.group(1) if status_match else "Active"

    # Extract overview/description
    overview_match = re.search(r"##\s+Overview\s+(.+?)(?=\n##|\Z)", content, re.DOTALL)
    if overview_match:
        description = overview_match.group(1).strip().split("\n")[0]
        # Clean up markdown formatting
        description = re.sub(r"\[([^\]]+)\]\([^\)]+\)", r"\1", description)
        description = re.sub(r"\*\*([^\*]+)\*\*", r"\1", description)
        description = description[:150] + "..." if len(description) > 150 else description
    else:
        description = ""

    return title, status, description


def scan_directory(base_path: Path, category: str) -> List[Dict]:
    """Scan a directory and return list of files with metadata."""
    files = []
    category_path = base_path / category

    if not category_path.exists():
        return files

    for file_path in sorted(category_path.glob("*.md")):
        if file_path.name == "README.md":
            continue

        title, status, description = extract_metadata(file_path)

        files.append(
            {
                "name": file_path.name,
                "path": f"{category}/{file_path.name}",
                "title": title,
                "status": status,
                "description": description,
            }
        )

    return files


def count_files_by_status(all_files: List[Dict]) -> tuple:
    """Count total, active, and deprecated files."""
    total = len(all_files)
    active = sum(1 for f in all_files if f["status"] == "Active")
    deprecated = sum(1 for f in all_files if f["status"] == "Deprecated")
    return total, active, deprecated


def format_file_list(files: List[Dict]) -> str:
    """Format a list of files as markdown."""
    result = ""
    for file in files:
        status_emoji = "⚠️" if file["status"] == "Deprecated" else ""
        result += f"- **[{file['title']}]({file['path']})** {status_emoji}\n"
        if file["description"]:
            result += f"  - {file['description']}\n"
    return result


def generate_index(base_path: Path) -> str:
    """Generate the complete INDEX.md content."""

    # Scan all categories
    patterns = scan_directory(base_path, "patterns")
    standards = scan_directory(base_path, "standards")
    architecture = scan_directory(base_path, "architecture")
    quick_refs = scan_directory(base_path, "quick-references")
    commands = scan_directory(base_path, "commands")

    # Count statistics
    all_files = patterns + standards + architecture + quick_refs + commands
    total_files, active_files, deprecated_files = count_files_by_status(all_files)

    # Generate content
    content = f"""# AIMQ Knowledge Base Index

> Your comprehensive guide to building AIMQ together 🚀

**Last Updated**: {datetime.now().strftime('%Y-%m-%d')}

## 🎯 Start Here

- **[agents.md](../agents.md)** - Quick reference guide for AI agents (START HERE!)
- **[CONSTITUTION.md](../CONSTITUTION.md)** - Our guiding principles and non-negotiables
- **[PLAN.md](../PLAN.md)** - Current status and next steps (working memory)
- **[CLAUDE.md](../CLAUDE.md)** - Comprehensive technical documentation
- **[GARDENING.md](../GARDENING.md)** - Knowledge garden philosophy and cultivation

## 📊 Garden Statistics

- **Total Files**: {total_files} markdown files
- **Active**: {active_files} files
- **Deprecated**: {deprecated_files} files (kept for reference)
- **Categories**: 5 (patterns, standards, architecture, quick-references, commands)

## 📁 Knowledge Base Structure

### Patterns (`patterns/`)

Established patterns for consistency across the codebase.

"""

    # Add file listings
    content += format_file_list(patterns)
    content += "\n### Standards (`standards/`)\n\n"
    content += "Best practices for coding, testing, git workflow, and more.\n\n"
    content += format_file_list(standards)
    content += "\n### Architecture (`architecture/`)\n\n"
    content += "System design and library references.\n\n"
    content += format_file_list(architecture)
    content += "\n### Quick References (`quick-references/`)\n\n"
    content += "Fast guidance for common tasks.\n\n"
    content += format_file_list(quick_refs)
    content += "\n### Commands (`commands/`)\n\n"
    content += "Custom workflow commands for development, planning, and knowledge management.\n\n"
    content += format_file_list(commands)

    content += """
### Templates (`templates/`)

Standard templates for creating consistent documentation.

- **[Templates README](templates/README.md)** - Usage guidelines and available templates

## 🗺️ Navigation Guide

### I want to...

#### Learn the Basics
1. Read [agents.md](../agents.md) for quick overview
2. Read [CONSTITUTION.md](../CONSTITUTION.md) for principles
3. Read [architecture/aimq-overview.md](architecture/aimq-overview.md) for architecture

#### Write Code
1. Check [patterns/module-organization.md](patterns/module-organization.md) for where to put code
2. Check [standards/code-style.md](standards/code-style.md) for style guide
3. Check [patterns/error-handling.md](patterns/error-handling.md) for error patterns

#### Test Code
1. Check [quick-references/testing.md](quick-references/testing.md) for commands
2. Check [standards/testing.md](standards/testing.md) for patterns
3. Run `just test-cov` to check coverage

#### Commit Changes
1. Check [standards/conventional-commits.md](standards/conventional-commits.md) for format
2. Check [quick-references/git-commands.md](quick-references/git-commands.md) for commands
3. Use `/commit` command for help

#### Work with Dependencies
1. Check [quick-references/dependency-management.md](quick-references/dependency-management.md)
2. Always use `uv` (never pip/poetry)
3. Run `uv add package-name` to add dependencies

#### Understand Architecture
1. Read [architecture/aimq-overview.md](architecture/aimq-overview.md)
2. Read [architecture/langchain-integration.md](architecture/langchain-integration.md)
3. Read [architecture/langgraph-integration.md](architecture/langgraph-integration.md)

## 🔄 Maintenance Guidelines

### Keep It Updated
- Update docs when you change architecture
- Document new patterns as they emerge
- Keep PLAN.md current with progress
- Review CONSTITUTION.md regularly

### Keep It Clean
- Remove outdated information (or mark as deprecated)
- Consolidate duplicate content
- Keep files under 400 lines
- Use links to avoid duplication

### Keep It Concise
- Focus on "how-to" over "what is"
- Use examples and code snippets
- Link to external docs for details
- One topic per file

### Keep It Shallow
- No nested directories in .claude/
- Just markdown files in each folder
- Use links to connect topics
- Build a knowledge graph, not a tree

## 🎓 Learning Path

### Day 1: Foundations
1. Read [agents.md](../agents.md)
2. Read [CONSTITUTION.md](../CONSTITUTION.md)
3. Read [architecture/aimq-overview.md](architecture/aimq-overview.md)
4. Run `just test` to see tests pass

### Day 2: Development
1. Read [patterns/module-organization.md](patterns/module-organization.md)
2. Read [standards/code-style.md](standards/code-style.md)
3. Read [standards/testing.md](standards/testing.md)
4. Write your first test

### Day 3: Workflow
1. Read [standards/git-workflow.md](standards/git-workflow.md)
2. Read [standards/conventional-commits.md](standards/conventional-commits.md)
3. Make your first commit with `/commit` command
4. Create your first PR

### Day 4: Advanced
1. Read [architecture/langchain-integration.md](architecture/langchain-integration.md)
2. Read [architecture/langgraph-integration.md](architecture/langgraph-integration.md)
3. Read [patterns/error-handling.md](patterns/error-handling.md)
4. Build your first agent or workflow

## 🤝 Contributing to Knowledge Base

When you discover something new:

1. **Document it**: Add to appropriate section
2. **Link it**: Cross-reference related docs
3. **Keep it concise**: Under 400 lines
4. **Update index**: Run `python .claude/scripts/generate_index.py`
5. **Commit it**: Use conventional commits

## 🌟 Remember

**We're not just writing code—we're building the future together!**

Every line of documentation makes us smarter. Every pattern we establish makes us more consistent. Every standard we follow makes us more professional.

You're amazing, and together we're unstoppable! 💪✨

---

**Maintainers**: Human + AI Team 🚀
**Auto-generated**: This file is generated by `.claude/scripts/generate_index.py`
"""

    return content


def main():
    """Main entry point."""
    # Get the .claude directory
    script_dir = Path(__file__).parent
    claude_dir = script_dir.parent

    # Generate index
    index_content = generate_index(claude_dir)

    # Write to INDEX.md
    index_path = claude_dir / "INDEX.md"
    with open(index_path, "w", encoding="utf-8") as f:
        f.write(index_content)

    print(f"✅ Generated {index_path}")
    print(f"📊 Total files indexed: {len(index_content.splitlines())}")


if __name__ == "__main__":
    main()

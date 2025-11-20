# Knowledge Garden Hooks

Automation scripts for maintaining the knowledge garden.

## Available Hooks

### check_garden.py

Check the health of the knowledge garden.

**Usage:**
```bash
# Basic check (files over 380 lines)
python .claude/hooks/check_garden.py

# Custom line limit
python .claude/hooks/check_garden.py --max-lines 400

# Check for broken links
python .claude/hooks/check_garden.py --check-links

# Verbose output with file counts
python .claude/hooks/check_garden.py --verbose

# All checks
python .claude/hooks/check_garden.py --check-links --verbose
```

**What it checks:**
- ✅ Files exceeding line limit (default: 380 lines)
- ✅ Broken internal links (optional with `--check-links`)
- ✅ File counts by directory (with `--verbose`)

**Exit codes:**
- `0` - Garden is healthy
- `1` - Issues found

## Integration

### Manual Usage

Run before committing:
```bash
python .claude/hooks/check_garden.py
```

### With Git Hooks

Add to `.git/hooks/pre-commit`:
```bash
#!/bin/bash
python .claude/hooks/check_garden.py || exit 1
```

### With CI/CD

Add to your CI pipeline:
```yaml
- name: Check Garden Health
  run: python .claude/hooks/check_garden.py --check-links --verbose
```

### With Just

Add to `justfile`:
```just
# Check knowledge garden health
check-garden:
    python .claude/hooks/check_garden.py --verbose

# Check garden with link validation
check-garden-full:
    python .claude/hooks/check_garden.py --check-links --verbose
```

## Future Hooks

Potential hooks to add:

- **validate_structure.py** - Ensure proper directory structure
- **check_cross_links.py** - Verify all files have "Related" sections
- **generate_index.py** - Auto-generate INDEX.md from files
- **check_duplicates.py** - Find duplicate content
- **validate_frontmatter.py** - Check YAML frontmatter consistency

## Related

- [@.claude/architecture/knowledge-systems-workflow.md](../architecture/knowledge-systems-workflow.md) - Gardening workflow
- [@.claude/commands/cultivate.md](../commands/cultivate.md) - Cultivation command
- [@GARDENING.md](../../GARDENING.md) - Gardening philosophy

---

**Remember**: Automation helps, but human judgment is essential! 🤖✨

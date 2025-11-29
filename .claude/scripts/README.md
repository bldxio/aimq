# Knowledge Garden Scripts

> Automation scripts for maintaining the knowledge garden

## Available Scripts

### generate_index.py

Automatically generates `INDEX.md` from the knowledge garden structure.

**Usage:**
```bash
python .claude/scripts/generate_index.py
```

**What it does:**
- Scans all markdown files in patterns/, standards/, architecture/, quick-references/, and commands/
- Extracts metadata (title, status, description) from each file
- Generates a comprehensive INDEX.md with:
  - File listings organized by category
  - Status indicators (Active, Deprecated, Experimental)
  - Brief descriptions
  - Statistics (total files, active files, deprecated files)
  - Navigation guides
  - Learning paths

**When to run:**
- After adding new files to the garden
- After updating file metadata (status, title, description)
- During weekly garden maintenance (`/cultivate`)
- Before committing major documentation changes

**Output:**
- Overwrites `.claude/INDEX.md` with fresh content
- Marks deprecated files with ⚠️ emoji
- Includes auto-generation timestamp

## Adding New Scripts

When adding new automation scripts:

1. **Create the script** in this directory
2. **Make it executable**: `chmod +x script_name.py`
3. **Add documentation** to this README
4. **Test thoroughly** before committing
5. **Update `/cultivate` command** if it should run automatically

## Related

- [/cultivate command](../commands/cultivate.md) - Garden maintenance workflow
- [GARDENING.md](../../GARDENING.md) - Knowledge garden philosophy
- [INDEX.md](../INDEX.md) - Auto-generated index

---

**Remember**: Automation helps you helps me! 🤖✨

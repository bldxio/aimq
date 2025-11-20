# Knowledge Systems Workflow

How to maintain and grow your knowledge garden over time.

## Gardening Workflow

### 1. Capture (Daily)

As you work, capture insights:

```bash
# After solving a problem
/remember "Workers should catch all exceptions in the main loop"

# After learning something
/remember "Mock external services for reliable tests"

# After making a decision
/remember "Chose exponential backoff for retries because..."
```

### 2. Learn (Weekly)

Extract lessons from recent work:

```bash
# Review recent work
/learn

# Focus on specific area
/learn "focus on testing patterns"

# Learn from failures
/learn "what went wrong and how we fixed it"
```

### 3. Organize (Monthly)

Keep the garden healthy:

```bash
# Review and organize
/cultivate

# Check for duplicates
# Merge related content
# Remove outdated info
# Update links
```

### 4. Explore (As Needed)

Find relevant knowledge:

```bash
# Explore a topic
/focus "error handling"

# Research new topics
/levelup "LangGraph memory"

# Review progress
/plan
```

## Best Practices

### ✅ Do

- **Capture while fresh** - Don't wait
- **Keep files small** - Under 400 lines
- **Link everything** - Build a knowledge graph
- **Use examples** - Show, don't just tell
- **Update regularly** - Knowledge evolves
- **Prune aggressively** - Remove outdated content
- **Make it searchable** - Use clear headings

### ❌ Don't

- Don't wait to document
- Don't write novels (keep it concise)
- Don't duplicate content
- Don't use jargon without explanation
- Don't let it get stale
- Don't hoard outdated info
- Don't bury important info

## Real-World Example

From our project:

**Before Knowledge System**:
- Lessons in chat history
- Patterns in code comments
- Decisions undocumented
- Context lost over time

**After Knowledge System**:
- 12 pattern documents
- 7 standard documents
- 7 architecture documents
- 8 quick reference guides
- 12 helper commands

**Result**:
- Faster onboarding
- Fewer repeated mistakes
- Better decisions
- Clearer direction
- Shared understanding

## Measuring Success

### Quantitative

- Number of documents
- Lines of documentation
- Links between documents
- Update frequency
- Usage in conversations

### Qualitative

- Easier onboarding?
- Fewer repeated questions?
- Better decisions?
- More consistent code?
- Faster problem solving?

## Evolution

### Phase 1: Bootstrap (Week 1)

Create initial structure:
- CONSTITUTION.md
- VISION.md
- .claude/ folders
- PLAN.md
- README updates

### Phase 2: Populate (Month 1)

Add core knowledge:
- Key patterns
- Essential standards
- Architecture docs
- Quick references

### Phase 3: Refine (Month 2-3)

Improve quality:
- Add examples
- Link content
- Remove duplicates
- Update outdated info

### Phase 4: Maintain (Ongoing)

Keep it healthy:
- Weekly reviews
- Monthly cultivation
- Continuous updates
- Regular pruning

## Tools and Commands

### Helper Commands

Use these to manage the garden:

- `/remember` - Capture insights
- `/learn` - Extract lessons
- `/focus` - Explore topics
- `/levelup` - Research new topics
- `/plan` - Review progress
- `/cultivate` - Maintain garden
- `/seed` - Bootstrap new knowledge system

### File Operations

```bash
# Find files
fd pattern .claude/

# Search content
rg "search term" .claude/

# Count files
fd . .claude/ | wc -l

# Check file sizes
fd . .claude/ -x wc -l

# Check for large files
fd . .claude/ -x wc -l | awk '$1 > 400 {print}'
```

## Maintenance Checklist

### Weekly
- [ ] Run `/learn` to extract lessons
- [ ] Update PLAN.md with progress
- [ ] Capture new insights with `/remember`
- [ ] Review recent commits for patterns

### Monthly
- [ ] Run `/cultivate` to organize
- [ ] Check for files over 400 lines
- [ ] Remove outdated content
- [ ] Update cross-links
- [ ] Verify patterns match code
- [ ] Update INDEX.md if needed

### Quarterly
- [ ] Review CONSTITUTION.md
- [ ] Update VISION.md
- [ ] Audit all documentation
- [ ] Consolidate duplicate content
- [ ] Measure success metrics
- [ ] Plan improvements

## Related

- [@.claude/architecture/knowledge-systems-overview.md](./knowledge-systems-overview.md) - Philosophy and hierarchy
- [@.claude/architecture/knowledge-systems-templates.md](./knowledge-systems-templates.md) - File templates
- [@.claude/architecture/knowledge-systems.md](./knowledge-systems.md) - Complete guide
- [@GARDENING.md](../../GARDENING.md) - Gardening philosophy
- [@.claude/commands/cultivate.md](../commands/cultivate.md) - Cultivation command
- [@.claude/commands/learn.md](../commands/learn.md) - Learning command
- [@.claude/commands/remember.md](../commands/remember.md) - Remember command

---

**Remember**: A knowledge garden is never finished, it's always growing! 🌱✨

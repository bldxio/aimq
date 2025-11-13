---
description: Cultivate the knowledge garden through maintenance and organization
---

# Cultivate Helper

Cultivate the knowledge garden by organizing, linking, verifying, and keeping it healthy.

## Overview

This command helps maintain the knowledge garden by:
1. Organizing content logically
2. Creating links between related topics
3. Verifying patterns match actual code
4. Distilling and summarizing content
5. Weeding out outdated information
6. Keeping files manageable (<400 lines)
7. Ensuring easy navigation

## Usage

```
/cultivate
```

Performs comprehensive garden cultivation and maintenance.

## Task List

### Step 1: Survey the Garden

Get an overview of the current state:

```bash
# Count files in each category
echo "Patterns: $(fd -e md . .claude/patterns/ | wc -l)"
echo "Standards: $(fd -e md . .claude/standards/ | wc -l)"
echo "Architecture: $(fd -e md . .claude/architecture/ | wc -l)"
echo "Quick Refs: $(fd -e md . .claude/quick-references/ | wc -l)"

# Check file sizes
fd -e md . .claude/ -x wc -l {} \; | sort -rn | head -20

# List all files
fd -e md . .claude/
```

**Assess**:
- How many files in each category?
- Are any files too large (>400 lines)?
- Is the structure clear?
- Are files well-named?

### Step 2: Check File Sizes

Identify files that need splitting:

```bash
# Find large files
fd -e md . .claude/ -x sh -c 'lines=$(wc -l < "$1"); if [ $lines -gt 400 ]; then echo "$lines $1"; fi' _ {} \; | sort -rn
```

**For files >400 lines**:
- Identify logical sections
- Split into multiple files
- Create index file if needed
- Update links

**Example split**:
```
Before:
- testing.md (600 lines)

After:
- testing-overview.md (200 lines)
- testing-mocks.md (150 lines)
- testing-fixtures.md (150 lines)
- testing-parametrize.md (100 lines)
```

### Step 3: Verify Against Code

Check if documented patterns match actual code:

**For each pattern**:
1. Find examples in codebase
2. Compare with documented pattern
3. Note discrepancies
4. Decide: update docs or update code?

```bash
# Search for pattern usage
rg "pattern_keyword" src/

# Compare with documented pattern
cat .claude/patterns/pattern-name.md
```

**Create verification report**:
```
📋 Pattern Verification

## Patterns Matching Code ✅
- error-handling.md: Matches worker implementation
- testing-mocks.md: Matches test patterns
- module-structure.md: Matches current structure

## Patterns Needing Updates ⚠️
- retry-logic.md: Code uses exponential backoff, docs show linear
  → Update docs to match code

## Patterns Not Used ❌
- singleton-pattern.md: No usage found in codebase
  → Consider removing or marking as reference

## Code Not Documented 💡
- Checkpoint pattern in memory/checkpoint.py
  → Should document this pattern
```

### Step 4: Organize and Link

Create connections between related content:

**Add "Related" sections**:
```markdown
## Related
- [Error Logging](../standards/error-logging.md)
- [Worker Design](../architecture/worker-design.md)
- [Testing Error Paths](../standards/testing.md#error-paths)
```

**Create index files**:
```markdown
# Patterns Index

## Error Handling
- [Graceful Error Handling](./graceful-error-handling.md)
- [Retry Logic](./retry-logic.md)
- [Circuit Breaker](./circuit-breaker.md)

## Testing
- [Testing Mocks](./testing-mocks.md)
- [Parametrized Tests](./parametrized-tests.md)
- [Test Fixtures](./test-fixtures.md)
```

**Build knowledge graph**:
```
Error Handling
├── Patterns
│   ├── Graceful Error Handling
│   ├── Retry Logic
│   └── Circuit Breaker
├── Standards
│   ├── Error Logging
│   └── Exception Handling
└── Architecture
    └── Worker Design
```

### Step 5: Distill and Summarize

Simplify verbose content:

**Before** (verbose):
```markdown
When you are implementing error handling in your worker processes,
it is very important to remember that you should always catch
exceptions and log them properly instead of letting them propagate
up the call stack which could cause the entire worker process to
crash and stop processing jobs...
```

**After** (concise):
```markdown
## Error Handling in Workers

**Rule**: Catch and log exceptions, don't let them crash the worker.

**Why**: Keeps the worker running even when individual jobs fail.

**How**:
```python
try:
    process_job(job)
except Exception as e:
    logger.error(f"Job failed: {e}", exc_info=True)
```
```

**Distillation checklist**:
- Remove redundant explanations
- Use bullet points over paragraphs
- Show code over prose
- Keep examples concise
- Link to details instead of including them

### Step 6: Weed Out Outdated Content

Remove or update obsolete information:

**Check for**:
- Deprecated patterns
- Old technology versions
- Superseded approaches
- Unused patterns
- Incorrect information

**Actions**:
- **Remove**: If no longer relevant
- **Archive**: If historically interesting
- **Update**: If still relevant but changed
- **Mark**: If deprecated but still in use

**Example**:
```markdown
# Old Pattern (Deprecated)

> ⚠️ **Deprecated**: This pattern is no longer used.
> See [New Pattern](./new-pattern.md) instead.

[Keep for reference but mark clearly]
```

### Step 7: Improve Discoverability

Make content easy to find:

**File naming**:
- Use clear, descriptive names
- Use kebab-case
- Be specific
- Avoid abbreviations

**Good names**:
- `graceful-error-handling.md`
- `testing-with-mocks.md`
- `worker-design-decisions.md`

**Bad names**:
- `pattern1.md`
- `stuff.md`
- `notes.md`

**Add descriptions**:
```markdown
---
description: How to handle errors gracefully in worker processes
tags: [error-handling, workers, resilience]
---
```

**Create README files**:
```markdown
# Patterns

This directory contains reusable code patterns and design patterns.

## Categories
- [Error Handling](#error-handling)
- [Testing](#testing)
- [Architecture](#architecture)

## Error Handling
- [Graceful Error Handling](./graceful-error-handling.md) - Never crash the worker
- [Retry Logic](./retry-logic.md) - Exponential backoff for retries
```

### Step 8: Check Consistency

Ensure consistent formatting and style:

**Formatting checklist**:
- [ ] All files use same heading levels
- [ ] Code blocks have language specified
- [ ] Links use relative paths
- [ ] Examples are complete and runnable
- [ ] Sections follow consistent order

**Style checklist**:
- [ ] Tone is consistent (encouraging, concise)
- [ ] Terminology is consistent
- [ ] Examples use project conventions
- [ ] Structure matches templates

### Step 9: Create Maintenance Report

Document what was done:

```
🌱 Garden Maintenance Report

**Date**: 2025-11-12

## Summary
- 📁 Files: 23 total (5 patterns, 6 standards, 4 architecture, 8 quick-refs)
- 📏 Average size: 180 lines
- 🔗 Links added: 15
- ✂️ Files split: 2
- 🗑️ Files removed: 1
- ✅ Patterns verified: 5/5

## Actions Taken

### Organization
- Split testing.md into 3 focused files
- Created patterns/README.md index
- Renamed vague-notes.md to worker-error-handling.md

### Verification
- ✅ All patterns match current code
- Updated retry-logic.md to match implementation
- Documented checkpoint pattern (was missing)

### Linking
- Added "Related" sections to 8 files
- Created knowledge graph in architecture/overview.md
- Linked all error handling content

### Cleanup
- Removed deprecated singleton-pattern.md
- Updated outdated testing examples
- Distilled verbose content in 4 files

### Improvements
- All files now <400 lines ✅
- Added descriptions to all files ✅
- Consistent formatting ✅
- Easy to navigate ✅

## Recommendations

### Immediate
- None - garden is healthy! 🌱

### Future
- Consider adding more testing patterns
- Document deployment patterns
- Create troubleshooting guides

## Next Maintenance
Recommended: In 2 weeks or after major changes
```

### Step 10: Create Cleanup Tasks (If Needed)

If issues found, add to PLAN.md:

```markdown
## Knowledge Garden Cleanup

**Priority**: Medium
**Effort**: 2-3 hours

### Issues Found
1. **Code-Documentation Mismatch**
   - retry-logic.md doesn't match implementation
   - Decision: Update docs to match code

2. **Missing Documentation**
   - Checkpoint pattern not documented
   - Should add to patterns/

3. **Outdated Content**
   - Old testing examples using deprecated API
   - Need to update

### Tasks
- [ ] Update retry-logic.md
- [ ] Document checkpoint pattern
- [ ] Update testing examples
- [ ] Verify all patterns against code

**Question**: Should we update docs or code?
- Docs: Faster, preserves working code
- Code: Better if docs represent ideal state
```

## Maintenance Strategies

### Strategy 1: Regular Pruning
- Review monthly
- Remove dead content
- Update changed patterns
- Keep it current

### Strategy 2: Continuous Verification
- Check patterns when code changes
- Update docs with code
- Keep them in sync
- Prevent drift

### Strategy 3: Growth Management
- Split large files
- Create indexes
- Maintain structure
- Prevent sprawl

### Strategy 4: Link Cultivation
- Add links as you learn
- Connect related topics
- Build knowledge graph
- Improve navigation

## Best Practices

### 1. Keep It Manageable
- Files under 400 lines
- Clear structure
- Easy to navigate
- Not overwhelming

### 2. Stay Truthful
- Docs match code
- Remove outdated content
- Update when things change
- Verify regularly

### 3. Make It Useful
- Actionable content
- Clear examples
- Easy to find
- Practical focus

### 4. Maintain Regularly
- Don't let it grow wild
- Prune regularly
- Organize continuously
- Keep it healthy

### 5. Encourage Growth
- Add new learnings
- Document patterns
- Capture insights
- Let it evolve

### 6. Collaborate
- Discuss major changes
- Get feedback
- Share decisions
- Work together

## Examples

### Example 1: Full Garden Maintenance

**Command**: `/cultivate`

**Output**:
```
🌱 Tending the knowledge garden...

**Current State**:
- 23 files total
- Average size: 180 lines
- Largest file: testing.md (450 lines) ⚠️

**Checking file sizes...**
- testing.md: 450 lines → Should split
- error-handling.md: 380 lines → OK
- All others: <300 lines ✅

**Verifying patterns against code...**
- graceful-error-handling.md: ✅ Matches worker.py
- testing-mocks.md: ✅ Matches test patterns
- retry-logic.md: ⚠️ Docs show linear, code uses exponential

**Checking links...**
- 15 files have "Related" sections ✅
- 8 files missing links ⚠️

**Recommendations**:

1. **Split testing.md** (450 lines)
   - testing-overview.md
   - testing-mocks.md
   - testing-fixtures.md

2. **Update retry-logic.md**
   - Change to exponential backoff
   - Match current implementation

3. **Add links to 8 files**
   - Connect related patterns
   - Build knowledge graph

Should I proceed with these improvements?
```

### Example 2: Verification Focus

**Command**: `/cultivate` (focusing on verification)

**Output**:
```
🌱 Verifying patterns against code...

**Checking each pattern**:

✅ graceful-error-handling.md
- Found in: src/aimq/worker.py
- Matches: Yes
- Example: Lines 45-52

✅ testing-mocks.md
- Found in: tests/aimq/test_worker.py
- Matches: Yes
- Example: Lines 10-15

⚠️ retry-logic.md
- Found in: src/aimq/queue.py
- Matches: No
- Issue: Docs show linear backoff, code uses exponential
- Recommendation: Update docs to match code

❌ singleton-pattern.md
- Found in: Nowhere
- Matches: N/A
- Issue: Pattern not used in codebase
- Recommendation: Remove or mark as reference

💡 checkpoint pattern
- Found in: src/aimq/memory/checkpoint.py
- Documented: No
- Recommendation: Should document this pattern

**Summary**:
- 2 patterns verified ✅
- 1 needs update ⚠️
- 1 not used ❌
- 1 missing documentation 💡

Should I:
1. Update retry-logic.md?
2. Remove singleton-pattern.md?
3. Document checkpoint pattern?
```

### Example 3: Organization Focus

**Command**: `/cultivate` (focusing on organization)

**Output**:
```
🌱 Organizing the knowledge garden...

**Current Structure**:
```
.claude/
├── patterns/ (5 files)
├── standards/ (6 files)
├── architecture/ (4 files)
└── quick-references/ (8 files)
```

**Issues Found**:

1. **No index files**
   - Hard to discover content
   - No overview of what's available

2. **Weak linking**
   - Only 15/23 files have "Related" sections
   - Knowledge graph incomplete

3. **Inconsistent naming**
   - Some use underscores, some use hyphens
   - Some too vague (notes.md, stuff.md)

**Improvements**:

1. **Create index files**
   - patterns/README.md
   - standards/README.md
   - architecture/README.md
   - quick-references/README.md

2. **Add links**
   - Connect error handling content
   - Link testing patterns
   - Build knowledge graph

3. **Rename files**
   - notes.md → worker-error-handling.md
   - stuff.md → testing-utilities.md

Should I make these improvements?
```

## Error Handling

### Garden Too Large
**Solution**:
- Prioritize by category
- Split into phases
- Focus on high-impact areas
- Don't try to fix everything at once

### Unclear What to Keep
**Solution**:
- Check usage in code
- Ask user about relevance
- Mark as deprecated if unsure
- Can always restore from git

### Code-Docs Conflict
**Solution**:
- Present both versions
- Explain the difference
- Ask which is correct
- Update accordingly

### Too Much to Fix
**Solution**:
- Create task list in PLAN.md
- Prioritize by impact
- Fix incrementally
- Track progress

## Reusability

This command works across:
- Any project with a knowledge garden
- Any programming language
- Any team size
- Any agent or AI assistant

The key is to:
- Maintain regularly
- Keep it truthful
- Make it useful
- Let it grow healthily

---

**Remember**: A well-tended garden is a joy to explore! 🌱✨

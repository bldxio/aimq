---
description: Extract lessons from conversation and git history
---

# Learn Helper

Analyze recent work to extract patterns, lessons, and insights for the knowledge garden.

## Overview

This command helps learn from experience by:
1. Analyzing recent conversation for patterns
2. Reviewing git commit history for lessons
3. Identifying what went wrong and how it was fixed
4. Extracting reusable knowledge
5. Adding insights to the knowledge garden

## Usage

### Without Arguments
```
/learn
```
Analyzes current conversation and recent git history for lessons learned.

### With Arguments
```
/learn <guidance or focus area>
```
Uses the provided guidance to focus the learning process.

## Task List

### Step 1: Analyze Current Conversation

Review the conversation for:

**Successful patterns**:
- Solutions that worked well
- Approaches that were effective
- Decisions that paid off
- Techniques that helped

**Challenges faced**:
- Problems encountered
- Obstacles overcome
- Mistakes made
- Dead ends explored

**Insights gained**:
- Understanding deepened
- Assumptions challenged
- New perspectives
- Aha moments

**Decisions made**:
- Why we chose X over Y
- Trade-offs accepted
- Priorities set
- Direction changes

### Step 2: Review Git History

Analyze recent commits for patterns:

```bash
# Get recent commits with details
git log --oneline -20

# Get commit messages and stats
git log --stat -10

# Look for fix commits
git log --oneline --grep="fix" -10

# Look for refactor commits
git log --oneline --grep="refactor" -10

# See what changed recently
git diff HEAD~10..HEAD --stat
```

**Look for**:
- **Fix commits**: What broke and how was it fixed?
- **Refactor commits**: What improved and why?
- **Feature commits**: What patterns emerged?
- **Test commits**: What testing approaches worked?
- **Revert commits**: What didn't work?

### Step 3: Identify Patterns

Categorize learnings:

**Technical Patterns**:
- Code patterns that worked
- Architecture decisions
- Design approaches
- Implementation techniques

**Process Patterns**:
- Development workflow
- Testing strategies
- Debugging approaches
- Problem-solving methods

**Mistakes and Fixes**:
- What went wrong
- Why it went wrong
- How it was fixed
- How to prevent it

**Best Practices**:
- What works well
- What to avoid
- When to use what
- Trade-offs to consider

### Step 4: Extract Lessons

For each pattern, create a lesson:

**Lesson format**:
```markdown
# [Lesson Title]

## What Happened
[Describe the situation]

## What We Learned
[The key insight or lesson]

## Why It Matters
[Impact and importance]

## How to Apply
[Actionable guidance]

## Example
[Concrete example from the code]

## Related
- [Links to related lessons]
```

### Step 5: Analyze Specific Commits

For interesting commits, dig deeper:

```bash
# Show full commit details
git show <commit-hash>

# See what changed
git diff <commit-hash>^..<commit-hash>

# Find related commits
git log --all --grep="<keyword>"
```

**Questions to ask**:
- Why was this change needed?
- What problem did it solve?
- What approach was taken?
- What alternatives were considered?
- What was the outcome?

### Step 6: Look for Anti-Patterns

Identify things that didn't work:

**Common anti-patterns**:
- Code that was reverted
- Bugs that recurred
- Performance issues
- Complexity that grew
- Tests that were flaky

**For each anti-pattern**:
- What was the mistake?
- Why did it happen?
- How was it fixed?
- How to avoid it?

### Step 7: Categorize Learnings

Determine where each lesson belongs:

**Patterns** (`.claude/patterns/`):
- Reusable code solutions
- Design patterns discovered
- Architecture patterns that worked

**Standards** (`.claude/standards/`):
- Best practices identified
- Conventions that emerged
- Guidelines that helped

**Architecture** (`.claude/architecture/`):
- Design decisions made
- System insights gained
- Integration lessons

**Quick References** (`.claude/quick-references/`):
- Troubleshooting guides
- Common pitfalls
- How-to guides

### Step 8: Present Learnings

Show what was learned:

```
📚 Lessons learned from recent work:

**From Conversation**:
1. **Pattern**: Graceful Error Handling
   - Workers should catch and log errors, not crash
   - Keeps system stable under failure
   - Add to: .claude/patterns/error-handling.md

2. **Lesson**: Mock External Dependencies
   - Tests with real APIs are slow and flaky
   - Mocking makes tests fast and reliable
   - Add to: .claude/standards/testing.md

**From Git History** (last 10 commits):
3. **Fix Pattern**: Type Errors in Tests
   - Commit abc123: Fixed None type errors
   - Lesson: Always check for None before accessing
   - Add to: .claude/quick-references/common-pitfalls.md

4. **Refactor Insight**: Module Organization
   - Commit def456: Split monolithic module
   - Lesson: Keep modules focused and small
   - Add to: .claude/architecture/module-design.md

5. **Anti-Pattern**: Re-raising Exceptions
   - Commit ghi789: Removed exception re-raising
   - Problem: Caused worker crashes
   - Solution: Log and continue
   - Add to: .claude/patterns/error-handling.md

**Summary**:
- 5 lessons extracted
- 3 patterns identified
- 2 anti-patterns avoided
- Ready to add to knowledge garden

Should I add these learnings?
```

### Step 9: Add to Knowledge Garden

For approved learnings:
- Create or update files
- Add examples from actual code
- Link related content
- Keep it organized

### Step 10: Suggest Follow-up

Based on learnings, suggest:

```
💡 Based on what we learned:

**Immediate actions**:
- Update error handling in other workers
- Add None checks in similar code
- Document the module organization pattern

**Future considerations**:
- Consider adding error handling tests
- Review other modules for similar issues
- Create a refactoring guide

Should we tackle any of these now?
```

## Learning Strategies

### Strategy 1: Pattern Recognition
Look for repeated solutions:
- Same fix applied multiple times
- Similar code patterns
- Consistent approaches
- Common decisions

### Strategy 2: Failure Analysis
Learn from mistakes:
- What broke?
- Why did it break?
- How was it fixed?
- How to prevent it?

### Strategy 3: Evolution Tracking
See how code evolved:
- Initial implementation
- Problems discovered
- Improvements made
- Final solution

### Strategy 4: Decision Archaeology
Understand past decisions:
- Why was this approach chosen?
- What alternatives existed?
- What trade-offs were made?
- Would we decide differently now?

## Best Practices

### 1. Learn from Both Success and Failure
- Successful patterns are valuable
- Failures teach important lessons
- Both deserve documentation
- Context matters for both

### 2. Focus on Transferable Knowledge
- Not just "what" but "why"
- Principles over specifics
- Patterns over one-off solutions
- Reusable insights

### 3. Document the Journey
- Show the evolution
- Explain the reasoning
- Include alternatives considered
- Capture the context

### 4. Make It Actionable
- Clear guidance
- Concrete examples
- When to apply
- When not to apply

### 5. Connect the Dots
- Link related lessons
- Show patterns across commits
- Build knowledge graph
- Create learning paths

### 6. Stay Humble
- We're always learning
- Patterns evolve
- Context changes
- Be open to revision

## Examples

### Example 1: Learn from Recent Work

**Command**: `/learn`

**Output**:
```
📚 Analyzing recent work for lessons...

**Conversation Analysis**:
- Discussed error handling strategies
- Implemented graceful error handling
- Chose stability over error propagation

**Git History** (last 10 commits):
- 3 fix commits (error handling, type errors, imports)
- 2 test commits (added 40 tests, improved coverage)
- 1 refactor commit (module reorganization)

**Lessons Extracted**:

1. **Error Handling Pattern** ⭐
   - Commit: beefa3f
   - Lesson: Workers should never crash on job errors
   - Why: System stability is critical
   - How: Catch, log, continue
   - Add to: .claude/patterns/worker-error-handling.md

2. **Testing Strategy** ⭐
   - Commits: Multiple test additions
   - Lesson: Mock external dependencies for reliable tests
   - Why: Real APIs are slow and flaky
   - How: Use pytest-mock, unittest.mock
   - Add to: .claude/standards/testing-mocks.md

3. **Module Organization** ⭐
   - Commit: c28cc52
   - Lesson: Split large modules by domain
   - Why: Easier to navigate and maintain
   - How: Group by functionality, not type
   - Add to: .claude/architecture/module-structure.md

Should I add these to the knowledge garden?
```

### Example 2: Learn with Focus

**Command**: `/learn focus on testing patterns`

**Output**:
```
📚 Learning about testing patterns...

**From Conversation**:
- Discussed mocking strategies
- Implemented 40 new tests
- Achieved 82% coverage

**From Git History**:
- test: add comprehensive test suite (beefa3f)
- test: add error handling tests (previous)
- test: improve coverage for agents (previous)

**Testing Patterns Discovered**:

1. **Mock External Services**
   - Always mock Supabase, Mistral, APIs
   - Use fixtures for common mocks
   - Keep tests fast (<1s per test)

2. **Test Error Paths**
   - Don't just test happy path
   - Test exceptions and edge cases
   - Verify error messages

3. **Parametrize Similar Tests**
   - Use @pytest.mark.parametrize
   - Test multiple inputs efficiently
   - Keep tests DRY

4. **Organize by Module**
   - Mirror source structure in tests/
   - One test file per source file
   - Group related tests in classes

**Example from Code**:
[Shows actual test code from recent commits]

Add these patterns to .claude/standards/testing.md?
```

### Example 3: Learn from Failures

**Command**: `/learn what went wrong and how we fixed it`

**Output**:
```
📚 Analyzing failures and fixes...

**Fix Commits Found**:

1. **fix(worker): handle exceptions gracefully** (ghi789)
   - Problem: Worker crashed on job errors
   - Root cause: Exceptions were re-raised
   - Fix: Catch and log instead
   - Lesson: Stability > error propagation
   - Prevention: Always catch in worker loops

2. **fix(tests): resolve type errors** (jkl012)
   - Problem: Tests failed with None type errors
   - Root cause: Didn't check for None
   - Fix: Added None checks
   - Lesson: Always validate optional values
   - Prevention: Use type hints, mypy

3. **fix(imports): update after refactor** (mno345)
   - Problem: Import errors after module split
   - Root cause: Didn't update all imports
   - Fix: Updated import paths
   - Lesson: Search for all usages before refactoring
   - Prevention: Use IDE refactoring tools

**Common Themes**:
- Defensive programming prevents crashes
- Type checking catches errors early
- Thorough testing reveals issues

Add these lessons to knowledge garden?
```

## Error Handling

### No Recent Commits
**Solution**:
- Focus on conversation only
- Ask about past experiences
- Suggest starting fresh
- Document current patterns

### Unclear Lessons
**Solution**:
- Ask for clarification
- Discuss with user
- Focus on clear patterns
- Skip ambiguous items

### Too Many Lessons
**Solution**:
- Prioritize by importance
- Group related lessons
- Add incrementally
- Don't overwhelm

### Conflicting Patterns
**Solution**:
- Note the conflict
- Explain context for each
- Document when to use which
- Ask user to decide

## Reusability

This command works across:
- Any git repository
- Any programming language
- Any project type
- Any agent or AI assistant

The key is to:
- Analyze conversation and history
- Extract transferable knowledge
- Document clearly
- Organize logically

---

**Remember**: Every commit is a lesson, every bug is a teacher! 📚✨

# Command Structure Standard

## What Happened

Commands had inconsistent structure, making them harder to parse and understand. Some led with context, others with steps, others with philosophy.

**Examples of inconsistency:**
- Some started with "Overview" sections
- Some had steps before action
- Some had extensive context upfront
- Some had no clear structure at all

**Result:** Confusion about what commands do and how to use them.

## What We Learned

Consistent structure across all commands creates predictability and reduces cognitive load. When every command follows the same pattern, you know exactly where to look for information.

**Key insight:** Structure is a user interface. Consistent structure means consistent experience.

## Why It Matters

### Cognitive Benefits
- **Faster to understand** - Know what to expect
- **Easier to scan** - Information in predictable places
- **Better retention** - Remember the pattern, not each command
- **Less mental overhead** - Don't have to figure out structure each time

### Maintenance Benefits
- **Easier to update** - Same pattern everywhere
- **Easier to review** - Spot inconsistencies quickly
- **Easier to create** - Template to follow
- **Quality control** - Standard to measure against

### Professional Benefits
- **Shows attention to detail** - Consistency matters
- **Builds trust** - Reliable, predictable system
- **Easier to teach** - One pattern to learn
- **Scales better** - Works with many commands

## How to Apply

### Standard Command Structure

```markdown
# 🎯 ACTION: [Verb Phrase]
[One sentence description]

See @FILE.md for [relevant context]

## 📋 STEPS
[Numbered list of concrete actions]

## 💡 CONTEXT
[Minimal essential guidance]

## 🔗 Follow-up Commands
[Suggested next steps]
```

### Section Guidelines

#### 1. ACTION Header (Required)
```markdown
# 🎯 ACTION: [Verb Phrase]
```

**Rules:**
- Always start with 🎯 emoji
- Use imperative verb (Extract, Analyze, Fix, etc.)
- Keep it short (2-5 words)
- Make it action-oriented

**Examples:**
- ✅ `🎯 ACTION: Extract and Document Lessons`
- ✅ `🎯 ACTION: Fix Failing Tests`
- ✅ `🎯 ACTION: Review Progress and Plan Next Steps`
- ❌ `🎯 ACTION: Learning System` (not a verb)
- ❌ `🎯 ACTION: This command helps you learn` (too long)

#### 2. Description (Required)
```markdown
[One sentence description]
```

**Rules:**
- One sentence only
- Expand on the action
- Explain the outcome
- Keep it concise

**Examples:**
- ✅ `Analyze recent conversation and git history to extract patterns, lessons, and insights for the knowledge garden.`
- ✅ `Identify and fix failing tests, linting errors, or other issues in the codebase.`
- ❌ `This command is used to help you learn from your work. It looks at your conversation and git history...` (too long)

#### 3. Reference Links (Optional)
```markdown
See @FILE.md for [relevant context]
```

**Rules:**
- Use @ syntax for file references
- Link to relevant project files
- Keep it one line
- Only include if needed

**Examples:**
- ✅ `See @CONSTITUTION.md for project conventions and @.claude/GARDENING.md for knowledge garden structure.`
- ✅ `See @PLAN.md for current priorities.`

#### 4. STEPS Section (Required)
```markdown
## 📋 STEPS
1. **Action** - Brief description
2. **Action** - Brief description
```

**Rules:**
- Always use 📋 emoji
- Numbered list
- Bold the action verb/phrase
- Brief description after dash
- 3-10 steps (if more, break into sub-commands)
- Concrete and actionable

**Examples:**
- ✅ `1. **Analyze conversation** - Review for patterns and insights`
- ✅ `2. **Review git history** - Run git log --oneline -20`
- ❌ `1. First, you should analyze the conversation to look for patterns` (too wordy)
- ❌ `1. Analyze` (no description)

#### 5. CONTEXT Section (Optional)
```markdown
## 💡 CONTEXT
[Minimal essential guidance]
```

**Rules:**
- Always use 💡 emoji
- Keep it minimal (10-30 lines)
- Only essential information
- Use subsections if needed
- Examples, formats, principles

**What to include:**
- Format examples
- Key principles
- Common pitfalls
- Important notes

**What NOT to include:**
- Philosophy or theory
- Extensive explanations
- Redundant information
- Things covered in linked docs

#### 6. Follow-up Commands (Optional)
```markdown
## 🔗 Follow-up Commands

- `/command` - Description
- `/command` - Description
```

**Rules:**
- Always use 🔗 emoji
- Bullet list
- Command name with slash
- Brief description
- 2-5 suggestions

**Examples:**
- ✅ `- /commit - Commit the new knowledge`
- ✅ `- /test - Verify the fix works`
- ❌ `- commit - Save changes` (missing slash)
- ❌ `- /commit` (no description)

### File Size Guidelines

**Target:** 50-70 lines per command

**Breakdown:**
- Header: 5-10 lines
- Steps: 10-20 lines
- Context: 20-40 lines
- Follow-up: 5-10 lines

**If exceeding 100 lines:**
- Move details to separate docs
- Link to those docs
- Keep command focused

## Example

### ✅ Perfect Structure

```markdown
# 🎯 ACTION: Extract and Document Lessons

Analyze recent conversation and git history to extract patterns,
lessons, and insights for the knowledge garden.

See @CONSTITUTION.md for project conventions and @.claude/GARDENING.md for knowledge garden structure.

## 📋 STEPS

1. **Analyze conversation** - Review for successful patterns, challenges, insights, and decisions
2. **Review git history** - Run `git log --oneline -20`, `git log --stat -10`, look for fix/refactor/test commits
3. **Identify patterns** - Categorize as technical patterns, process patterns, mistakes/fixes, or best practices
4. **Extract lessons** - For each pattern, create lesson with what happened, what we learned, why it matters
5. **Add to knowledge garden** - Create or update files with examples and cross-links
6. **Suggest follow-up** - Recommend immediate actions or future considerations

## 💡 CONTEXT

**Lesson format:**
```markdown
# [Lesson Title]

## What Happened
[Describe the situation]

## What We Learned
[The key insight or lesson]

## Why It Matters
[Impact and importance]
```

**Learning strategies:**
- Pattern recognition (repeated solutions)
- Failure analysis (what broke and why)
- Evolution tracking (how code improved)

**Knowledge garden structure:**
- `.claude/patterns/` - Reusable code solutions
- `.claude/standards/` - Best practices and conventions
- `.claude/architecture/` - Design decisions and system insights

## 🔗 Follow-up Commands

- `/commit` - Commit the new knowledge
- `/cultivate` - Organize and maintain the garden
- `/focus` - Explore related topics
```

**Why this works:**
- Clear action in header
- Concise description
- Relevant references
- Concrete steps
- Minimal context
- Helpful follow-ups
- 72 lines total

## Structure Checklist

Use this checklist when creating or reviewing commands:

- [ ] Header starts with 🎯 ACTION
- [ ] Action uses imperative verb
- [ ] One sentence description
- [ ] @ syntax for file references
- [ ] STEPS section with 📋 emoji
- [ ] Steps are numbered and bold
- [ ] Steps are concrete and actionable
- [ ] CONTEXT section with 💡 emoji (if needed)
- [ ] Context is minimal and essential
- [ ] Follow-up section with 🔗 emoji (if needed)
- [ ] Follow-ups include descriptions
- [ ] Total length 50-70 lines
- [ ] Consistent formatting throughout

## Related

- [@.claude/patterns/documentation-as-interface.md](../patterns/documentation-as-interface.md) - Command vs documentation
- [@.claude/patterns/progressive-disclosure.md](../patterns/progressive-disclosure.md) - Information hierarchy
- [@.claude/patterns/portable-commands.md](../patterns/portable-commands.md) - Keeping commands generic
- [@.claude/patterns/command-composition.md](../patterns/command-composition.md) - How commands work together
- [@.claude/INDEX.md](../INDEX.md) - All available commands

## Common Mistakes

### ❌ Missing Action Header
```markdown
# Learn Command

This command helps you extract lessons...
```
**Fix:** Start with `# 🎯 ACTION: Extract and Document Lessons`

### ❌ Steps Before Action
```markdown
## Steps
1. Do this
2. Do that

# Learn Command
```
**Fix:** Action header always comes first

### ❌ Too Much Context
```markdown
## 💡 CONTEXT
[300 lines of explanation]
```
**Fix:** Keep context minimal, link to detailed docs

### ❌ Inconsistent Formatting
```markdown
## Steps (no emoji)
- Step 1 (bullets not numbers)
- Step 2
```
**Fix:** Use `## 📋 STEPS` with numbered list

### ❌ No Follow-ups
```markdown
[Command ends abruptly]
```
**Fix:** Add `## 🔗 Follow-up Commands` section

## Key Takeaway

**Structure is a user interface.** Consistent structure creates consistent experience. Follow the standard format for every command: ACTION → STEPS → CONTEXT → FOLLOW-UPS. This makes commands predictable, scannable, and reliable.

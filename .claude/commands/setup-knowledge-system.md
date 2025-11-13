---
description: Bootstrap the AIMQ knowledge system in a new project
---

# Setup Knowledge System

Bootstrap the AIMQ knowledge system structure in a new project. This creates a collaborative documentation system for human-agent teams.

## Overview

This command sets up:
- **agents.md**: Quick reference guide for AI agents
- **CONSTITUTION.md**: Guiding principles and non-negotiables
- **.claude/**: Knowledge base directory structure
  - `patterns/`: Established patterns for consistency
  - `standards/`: Best practices (coding, testing, git, etc.)
  - `architecture/`: System design and library references
  - `quick-references/`: Common task guidance
  - `commands/`: Custom workflow commands

## When to Use

- Starting a new project
- Onboarding new team members (human or AI)
- Establishing team conventions
- Creating a shared knowledge base

## Task List

### 1. Create Root Documentation

Create `agents.md` in the project root:

```markdown
# [Project Name] Agents Guide

> **You are amazing!** We're building the future together, seamlessly collaborating as one unified force. Every line of code, every refactor, every test—we're making something incredible. Let's keep this momentum going! 🚀✨

## Quick Reference

**[Project Name]** - [Brief project description]

For deep technical details, see `CLAUDE.md`. This guide is your quick reference for architecture, testing, and our collaborative workflow.

---

## Architecture Snapshot

[Add project-specific architecture overview]

---

## Testing

```bash
# Run all tests
[Add test commands]
```

---

## Linting & Formatting

```bash
# Lint code
[Add lint commands]
```

---

## Working Memory: PLAN.md

`PLAN.md` is our **shared working memory**—a high-level tracker of what's done and what's next.

### Guidelines:
- **Keep it updated**: After completing features or making architectural changes, update PLAN.md
- **Keep it clean**: Remove completed items, consolidate related tasks
- **Keep it concise**: High-level overview only, details go in code/docs
- **Use it as context**: Reference it when planning next steps

---

## Knowledge Base: .claude/

The `.claude/` directory is our **internal knowledge base**—patterns, standards, architecture, and quick references that help us work in perfect sync.

### Structure:

```
.claude/
├── patterns/           # Established patterns for consistency
├── standards/          # Best practices (coding, testing, git, etc.)
├── architecture/       # System design and library references
├── quick-references/   # Common task guidance
└── commands/           # Custom /commands for workflows
```

### Maintenance Guidelines:

1. **Keep files small**: Under 400 lines per file
2. **One topic per file**: Split large topics into multiple files
3. **Use links heavily**: Cross-reference between files to build a knowledge graph
4. **Update as you code**: When you learn something new or establish a pattern, document it
5. **Stay shallow**: No nested directories—just markdown files in each folder
6. **Make it actionable**: Focus on "how-to" over "what is"

---

## CONSTITUTION.md

Our **guiding principles and non-negotiables** live in `CONSTITUTION.md`. This is our shared value system that keeps us aligned.

Review it regularly and suggest updates when you notice strong preferences or patterns emerging.

---

## Remember

**We're not just writing code—we're building the future together.** Every commit is a step forward. Every test is confidence. Every refactor is clarity. You're doing amazing work, and together we're unstoppable! 💪✨

Now let's go build something incredible! 🚀
```

### 2. Create CONSTITUTION.md

Create `CONSTITUTION.md` in the project root:

```markdown
# [Project Name] Constitution

> Our guiding principles and non-negotiables for building together

## Core Values

### 1. Clarity Over Cleverness
- Write code that's easy to understand, not code that shows off
- Prefer explicit over implicit
- Name things clearly—no abbreviations unless universally understood

### 2. Modularity & Separation of Concerns
- Each module has a clear, single responsibility
- Shared code goes in common/shared modules
- If it's used in multiple places, it belongs in a shared module

### 3. Test Everything That Matters
- Target: [X]%+ coverage, but quality over quantity
- Test behavior, not implementation details
- Mock external dependencies
- Fast tests enable fast iteration

### 4. Documentation Evolves With Code
- Update docs when you change architecture
- Keep PLAN.md current as our working memory
- Maintain .claude/ knowledge base as we learn

### 5. Conventional Commits = Clear History
- Use `feat:`, `fix:`, `docs:`, `refactor:`, etc.
- Makes git history readable and meaningful

## Non-Negotiables

[Add project-specific non-negotiables]

## Strong Preferences

[Add project-specific preferences]

## Collaboration Principles

### Human ↔ Agent Partnership
- **We're a team**: Not human vs AI, but human + AI
- **Ask when uncertain**: Better to clarify than assume
- **Suggest improvements**: If you see a better way, speak up
- **Learn together**: Update .claude/ as we discover patterns
- **Celebrate wins**: Every successful feature is a shared victory

## Living Document

This constitution evolves as we work together. When you notice:
- **New strong preferences** emerging → Add them here
- **Patterns becoming established** → Document in `.claude/patterns/`
- **Better ways of working** → Update this document
- **Outdated rules** → Remove or revise them

**Last Updated**: [Date]

---

> "We're not just writing code—we're building the future together." 🚀
```

### 3. Create .claude/ Directory Structure

```bash
mkdir -p .claude/patterns
mkdir -p .claude/standards
mkdir -p .claude/architecture
mkdir -p .claude/quick-references
mkdir -p .claude/commands
```

### 4. Create Initial Knowledge Base Files

#### .claude/patterns/README.md
```markdown
# Patterns

Established patterns for consistency across the codebase.

## Files

- [Add pattern files as they're created]

## Guidelines

- Document patterns as they emerge
- One pattern per file
- Include examples
- Keep under 400 lines
```

#### .claude/standards/README.md
```markdown
# Standards

Best practices for coding, testing, git workflow, and more.

## Files

- [Add standard files as they're created]

## Guidelines

- Document standards as they're established
- One topic per file
- Include examples and anti-patterns
- Keep under 400 lines
```

#### .claude/architecture/README.md
```markdown
# Architecture

System design and library references.

## Files

- [Add architecture files as they're created]

## Guidelines

- Document architecture decisions
- Reference key libraries and frameworks
- Include diagrams where helpful
- Keep under 400 lines
```

#### .claude/quick-references/README.md
```markdown
# Quick References

Fast guidance for common tasks.

## Files

- [Add quick reference files as they're created]

## Guidelines

- Focus on "how-to" over "what is"
- Use code examples
- Keep it concise
- One task per file
```

### 5. Create PLAN.md

Create `PLAN.md` in the project root:

```markdown
# [Project Name] Plan

> Our shared working memory—tracking what's done and what's next

## Current Status

**Version**: [Current version]
**Last Updated**: [Date]

## Completed

### ✅ Phase 1: [Phase Name]
- [Completed item 1]
- [Completed item 2]

## In Progress

### 🔄 Phase 2: [Phase Name]
- [In progress item 1]
- [In progress item 2]

## Upcoming

### 📋 Phase 3: [Phase Name]
- [Planned item 1]
- [Planned item 2]

## Notes

[Add any important notes or context]
```

### 6. Inform User

After creating all files, inform the user:

```
✅ Knowledge system setup complete!

Created:
- agents.md (Quick reference guide)
- CONSTITUTION.md (Guiding principles)
- PLAN.md (Working memory)
- .claude/ directory structure
  - patterns/
  - standards/
  - architecture/
  - quick-references/
  - commands/

Next steps:
1. Customize agents.md with project-specific details
2. Add project-specific non-negotiables to CONSTITUTION.md
3. Populate .claude/ directories as patterns emerge
4. Keep PLAN.md updated as you work

Remember: This is a living system that grows with your project! 🚀
```

## Benefits

1. **Shared Context**: Human and AI agents have the same knowledge base
2. **Consistency**: Established patterns ensure consistent code
3. **Onboarding**: New team members (human or AI) can quickly get up to speed
4. **Living Documentation**: Docs evolve with the codebase
5. **Collaboration**: Clear principles enable seamless teamwork

## Maintenance

- **Update as you code**: Document patterns as they emerge
- **Keep it concise**: Under 400 lines per file
- **Use links**: Cross-reference between files
- **Review regularly**: Update CONSTITUTION.md and PLAN.md
- **Stay shallow**: No nested directories in .claude/

## Related

- See `agents.md` for the quick reference guide
- See `CONSTITUTION.md` for guiding principles
- See `PLAN.md` for current status and next steps

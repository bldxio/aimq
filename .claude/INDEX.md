# AIMQ Knowledge Base Index

> Your comprehensive guide to building AIMQ together 🚀

## 🎯 Start Here

- **[agents.md](../agents.md)** - Quick reference guide for AI agents (START HERE!)
- **[CONSTITUTION.md](../CONSTITUTION.md)** - Our guiding principles and non-negotiables
- **[PLAN.md](../PLAN.md)** - Current status and next steps (working memory)
- **[CLAUDE.md](../CLAUDE.md)** - Comprehensive technical documentation

## 📁 Knowledge Base Structure

### Patterns (`patterns/`)
Established patterns for consistency across the codebase.

- **[module-organization.md](patterns/module-organization.md)** - How to organize code into modules
- **[error-handling.md](patterns/error-handling.md)** - Error handling patterns and best practices
- **[progressive-enhancement.md](patterns/progressive-enhancement.md)** - Build features in valuable phases
- **[cli-ux-patterns.md](patterns/cli-ux-patterns.md)** - Helpful CLI error messages and UX
- **[documentation-as-interface.md](patterns/documentation-as-interface.md)** - Structure commands as interfaces
- **[progressive-disclosure.md](patterns/progressive-disclosure.md)** - Reveal information progressively
- **[portable-commands.md](patterns/portable-commands.md)** - Keep commands generic and portable
- **[command-composition.md](patterns/command-composition.md)** - Compose commands through suggestion

### Standards (`standards/`)
Best practices for coding, testing, git workflow, and more.

- **[conventional-commits.md](standards/conventional-commits.md)** - Commit message format
- **[testing.md](standards/testing.md)** - Testing standards and patterns
- **[code-style.md](standards/code-style.md)** - Code formatting and style guide
- **[git-workflow.md](standards/git-workflow.md)** - Git branching and workflow
- **[precommit-workflow.md](standards/precommit-workflow.md)** - Run quality checks before committing
- **[command-structure.md](standards/command-structure.md)** - Standard structure for command files

### Architecture (`architecture/`)
System design and library references.

- **[aimq-overview.md](architecture/aimq-overview.md)** - High-level architecture overview
- **[database-schema-organization.md](architecture/database-schema-organization.md)** - Multi-schema database patterns
- **[key-libraries.md](architecture/key-libraries.md)** - Reference for main libraries
- **[langchain-integration.md](architecture/langchain-integration.md)** - LangChain Runnable patterns
- **[langgraph-integration.md](architecture/langgraph-integration.md)** - LangGraph workflow patterns

### Quick References (`quick-references/`)
Fast guidance for common tasks.

- **[testing.md](quick-references/testing.md)** - Quick testing commands
- **[linting.md](quick-references/linting.md)** - Quick linting commands
- **[common-tasks.md](quick-references/common-tasks.md)** - Common development tasks
- **[git-commands.md](quick-references/git-commands.md)** - Git command reference
- **[dependency-management.md](quick-references/dependency-management.md)** - uv dependency management

### Commands (`commands/`)
Custom workflow commands for development, planning, and knowledge management.

#### Development Workflow
- **[/commit](commands/commit.md)** - Stage changes, run checks, and create a conventional commit
- **[/test](commands/test.md)** - Run the test suite and report results
- **[/fix](commands/fix.md)** - Run tests, identify failures, and implement fixes
- **[/debug](commands/debug.md)** - Debug issues systematically

#### Planning & Documentation
- **[/plan](commands/plan.md)** - Review progress and update the project plan
- **[/tidyup](commands/tidyup.md)** - Archive completed work to CHANGELOG.md
- **[/remember](commands/remember.md)** - Capture insights and patterns from conversation
- **[/learn](commands/learn.md)** - Extract lessons from conversation and git history

#### Knowledge Garden
- **[/focus](commands/focus.md)** - Explore topics in the knowledge garden
- **[/levelup](commands/levelup.md)** - Research new topics and add to the garden
- **[/cultivate](commands/cultivate.md)** - Maintain and organize the knowledge garden
- **[/seed](commands/seed.md)** - Bootstrap a complete knowledge system for a new project

#### Project Setup
- **[/release](commands/release.md)** - Prepare and execute a release

> **How to use:** Type `/command` (e.g., `/fix`) and follow the steps. Commands reference project files using @ syntax and suggest follow-up commands.

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

#### Release Software
1. Check [CLAUDE.md](../CLAUDE.md) for release workflow
2. Use `just release-beta` for beta releases
3. Use `just release` for stable releases

## 📊 File Statistics

- **Total Files**: 20+ markdown files
- **Total Lines**: ~5,000+ lines of documentation
- **Coverage**: Architecture, patterns, standards, quick references
- **Maintenance**: Living documentation that evolves with code

## 🔄 Maintenance Guidelines

### Keep It Updated
- Update docs when you change architecture
- Document new patterns as they emerge
- Keep PLAN.md current with progress
- Review CONSTITUTION.md regularly

### Keep It Clean
- Remove outdated information
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
4. **Update index**: Add to this file
5. **Commit it**: Use conventional commits

## 🌟 Remember

**We're not just writing code—we're building the future together!**

Every line of documentation makes us smarter. Every pattern we establish makes us more consistent. Every standard we follow makes us more professional.

You're amazing, and together we're unstoppable! 💪✨

---

**Last Updated**: 2025-11-16
**Version**: 1.1.0
**Maintainers**: Human + AI Team 🚀

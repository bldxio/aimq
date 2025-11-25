# AIMQ Knowledge Base Index

> Your comprehensive guide to building AIMQ together 🚀

**Last Updated**: 2025-11-24

## 🎯 Start Here

- **[agents.md](../agents.md)** - Quick reference guide for AI agents (START HERE!)
- **[CONSTITUTION.md](../CONSTITUTION.md)** - Our guiding principles and non-negotiables
- **[PLAN.md](../PLAN.md)** - Current status and next steps (working memory)
- **[CLAUDE.md](../CLAUDE.md)** - Comprehensive technical documentation
- **[GARDENING.md](../GARDENING.md)** - Knowledge garden philosophy and cultivation

## 📊 Garden Statistics

- **Total Files**: 76 markdown files
- **Active**: 71 files
- **Archived**: 5 files (kept for reference with redirects)
- **Categories**: 8 (patterns, standards, architecture, quick-references, commands, hooks, scripts, templates)
- **Last Cultivation**: 2025-11-24

## 📁 Knowledge Base Structure

### Patterns (`patterns/`)

Established patterns for consistency across the codebase.

- **[CLI UX Core Patterns](patterns/cli-ux-core.md)**
  - Command-line interfaces should be helpful, not cryptic. Good CLI UX means users know what went wrong and what to do next, without needing to read docu...
- **[CLI UX Examples and Visual Design](patterns/cli-ux-examples.md)**
  - Real-world examples of CLI UX patterns in action, plus visual design guidelines for creating beautiful, helpful command-line interfaces.
- **[CLI UX Patterns](patterns/cli-ux-patterns.md)** ⚠️
  - Command-line interfaces should be helpful, not cryptic. Good CLI UX means users know what went wrong and what to do next, without needing to read docu...
- **[Command Composition Pattern](patterns/command-composition.md)**
- **[Composable Tool Architecture](patterns/composable-tools.md)**
- **[Database Migration Wrapper Functions](patterns/database-migration-wrappers.md)**
- **[Demo-Driven Development](patterns/demo-driven-development-core.md)**
- **[Demo-Driven Development: Best Practices](patterns/demo-driven-development-practices.md)**
- **[Demo-Driven Development](patterns/demo-driven-development.md)**
  - Demo-Driven Development (DDD) is about ruthless prioritization with a concrete goal. It's not about cutting corners—it's about focusing on what matter...
- **[Documentation as Interface Pattern](patterns/documentation-as-interface.md)**
  - [What this is about]
- **[Error Handling Pattern](patterns/error-handling.md)**
  - AIMQ uses custom exceptions and consistent error handling patterns to make debugging easier and provide clear error messages.
- **[Module Organization Pattern](patterns/module-organization.md)**
  - AIMQ uses a modular architecture where each top-level module has a clear, single responsibility. This pattern emerged from refactoring the monolithic ...
- **[Portable Commands Pattern](patterns/portable-commands.md)**
- **[Progressive Disclosure Pattern](patterns/progressive-disclosure.md)**
  - This command helps you extract lessons from recent work by analyzing
- **[Progressive Enhancement: Supabase Realtime Case Study](patterns/progressive-enhancement-case-study.md)**
  - Real-world example of progressive enhancement: building instant worker wake-up for AIMQ using Supabase Realtime.
- **[Progressive Enhancement: Core Principles](patterns/progressive-enhancement-core.md)**
  - Progressive enhancement is a development strategy where you build features in independent, valuable phases. Each phase delivers working functionality ...
- **[Progressive Enhancement: Common Patterns](patterns/progressive-enhancement-patterns.md)**
  - Common patterns and anti-patterns for implementing progressive enhancement in your codebase.
- **[Progressive Enhancement Pattern](patterns/progressive-enhancement.md)** ⚠️
  - Progressive enhancement is a development strategy where you build features in independent, valuable phases. Each phase delivers working functionality ...
- **[Queue Error Handling](patterns/queue-error-handling.md)**
  - Robust error handling for message queue operations, including dead-letter queues (DLQ), retry logic, and custom error handlers. Ensures failed jobs ar...
- **[Test Mocking Evolution for External Services](patterns/test-mocking-external-services.md)**
- **[Testing Strategy](patterns/testing-strategy.md)**
  - A systematic approach to testing that balances coverage, maintainability, and pragmatism. Focus on testing what matters most first, and don't let perf...
- **[Worker Error Handling](patterns/worker-error-handling.md)**
  - Workers should never crash on job errors. This pattern ensures workers remain stable and continue processing jobs even when individual jobs fail.

### Standards (`standards/`)

Best practices for coding, testing, git workflow, and more.

- **[Code Style Standards](standards/code-style.md)**
  - AIMQ follows PEP 8 with some project-specific conventions. We use automated tools (black, flake8) to enforce consistency.
- **[Command Structure Standard](standards/command-structure.md)**
- **[Conventional Commits Standard](standards/conventional-commits.md)**
  - AIMQ uses Conventional Commits for all commit messages. This enables automatic CHANGELOG generation and makes git history readable and meaningful.
- **[Git Workflow Standards](standards/git-workflow.md)**
  - AIMQ uses a feature branch workflow with conventional commits and automated releases.
- **[Precommit Workflow Standard](standards/precommit-workflow.md)**
- **[Testing Standards](standards/testing.md)**
  - AIMQ maintains high test coverage (79%+) with fast, reliable tests that enable confident refactoring and rapid iteration.

### Architecture (`architecture/`)

System design and library references.

- **[AIMQ Architecture Overview](architecture/aimq-overview.md)**
- **[Database Schema Migration and Testing](architecture/database-schema-migration.md)**
  - Strategies for testing database schema organization and migrating existing projects to use the three-schema pattern.
- **[Database Schema Organization](architecture/database-schema-organization.md)** ⚠️
  - Strategic organization of database objects across multiple schemas provides security, usability, and maintainability benefits. This pattern is especia...
- **[Database Schema Organization Patterns](architecture/database-schema-patterns.md)**
  - Strategic organization of database objects across multiple schemas provides security, usability, and maintainability benefits. This pattern is especia...
- **[Key Libraries Reference](architecture/key-libraries.md)**
  - Quick reference for the main libraries and frameworks used in AIMQ.
- **[Knowledge Systems Overview](architecture/knowledge-systems-overview.md)**
- **[Knowledge Systems Templates](architecture/knowledge-systems-templates.md)**
  - What is this standard?
- **[Knowledge Systems Workflow](architecture/knowledge-systems-workflow.md)**
- **[Knowledge Systems](architecture/knowledge-systems.md)**
  - This guide is split into focused topics:
- **[LangChain Integration](architecture/langchain-integration.md)**
  - AIMQ uses LangChain's Runnable interface as the foundation for task processing. Every task in AIMQ is a LangChain Runnable, enabling composition, stre...
- **[LangGraph Advanced Features](architecture/langgraph-advanced.md)**
- **[LangGraph in AIMQ](architecture/langgraph-aimq.md)**
- **[LangGraph Basics](architecture/langgraph-basics.md)**
  - LangGraph enables building stateful, multi-step workflows with agents. It provides state management, checkpointing, and complex orchestration patterns...
- **[LangGraph Integration](architecture/langgraph-integration.md)**
  - AIMQ uses LangGraph to build stateful, multi-step workflows with agents. LangGraph enables complex agent orchestration, memory management, and human-i...
- **[Vision-Driven Development](architecture/vision-driven-development.md)**
  - A development approach that separates long-term vision from tactical execution. The vision guides direction while the plan tracks progress.

### Quick References (`quick-references/`)

Fast guidance for common tasks.

- **[AIMQ-Specific Pitfalls](quick-references/aimq-pitfalls.md)**
- **[Common Pitfalls](quick-references/common-pitfalls.md)**
  - Common mistakes and how to avoid them. Learn from others' mistakes so you don't have to make them yourself!
- **[Common Tasks Quick Reference](quick-references/common-tasks.md)**
- **[Dependency Management Quick Reference](quick-references/dependency-management.md)**
  - AIMQ uses uv for dependency management (NOT pip or poetry).
- **[Development Pitfalls](quick-references/development-pitfalls.md)**
- **[Git Commands Quick Reference](quick-references/git-commands.md)**
- **[Linting Quick Reference](quick-references/linting.md)**
- **[LLM Provider API Differences](quick-references/llm-api-differences.md)**
  - Different LLM providers have different APIs, causing runtime errors when switching providers. This guide helps you navigate those differences.
- **[LLM Provider API Differences](quick-references/llm-provider-apis.md)** ⚠️
- **[LLM Provider Best Practices](quick-references/llm-provider-best-practices.md)**
  - Strategies for working with multiple LLM providers and avoiding common integration pitfalls.
- **[LLM Provider API Comparison](quick-references/llm-provider-comparison.md)**
  - Different LLM providers have different APIs, causing runtime errors when switching providers or using multiple providers in the same application.
- **[Pre-commit Hook Troubleshooting](quick-references/precommit-troubleshooting.md)**
- **[Python Pitfalls](quick-references/python-pitfalls.md)**
- **[Supabase Local Development Setup](quick-references/supabase-local-setup.md)** ⚠️
  - Archived - Split into focused guides below
- **[Supabase Local: Overview](quick-references/supabase-local/overview.md)**
  - Getting started with Supabase local development
- **[Supabase Local: Configuration](quick-references/supabase-local/configuration.md)**
  - Port configuration and settings
- **[Supabase Local: Migrations](quick-references/supabase-local/migrations.md)**
  - Database migration workflows
- **[Supabase Local: Troubleshooting](quick-references/supabase-local/troubleshooting.md)**
  - Common issues and solutions
- **[Supabase Local: Integration](quick-references/supabase-local/integration.md)**
  - AIMQ integration guide
- **[Testing Quick Reference](quick-references/testing.md)**

### Commands (`commands/`)

Custom workflow commands for development, planning, and knowledge management.

- **[🎯 ACTION: Create Conventional Commit](commands/commit.md)**
- **[🎯 ACTION: Maintain and Organize Knowledge Garden](commands/cultivate.md)**
- **[🎯 ACTION: Debug Issues Systematically](commands/debug.md)**
- **[🎯 ACTION: Fix Test Failures](commands/fix.md)**
- **[🎯 ACTION: Explore Knowledge Garden Topics](commands/focus.md)**
- **[🎯 ACTION: Extract and Document Lessons](commands/learn.md)**
- **[🎯 ACTION: Research and Add New Knowledge](commands/levelup.md)**
- **[🎯 ACTION: Review and Update Project Plan](commands/plan.md)**
- **[🎯 ACTION: Execute Release Workflow](commands/release.md)**
- **[🎯 ACTION: Capture Insights and Patterns](commands/remember.md)**
- **[🎯 ACTION: Seed Knowledge System](commands/seed.md)**
- **[🎯 ACTION: Analyze Coverage and Write Tests](commands/test.md)**
- **[🎯 ACTION: Tidy Up Planning Documents](commands/tidyup.md)**

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

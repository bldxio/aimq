# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Email Processing MVP with complete AI-powered email workflow (Nov 25)
  - Multi-tenant database schema (7 tables: workspaces, profiles, channels, members, participants, messages, attachments)
  - Resend client wrapper using official Python SDK
  - Supabase Edge Function for webhook handling with intelligent routing
  - Email Agent using LangChain + OpenAI (GPT-4) for contextual responses
  - Comprehensive testing infrastructure with dry-run mode
  - Demo organization in `demos/email-processing/` directory
  - Full documentation in `SPRINT_SUMMARY.md`
- Textual TUI framework integration (planned)
  - Dashboard for monitoring queues and workers
  - Enhanced chat CLI with full-featured interface
- LangGraph integration with `@agent` and `@workflow` decorators
- Built-in agents: ReActAgent and PlanExecuteAgent
- Built-in workflows: DocumentWorkflow and MultiAgentWorkflow
- Supabase-backed checkpointing for stateful workflows
- Security features: LLM whitelisting, prompt controls, and tool validation
- Comprehensive examples in `examples/langgraph/`
- User documentation in `docs/user-guide/`
- Message routing system with @mention detection and queue resolution (Nov 13)
- Interactive chat CLI with Rich UI, markdown rendering, and syntax highlighting (Nov 15)
- Weather tool (Open-Meteo API) and QueryTable tool for Supabase queries (Nov 15)
- Supabase Realtime wake-up service for instant worker notifications (<1s latency) (Nov 16)
- Worker presence tracking (idle/busy status) with broadcast channels (Nov 16)
- Database triggers for automatic realtime notifications on job enqueue (Nov 19)
- CLI commands: `aimq create`, `aimq list`, `aimq realtime`, `aimq schema`, `aimq chat` (Nov 19-20)
- Webhook tool system for calling external APIs (Zapier, Make.com, custom) (Nov 20)
- VISION.md as living north star document (Nov 13)
- 9 helper commands for knowledge garden management (`/fix`, `/debug`, `/test`, `/plan`, `/remember`, `/learn`, `/focus`, `/levelup`, `/cultivate`) (Nov 12-13)
- `/tidyup` command for archiving completed work (Nov 19)
- 19 new knowledge garden documents covering patterns, architecture, and quick-references (Nov 13-20)
- Standard templates for documentation consistency (8 templates) (Nov 20)
- Automated INDEX.md generation script (Nov 20)
- GARDENING.md crash course guide (Nov 13)
- `ideas/` directory with 9 independently buildable components (Nov 13)
- 90 new tests across worker, queue, routing, and realtime modules (Nov 12-16)

### Changed

- Reorganized demos into dedicated `demos/` directory structure (Nov 25)
- Refactored email worker to reduce complexity (extracted helper functions) (Nov 25)
- Reorganized from monolithic `langgraph/` to modular structure: `agents/`, `workflows/`, `memory/`, `common/` (Nov 12)
- Split decorators by domain (agents vs workflows) (Nov 12)
- Refactored 12 command files for clarity and conciseness (83% reduction) (Nov 16-19)
- Split 9 oversized files into 34 focused files (<400 lines each) (Nov 16-20)
- Standardized command structure with 🎯 ACTION headers (Nov 16)
- Adopted @ syntax for file references (Claude-compatible) (Nov 16)
- Removed project-specific tooling for portability (Nov 16)
- Updated hierarchy: CONSTITUTION → VISION → GARDEN → PLAN (Nov 13)
- Improved test coverage from 79% to 84% overall (Nov 12-13)
- Worker coverage: 75% → 84% (+9%) (Nov 13)
- Queue coverage: 75% → 93% (+18%) (Nov 13)
- CLI restructured with subcommands: `aimq realtime`, `aimq schema`, `aimq chat` (Nov 20)
- Realtime module refactored with base class + specialized listeners (Nov 20)
- Realtime broadcasting changed from `pg_notify()` to `realtime.send()` (Nov 20)

### Fixed

- Graceful error handling in worker (no re-raising) (Nov 12)
- Deprecation warning: `datetime.utcnow()` → `datetime.now(timezone.utc)` (Nov 13)
- Graceful shutdown bug in realtime service (proper task cancellation) (Nov 16)
- ReAct agent mocks and realtime mock setup in tests (Nov 16)
- SQL identifier quoting for hyphenated queue names (Nov 19)
- PostgREST jsonb parsing workaround (code 200 error) (Nov 19)
- Mutable default arguments in routing tools (Nov 13)
- Noisy logging in routing workflow (Nov 13)
- Mistral API compatibility (`chat.complete` vs `chat.completions.create`) (Nov 13)
- Message serialization for queue compatibility (Nov 13)
- Email detection in @mention regex (Nov 13)

## [0.1.2] - 2025-10-21

### Fixed

- include template files in package distribution


## [0.1.1] - 2025-10-21

### Added

- enhance release workflow with changelog finalization and PR automation

### Security

- update dependency constraints to fix CVE-2025-6985 and torch vulnerability


## [0.1.0] - 2025-01-17

### Added

- Initial release
- Basic project structure
- Core functionality for processing tasks from Supabase pgmq
- OCR processing capabilities
- Docker configuration for development and production environments

[0.1.0]: https://github.com/bldxio/aimq/releases/tag/v0.1.0
[0.1.1]: https://github.com/bldxio/aimq/compare/v0.1.0...v0.1.1
[0.1.2]: https://github.com/bldxio/aimq/compare/v0.1.1...v0.1.2

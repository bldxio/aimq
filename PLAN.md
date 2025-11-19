# AIMQ Development Plan

**Last Updated**: 2025-11-16
**Current Version**: 0.1.x
**Target Version**: 0.2.0

> **Our Vision**: See [VISION.md](./VISION.md) for where we're going
> **Our Principles**: See [CONSTITUTION.md](./CONSTITUTION.md) for who we are

---

## ✅ Completed Work

### Module Refactoring (Nov 12, 2025)
- ✅ Reorganized from monolithic `langgraph/` to modular structure:
  - `agents/` - Agent implementations, decorators, states, validation
  - `workflows/` - Workflow implementations, decorators, states
  - `memory/` - Checkpointing and persistence
  - `common/` - Shared utilities (exceptions, LLM resolution)
- ✅ Split decorators by domain (agents vs workflows)
- ✅ Improved code organization and maintainability

### Testing & Stability (Nov 12, 2025)
- ✅ Added comprehensive test suite (40 new tests)
- ✅ Achieved 82% overall test coverage (up from 79%)
- ✅ 4 modules now at 100% coverage (workflows, agents)
- ✅ Mock-based testing for external dependencies
- ✅ Error handling and edge case coverage
- ✅ Graceful error handling in worker (no re-raising)

### Knowledge Garden Enhancement (Nov 12-13, 2025)
- ✅ Created 9 helper commands for knowledge management
- ✅ Commands are language-agnostic and agent-agnostic
- ✅ Added `/fix` - Run tests and fix issues
- ✅ Added `/debug` - Troubleshoot build/test issues
- ✅ Added `/test` - Suggest or write tests
- ✅ Added `/plan` - Review and update PLAN.md (working memory)
- ✅ Added `/remember` - Record patterns in knowledge garden
- ✅ Added `/learn` - Extract lessons from history
- ✅ Added `/focus` - Explore knowledge garden topics
- ✅ Added `/levelup` - Research and add new knowledge
- ✅ Added `/cultivate` - Maintain and organize knowledge garden
- ✅ Updated `/commit` to remind about PLAN.md updates
- ✅ Created GARDENING.md - Crash course guide with collaboration framework
- ✅ Updated agents.md to reference GARDENING.md
- ✅ Established hierarchy: CONSTITUTION → GARDEN → PLAN

### Vision & Ideas (Nov 13, 2025)
- ✅ Created VISION.md as living north star document
- ✅ Updated hierarchy: CONSTITUTION → VISION → GARDEN → PLAN
- ✅ Created `ideas/` directory for future feature planning
- ✅ Added comprehensive multi-agent group chat design
- ✅ Documented RAG workflows architecture
- ✅ Planned Zep knowledge graph integration
- ✅ Designed Supabase Realtime streaming
- ✅ Outlined human-in-the-loop workflows
- ✅ Broke down vision into 9 independently buildable components

### Testing Improvements (Nov 13, 2025)
- ✅ Improved worker coverage: 75% → 84% (+9%)
- ✅ Improved queue coverage: 75% → 93% (+18%)
- ✅ Added 11 new tests for core functionality:
  - 4 worker tests (signal handling, graceful shutdown)
  - 7 queue tests (DLQ, error handlers, max retries)
- ✅ Fixed deprecation warning: `datetime.utcnow()` → `datetime.now(timezone.utc)`
- ✅ Overall coverage: 82% → 84%
- ✅ Total tests: 421 passing

### Knowledge Garden Expansion (Nov 13, 2025)
- ✅ Extracted lessons from recent work using `/learn`
- ✅ Created 6 new knowledge documents:
  - `patterns/testing-strategy.md` - Systematic testing approach
  - `patterns/queue-error-handling.md` - DLQ and retry patterns
  - `patterns/worker-error-handling.md` - Worker stability patterns
  - `architecture/vision-driven-development.md` - Vision vs Plan
  - `architecture/knowledge-systems.md` - Knowledge garden benefits
  - `quick-references/common-pitfalls.md` - Common mistakes
- ✅ Updated 5 existing documents with new insights
- ✅ Updated all README files with new content

### Message Agent Lessons (Nov 13, 2025)
- ✅ Extracted lessons from message agent development using `/learn`
- ✅ Created 3 new knowledge documents:
  - `patterns/composable-tools.md` - Build small, focused tools that compose
  - `patterns/demo-driven-development.md` - Use demo deadlines to focus
  - `quick-references/llm-api-differences.md` - LLM provider API compatibility
- ✅ Updated `quick-references/common-pitfalls.md` with 3 new sections:
  - Message serialization for queues (LangChain objects)
  - Regex edge cases (email addresses in @mentions)
  - pgmq function signatures
- ✅ Updated pattern and quick-reference README files

### Message Agent MVP (Nov 13, 2025)
- ✅ Built composable message routing system in ~2 hours
- ✅ Created 3 routing tools:
  - `DetectMentions` - Extract @mentions from text
  - `ResolveQueue` - Map mentions to queue names
  - `LookupProfile` - Query Supabase profiles (ready for future)
- ✅ Implemented `MessageRoutingWorkflow` for intelligent routing
- ✅ Created working demo with 3 queues:
  - `incoming-messages` - Entry point for all messages
  - `default-assistant` - General questions handler
  - `react-assistant` - Complex queries with tools
- ✅ Added 39 comprehensive tests (all passing)
- ✅ Fixed bugs:
  - Mutable default arguments in tools
  - Noisy logging in routing workflow
  - Mistral API compatibility (`chat.complete` vs `chat.completions.create`)
  - Message serialization for queue compatibility
  - Email detection in @mention regex
- ✅ Created demo script and queue clearing utility
- ✅ Full documentation in `examples/message_agent/`
- ✅ Committed: feat(routing): add composable message routing system (17f7204)

### Interactive Chat CLI (Nov 15, 2025)
- ✅ Built beautiful Rich-based CLI for demoing the system
- ✅ Added Weather tool (Open-Meteo API)
- ✅ Added QueryTable tool for Supabase database queries
- ✅ Implemented outbound message queue handling
- ✅ Full markdown rendering, syntax highlighting, spinners
- ✅ Successfully demoed in meeting - exposed performance bottlenecks
- ✅ Committed: feat(message-agent): add interactive chat CLI with weather and database tools (99d4773)

### Supabase Realtime Worker Wake-up - Phase 1 (Nov 16, 2025)
- ✅ Added configuration for realtime service
- ✅ Created `RealtimeWakeupService` with async client in daemon thread
- ✅ Implemented broadcast channel subscription for job notifications
- ✅ Added worker presence tracking (idle/busy status)
- ✅ Implemented reconnection with exponential backoff
- ✅ Integrated with `WorkerThread` for wake-up signaling
- ✅ Added comprehensive tests (9 tests, all passing)
- ✅ Fixed graceful shutdown bug (proper task cancellation)
- ✅ Fixed test issues (ReAct agent mocks, realtime mock setup)
- ✅ Workers now wake within 1 second of job enqueue
- ✅ Polling continues as fallback if realtime unavailable
- ✅ Clean shutdown on Ctrl+C (no pending task errors, no warnings)
- ✅ All 469 tests passing with zero warnings
- ✅ Committed: feat(realtime): add Supabase Realtime wake-up service (0166213)

### Knowledge Garden Refactoring (Nov 16, 2025)
- ✅ Refactored all 12 command files for clarity and conciseness (83% reduction)
- ✅ Standardized command structure with 🎯 ACTION headers
- ✅ Adopted @ syntax for file references (Claude-compatible)
- ✅ Removed project-specific tooling for portability
- ✅ Split 5 oversized files into 17 focused files (<400 lines each):
  - `knowledge-systems.md` → 3 files (overview, templates, workflow)
  - `langgraph-integration.md` → 3 files (basics, advanced, aimq)
  - `demo-driven-development.md` → 2 files (core, practices)
  - `common-pitfalls.md` → 3 files (aimq, development, python)
  - `llm-api-differences.md` → 2 files (differences, provider APIs)
- ✅ Created 4 new patterns:
  - `command-composition.md` - Composable command design
  - `documentation-as-interface.md` - Docs as AI-human interface
  - `portable-commands.md` - Generic, reusable commands
  - `progressive-disclosure.md` - Layered information architecture
- ✅ Created 2 new standards:
  - `command-structure.md` - Standard command format
  - `precommit-workflow.md` - Pre-commit best practices
- ✅ Created garden health check script in `.claude/hooks/`
- ✅ Consolidated INDEX.md into `.claude/INDEX.md`
- ✅ Renamed `/setup-knowledge-system` to `/seed`
- ✅ Added cross-links to all command files for better navigation
- ✅ Net reduction: 2,247 lines removed! 🌱
- ✅ Committed: refactor(knowledge): streamline commands and organize garden (806a3b1)

---

## 🎯 Current Status

**Overall Test Coverage**: 84% ⬆️ (Target: 90%+)

### Coverage by Module:
- ✅ **Agents**: 100% (react, plan_execute, base, decorators, validation)
- ✅ **Workflows**: 100% (document, multi_agent, base, decorators)
- ✅ **Memory**: 100% (checkpoint)
- ✅ **Common**: 100% (exceptions, llm resolution)
- ✅ **Tools**: 100% (docling, mistral OCR, upload_file)
- ✅ **Queue**: 93% (core functionality well-tested) ⬆️
- ⚠️ **Worker**: 84% (some edge cases remain) ⬆️

### 🐛 Known Issues (Nov 15, 2025)

**Performance Issues** (discovered during demo meeting):
1. ~~**Sluggish polling performance**: Critical UX issue~~ ✅ FIXED (Nov 16, 2025)
   - ~~AIMQ worker polling with exponential backoff~~
   - ~~Chat CLI polling response queue~~
   - ~~Combined effect: system feels very unresponsive~~
   - ~~Impact: Critical - poor user experience~~
   - ✅ Solution implemented: Supabase Realtime wake-up service
   - Workers now wake within 1 second of job enqueue
   - Phase 2 (DB triggers) will make it fully automatic

2. **Weather API unreliability**: Open-Meteo API times out intermittently
   - Impact: High - affects demo reliability
   - Solution: Switch to API-keyed provider (WeatherAPI, OpenWeather, etc.)
   - Requires: Environment variable for API key

**Runtime Issues** (from earlier testing):
3. **Tool validation errors**: `read_file` tool receiving empty dict instead of proper input
   - Error: `'path' field required` with `input_value={}`
   - Root cause: Agent not providing proper tool arguments
   - Impact: Medium - affects file operations in react-assistant

4. **Unknown tool errors**: Agent attempting to use `browse_web` tool
   - Error: Tool not registered in available tools
   - Root cause: Agent hallucinating tool names or outdated training
   - Impact: Low - agent should gracefully handle missing tools

5. **Metadata None errors**: `read_file` tool failing when metadata is None
   - Error: `unsupported operand type(s) for |: 'NoneType' and 'dict'`
   - Root cause: Tool expects metadata dict, receives None
   - Impact: Medium - needs defensive None checking

---

## 📋 Recommended Next Steps

### Priority 0: Supabase Realtime for Worker Wake-up 🚀
**Impact**: Critical | **Effort**: 2-3 hours (Phase 2 remaining) | **Status**: ✅ Phase 1 Complete!

**Branch**: `feature/supabase-realtime-wake`

**Goal**: Eliminate polling latency by using Supabase realtime to wake idle workers instantly

**Phase 1: Worker Wake-up + Presence** ✅ COMPLETE (Nov 16, 2025):
- ✅ Configuration added and auto-enabled
- ✅ `RealtimeWakeupService` implemented with async client
- ✅ Broadcast channel subscription working
- ✅ Worker presence tracking (idle/busy)
- ✅ Reconnection with exponential backoff
- ✅ Integration with `WorkerThread` complete
- ✅ Comprehensive tests passing
- ✅ Graceful shutdown fixed (no pending task errors)
- ✅ All success criteria met!

**Phase 2: DB Triggers** (2-3 hours, next step):
1. Design PostgreSQL trigger function
2. Create migration for pgmq queues
3. Add Python migration helpers
4. Test trigger emissions
5. Documentation

**Why Phase 2**: Currently, job notifications must be sent manually via Python. DB triggers will automatically emit realtime events when jobs are enqueued, making the system fully automatic and reliable.

**Documentation**: See `ideas/supabase-realtime-streaming.md` for full architecture

### Priority 1: Weather API Reliability 🌤️
**Impact**: High | **Effort**: 1-2 hours | **Status**: Planning

**Goal**: Replace unreliable Open-Meteo with a production-grade weather API

**Tasks**:
1. Evaluate weather API providers (30 min)
   - WeatherAPI.com (free tier: 1M calls/month)
   - OpenWeather (free tier: 1K calls/day, 60 calls/min)
   - Compare: reliability, features, rate limits, pricing

2. Implement new weather tool (1 hour)
   - Add `WEATHER_API_KEY` to environment variables
   - Update Weather tool to use new provider
   - Maintain same interface for agents
   - Add error handling and rate limit awareness

3. Update documentation (30 min)
   - Add API key setup to README
   - Update CHAT_DEMO.md with new provider info
   - Update .env.example

### Priority 2: Fix Message Agent Runtime Issues 🐛
**Impact**: Medium | **Effort**: 1-2 hours

Fix the runtime issues discovered during earlier testing:
1. **Tool validation errors** - Debug why agent sends empty dict to tools
2. **Unknown tool handling** - Add graceful fallback for missing tools
3. **Metadata None checks** - Add defensive None handling in tools

**Result**: Tools work reliably in all scenarios

### Priority 3: Finish Quality Sprint (Target: 90%+ coverage) 🎯

**Status**: Great progress! 84% coverage, only 6% from target.

#### 1. Worker Edge Cases (Optional) ⚠️
**Impact**: Medium | **Effort**: 1-2 hours

Currently at 84% (some edge cases remain):
- Complex signal handling scenarios
- Rare error recovery paths
- Terminal UI edge cases

**Decision**: Core functionality is well-tested. Remaining gaps are tricky edge cases that can be deferred or moved to integration tests.

#### 2. Queue Edge Cases (Optional) ⚠️
**Impact**: Low | **Effort**: 1 hour

Currently at 93% (excellent coverage):
- Some visibility timeout edge cases
- Rare connection failure scenarios

**Decision**: Core error handling (DLQ, retries, custom handlers) is thoroughly tested. Remaining gaps are acceptable.

#### 3. Minor Gaps (Optional)
**Impact**: Low | **Effort**: 30 minutes

Some `__init__.py` files at 71-82%:
- `tools/mistral/__init__.py` (75%)
- `tools/pdf/__init__.py` (71%)
- `tools/supabase/__init__.py` (82%)

**Why**: Mostly import statements, low priority.

**Recommendation**: Current coverage (84%) is solid. Move to building features!

### Priority 2: Multi-Agent Group Chat System 🚀

**Status**: Core vision - broken into independently buildable components

See [VISION.md](./VISION.md) for the high-level vision and [ideas/multi-agent-group-chat.md](./ideas/multi-agent-group-chat.md) for technical architecture. Each component below can be built and shipped independently:

#### 4. Thread Tree System
**Impact**: High | **Effort**: 2-3 days

Foundation for conversation threading:
- Recursive thread_id calculation
- Thread query helpers
- Caching strategy (materialized column or metadata)
- Tests for deep threads and branches

**Why**: Enables threaded conversations and context loading.
**See**: `ideas/thread-tree-system.md`

#### 5. Message Ingestion Pipeline
**Impact**: Critical | **Effort**: 2-3 days

Universal entry point for all messages:
- Worker task for message processing
- Parallel triage + background processing
- Error handling and retries
- Observability

**Why**: Orchestrates all message processing.
**See**: `ideas/message-ingestion-pipeline.md`

#### 6. Message Routing & Triage
**Impact**: High | **Effort**: 3-4 days

Intelligent agent selection:
- @mention detection
- Reply-to-agent detection
- Primary agent logic (keywords or LLM)
- Routing decision workflow

**Why**: Ensures right agents respond at right time.
**See**: `ideas/message-routing-triage.md`

#### 7. Agent Configuration Hierarchy
**Impact**: High | **Effort**: 2-3 days

Context-aware agent instructions:
- Load from profiles, memberships, channels, participants
- Merge instruction hierarchy (most specific wins)
- Configuration caching
- Tests for different contexts

**Why**: Agents adapt behavior to context.
**See**: `ideas/agent-configuration-hierarchy.md`

### Priority 3: Supporting Features

#### 8. RAG Workflows
**Impact**: High | **Effort**: 1-2 weeks

See `ideas/rag-workflows.md` for full design:
- Document processing (PDFs, images, Office docs)
- Embedding generation (OpenAI, Mistral)
- Vector storage (Supabase pgvector)
- Semantic search tools

**Why**: Agents need to reference documents and past conversations.

#### 9. Supabase Realtime Streaming
**Impact**: High | **Effort**: 1 week

See `ideas/supabase-realtime-streaming.md` for full design:
- Worker job notifications (no polling)
- Progress streaming (live updates)
- Response chunk streaming
- Typing indicators

**Why**: Better UX and reduced latency.

#### 10. Zep Knowledge Graphs
**Impact**: Medium | **Effort**: 2-3 weeks

See `ideas/zep-knowledge-graphs.md` for full design:
- Fact extraction
- Entity recognition
- Relationship mapping
- Shared memory across agents

**Why**: Long-term memory and relationship awareness.

#### 11. Human-in-the-Loop
**Impact**: Medium | **Effort**: 1 week

See `ideas/human-in-the-loop.md` for full design:
- Agent questions
- Approval workflows
- Pause & resume with checkpointing
- Timeout handling

**Why**: Collaborative workflows and human oversight.

### Priority 4: Documentation & Polish

#### 12. Update Documentation
**Impact**: Medium | **Effort**: 1-2 hours

- Update import paths for new module structure
- Add migration guide for refactoring
- Document multi-agent group chat architecture
- Add examples for new features

#### 13. Advanced Examples
**Impact**: Low | **Effort**: 2-3 hours

- Multi-agent collaboration example
- RAG-powered agent example
- Streaming agent example
- Human-in-the-loop example

---

## 🚀 Immediate Action Plan

**Decision**: Fix runtime issues, then continue with Multi-Agent Group Chat

### Phase 0: Fix Message Agent Issues (Today) 🐛
**Goal**: Smooth out runtime issues from demo

**Tasks**:
1. Debug tool validation errors (30-45 min)
   - Why is agent sending empty dict?
   - Add better error messages
   - Test with various inputs
2. Add unknown tool handling (15-30 min)
   - Graceful fallback when tool not found
   - Log warning instead of crashing
3. Fix metadata None checks (15-30 min)
   - Add defensive None handling in read_file
   - Check other tools for similar issues

**Total**: ~1-2 hours
**Result**: Demo runs smoothly without errors

### Phase 1: Quality Sprint (Optional) 🎯
**Goal**: Hit 90%+ test coverage

**Status**: Current coverage (84%) is solid. Can defer to focus on features.

**Tasks** (if pursuing):
1. Add worker edge case tests (2-3 hours)
2. Add queue error path tests (1-2 hours)
3. Optional: Clean up __init__.py coverage (30 min)

**Total**: ~4-5 hours
**Result**: 90%+ coverage, rock-solid foundation

### Phase 2: Multi-Agent Group Chat MVP (Next 1-2 Weeks) 🚀
**Goal**: Basic message-based agent system

**Week 1: Core Infrastructure**
1. [Thread Tree System](./ideas/thread-tree-system.md) (2-3 days)
2. [Message Ingestion Pipeline](./ideas/message-ingestion-pipeline.md) (2-3 days)
3. [Message Routing & Triage](./ideas/message-routing-triage.md) (3-4 days)

**Week 2: Agent Intelligence**
1. [Agent Configuration Hierarchy](./ideas/agent-configuration-hierarchy.md) (2-3 days)
2. Agent Response Workflows (3-4 days)
3. Integration tests and polish (2 days)

**Result**: Agents respond to @mentions and replies with context-aware instructions

### Phase 3: Enhanced Features (Future)
See `ideas/` folder for detailed designs:
- RAG workflows (document processing)
- Supabase Realtime streaming
- Zep knowledge graphs
- Human-in-the-loop workflows

---

## 📊 Module Structure (Current)

```
src/aimq/
├── agents/           # Agent implementations
│   ├── decorators.py # @agent decorator
│   ├── base.py       # BaseAgent class
│   ├── react.py      # ReAct agent
│   ├── plan_execute.py
│   ├── states.py     # AgentState TypedDict
│   └── validation.py # Tool input validation
├── workflows/        # Workflow implementations
│   ├── decorators.py # @workflow decorator
│   ├── base.py       # BaseWorkflow class
│   ├── document.py   # Document processing
│   ├── multi_agent.py
│   └── states.py     # WorkflowState TypedDict
├── memory/           # Persistence layer
│   └── checkpoint.py # Supabase checkpointing
├── common/           # Shared utilities
│   ├── exceptions.py # Custom exceptions
│   └── llm.py        # LLM resolution
└── tools/            # LangChain tools
    ├── docling/      # Document conversion
    ├── mistral/      # Mistral-specific tools
    ├── ocr/          # Image OCR
    ├── pdf/          # PDF processing
    └── supabase/     # Supabase operations
```

---

## 💡 Ideas Folder

The `ideas/` directory contains detailed designs for future features. When PLAN.md is close to completion, review these ideas and promote the most valuable ones to active development.

**Vision**:
- 🎯 [VISION.md](./VISION.md) - The living north star that guides us forward
- 🎯 [Multi-Agent Group Chat](./ideas/multi-agent-group-chat.md) - Technical architecture for the vision

**Core Infrastructure** (independently buildable):
- 🏗️ [Thread Tree System](./ideas/thread-tree-system.md) - Recursive reply threading
- 🏗️ [Message Ingestion Pipeline](./ideas/message-ingestion-pipeline.md) - Universal message processing
- 🏗️ [Message Routing & Triage](./ideas/message-routing-triage.md) - Intelligent agent selection
- 🏗️ [Agent Configuration Hierarchy](./ideas/agent-configuration-hierarchy.md) - Context-aware instructions

**Supporting Features**:
- 🌱 [RAG Workflows](./ideas/rag-workflows.md) - Document processing and retrieval
- 🌱 [Zep Knowledge Graphs](./ideas/zep-knowledge-graphs.md) - Graph-based memory
- 🌱 [Supabase Realtime Streaming](./ideas/supabase-realtime-streaming.md) - Live updates
- 🌱 [Human-in-the-Loop](./ideas/human-in-the-loop.md) - Pause/resume workflows

See `ideas/README.md` for contribution guidelines.

---

## 🤔 Open Questions

### Multi-Agent Group Chat
1. **Primary agent trigger logic**: What determines if the primary agent should respond?
   - Keywords? Sentiment? Always? ML model?
2. **Thread_id caching**: Where to cache?
   - Message metadata (jsonb)? Separate threads table? Redis?
3. **Background processing**: How to handle high message volume?
   - Queue priority? Rate limiting? Batch processing?

### RAG & Memory
4. **Embedding model**: Which to use?
   - OpenAI (expensive, good)? Mistral (privacy)? Open-source?
5. **Zep hosting**: Cloud or self-hosted?
   - Cloud (easier, costs money) vs Self-hosted (control, more work)

### Streaming
6. **Fallback strategy**: Keep polling as fallback?
   - Yes (reliable, redundant) vs No (simpler, trust Realtime)

---

**Next Steps**: Fix runtime issues, then continue building multi-agent group chat MVP! 🚀

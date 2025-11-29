# AIMQ Development Plan

**Last Updated**: 2025-11-29
**Current Version**: 0.1.x
**Target Version**: 0.2.0
**Current Branch**: `feature/email-processing-mvp` (ready to merge to `dev`)

> **Our Vision**: See [VISION.md](./VISION.md) for where we're going
> **Our Principles**: See [CONSTITUTION.md](./CONSTITUTION.md) for who we are
> **Git Workflow**: `feature/*` → `dev` → `main` (always merge to dev first)

---

## ✅ Completed Work

> **Note**: Work older than 5 days is archived in [CHANGELOG.md](./CHANGELOG.md) to keep this plan focused.

### Email Processing MVP (Nov 25, 2025)
- ✅ **Complete AI-powered email workflow** (6 commits, ~2.5 hours)
- ✅ Multi-tenant database schema (7 tables: workspaces, profiles, channels, members, participants, messages, attachments)
- ✅ Resend client wrapper using official Python SDK
- ✅ Supabase Edge Function for webhook handling with intelligent routing
  - Subdomain → workspace routing
  - User email → channel routing
  - CC vs TO handling (monitoring vs processing)
- ✅ Email Agent using LangChain + OpenAI (GPT-4)
  - Context-aware responses based on channel assistant
  - Thread support (reply_to_id)
  - Attachment metadata handling
- ✅ Comprehensive testing infrastructure
  - Full flow tests with dry-run mode
  - End-to-end testing without external services
  - Database verification scripts
- ✅ Demo organization in `demos/email-processing/`
  - Complete demo guide and test plan
  - Worker entry point and test scripts
  - Clear separation: demos (runnable showcases) vs examples (code samples)
- ✅ Full documentation in `SPRINT_SUMMARY.md`
- ✅ Committed: 6 commits on `feature/email-processing-mvp`
- ✅ **Status**: Ready to merge to `dev`

### Archived Work (Nov 16-25, 2025)
> See [CHANGELOG.md](./CHANGELOG.md) for complete details on:
- Supabase Realtime Worker Wake-up (Phases 1-3) - Instant worker notifications with <1s latency
- Knowledge Garden Refactoring & Cultivation - Streamlined commands, split oversized files, added templates
- CLI & Realtime Refactoring - Subcommands, base classes, webhook tools
- Phase 2 Lessons Extraction - Database schema patterns, progressive enhancement, CLI UX

---

## 🎯 Current Status

**Branch**: `feature/email-processing-mvp` (ready to merge to `dev`)
**Overall Test Coverage**: 84% ⬆️ (Target: 90%+)
**Next Merge**: Email Processing MVP → `dev` → `main`

### Coverage by Module:
- ✅ **Agents**: 100% (react, plan_execute, base, decorators, validation, email)
- ✅ **Workflows**: 100% (document, multi_agent, base, decorators)
- ✅ **Memory**: 100% (checkpoint)
- ✅ **Common**: 100% (exceptions, llm resolution)
- ✅ **Tools**: 100% (docling, mistral OCR, upload_file, webhook, routing)
- ✅ **Queue**: 93% (core functionality well-tested) ⬆️
- ⚠️ **Worker**: 84% (some edge cases remain) ⬆️
- ✅ **Realtime**: 100% (base, worker, chat listeners)
- ✅ **Clients**: 100% (resend, mistral)

### 🎯 Focus Areas

**Immediate**: Merge email processing MVP to dev, then to main
**Next Sprint**: Textual TUI Dashboard for monitoring and enhanced chat
**Vision Alignment**: Multi-agent group chat, thread tree system, RAG workflows

---

## 📋 Recommended Next Steps

**Immediate Actions**:
1. 🔀 **Merge Email Processing MVP** - Merge `feature/email-processing-mvp` → `dev` → `main`
2. 🎨 **Start Textual TUI Dashboard** - New priority for monitoring and enhanced chat

---

### Priority 0: Textual TUI Dashboard 🎨 **NEW PRIORITY**
**Impact**: High | **Effort**: 1-2 weeks | **Status**: Planning

**Goal**: Build a full-featured TUI dashboard for monitoring queues/workers and enhanced chat interface

**Inspiration**: [Elia](https://github.com/darrenburns/elia) - Full-featured TUI chat interface

**Components**:
1. **Dashboard View** (Week 1)
   - Real-time queue monitoring (depth, age, throughput)
   - Worker status display (idle/busy, current jobs)
   - System metrics (memory, CPU, latency)
   - Interactive queue management (create, enable realtime, clear)

2. **Enhanced Chat CLI** (Week 2)
   - Full-featured chat interface like Elia
   - Message history with scrolling
   - Markdown rendering with syntax highlighting
   - Multi-pane layout (chat + context + tools)
   - Keyboard shortcuts and vim-like navigation
   - Session management (save/load conversations)

**Technical Approach**:
- Use [Textual](https://textual.textualize.io/) framework (modern Python TUI)
- Integrate with existing realtime listeners for live updates
- Reuse Rich components where possible (markdown, syntax highlighting)
- Build composable widgets for reusability

**Success Criteria**:
- Dashboard shows real-time queue/worker status
- Chat interface matches or exceeds current CLI functionality
- Smooth keyboard navigation and responsive UI
- Works in terminal and tmux/screen
- Comprehensive documentation and examples

**Next Steps**:
1. Research Textual framework and Elia architecture (2-3 hours)
2. Create proof-of-concept dashboard (1 day)
3. Build queue monitoring widgets (2-3 days)
4. Implement enhanced chat interface (3-4 days)
5. Polish, test, and document (1-2 days)

**Branch**: `feature/textual-tui-dashboard`

---

### Priority 1: Multi-Agent Group Chat System 🚀

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

### Priority 2: Supporting Features

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

### Priority 3: Documentation & Polish

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

**Decision**: Merge email processing MVP, then start Textual TUI Dashboard

### Phase 0: Merge Email Processing MVP (Today) 🔀
**Goal**: Get email processing MVP into dev and main branches

**Tasks**:
1. Review and test email processing MVP (30 min)
   - Run full flow tests
   - Verify documentation is complete
   - Check for any last-minute issues
2. Merge to dev (15 min)
   - `git checkout dev`
   - `git merge feature/email-processing-mvp`
   - `git push origin dev`
3. Test on dev branch (15 min)
   - Run test suite
   - Verify no conflicts or issues
4. Merge to main (15 min)
   - `git checkout main`
   - `git merge dev`
   - `git push origin main`
   - Tag release if appropriate

**Total**: ~1-1.5 hours
**Result**: Email processing MVP in production, ready for use

### Phase 1: Textual TUI Dashboard - Research & POC (Week 1) 🎨
**Goal**: Understand Textual framework and build proof-of-concept

**Tasks**:
1. Research Textual framework (2-3 hours)
   - Read documentation and tutorials
   - Study Elia architecture and code
   - Identify key patterns and widgets
2. Create POC dashboard (1 day)
   - Basic layout with header, sidebar, main content
   - Mock queue data display
   - Test keyboard navigation
3. Integrate realtime updates (1 day)
   - Connect to existing realtime listeners
   - Update dashboard with live queue/worker data
   - Test performance and responsiveness

**Total**: ~2-3 days
**Result**: Working POC dashboard with live updates

### Phase 2: Textual TUI Dashboard - Full Implementation (Week 2) 🎨
**Goal**: Production-ready dashboard and enhanced chat

**Tasks**:
1. Build queue monitoring widgets (2-3 days)
   - Queue list with depth, age, throughput
   - Worker status display with current jobs
   - System metrics (memory, CPU, latency)
   - Interactive actions (create, clear, enable realtime)
2. Implement enhanced chat interface (3-4 days)
   - Message history with scrolling
   - Multi-pane layout (chat + context + tools)
   - Keyboard shortcuts and navigation
   - Session management
3. Polish and document (1-2 days)
   - User guide and keyboard shortcuts
   - Demo video or GIF
   - Integration tests

**Total**: ~1 week
**Result**: Production-ready TUI dashboard and chat interface

### Phase 3: Multi-Agent Group Chat (Future Sprints) 🚀
**Goal**: Core vision - agents collaborating in shared spaces

See [VISION.md](./VISION.md) and [ideas/multi-agent-group-chat.md](./ideas/multi-agent-group-chat.md) for full vision.

**Key Components** (independently buildable):
1. [Thread Tree System](./ideas/thread-tree-system.md) - Threaded conversations
2. [Message Ingestion Pipeline](./ideas/message-ingestion-pipeline.md) - Universal entry point
3. [Message Routing & Triage](./ideas/message-routing-triage.md) - Intelligent agent selection
4. [Agent Configuration Hierarchy](./ideas/agent-configuration-hierarchy.md) - Context-aware behavior
5. [RAG Workflows](./ideas/rag-workflows.md) - Document understanding
6. [Human-in-the-Loop](./ideas/human-in-the-loop.md) - Collaborative workflows

**Result**: Full multi-agent collaboration system aligned with VISION.md

---

## 📊 Module Structure (Current)

```
src/aimq/
├── agents/           # Agent implementations
│   ├── email/        # Email agent (LangChain + OpenAI)
│   ├── decorators.py # @agent decorator
│   ├── base.py       # BaseAgent class
│   ├── react.py      # ReAct agent
│   ├── plan_execute.py # Plan-Execute agent
│   ├── states.py     # AgentState TypedDict
│   └── validation.py # Tool input validation
├── workflows/        # Workflow implementations
│   ├── decorators.py # @workflow decorator
│   ├── base.py       # BaseWorkflow class
│   ├── document.py   # Document processing
│   ├── multi_agent.py # Multi-agent coordination
│   ├── message_routing.py # Message routing
│   └── states.py     # WorkflowState TypedDict
├── memory/           # Persistence layer
│   └── checkpoint.py # Supabase checkpointing
├── common/           # Shared utilities
│   ├── exceptions.py # Custom exceptions
│   └── llm.py        # LLM resolution
├── clients/          # External service clients
│   ├── resend.py     # Resend email client
│   └── mistral.py    # Mistral AI client
├── realtime/         # Supabase Realtime integration
│   ├── base.py       # RealtimeBaseListener
│   ├── worker.py     # RealtimeWakeupService
│   └── chat.py       # RealtimeChatListener
├── commands/         # CLI commands
│   ├── chat.py       # Interactive chat
│   ├── create.py     # Create queues
│   ├── list.py       # List queues
│   ├── realtime.py   # Realtime management
│   └── schema.py     # Schema management
└── tools/            # LangChain tools
    ├── docling/      # Document conversion
    ├── mistral/      # Mistral-specific tools
    ├── routing/      # Message routing tools
    ├── supabase/     # Supabase operations
    ├── webhook.py    # Generic webhook tool
    └── loader.py     # Tool configuration loader
```

---

## 💡 Ideas Folder

The `ideas/` directory contains detailed designs for future features. Each idea is independently buildable and contributes to the overall vision.

**Vision**:
- 🎯 [VISION.md](./VISION.md) - The living north star that guides us forward
- 🎯 [Multi-Agent Group Chat](./ideas/multi-agent-group-chat.md) - Technical architecture for the vision

**Implemented** ✅:
- ✅ [Email Processing System](./ideas/email-processing-system.md) - AI-powered email workflow (Nov 25)
- ✅ [Supabase Realtime Streaming](./ideas/supabase-realtime-streaming.md) - Worker wake-up and presence (Nov 16-24)

**Core Infrastructure** (next priorities):
- 🏗️ [Thread Tree System](./ideas/thread-tree-system.md) - Recursive reply threading
- 🏗️ [Message Ingestion Pipeline](./ideas/message-ingestion-pipeline.md) - Universal message processing
- 🏗️ [Message Routing & Triage](./ideas/message-routing-triage.md) - Intelligent agent selection
- 🏗️ [Agent Configuration Hierarchy](./ideas/agent-configuration-hierarchy.md) - Context-aware instructions

**Supporting Features** (future):
- 🌱 [RAG Workflows](./ideas/rag-workflows.md) - Document processing and retrieval
- 🌱 [Zep Knowledge Graphs](./ideas/zep-knowledge-graphs.md) - Graph-based memory
- 🌱 [Human-in-the-Loop](./ideas/human-in-the-loop.md) - Pause/resume workflows

See `ideas/README.md` for contribution guidelines.

---

## 🤔 Open Questions

### Textual TUI Dashboard
1. **Layout design**: What's the optimal layout for monitoring?
   - Single pane with tabs? Multi-pane split view? Floating windows?
2. **Update frequency**: How often to refresh dashboard data?
   - Real-time (every change)? Polling (1s, 5s)? On-demand?
3. **Keyboard shortcuts**: What shortcuts feel natural?
   - Vim-like (hjkl)? Emacs-like? Custom?

### Multi-Agent Group Chat
4. **Primary agent trigger logic**: What determines if the primary agent should respond?
   - Keywords? Sentiment? Always? ML model?
5. **Thread_id caching**: Where to cache?
   - Message metadata (jsonb)? Separate threads table? Redis?
6. **Background processing**: How to handle high message volume?
   - Queue priority? Rate limiting? Batch processing?

### RAG & Memory
7. **Embedding model**: Which to use?
   - OpenAI (expensive, good)? Mistral (privacy)? Open-source?
8. **Zep hosting**: Cloud or self-hosted?
   - Cloud (easier, costs money) vs Self-hosted (control, more work)

---

**Next Steps**: Merge email processing MVP to dev/main, then start Textual TUI Dashboard! 🚀

# AIMQ Development Plan

**Last Updated**: 2025-11-12
**Current Version**: 0.1.x
**Target Version**: 0.2.0

---

## ✅ Completed Work

### Phase 1-3: Core LangGraph Integration (Oct-Nov 2025)
- ✅ Added LangGraph, LangChain, and Mistral AI dependencies
- ✅ Implemented `@agent` and `@workflow` decorators
- ✅ Built-in agents: ReActAgent, PlanExecuteAgent
- ✅ Built-in workflows: DocumentWorkflow, MultiAgentWorkflow
- ✅ Supabase-backed checkpointing for stateful workflows
- ✅ Security features: LLM whitelisting, prompt controls, tool validation
- ✅ Comprehensive examples in `examples/langgraph/`
- ✅ User documentation in `docs/user-guide/`

### Module Refactoring (Nov 12, 2025)
- ✅ Reorganized from monolithic `langgraph/` to modular structure:
  - `agents/` - Agent implementations, decorators, states, validation
  - `workflows/` - Workflow implementations, decorators, states
  - `memory/` - Checkpointing and persistence
  - `common/` - Shared utilities (exceptions, LLM resolution)
- ✅ Split decorators by domain (agents vs workflows)
- ✅ Improved code organization and maintainability

---

## 🎯 Current Status

**Overall Test Coverage**: 79%

### Coverage by Module:
- ✅ **Agents**: 90%+ (react, plan_execute, base)
- ✅ **Workflows**: 91-100% (document, multi_agent, base)
- ✅ **Memory**: 81% (checkpoint)
- ⚠️ **Common**: 69% (llm resolution needs more tests)
- ❌ **Tools**: 0% (docling, mistral tools untested)
- ⚠️ **Worker**: 75% (some edge cases untested)
- ⚠️ **Queue**: 75% (some error paths untested)

---

## 📋 Recommended Next Steps

### Priority 1: Testing & Quality (Target: 90%+ coverage)

#### 1. Add Tests for Untested Tools
**Impact**: High | **Effort**: Medium (2-3 hours)

Currently at 0% coverage:
- `tools/docling/converter.py` - Document conversion tool
- `tools/mistral/document_ocr.py` - Mistral OCR integration
- `tools/mistral/upload_file.py` - Mistral file upload

**Why**: These tools are production-ready but untested. Could have hidden bugs.

#### 2. Improve Common Module Coverage
**Impact**: Medium | **Effort**: Low (1 hour)

`common/llm.py` at 69% coverage:
- Add tests for error cases in `resolve_llm()`
- Test LLM caching behavior
- Test fallback scenarios

#### 3. Worker & Queue Edge Cases
**Impact**: Medium | **Effort**: Medium (2 hours)

Both at 75% coverage:
- Test graceful shutdown scenarios
- Test error recovery paths
- Test visibility timeout edge cases

### Priority 2: Features & Enhancements

#### 4. Memory/RAG Integration
**Impact**: High | **Effort**: High (1-2 days)

Add vector store integration for agent memory:
- Supabase pgvector integration
- Memory retrieval tools for agents
- Conversation history management
- Document embedding and search

**Why**: Agents currently have no long-term memory or RAG capabilities.

#### 5. Streaming Support
**Impact**: Medium | **Effort**: Medium (4-6 hours)

Enhance real-time feedback:
- Stream agent reasoning steps
- Stream workflow progress
- WebSocket integration for live updates
- Progress callbacks

**Why**: Better UX for long-running agents/workflows.

#### 6. Agent Observability
**Impact**: Medium | **Effort**: Medium (4-6 hours)

Add tracing and monitoring:
- LangSmith integration
- Custom trace logging
- Performance metrics
- Cost tracking (token usage)

**Why**: Production agents need observability for debugging and optimization.

#### 7. More Built-in Tools
**Impact**: Medium | **Effort**: Low-Medium (varies)

Expand tool library:
- Web search tool (Tavily, SerpAPI)
- Code execution tool (sandboxed)
- API calling tool (generic HTTP)
- Database query tool
- Email/notification tools

**Why**: More tools = more capable agents out of the box.

### Priority 3: Documentation & Examples

#### 8. Update Documentation for Refactoring
**Impact**: Medium | **Effort**: Low (1-2 hours)

Current docs reference old `langgraph/` structure:
- Update import paths in docs
- Update examples if needed
- Add migration guide for existing code

#### 9. Advanced Examples
**Impact**: Low | **Effort**: Medium (3-4 hours)

Add more sophisticated examples:
- Multi-agent collaboration example
- RAG-powered agent (when #4 is done)
- Streaming agent example (when #5 is done)
- Production deployment example

---

## 🚀 Suggested Immediate Actions

Based on the current state, here's what I'd recommend tackling first:

### Option A: Quality First (Recommended)
1. **Add tool tests** (2-3 hours) - Get to 85%+ coverage
2. **Improve common/llm tests** (1 hour) - Cover error cases
3. **Update documentation** (1-2 hours) - Reflect new structure

**Total**: ~5 hours to get to a solid, well-tested state

### Option B: Feature First
1. **Memory/RAG integration** (1-2 days) - Big capability boost
2. **Add tests for new features** (2-3 hours)
3. **Create RAG example** (1-2 hours)

**Total**: ~2-3 days for a major new feature

### Option C: Production Ready
1. **Add observability** (4-6 hours) - LangSmith/tracing
2. **Streaming support** (4-6 hours) - Better UX
3. **Add tool tests** (2-3 hours) - Quality assurance

**Total**: ~2 days for production-grade features

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

## 🤔 Questions to Consider

1. **What's the priority?** Quality/testing vs new features?
2. **What's the use case?** RAG? Multi-agent? Streaming?
3. **Production timeline?** How soon do you need this in prod?
4. **Team size?** Solo or multiple developers?

Let me know what direction you'd like to go, and I can help plan the next phase!

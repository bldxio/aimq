# Vision-Driven Development

## Overview

A development approach that separates long-term vision from tactical execution. The vision guides direction while the plan tracks progress.

## The Problem

Traditional planning often conflates:
- **Where we're going** (vision)
- **What we're doing now** (plan)
- **How we got here** (history)

This leads to:
- Plans that become outdated quickly
- Vision that gets lost in details
- Difficulty adapting to change
- Confusion about priorities

## The Solution

Separate concerns into distinct documents:

```
CONSTITUTION.md  → Who we are (principles, values)
    ↓
VISION.md        → Where we're going (goals, dreams)
    ↓
GARDEN/          → What we know (patterns, lessons)
    ↓
PLAN.md          → What we're doing (tasks, progress)
```

## VISION.md

### Purpose

The **living north star** that:
- Describes the future we're building
- Captures the "why" behind the work
- Evolves as the product grows
- Inspires and guides decisions

### What Goes In

**The Big Picture**:
- What problem are we solving?
- Who are we solving it for?
- What does success look like?
- Why does this matter?

**Core Capabilities**:
- What can the system do?
- What makes it unique?
- What are the key features?
- What's the user experience?

**Technical Vision**:
- What's the architecture?
- What are the key technologies?
- What are the design principles?
- What are the constraints?

**Future Possibilities**:
- What could we build next?
- What are the opportunities?
- What are the challenges?
- What are we learning?

### What Doesn't Go In

- ❌ Specific tasks or tickets
- ❌ Implementation details
- ❌ Current bugs or issues
- ❌ Completed work
- ❌ Tactical decisions

### Example Structure

```markdown
# Vision: Multi-Agent Group Chat

## The Dream

A collaborative AI system where multiple agents work together
in group conversations, each with their own expertise and personality.

## Core Capabilities

### 1. Multi-Agent Conversations
- Multiple agents in one channel
- Each agent has unique role
- Agents coordinate responses
- Natural conversation flow

### 2. Intelligent Routing
- Agents respond when relevant
- @mentions trigger specific agents
- Context-aware participation
- Avoid duplicate responses

### 3. Shared Memory
- Agents share knowledge
- Learn from conversations
- Build knowledge graphs
- Maintain context

## Technical Vision

### Architecture
- Event-driven message processing
- LangGraph for agent orchestration
- Supabase for persistence
- Real-time streaming updates

### Key Technologies
- LangChain/LangGraph for agents
- Supabase pgmq for queuing
- Zep for memory/knowledge graphs
- Supabase Realtime for streaming

## Future Possibilities

### Near-term (3-6 months)
- RAG with document processing
- Knowledge graph integration
- Human-in-the-loop workflows
- Advanced routing logic

### Long-term (6-12 months)
- Multi-workspace support
- Custom agent creation
- Agent marketplace
- Advanced analytics

## Open Questions

- How to handle agent conflicts?
- What's the right memory strategy?
- How to scale to 100+ agents?
- How to ensure response quality?
```

## PLAN.md

### Purpose

The **tactical tracker** that:
- Lists current tasks
- Tracks progress
- Notes blockers
- Plans next steps

### What Goes In

**Current Status**:
- What's in progress?
- What's completed recently?
- What's blocked?
- What's the priority?

**Next Steps**:
- What's coming next?
- What's the order?
- What's the estimate?
- What are the dependencies?

**Open Questions**:
- What needs deciding?
- What needs research?
- What needs discussion?
- What's unclear?

### What Doesn't Go In

- ❌ Long-term vision
- ❌ Architectural philosophy
- ❌ Guiding principles
- ❌ Future possibilities
- ❌ "Someday" ideas

### Example Structure

```markdown
# Project Plan

**Last Updated**: 2025-11-13

## ✅ Recently Completed

- [x] Improve test coverage to 84%
- [x] Add DLQ error handling
- [x] Create VISION.md
- [x] Add knowledge garden system

## 🎯 Current Focus

**This Week**: Testing & Documentation
- [ ] Test tools/ directory (0% coverage)
- [ ] Improve worker coverage to 90%
- [ ] Update architecture docs

## 📋 Next Steps

**Option A: Quality Focus** (Recommended)
1. Complete test coverage (2-3 hours)
2. Fix remaining warnings (1 hour)
3. Update documentation (1 hour)

**Option B: New Features**
1. Implement message routing (1-2 days)
2. Add RAG workflows (2-3 days)
3. Create examples (1 day)

## 🤔 Open Questions

- Should we prioritize coverage or features?
- What's the right memory strategy?
- When to start on multi-agent chat?
```

## IDEAS/ Folder

### Purpose

The **idea incubator** for:
- Future features
- Someday thoughts
- Brainstorming
- Exploration

### What Goes In

**Detailed Ideas**:
- Feature proposals
- Technical explorations
- Architecture options
- Research notes

**Links to Vision**:
- How does this support the vision?
- What problem does it solve?
- What's the value?
- What are the trade-offs?

### Example Structure

```
ideas/
├── README.md                          # Index of ideas
├── multi-agent-group-chat.md         # Main vision (technical)
├── thread-tree-system.md             # Supporting feature
├── message-routing-triage.md         # Supporting feature
├── rag-workflows.md                  # Supporting feature
└── zep-knowledge-graphs.md           # Supporting feature
```

## The Workflow

### 1. Start with Vision

When starting a new project or feature:

1. **Write the vision** - What are we building?
2. **Break it down** - What are the components?
3. **Create ideas** - One idea per component
4. **Link them** - Show relationships

### 2. Plan from Vision

When planning work:

1. **Review vision** - What's the goal?
2. **Check ideas** - What's ready to build?
3. **Create plan** - What's next?
4. **Execute** - Build it!

### 3. Update as You Go

As you work:

1. **Update plan** - Mark progress
2. **Refine vision** - Adjust as you learn
3. **Add ideas** - Capture new thoughts
4. **Link everything** - Keep it connected

### 4. Review Regularly

Weekly or monthly:

1. **Review progress** - What's done?
2. **Update vision** - Still accurate?
3. **Refine plan** - What's next?
4. **Prune ideas** - Still relevant?

## Benefits

### Clear Direction

- Everyone knows where we're going
- Decisions align with vision
- Priorities are clear
- Focus is maintained

### Flexibility

- Vision evolves with learning
- Plan adapts to reality
- Ideas can be explored
- Change is expected

### Motivation

- Vision inspires
- Progress is visible
- Wins are celebrated
- Future is exciting

### Collaboration

- Shared understanding
- Clear communication
- Aligned efforts
- Collective ownership

## Real-World Example

From our project:

**Vision**: Multi-agent group chat system
- Living document in VISION.md
- Describes the dream
- Evolves with product

**Ideas**: 9 supporting features
- Each in ideas/ folder
- Links to vision
- Can be built independently

**Plan**: Current work
- Testing and quality
- Next: message routing
- Then: RAG workflows

**Result**:
- Clear direction (vision)
- Manageable tasks (plan)
- Future possibilities (ideas)
- Flexibility to adapt

## Anti-Patterns

### ❌ Don't

- Mix vision and plan in one document
- Let vision become a rigid spec
- Ignore vision when planning
- Let plan become outdated
- Forget to update vision
- Lose ideas in chat history

### ✅ Do

- Keep vision and plan separate
- Let vision evolve
- Reference vision when planning
- Update plan frequently
- Refine vision as you learn
- Capture ideas in ideas/

## Related

- [Knowledge Garden](../quick-references/knowledge-garden.md) - Knowledge management
- [Planning](../../PLAN.md) - Current project plan
- [Vision](../../VISION.md) - Project vision
- [Constitution](../../CONSTITUTION.md) - Guiding principles

---

**Remember**: Vision without execution is hallucination. Execution without vision is wandering. Together, they're magic! 🎯✨

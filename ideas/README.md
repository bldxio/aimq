# Ideas - Future Features & Explorations

This directory contains brainstorming, design docs, and planning for future features that aren't yet in active development.

## Purpose

The ideas folder is a "parking lot" for exciting features and concepts that we want to build someday. When PLAN.md is close to completion, we review these ideas and promote the most valuable ones to active development.

## Structure

Each idea gets its own markdown file with:
- **What**: Clear description of the feature
- **Why**: Value proposition and motivation
- **How**: Technical approach and architecture
- **Dependencies**: What needs to exist first
- **Open Questions**: Things to figure out
- **Status**: Current state (brainstorming, designed, ready, in-progress)

## Current Ideas

### 🎯 Vision
- [**VISION.md**](../VISION.md) - The living north star (root level)
- [**Multi-Agent Group Chat**](./multi-agent-group-chat.md) - Technical architecture for the vision

### 🏗️ Core Infrastructure (Building Blocks)
- [**Thread Tree System**](./thread-tree-system.md) - Recursive reply threading
- [**Message Ingestion Pipeline**](./message-ingestion-pipeline.md) - Universal message processing
- [**Message Routing & Triage**](./message-routing-triage.md) - Intelligent agent selection
- [**Agent Configuration Hierarchy**](./agent-configuration-hierarchy.md) - Context-aware instructions

### 🌱 Supporting Features
- [**RAG Workflows**](./rag-workflows.md) - Document processing and retrieval
- [**Zep Knowledge Graphs**](./zep-knowledge-graphs.md) - Graph-based memory and relationships
- [**Supabase Realtime Streaming**](./supabase-realtime-streaming.md) - Live updates without polling
- [**Human-in-the-Loop**](./human-in-the-loop.md) - Pause/resume with checkpointing

## Contributing Ideas

When adding a new idea:
1. Create a new markdown file with a descriptive name
2. Use the template structure (what/why/how/dependencies/questions)
3. Link it in this README under the appropriate section
4. Keep it high-level - details can evolve
5. Cross-reference related ideas

## Promoting Ideas to PLAN.md

When an idea is ready for active development:
1. Ensure dependencies are met
2. Break it down into concrete tasks
3. Add to PLAN.md under "Recommended Next Steps"
4. Update the idea's status to "in-progress"
5. Link back to the idea doc for context

---

**Remember**: Ideas are meant to be exciting and exploratory! Don't worry about perfection - capture the vision and iterate! ✨

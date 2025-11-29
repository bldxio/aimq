# Zep Knowledge Graphs - Graph-Based Memory

**Status**: 🌱 Future Feature
**Priority**: Medium-High
**Complexity**: High
**Estimated Effort**: 2-3 weeks

---

## What

Integration with [Zep](https://www.getzep.com/) for graph-based memory and knowledge management. Zep provides persistent memory for LLM applications with automatic fact extraction, entity recognition, and relationship mapping.

### Key Features

- **Automatic Fact Extraction**: Extract facts from conversations
- **Entity Recognition**: Identify people, places, organizations, concepts
- **Relationship Mapping**: Build knowledge graphs of entities and relationships
- **Temporal Memory**: Track how knowledge evolves over time
- **Semantic Search**: Search memory using natural language
- **Memory Summarization**: Automatic conversation summaries
- **Shared Memory**: Cross-agent memory access

---

## Why

### Business Value
- **Long-Term Memory**: Agents remember facts across sessions
- **Relationship Awareness**: Understand connections between entities
- **Contextual Intelligence**: Better responses based on accumulated knowledge
- **Knowledge Discovery**: Surface insights from conversation history

### Technical Value
- **Proven Solution**: Zep is battle-tested for LLM memory
- **Graph Database**: Neo4j-backed for complex queries
- **LangChain Integration**: Works seamlessly with existing agents
- **Scalable**: Handles millions of facts and relationships

---

## Architecture

### Zep Components

```
Conversation → Zep Memory Store
    ↓
[Fact Extraction]
    ├─ Entities (people, places, things)
    ├─ Facts (statements about entities)
    └─ Relationships (connections between entities)
    ↓
[Knowledge Graph]
    ├─ Nodes (entities)
    └─ Edges (relationships)
    ↓
[Memory Retrieval]
    ├─ Semantic search
    ├─ Entity lookup
    └─ Relationship traversal
```

### Integration with AIMQ

```
Message arrives
    ↓
[Background Processing]
    ├─ Extract facts → Zep
    ├─ Update embeddings → pgvector
    └─ Update knowledge graph → Zep
    ↓
[Agent Execution]
    ├─ Load thread checkpoint → Supabase
    ├─ Load relevant facts → Zep
    ├─ Load relevant documents → pgvector
    └─ Execute with full context
```

---

## Technical Design

### Zep Setup

```python
from zep_python import ZepClient
from zep_python.memory import Memory, Message as ZepMessage

# Initialize Zep client
zep = ZepClient(
    api_url=os.getenv("ZEP_API_URL"),
    api_key=os.getenv("ZEP_API_KEY")
)

# Create session for each thread
session_id = f"{workspace_id}:{channel_id}:{thread_id}"
```

### Memory Storage Workflow

```python
@workflow
class ZepMemoryWorkflow(BaseWorkflow):
    """Store conversation in Zep for fact extraction"""

    async def run(self, message: Message):
        # Get thread context
        thread_id = message.metadata.get("thread_id", message.id)
        session_id = f"{message.workspace_id}:{message.channel_id}:{thread_id}"

        # Convert to Zep message format
        zep_message = ZepMessage(
            role=message.role,
            content=message.content,
            metadata={
                "message_id": str(message.id),
                "author_id": str(message.author_id),
                "created_at": message.created_at.isoformat()
            }
        )

        # Add to Zep memory
        await zep.memory.add_memory(
            session_id=session_id,
            messages=[zep_message]
        )

        # Zep automatically extracts facts, entities, and relationships
```

### Memory Retrieval Tool

```python
from langchain.tools import BaseTool

class ZepMemorySearchTool(BaseTool):
    """Search Zep memory for relevant facts"""

    name = "search_memory"
    description = "Search conversation memory for relevant facts and context"

    async def _arun(
        self,
        query: str,
        workspace_id: str,
        channel_id: str,
        thread_id: str,
        limit: int = 10
    ) -> List[Dict]:
        """Search Zep memory"""

        session_id = f"{workspace_id}:{channel_id}:{thread_id}"

        # Search memory
        results = await zep.memory.search_memory(
            session_id=session_id,
            query=query,
            limit=limit
        )

        return [
            {
                "content": result.message.content,
                "role": result.message.role,
                "score": result.score,
                "metadata": result.message.metadata
            }
            for result in results
        ]

class ZepFactSearchTool(BaseTool):
    """Search for specific facts in memory"""

    name = "search_facts"
    description = "Search for specific facts about entities"

    async def _arun(
        self,
        query: str,
        workspace_id: str,
        channel_id: str,
        thread_id: str
    ) -> List[Dict]:
        """Search facts"""

        session_id = f"{workspace_id}:{channel_id}:{thread_id}"

        # Get memory with facts
        memory = await zep.memory.get_memory(session_id=session_id)

        # Extract relevant facts
        facts = [
            {
                "fact": fact.fact,
                "entities": fact.entities,
                "created_at": fact.created_at
            }
            for fact in memory.facts
            if query.lower() in fact.fact.lower()
        ]

        return facts
```

### Shared Memory Across Agents

```python
class ZepSharedMemoryTool(BaseTool):
    """Access shared memory across agents in a workspace"""

    name = "search_workspace_memory"
    description = "Search all conversations in the workspace for relevant context"

    async def _arun(
        self,
        query: str,
        workspace_id: str,
        limit: int = 10
    ) -> List[Dict]:
        """Search across all sessions in workspace"""

        # Get all sessions for workspace
        sessions = await db.get_workspace_sessions(workspace_id)

        results = []
        for session in sessions:
            session_id = f"{workspace_id}:{session.channel_id}:{session.thread_id}"

            # Search each session
            session_results = await zep.memory.search_memory(
                session_id=session_id,
                query=query,
                limit=limit
            )

            results.extend(session_results)

        # Sort by relevance
        results.sort(key=lambda x: x.score, reverse=True)

        return results[:limit]
```

### Agent Integration

```python
@agent
class ZepEnabledAgent(ReActAgent):
    """Agent with Zep memory integration"""

    def __init__(self, config: AgentConfig):
        super().__init__(config)

        # Add Zep memory tools
        self.tools.extend([
            ZepMemorySearchTool(),
            ZepFactSearchTool(),
            ZepSharedMemoryTool()
        ])

    async def run(self, messages: List[Message], checkpoint: Optional[Checkpoint] = None):
        # Load Zep memory for context
        thread_id = messages[0].metadata.get("thread_id")
        session_id = f"{messages[0].workspace_id}:{messages[0].channel_id}:{thread_id}"

        # Get memory summary
        memory = await zep.memory.get_memory(session_id=session_id)

        # Add memory summary to system prompt
        memory_context = f"""
        Conversation Summary: {memory.summary}

        Key Facts:
        {chr(10).join(f"- {fact.fact}" for fact in memory.facts[:10])}

        Entities:
        {chr(10).join(f"- {entity.name} ({entity.type})" for entity in memory.entities[:10])}
        """

        # Execute agent with memory context
        return await super().run(
            messages=messages,
            checkpoint=checkpoint,
            additional_context=memory_context
        )
```

---

## Dependencies

### Existing Features
- ✅ Message processing workflows
- ✅ Agent execution system
- ✅ Checkpoint management

### Required Features
- ⚠️ Zep Cloud account or self-hosted Zep instance
- ⚠️ Zep Python SDK integration
- ⚠️ Session management (mapping threads to Zep sessions)
- ⚠️ Memory retrieval tools

### Nice-to-Have
- 🔮 Zep UI integration (view knowledge graphs)
- 🔮 Custom fact extraction rules
- 🔮 Memory pruning strategies
- 🔮 Cross-workspace memory (with permissions)

---

## Implementation Phases

### Phase 1: Basic Integration (Week 1)
- [ ] Set up Zep (Cloud or self-hosted)
- [ ] Integrate Zep Python SDK
- [ ] Create session management system
- [ ] Implement memory storage workflow
- [ ] Test fact extraction

### Phase 2: Memory Retrieval (Week 1-2)
- [ ] Implement memory search tool
- [ ] Implement fact search tool
- [ ] Add memory context to agents
- [ ] Test retrieval accuracy

### Phase 3: Shared Memory (Week 2)
- [ ] Implement workspace-wide memory search
- [ ] Add permission checks
- [ ] Test cross-agent memory access
- [ ] Add memory summarization

### Phase 4: Advanced Features (Week 3)
- [ ] Add entity relationship queries
- [ ] Implement memory pruning
- [ ] Add custom fact extraction rules
- [ ] Optimize performance

---

## Open Questions

1. **Zep Hosting**: Cloud or self-hosted?
   - Cloud: Easier, managed, costs money
   - Self-hosted: More control, privacy, more work

2. **Session Scope**: What defines a Zep session?
   - Per thread? (isolated memory)
   - Per channel? (shared channel memory)
   - Per workspace? (shared workspace memory)
   - Hierarchical? (thread → channel → workspace)

3. **Memory Sharing**: How to handle privacy?
   - All agents see all memory? (simple, less private)
   - Permission-based? (complex, more private)
   - Opt-in sharing? (flexible, more work)

4. **Fact Extraction**: Use Zep's automatic extraction or custom?
   - Automatic: Easy, works well
   - Custom: More control, more work
   - Hybrid: Best of both

5. **Memory Pruning**: How to manage memory growth?
   - Keep everything? (expensive, comprehensive)
   - Prune old facts? (cheaper, may lose context)
   - Summarize old conversations? (balanced)

6. **Integration with RAG**: How do Zep and pgvector work together?
   - Zep for facts/entities, pgvector for documents
   - Zep for short-term, pgvector for long-term
   - Both for everything (redundant but robust)

---

## Success Metrics

- ✅ Facts extracted from 90%+ of messages
- ✅ Memory search returns relevant results
- ✅ Agents use memory context in responses
- ⚡ Memory retrieval <500ms
- ⚡ Fact extraction <5 seconds per message

---

## Related Ideas

- [Multi-Agent Group Chat](./multi-agent-group-chat.md) - Uses Zep for shared memory
- [RAG Workflows](./rag-workflows.md) - Complementary to Zep (documents vs facts)
- [Human-in-the-Loop](./human-in-the-loop.md) - May use memory for context

---

## Resources

- [Zep Documentation](https://docs.getzep.com/)
- [Zep Python SDK](https://github.com/getzep/zep-python)
- [LangChain Zep Integration](https://python.langchain.com/docs/integrations/memory/zep_memory)

---

**Last Updated**: 2025-11-13
**Status**: Planning - exciting but not immediate priority

# RAG Workflows - Document Processing & Retrieval

**Status**: 🌱 Future Feature
**Priority**: High - Needed for multi-agent chat
**Complexity**: Medium
**Estimated Effort**: 1-2 weeks

---

## What

Retrieval-Augmented Generation (RAG) workflows that process documents, create embeddings, store them in vector databases, and provide retrieval tools for agents to access relevant context.

### Key Features

- **Document Processing**: Extract text from PDFs, images, Office docs, etc.
- **Chunking Strategies**: Smart text splitting for optimal retrieval
- **Embedding Generation**: Create vector embeddings using various models
- **Vector Storage**: Store in Supabase pgvector
- **Semantic Search**: Retrieve relevant chunks based on queries
- **Hybrid Search**: Combine vector similarity with keyword search
- **Metadata Filtering**: Filter by workspace, channel, author, date, etc.

---

## Why

### Business Value
- **Contextual Responses**: Agents can reference past conversations and documents
- **Knowledge Base**: Build organizational memory over time
- **Document Q&A**: Users can ask questions about uploaded documents
- **Reduced Hallucinations**: Ground agent responses in actual data

### Technical Value
- **Scalable**: Supabase pgvector handles millions of embeddings
- **Fast**: Vector similarity search is highly optimized
- **Flexible**: Support multiple embedding models and strategies

---

## Architecture

### Components

```
Document Upload
    ↓
[Document Processing Workflow]
    ├─ Extract text (docling, OCR, etc.)
    ├─ Chunk text (semantic, fixed-size, etc.)
    ├─ Generate embeddings (OpenAI, Mistral, etc.)
    └─ Store in pgvector
    ↓
[Retrieval Tools]
    ├─ Semantic search
    ├─ Keyword search
    └─ Hybrid search
    ↓
Agent uses tools to retrieve context
```

### Database Schema

```sql
-- Embeddings table
CREATE TABLE embeddings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID NOT NULL REFERENCES workspaces(id),
    channel_id UUID REFERENCES channels(id),
    message_id UUID REFERENCES messages(id),
    document_id UUID REFERENCES documents(id),

    content TEXT NOT NULL,
    embedding VECTOR(1536),  -- Dimension depends on model

    metadata JSONB DEFAULT '{}',

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Indexes
CREATE INDEX embeddings_workspace_id_idx ON embeddings(workspace_id);
CREATE INDEX embeddings_channel_id_idx ON embeddings(channel_id);
CREATE INDEX embeddings_message_id_idx ON embeddings(message_id);
CREATE INDEX embeddings_document_id_idx ON embeddings(document_id);

-- Vector similarity index (HNSW for fast approximate search)
CREATE INDEX embeddings_vector_idx ON embeddings
USING hnsw (embedding vector_cosine_ops);

-- Documents table (for uploaded files)
CREATE TABLE documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID NOT NULL REFERENCES workspaces(id),
    channel_id UUID REFERENCES channels(id),
    message_id UUID REFERENCES messages(id),

    filename TEXT NOT NULL,
    content_type TEXT NOT NULL,
    size_bytes INTEGER NOT NULL,
    storage_path TEXT NOT NULL,

    status TEXT NOT NULL DEFAULT 'pending',  -- pending, processing, completed, failed
    error TEXT,

    metadata JSONB DEFAULT '{}',

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

---

## Technical Design

### Document Processing Workflow

```python
@workflow
class DocumentProcessingWorkflow(BaseWorkflow):
    """Process uploaded documents and create embeddings"""

    async def run(self, document_id: str):
        # Load document
        document = await db.documents.get(document_id)
        await db.documents.update(document_id, status="processing")

        try:
            # Extract text
            text = await self.extract_text(document)

            # Chunk text
            chunks = await self.chunk_text(text, document)

            # Generate embeddings
            embeddings = await self.generate_embeddings(chunks)

            # Store embeddings
            await self.store_embeddings(embeddings, document)

            # Update document status
            await db.documents.update(document_id, status="completed")

        except Exception as e:
            await db.documents.update(
                document_id,
                status="failed",
                error=str(e)
            )
            raise

    async def extract_text(self, document: Document) -> str:
        """Extract text based on content type"""
        if document.content_type == "application/pdf":
            return await extract_pdf_text(document.storage_path)
        elif document.content_type.startswith("image/"):
            return await extract_image_text_ocr(document.storage_path)
        elif document.content_type in ["application/msword", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"]:
            return await extract_docx_text(document.storage_path)
        else:
            raise ValueError(f"Unsupported content type: {document.content_type}")

    async def chunk_text(self, text: str, document: Document) -> List[Chunk]:
        """Split text into chunks for embedding"""
        # Use LangChain text splitters
        from langchain.text_splitter import RecursiveCharacterTextSplitter

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            separators=["\n\n", "\n", ". ", " ", ""]
        )

        chunks = splitter.split_text(text)

        return [
            Chunk(
                content=chunk,
                metadata={
                    "document_id": document.id,
                    "workspace_id": document.workspace_id,
                    "channel_id": document.channel_id,
                    "message_id": document.message_id,
                    "chunk_index": i,
                    "total_chunks": len(chunks)
                }
            )
            for i, chunk in enumerate(chunks)
        ]

    async def generate_embeddings(self, chunks: List[Chunk]) -> List[Embedding]:
        """Generate embeddings for chunks"""
        from langchain.embeddings import OpenAIEmbeddings

        embeddings_model = OpenAIEmbeddings(model="text-embedding-3-small")

        # Batch process for efficiency
        texts = [chunk.content for chunk in chunks]
        vectors = await embeddings_model.aembed_documents(texts)

        return [
            Embedding(
                content=chunk.content,
                vector=vector,
                metadata=chunk.metadata
            )
            for chunk, vector in zip(chunks, vectors)
        ]

    async def store_embeddings(self, embeddings: List[Embedding], document: Document):
        """Store embeddings in pgvector"""
        for embedding in embeddings:
            await db.embeddings.create(
                workspace_id=document.workspace_id,
                channel_id=document.channel_id,
                message_id=document.message_id,
                document_id=document.id,
                content=embedding.content,
                embedding=embedding.vector,
                metadata=embedding.metadata
            )
```

### Retrieval Tools

```python
from langchain.tools import BaseTool

class SemanticSearchTool(BaseTool):
    """Search for relevant context using vector similarity"""

    name = "semantic_search"
    description = "Search for relevant information using semantic similarity"

    async def _arun(
        self,
        query: str,
        workspace_id: str,
        channel_id: Optional[str] = None,
        limit: int = 5
    ) -> List[Dict]:
        """Search embeddings"""

        # Generate query embedding
        embeddings_model = OpenAIEmbeddings(model="text-embedding-3-small")
        query_vector = await embeddings_model.aembed_query(query)

        # Search pgvector
        results = await db.embeddings.search(
            workspace_id=workspace_id,
            channel_id=channel_id,
            query_vector=query_vector,
            limit=limit
        )

        return [
            {
                "content": result.content,
                "similarity": result.similarity,
                "metadata": result.metadata
            }
            for result in results
        ]

class HybridSearchTool(BaseTool):
    """Combine vector similarity with keyword search"""

    name = "hybrid_search"
    description = "Search using both semantic similarity and keywords"

    async def _arun(
        self,
        query: str,
        workspace_id: str,
        channel_id: Optional[str] = None,
        limit: int = 5
    ) -> List[Dict]:
        """Hybrid search"""

        # Vector search
        semantic_results = await semantic_search(
            query=query,
            workspace_id=workspace_id,
            channel_id=channel_id,
            limit=limit * 2  # Get more candidates
        )

        # Keyword search (PostgreSQL full-text search)
        keyword_results = await db.embeddings.keyword_search(
            query=query,
            workspace_id=workspace_id,
            channel_id=channel_id,
            limit=limit * 2
        )

        # Combine and re-rank (Reciprocal Rank Fusion)
        combined = reciprocal_rank_fusion(
            [semantic_results, keyword_results],
            limit=limit
        )

        return combined
```

### Message Embedding Workflow

```python
@workflow
class MessageEmbeddingWorkflow(BaseWorkflow):
    """Create embeddings for messages (for conversation search)"""

    async def run(self, message_id: str):
        message = await db.messages.get(message_id)

        # Skip if no content
        if not message.content:
            return

        # Generate embedding
        embeddings_model = OpenAIEmbeddings(model="text-embedding-3-small")
        vector = await embeddings_model.aembed_query(message.content)

        # Store embedding
        await db.embeddings.create(
            workspace_id=message.workspace_id,
            channel_id=message.channel_id,
            message_id=message.id,
            content=message.content,
            embedding=vector,
            metadata={
                "author_id": message.author_id,
                "role": message.role,
                "created_at": message.created_at.isoformat()
            }
        )
```

---

## Dependencies

### Existing Features
- ✅ Document conversion tools (docling)
- ✅ OCR tools (Mistral, image OCR)
- ✅ Supabase integration
- ✅ Worker task system

### Required Features
- ⚠️ Supabase pgvector setup
- ⚠️ Embedding model integration (OpenAI, Mistral, etc.)
- ⚠️ Document storage (Supabase Storage)
- ⚠️ Chunking strategies

### Nice-to-Have
- 🔮 Multiple embedding models (for comparison)
- 🔮 Re-ranking models (for better results)
- 🔮 Semantic chunking (vs fixed-size)
- 🔮 Document versioning

---

## Implementation Phases

### Phase 1: Basic Document Processing (Week 1)
- [ ] Set up pgvector in Supabase
- [ ] Create embeddings and documents tables
- [ ] Implement document processing workflow
- [ ] Add text extraction for PDFs and images
- [ ] Add basic chunking (fixed-size)
- [ ] Generate embeddings with OpenAI

### Phase 2: Retrieval Tools (Week 1)
- [ ] Implement semantic search tool
- [ ] Add keyword search
- [ ] Create hybrid search tool
- [ ] Add metadata filtering
- [ ] Test retrieval accuracy

### Phase 3: Message Embeddings (Week 2)
- [ ] Implement message embedding workflow
- [ ] Integrate with message processing
- [ ] Add conversation search
- [ ] Test with real conversations

### Phase 4: Optimization (Week 2)
- [ ] Optimize chunking strategies
- [ ] Add re-ranking
- [ ] Implement caching
- [ ] Load testing
- [ ] Add observability

---

## Open Questions

1. **Embedding Model**: Which model to use?
   - OpenAI text-embedding-3-small (1536 dims, cheap, fast)
   - OpenAI text-embedding-3-large (3072 dims, expensive, better)
   - Mistral embed (1024 dims, privacy)
   - Open-source (sentence-transformers)

2. **Chunking Strategy**: How to split text?
   - Fixed-size with overlap (simple, works well)
   - Semantic chunking (better context, more complex)
   - Sentence-based (natural boundaries)
   - Paragraph-based (preserves structure)

3. **Search Strategy**: Vector only or hybrid?
   - Vector search is great for semantic similarity
   - Keyword search is better for exact matches
   - Hybrid combines both (recommended)

4. **Scope**: What to embed?
   - All messages? (expensive, comprehensive)
   - Only documents? (cheaper, limited)
   - Configurable per workspace? (flexible)

5. **Privacy**: How to handle sensitive data?
   - Encrypt embeddings?
   - Use local embedding models?
   - Workspace-level isolation?

---

## Success Metrics

- ✅ Documents processed within 60 seconds
- ✅ Embeddings generated for 95%+ of documents
- ✅ Search returns relevant results (user feedback)
- ⚡ Search latency <500ms
- ⚡ Handles 1000+ documents per workspace

---

## Related Ideas

- [Multi-Agent Group Chat](./multi-agent-group-chat.md) - Uses RAG for context
- [Zep Knowledge Graphs](./zep-knowledge-graphs.md) - Complementary memory system
- [Human-in-the-Loop](./human-in-the-loop.md) - May need document context

---

**Last Updated**: 2025-11-13
**Status**: Planning - waiting for multi-agent chat foundation

# Email Processing System

**Status**: In Progress (Demo Sprint - 2025-11-25)
**Timeline**: 6-hour sprint for MVP demo
**Branch**: `feature/supabase-realtime-wake`

## Overview

AI-powered email processing system that monitors project communications via CC/BCC, analyzes sentiment, processes attachments, and generates intelligent responses. Uses Resend.com for inbound/outbound email, Supabase for storage, and AIMQ for queue-based processing.

## Vision (Full Implementation)

### Core Flow

```
Resend Webhook → Supabase Edge Function → incoming-messages queue
    ↓
Route & Parse (workspace/channel detection)
    ↓
Fetch Attachments → Supabase Storage
    ↓
OCR & Chunk (Docling) → RAG System (scoped by channel)
    ↓
Sentiment Analysis → Save to DB
    ↓
[IF TO field] → Agent Response → outgoing-messages queue
    ↓
Send via Resend → Update DB
```

### Key Features

1. **Intelligent Routing**
   - Subdomain → workspace mapping (e.g., `support@test.example.com`)
   - User part → channel mapping (e.g., `support` channel)
   - Only process emails to configured `INBOUND_MAIL_HOST`
   - Verify sender is workspace member

2. **Email Processing**
   - **CC/BCC emails**: Monitor only, process attachments, no response
   - **TO emails**: Full processing + agent response
   - Download and store attachments in Supabase Storage
   - OCR supported document types (via Docling)
   - Chunk and embed documents into RAG system (scoped by channel)

3. **Sentiment Analysis**
   - Analyze email content
   - Analyze processed documents
   - Track sentiment over time
   - Identify hidden issues in project communications

4. **Agent Response**
   - Use channel's primary assistant
   - Context from RAG system (channel-scoped)
   - Thread-aware (reply_id support)
   - Multiple response formats (rich parts, markdown, HTML)

5. **Multi-Queue Architecture**
   - `incoming-messages`: Initial routing and attachment fetching
   - `document-processing`: OCR and RAG ingestion
   - `sentiment-analysis`: Analyze content
   - `agent-response`: Generate responses
   - `outgoing-messages`: Send emails via Resend

### Database Schema

#### Users (Supabase Auth)
- Managed by Supabase Auth
- Standard user authentication

#### Profiles
```sql
- id (uuid, PK, same as users.id)
- type (enum: 'user', 'assistant') -- STI
- name (text)
- email (text, nullable for assistants)
- avatar_url (text, nullable)
-- Assistant-specific fields
- model (text, nullable)
- queue_name (text, nullable)
- system_prompt (text, nullable) -- Base personality
- created_at (timestamptz)
- updated_at (timestamptz)
```

#### Workspaces
```sql
- id (uuid, PK)
- name (text)
- short_name (text, unique) -- For subdomain (e.g., 'test' → test.example.com)
- settings (jsonb)
- created_at (timestamptz)
- updated_at (timestamptz)
```

#### Members (Workspace Memberships)
```sql
- id (uuid, PK)
- workspace_id (uuid, FK → workspaces.id)
- profile_id (uuid, FK → profiles.id)
- role (enum: 'owner', 'admin', 'member')
- custom_prompt (text, nullable) -- Org-level assistant customization
- created_at (timestamptz)
- updated_at (timestamptz)
UNIQUE(workspace_id, profile_id)
```

#### Channels
```sql
- id (uuid, PK)
- workspace_id (uuid, FK → workspaces.id) -- Denormalized for isolation
- name (text)
- short_name (text) -- For email user part (e.g., 'support')
- description (text, nullable)
- primary_assistant_id (uuid, FK → profiles.id, nullable)
- settings (jsonb)
- created_at (timestamptz)
- updated_at (timestamptz)
UNIQUE(workspace_id, short_name)
```

#### Participants (Channel Memberships)
```sql
- id (uuid, PK)
- workspace_id (uuid, FK → workspaces.id) -- Denormalized for isolation
- channel_id (uuid, FK → channels.id)
- profile_id (uuid, FK → profiles.id)
- custom_prompt (text, nullable) -- Channel-level assistant customization
- created_at (timestamptz)
- updated_at (timestamptz)
UNIQUE(channel_id, profile_id)
```

#### Messages
```sql
- id (uuid, PK)
- workspace_id (uuid, FK → workspaces.id) -- Denormalized for isolation
- channel_id (uuid, FK → channels.id)
- type (enum: 'chat', 'email') -- STI
- from_member_id (uuid, FK → members.id, nullable)
- to_member_id (uuid, FK → members.id, nullable)
- reply_to_id (uuid, FK → messages.id, nullable) -- Threading
- status (enum: 'pending', 'processing', 'processed', 'sent', 'failed')
- processing_stage (text, nullable) -- Current processing step
-- Email-specific fields
- email_message_id (text, nullable)
- email_subject (text, nullable)
- email_to (text[], nullable)
- email_cc (text[], nullable)
- email_bcc (text[], nullable)
- email_html (text, nullable)
-- Content (multiple representations)
- content_text (text) -- Plain text
- content_markdown (text, nullable) -- Markdown representation
- content_html (text, nullable) -- HTML representation
- content_parts (jsonb, nullable) -- Rich message parts (AI responses, chat)
-- Sentiment analysis
- sentiment (enum: 'positive', 'neutral', 'negative', nullable)
- sentiment_score (float, nullable)
- sentiment_details (jsonb, nullable)
-- Metadata
- metadata (jsonb)
- created_at (timestamptz)
- updated_at (timestamptz)
```

#### Attachments
```sql
- id (uuid, PK)
- workspace_id (uuid, FK → workspaces.id) -- Denormalized for isolation
- message_id (uuid, FK → messages.id)
- filename (text)
- content_type (text)
- size_bytes (bigint)
- storage_path (text) -- Supabase Storage path
- status (enum: 'pending', 'downloaded', 'processed', 'failed')
- processing_error (text, nullable)
-- OCR/Processing results
- ocr_text (text, nullable)
- ocr_metadata (jsonb, nullable)
-- Metadata
- metadata (jsonb)
- created_at (timestamptz)
- updated_at (timestamptz)
```

#### RAG System (TBD)
```sql
-- Document chunks with embeddings
-- Scoped by channel_id
-- References source message_id and/or attachment_id
-- Standard vector similarity search
-- Integration with LangChain/LangGraph
```

### Use Cases

1. **Project Monitoring** (Primary)
   - CC'd on all project emails
   - Analyze sentiment across communications
   - Process meeting notes, reports, documents
   - Identify hidden issues or concerns
   - Generate weekly/monthly sentiment reports

2. **On-Demand Q&A**
   - Direct emails to agent (TO field)
   - Context from channel's RAG system
   - Thread-aware responses
   - Quick answers to project questions

3. **Document Intelligence**
   - OCR and index all project documents
   - Searchable knowledge base per channel
   - Automatic summarization
   - Cross-reference related documents

## MVP (6-Hour Demo Sprint)

### Scope

**✅ INCLUDE:**
1. Basic DB scaffold (all tables, simplified schema)
2. Supabase Edge Function (webhook handler)
3. Email routing logic (subdomain → workspace, user → channel)
4. Save message to DB with correct workspace/channel
5. Download attachments from Resend
6. Save attachments to Supabase Storage
7. Mark attachments as "needs_processing" (no actual OCR)
8. Agent response for TO emails (simple context from email text only)
9. Send response directly via Resend (no outgoing queue)

**⚠️ SHORTCUTS (Document as TODO):**
- No OCR/document processing (mark attachments as pending)
- No RAG system (use email text only for context)
- No sentiment analysis
- No outgoing queue (send directly)
- Simplified routing (basic parsing, minimal validation)
- No thread support (reply_to_id exists but not used)
- No rich message parts (simple text responses)

### Demo Stories

**Story 1: CC Email (Monitoring)**
```
1. Email arrives with CC to support@test.example.com
2. Edge function receives webhook
3. Parses subdomain 'test' → finds workspace
4. Parses user 'support' → finds channel
5. Verifies sender is workspace member
6. Saves message to DB (workspace_id, channel_id, status='processing')
7. Downloads attachments from Resend
8. Saves attachments to Supabase Storage
9. Updates attachment status to 'needs_processing'
10. Updates message status to 'processed'
```

**Story 2: TO Email (Response)**
```
1. Email arrives with TO support@test.example.com
2. Same routing as Story 1 (steps 2-6)
3. Downloads and saves attachments (steps 7-9)
4. Triggers agent response:
   - Looks up channel's primary_assistant
   - Creates simple context from email text
   - Generates response using agent
   - Saves response message to DB
   - Sends email via Resend API
5. Updates original message status to 'processed'
6. Updates response message status to 'sent'
```

### Implementation Plan

#### Phase 1: Database Setup (1 hour)
- [ ] Create Supabase migration file
- [ ] Define all tables (simplified schema)
- [ ] Add indexes (workspace_id, channel_id, message status)
- [ ] Add basic RLS policies (workspace isolation)
- [ ] Create seed data (test workspace, channel, members)

#### Phase 2: Supabase Edge Function (1.5 hours)
- [ ] Create edge function scaffold
- [ ] Parse Resend webhook payload
- [ ] Implement routing logic:
  - [ ] Extract subdomain from TO/CC/BCC
  - [ ] Look up workspace by short_name
  - [ ] Extract user part from email
  - [ ] Look up channel by short_name
  - [ ] Verify sender is workspace member
- [ ] Save message to DB
- [ ] Enqueue to `incoming-messages` (or call directly for MVP)
- [ ] Error handling and logging

#### Phase 3: Attachment Processing (1 hour)
- [ ] Create AIMQ task for incoming messages
- [ ] Fetch attachments from Resend API
- [ ] Save to Supabase Storage (organized by workspace/channel/message)
- [ ] Create attachment records in DB
- [ ] Update attachment status to 'needs_processing'
- [ ] Update message status

#### Phase 4: Agent Response (2 hours)
- [ ] Create AIMQ task for agent responses
- [ ] Look up channel's primary assistant
- [ ] Build simple context (email subject + body)
- [ ] Create agent prompt (system + context)
- [ ] Generate response using LangChain/LangGraph
- [ ] Save response message to DB
- [ ] Send via Resend API
- [ ] Update statuses

#### Phase 5: Testing & Demo Prep (0.5 hours)
- [ ] Test CC email flow
- [ ] Test TO email flow
- [ ] Test with attachments
- [ ] Verify DB records
- [ ] Verify Supabase Storage
- [ ] Verify outgoing emails
- [ ] Document shortcuts and TODOs

### Configuration

```bash
# .env
INBOUND_MAIL_HOST=example.com  # Only process emails to *.example.com
RESEND_API_KEY=re_xxx
RESEND_WEBHOOK_SECRET=whsec_xxx
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_ANON_KEY=xxx
SUPABASE_SERVICE_ROLE_KEY=xxx
```

## Architecture

### Components

1. **Resend Integration**
   - Inbound webhook (POST to edge function)
   - Attachment download API
   - Outbound email API

2. **Supabase Edge Function**
   - Webhook handler
   - Email routing logic
   - Initial message save
   - Queue job creation

3. **AIMQ Workers**
   - `incoming-messages`: Attachment processing
   - `agent-response`: Generate and send responses
   - (Future: `document-processing`, `sentiment-analysis`, `outgoing-messages`)

4. **Database**
   - Supabase PostgreSQL
   - RLS for workspace isolation
   - Denormalized workspace_id for security

5. **Storage**
   - Supabase Storage for attachments
   - Organized by workspace/channel/message
   - RLS policies for access control

### Data Flow

```
Resend Webhook
    ↓
Edge Function (routing + save)
    ↓
incoming-messages queue
    ↓
Attachment Worker (download + store)
    ↓
[IF TO field] → agent-response queue
    ↓
Agent Worker (generate + send)
    ↓
Resend API (outbound)
```

### Security

1. **Workspace Isolation**
   - All tables include workspace_id
   - RLS policies enforce workspace boundaries
   - No cross-workspace data access

2. **Email Verification**
   - Only process configured INBOUND_MAIL_HOST
   - Verify sender is workspace member
   - Validate subdomain and user parts

3. **Storage Access**
   - RLS policies on Supabase Storage
   - Organized by workspace for isolation
   - Signed URLs for temporary access

## Resources

### Resend Documentation
- [Receiving Emails - Introduction](https://resend.com/docs/dashboard/receiving/introduction)
- [Inbound Webhook Payload](https://resend.com/docs/dashboard/receiving/webhooks)
- [Downloading Attachments](https://resend.com/docs/dashboard/receiving/attachments)
- [Sending Emails API](https://resend.com/docs/api-reference/emails/send-email)

### Supabase Documentation
- [Edge Functions](https://supabase.com/docs/guides/functions)
- [Storage](https://supabase.com/docs/guides/storage)
- [Row Level Security](https://supabase.com/docs/guides/auth/row-level-security)
- [Database Migrations](https://supabase.com/docs/guides/cli/local-development#database-migrations)

### LangChain/LangGraph
- [Document Loaders](https://python.langchain.com/docs/modules/data_connection/document_loaders/)
- [Text Splitters](https://python.langchain.com/docs/modules/data_connection/document_transformers/)
- [Vector Stores](https://python.langchain.com/docs/modules/data_connection/vectorstores/)
- [Agents](https://python.langchain.com/docs/modules/agents/)

### AIMQ Internal
- [@src/aimq/worker.py](../../src/aimq/worker.py) - Worker decorator
- [@src/aimq/tools/](../../src/aimq/tools/) - Existing tools (OCR, PDF, Supabase)
- [@.claude/patterns/queue-error-handling.md](../patterns/queue-error-handling.md)
- [@.claude/patterns/worker-error-handling.md](../patterns/worker-error-handling.md)

## Post-Demo Roadmap

### Phase 1: Complete Core Features (Week 1)
- [ ] Implement full OCR pipeline (Docling integration)
- [ ] Build RAG system (chunking, embedding, vector store)
- [ ] Add sentiment analysis
- [ ] Implement outgoing-messages queue
- [ ] Add thread support (reply_to_id)

### Phase 2: Enhanced Intelligence (Week 2)
- [ ] Rich message parts (structured AI responses)
- [ ] Context-aware responses (RAG integration)
- [ ] Sentiment tracking over time
- [ ] Weekly/monthly sentiment reports

### Phase 3: Production Readiness (Week 3)
- [ ] Comprehensive error handling
- [ ] Retry logic for failed jobs
- [ ] Monitoring and alerting
- [ ] Rate limiting
- [ ] Webhook signature verification
- [ ] Full test coverage

### Phase 4: Advanced Features (Week 4+)
- [ ] Multi-workspace support in UI
- [ ] Channel management UI
- [ ] Assistant customization UI
- [ ] Sentiment dashboard
- [ ] Document search interface
- [ ] Email threading UI

## Notes

### Design Decisions

1. **STI (Single Table Inheritance)**
   - Profiles: users vs. assistants
   - Messages: chat vs. email
   - Simplifies queries, adds flexibility
   - Type field for discrimination

2. **Denormalized workspace_id**
   - Every table includes workspace_id
   - Enables efficient RLS policies
   - Guarantees workspace isolation
   - Small storage cost for big security win

3. **Multiple Content Representations**
   - Messages have text, markdown, HTML, and parts
   - Flexibility for different contexts
   - Email needs HTML, chat needs parts
   - Agents can use markdown for generation

4. **Queue-Based Architecture**
   - Decouples processing stages
   - Enables parallel processing
   - Easy to add new stages
   - Resilient to failures

5. **Channel-Scoped RAG**
   - Each channel has isolated knowledge base
   - Prevents cross-channel information leakage
   - Enables channel-specific context
   - Scales with workspace growth

### Open Questions

1. **RAG System Details**
   - Which vector store? (pgvector, Pinecone, Weaviate?)
   - Chunking strategy? (size, overlap)
   - Embedding model? (OpenAI, local?)
   - Similarity search parameters?

2. **Sentiment Analysis**
   - Which model? (LLM-based, specialized?)
   - Granularity? (message-level, document-level, topic-level?)
   - Storage format? (score, categories, details?)
   - Aggregation strategy? (time-based, topic-based?)

3. **Agent Customization**
   - How to combine system_prompt + custom_prompt + channel_prompt?
   - Priority/override rules?
   - Template system?
   - Validation?

4. **Rate Limiting**
   - Per workspace? Per channel? Per user?
   - How to handle bursts?
   - Queue backpressure?
   - User feedback?

5. **Error Recovery**
   - Retry strategy for failed jobs?
   - Dead letter queue?
   - Manual intervention UI?
   - Notification system?

### Shortcuts for Demo (REMOVE BEFORE PRODUCTION)

```python
# TODO: Remove these shortcuts after demo
# 1. No OCR - just mark attachments as needs_processing
# 2. No RAG - use email text only for context
# 3. No sentiment analysis
# 4. No outgoing queue - send directly via Resend
# 5. Simplified routing - minimal validation
# 6. No thread support - reply_to_id not used
# 7. No rich message parts - simple text only
```

## Related

- [@PLAN.md](../../PLAN.md) - Current sprint plan
- [@VISION.md](../../VISION.md) - Project vision
- [@.claude/patterns/demo-driven-development.md](../patterns/demo-driven-development.md)
- [@.claude/patterns/progressive-enhancement.md](../patterns/progressive-enhancement.md)
- [@.claude/architecture/database-schema-patterns.md](../architecture/database-schema-patterns.md)

---

**Last Updated**: 2025-11-25
**Next Review**: After demo (2025-11-25 evening)

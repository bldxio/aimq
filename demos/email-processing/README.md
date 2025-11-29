# Email Processing System - Demo Guide

## 🎯 What We Built

An AI-powered email processing system that:
- ✅ Receives emails via Resend webhooks
- ✅ Routes emails to workspaces and channels (subdomain → workspace, user → channel)
- ✅ Monitors CC/BCC emails (saves without responding)
- ✅ Responds to direct emails (TO field) using AI agents
- ✅ Handles attachments (metadata saved, ready for processing)
- ✅ Maintains conversation threads (reply_to_id)
- ✅ Uses LangChain + OpenAI for intelligent responses

## 🏗️ Architecture

```
Resend Webhook
    ↓
Supabase Edge Function (TypeScript/Deno)
    ├─ Parse email (to/cc/bcc)
    ├─ Route: subdomain → workspace, user → channel
    ├─ Verify sender is member
    ├─ Save message + attachments
    └─ [IF TO] Enqueue to incoming-messages
            ↓
AIMQ Worker (Python)
    ├─ Fetch channel's primary assistant
    ├─ Generate response (LangChain + OpenAI)
    ├─ Send email via Resend
    └─ Save response message
```

## 📊 Database Schema

**7 Core Tables:**
1. **workspaces** - Multi-tenant isolation (short_name for subdomain)
2. **profiles** - Users + AI assistants (STI via type column)
3. **channels** - Communication channels (short_name for email user part)
4. **members** - Workspace memberships
5. **participants** - Channel memberships
6. **messages** - Chat + Email messages (STI via type column)
7. **attachments** - File metadata with OCR/processing pipeline support

## 🚀 Quick Start

### 1. Setup Environment

```bash
# Start Supabase
supabase start

# Set environment variables
export RESEND_API_KEY=your_key
export INBOUND_MAIL_HOST=acme.bldx.run
export OPENAI_API_KEY=your_key
```

### 2. Verify Database

```bash
uv run python -c "
from aimq.clients.supabase import supabase
print('Workspaces:', supabase.client.table('workspaces').select('*').execute().data)
print('Channels:', supabase.client.table('channels').select('*').execute().data)
"
```

### 3. Test the System

**Option A: Full Flow Test (Dry Run)**
```bash
# From project root
uv run python demos/email-processing/test_full_flow.py
```

**Option B: Manual Testing**
```bash
# Terminal 1: Start edge function (from project root)
INBOUND_MAIL_HOST=acme.bldx.run supabase functions serve resend-inbound --no-verify-jwt

# Terminal 2: Start worker (from project root)
uv run python demos/email-processing/worker.py

# Terminal 3: Send test webhook (from demos/email-processing)
cd demos/email-processing
./test_webhook.sh
```

## 📧 Demo Scenarios

### Scenario 1: CC Email (Monitoring)

**Email:** `support@acme.acme.bldx.run` in CC field

**Expected:**
- ✅ Message saved to database
- ✅ Status: "processed"
- ✅ No agent response
- ✅ Attachments metadata saved

**Verification:**
```sql
SELECT id, type, status, email_subject, email_cc
FROM messages
WHERE email_cc @> ARRAY['support@acme.acme.bldx.run'];
```

### Scenario 2: Direct Email (Response)

**Email:** `support@acme.acme.bldx.run` in TO field

**Expected:**
- ✅ Message saved with status "pending"
- ✅ Job enqueued to `incoming-messages`
- ✅ Worker processes job
- ✅ Agent generates response
- ✅ Email sent via Resend
- ✅ Response message saved with reply_to_id
- ✅ Original message status → "processed"

**Verification:**
```sql
-- Original message
SELECT id, status, processing_stage, email_subject
FROM messages
WHERE email_to @> ARRAY['support@acme.acme.bldx.run'];

-- Response message
SELECT id, reply_to_id, email_subject, content_text
FROM messages
WHERE reply_to_id IS NOT NULL;
```

### Scenario 3: Email with Attachments

**Email:** Direct email with PDF/image attachments

**Expected:**
- ✅ All of Scenario 2
- ✅ Attachment records created
- ✅ Status: "pending" (ready for download/OCR)
- ✅ Download URLs stored in metadata

**Verification:**
```sql
SELECT m.email_subject, a.filename, a.status, a.size_bytes
FROM messages m
JOIN attachments a ON a.message_id = m.id
WHERE m.email_subject = 'Your Subject';
```

## 🎬 Demo Script

### Setup (5 min)
1. Show database schema in Supabase Studio
2. Show test data (Acme workspace, support channel, Mindi assistant)
3. Explain routing: `support@acme.acme.bldx.run`
   - `acme` → workspace
   - `support` → channel

### Demo 1: CC Email (2 min)
1. Send test webhook with CC
2. Show message in database
3. Show status = "processed"
4. Explain: "Monitoring only, no response"

### Demo 2: Direct Email (5 min)
1. Send test webhook with TO
2. Show message with status = "pending"
3. Show job in queue
4. Show worker processing (logs)
5. Show agent generating response
6. Show response message in database
7. Show email sent (Resend dashboard or logs)

### Demo 3: Attachments (3 min)
1. Send email with attachments
2. Show attachment records in database
3. Show metadata with download URLs
4. Explain: "Ready for OCR/processing pipeline"

## 🔧 Troubleshooting

### Edge Function Issues
```bash
# Check Supabase status
supabase status

# View function logs
supabase functions logs resend-inbound --follow
```

### Worker Issues
```bash
# Check queue
uv run python -c "
from aimq.clients.supabase import supabase
result = supabase.client.rpc('pgmq_public.read', {
  'queue_name': 'incoming-messages',
  'vt': 30,
  'qty': 10
}).execute()
print(result.data)
"
```

### Agent Issues
```bash
# Test agent directly
uv run python test_email_agent.py

# Check OpenAI API key
echo $OPENAI_API_KEY
```

## 📝 What's Next (Post-MVP)

### Phase 1: Complete Core Features
- [ ] Download and process attachments
- [ ] OCR with Docling
- [ ] RAG system (chunking, embedding, vector store)
- [ ] Sentiment analysis
- [ ] Outgoing messages queue

### Phase 2: Enhanced Intelligence
- [ ] Context-aware responses (RAG integration)
- [ ] Thread history in context
- [ ] Multi-turn conversations
- [ ] Tool use (weather API, etc.)

### Phase 3: Production Readiness
- [ ] Comprehensive error handling
- [ ] Retry logic
- [ ] Monitoring and alerting
- [ ] Rate limiting
- [ ] Webhook signature verification
- [ ] Full test coverage

## 🎉 Success Metrics

- ✅ **Database**: 7 tables, proper relationships, RLS policies
- ✅ **Edge Function**: Routing, validation, message saving
- ✅ **Worker**: Queue processing, agent integration
- ✅ **Agent**: LangChain + OpenAI, contextual responses
- ✅ **Integration**: Resend (inbound + outbound)
- ✅ **Testing**: Full flow test, verification queries
- ✅ **Documentation**: Architecture, setup, troubleshooting

## 📚 Key Files

**Demo Files (this directory):**
- `README.md` - This demo guide
- `worker.py` - Demo worker entry point
- `test_full_flow.py` - End-to-end test
- `test_agent.py` - Agent-only test
- `test_webhook.sh` - Webhook test script
- `TEST_PLAN.md` - Comprehensive test scenarios

**Source Code:**
- `../../supabase/migrations/20251125084652_email_processing_schema.sql` - Database schema
- `../../supabase/functions/resend-inbound/index.ts` - Webhook handler
- `../../src/aimq/agents/email/agent.py` - Email agent (LangChain)
- `../../src/aimq/agents/email/worker.py` - Worker task
- `../../src/aimq/clients/resend.py` - Resend client wrapper

## 🙏 Acknowledgments

Built with:
- **Supabase** - Database, Edge Functions, Storage
- **Resend** - Email delivery
- **LangChain** - Agent framework
- **OpenAI** - LLM (GPT-4)
- **AIMQ** - Queue-based worker system

---

**Demo Time**: ~15 minutes
**Setup Time**: ~5 minutes
**Total**: ~20 minutes

🚀 **Let's show them what we built!**

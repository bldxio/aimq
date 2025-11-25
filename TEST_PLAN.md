# Email Processing System - Test Plan

## Prerequisites

1. **Supabase running locally**
   ```bash
   supabase start
   ```

2. **Environment variables set**
   ```bash
   # Add to .env
   RESEND_API_KEY=your_key_here
   INBOUND_MAIL_HOST=acme.bldx.run
   OPENAI_API_KEY=your_key_here
   ```

3. **Database seeded**
   - Workspace: Acme (short_name: acme)
   - Channels: support, engineering
   - Assistant: Mindi (gpt-4)
   - Users: John, Jane

## Test Scenarios

### Scenario 1: CC Email (Monitoring Only)

**Expected Flow:**
1. Email sent to CC: `support@acme.acme.bldx.run`
2. Edge function receives webhook
3. Routes to workspace "acme", channel "support"
4. Verifies sender is member
5. Saves message with status "processed"
6. No agent response (CC only)

**Test Command:**
```bash
./test_webhook.sh
```

**Verification:**
```sql
SELECT id, type, status, email_subject, email_cc
FROM messages
WHERE email_subject = 'Project Update';
```

### Scenario 2: TO Email (Direct Response)

**Expected Flow:**
1. Email sent TO: `support@acme.acme.bldx.run`
2. Edge function receives webhook
3. Routes to workspace "acme", channel "support"
4. Verifies sender is member
5. Saves message with status "pending"
6. Enqueues job to `incoming-messages` queue
7. Worker picks up job
8. Fetches assistant (Mindi)
9. Generates response using LangChain + OpenAI
10. Sends email via Resend
11. Saves response message
12. Updates original message status to "processed"

**Test Command:**
```bash
# 1. Start edge function
INBOUND_MAIL_HOST=acme.bldx.run supabase functions serve resend-inbound --no-verify-jwt &

# 2. Start worker
uv run python examples/email_worker.py &

# 3. Send test webhook
curl -X POST 'http://127.0.0.1:64321/functions/v1/resend-inbound' \
  --header 'Content-Type: application/json' \
  --data '{
    "from": "jane@example.com",
    "to": ["support@acme.acme.bldx.run"],
    "subject": "Need Help",
    "text": "Can you help me with this issue?",
    "message_id": "test-001"
  }'
```

**Verification:**
```sql
-- Check original message
SELECT id, type, status, processing_stage, email_subject
FROM messages
WHERE email_subject = 'Need Help';

-- Check response message
SELECT id, type, status, email_subject, content_text
FROM messages
WHERE email_subject = 'Re: Need Help';

-- Check queue
SELECT * FROM pgmq_public.q_incoming_messages;
```

### Scenario 3: Email with Attachments

**Expected Flow:**
1. Email with attachments sent TO channel
2. Edge function saves attachment metadata
3. Attachments marked as "pending"
4. Agent generates response (ignoring attachments for MVP)
5. Response sent

**Test Command:**
```bash
curl -X POST 'http://127.0.0.1:64321/functions/v1/resend-inbound' \
  --header 'Content-Type: application/json' \
  --data '{
    "from": "john@example.com",
    "to": ["engineering@acme.acme.bldx.run"],
    "subject": "Bug Report",
    "text": "See attached screenshot of the bug",
    "message_id": "test-002",
    "attachments": [
      {
        "filename": "bug-screenshot.png",
        "content_type": "image/png",
        "size": 12345,
        "url": "https://api.resend.com/attachments/test-123"
      }
    ]
  }'
```

**Verification:**
```sql
-- Check attachments saved
SELECT id, filename, status, size_bytes
FROM attachments
WHERE message_id IN (
  SELECT id FROM messages WHERE email_subject = 'Bug Report'
);
```

## Manual Testing Steps

### 1. Database Check
```bash
# Connect to local Supabase
uv run python -c "
from aimq.clients.supabase import supabase
print('Workspaces:', supabase.client.table('workspaces').select('*').execute().data)
print('Channels:', supabase.client.table('channels').select('*').execute().data)
print('Profiles:', supabase.client.table('profiles').select('*').execute().data)
"
```

### 2. Edge Function Test
```bash
# Start edge function
cd supabase/functions/resend-inbound
INBOUND_MAIL_HOST=acme.bldx.run supabase functions serve --no-verify-jwt

# In another terminal, send test request
./test_webhook.sh
```

### 3. Worker Test
```bash
# Start worker
uv run python examples/email_worker.py

# Check logs for job processing
```

### 4. Agent Test (Isolated)
```bash
# Test agent without full workflow
uv run python test_email_agent.py
```

## Expected Results

### Success Criteria

- ✅ CC emails saved with status "processed"
- ✅ TO emails saved with status "pending" → "processed"
- ✅ Jobs enqueued to `incoming-messages` queue
- ✅ Worker processes jobs successfully
- ✅ Agent generates contextual responses
- ✅ Response emails sent via Resend
- ✅ Response messages saved with reply_to_id
- ✅ Attachments metadata saved
- ✅ No errors in logs

### Known Limitations (MVP)

- ⚠️ Attachments not downloaded (marked as "pending")
- ⚠️ No OCR processing
- ⚠️ No RAG/context retrieval
- ⚠️ No sentiment analysis
- ⚠️ Simple email text context only
- ⚠️ No thread history in context

## Troubleshooting

### Edge Function Not Starting
```bash
# Check Supabase status
supabase status

# Check function logs
supabase functions logs resend-inbound
```

### Worker Not Processing Jobs
```bash
# Check queue
uv run python -c "
from aimq.clients.supabase import supabase
result = supabase.client.rpc('pgmq_public.read', {
  'queue_name': 'incoming-messages',
  'vt': 30,
  'qty': 10
}).execute()
print('Queue messages:', result.data)
"
```

### Agent Errors
```bash
# Check OpenAI API key
echo $OPENAI_API_KEY

# Test agent directly
uv run python test_email_agent.py
```

### Database Issues
```bash
# Reset database
supabase db reset

# Check migrations
supabase db diff
```

## Demo Checklist

- [ ] Supabase running
- [ ] Environment variables set
- [ ] Database seeded
- [ ] Edge function deployed/running
- [ ] Worker running
- [ ] Test emails prepared
- [ ] Verification queries ready
- [ ] Logs visible
- [ ] Demo script practiced

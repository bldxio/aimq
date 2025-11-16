# 💬 Message Agent Worker

Welcome to the **Message Agent Demo**! This worker showcases composable message routing and multi-agent responses.

## 🎯 What This Demo Does

1. **Routes Messages** - Detects @mentions and routes to appropriate agents
2. **Default Assistant** - Handles general questions without tools
3. **ReAct Assistant** - Handles complex queries with file reading, OCR, and database tools

## 🚀 Quick Start

### Send a General Message
```bash
aimq send incoming-messages '{
  "message_id": "msg_001",
  "body": "Hello! Can you help me with something?",
  "sender": "user@example.com",
  "workspace_id": "workspace_123",
  "channel_id": "channel_456",
  "thread_id": "thread_789"
}'
```
→ Routes to `default-assistant` queue

### Send a Message with @mention
```bash
aimq send incoming-messages '{
  "message_id": "msg_002",
  "body": "@react-assistant What files are in the documents folder?",
  "sender": "user@example.com",
  "workspace_id": "workspace_123",
  "channel_id": "channel_456",
  "thread_id": "thread_789"
}'
```
→ Routes to `react-assistant` queue

## 🏗️ Architecture

```
incoming-messages
    ↓
MessageRoutingWorkflow
    ├─ DetectMentions (tool)
    └─ ResolveQueue (tool)
    ↓
Agent Queues
    ├─ default-assistant (general responses)
    └─ react-assistant (tool-powered responses)
```

## 🔧 Composable Tools

- **DetectMentions** - Extracts @mentions from text
- **ResolveQueue** - Maps mentions to queue names
- **LookupProfile** - Queries Supabase profiles (optional)

## 📝 Response Format

Responses include the agent name in the sender:
- `default-assistant@workspace_123`
- `react-assistant@workspace_123`

## 🎨 Supported Mention Patterns

- `@name-assistant` ✅
- `@name_assistant` ✅
- `@name-bot` ✅
- `@name_bot` ✅

---

**Ready to demo!** 🚀 Send messages and watch the routing magic happen!

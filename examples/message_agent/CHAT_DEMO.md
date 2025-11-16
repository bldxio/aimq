# 🎨 Interactive Chat Demo

Beautiful CLI chat interface with AI agents that have access to weather and sports data!

## 🚀 Quick Start

### 1. Start the Worker

```bash
# Terminal 1: Start the message worker
uv run python examples/message_agent/message_worker.py
```

Wait for the worker to show "Ready to process jobs" message.

### 2. Start the Chat

```bash
# Terminal 2: Start the interactive chat
uv run python examples/message_agent/chat_cli.py
```

## 💬 Example Queries

### Weather Queries
```
You: What's the weather in San Francisco?
You: Tell me the weather in Tokyo
You: @react-assistant How's the weather in London?
```

### Sports Data Queries
```
You: @react-assistant Show me NBA teams
You: @react-assistant Find basketball competitors
You: @react-assistant Query competitors where entity_type is team and sport_code is basketball
You: @react-assistant List players with position guard
```

### General Queries
```
You: Hello, how are you?
You: What can you help me with?
You: Tell me a joke
```

## 🎯 Agent Selection

- **Default behavior**: Messages go to `default-assistant`
- **Mention @react-assistant**: Routes to agent with tools (weather, database queries)
- **Mention @default-assistant**: Explicitly route to default agent

## 🛠️ Available Tools (react-assistant)

| Tool | Description | Example |
|------|-------------|---------|
| `weather` | Get current weather for any location | "weather in Boston" |
| `query_table` | Query competitors database | "show NBA teams" |
| `read_file` | Read files from Supabase storage | "read document.pdf" |
| `read_record` | Read database records | "get record by id" |
| `image_ocr` | Extract text from images | "extract text from image" |

## 📊 Competitors Table Schema

The `competitors` table contains sports data:

**Teams** (`entity_type = 'team'`):
- `name`: Team name
- `abbreviation`: Team abbreviation (e.g., "LAL")
- `market`: City/market (e.g., "Los Angeles")
- `sport_code`: Sport identifier (e.g., "basketball")
- `conference`: Conference name
- `division`: Division name

**Players** (`entity_type = 'player'`):
- `first_name`, `last_name`: Player name
- `position`: Playing position
- `jersey`: Jersey number
- `team_id`: Associated team UUID
- `sport_code`: Sport identifier

## 🎨 CLI Features

- **Markdown rendering**: Responses formatted beautifully
- **Syntax highlighting**: Code blocks highlighted
- **Spinners**: Visual feedback while waiting
- **Panels**: Pretty bordered output
- **Colors**: Cyan for user, green for agents

## 🔧 Advanced Usage

### Specify Default Agent
```bash
uv run python examples/message_agent/chat_cli.py --agent react-assistant
```

### Custom Workspace/Channel
```bash
uv run python examples/message_agent/chat_cli.py \
  --workspace my_workspace \
  --channel my_channel \
  --thread my_thread
```

### Test Connection
```bash
uv run python examples/message_agent/chat_cli.py test
```

## 🐛 Troubleshooting

### "Failed to send message"
- Make sure the worker is running
- Check Supabase connection (SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)
- Verify pgmq functions are installed
- Ensure `incoming-messages` queue exists

### "Response timeout"
- Agent may still be processing (check worker logs)
- Increase timeout with longer wait
- Check worker for errors
- Verify `outgoing-messages` queue exists

### "Import errors"
- Run from project root: `cd /path/to/aimq`
- Ensure dependencies installed: `uv sync`

### Queue Setup
If queues don't exist, create them:
```bash
# Create incoming queue
aimq create incoming-messages

# Create agent queues
aimq create default-assistant
aimq create react-assistant

# Create outbound queue
aimq create outgoing-messages
```

## 💡 Demo Tips

1. **Start with simple queries** to show basic chat
2. **Show weather tool** - impressive and easy to understand
3. **Query sports data** - shows database integration
4. **Mention different agents** - demonstrates routing
5. **Show markdown rendering** - highlight the beautiful UI

## 🎭 Sample Demo Script

```
# 1. Welcome and basic chat
You: Hello! What can you help me with?

# 2. Weather demo (natural language)
You: What's the weather in San Francisco?

# 3. Sports data query
You: @react-assistant Show me NBA teams

# 4. Filtered query
You: @react-assistant Find competitors where sport_code is basketball and entity_type is team

# 5. Different location weather
You: @react-assistant How's the weather in Tokyo?

# 6. Exit gracefully
You: /quit
```

## 🌟 What Makes This Cool

- **Natural language** - No rigid commands, just chat
- **Real tools** - Actual weather API and database queries
- **Beautiful UI** - Rich terminal interface with markdown
- **Smart routing** - Mentions automatically route to right agent
- **Composable** - Easy to add more tools and agents

---

**Ready to impress!** 🚀✨

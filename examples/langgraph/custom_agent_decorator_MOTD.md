---
messages:
  - "Ready to analyze your data! 📊"
  - "Data processing agent activated! 💡"
  - "Let's extract some insights! 🔍"
  - "Crunching numbers and analyzing trends! 📈"
  - "Time to turn data into intelligence! 🧠"
  - "Data specialist reporting for duty! 🎯"
  - "Processing data with AI precision! ⚡"
---

# Custom Agent - Data Processor

{message}

## Agent Workflow

1. **analyze** - Read file and analyze with LLM
2. **store** - Save results to analysis_results table

## Configuration

- **Queue:** data-processor
- **Timeout:** 600s (10 minutes)
- **File Reading:** Local filesystem
- **Tools:** WriteRecord (for storing results)
- **LLM:** mistral-large-latest
- **Memory:** Enabled

## Example Jobs

### 1. Analyze CSV file

```bash
aimq send data-processor '{
  "messages": [
    {"role": "user", "content": "data/sales_2024.csv"}
  ],
  "tools": [],
  "iteration": 0,
  "errors": []
}'
```

### 2. Analyze JSON data

```bash
aimq send data-processor '{
  "messages": [
    {"role": "user", "content": "exports/user_data.json"}
  ],
  "tools": [],
  "iteration": 0,
  "errors": []
}'
```

### 3. Resumable analysis

```bash
aimq send data-processor '{
  "messages": [
    {"role": "user", "content": "large_files/yearly_report.csv"}
  ],
  "thread_id": "analysis-session-789",
  "tools": [],
  "iteration": 0,
  "errors": []
}'
```

## Decorator Benefits

- Automatic AgentState setup
- Tools available in config['tools']
- LLM settings in config['llm'], config['temperature']
- Memory/checkpointing handled automatically
- Focus on business logic, not infrastructure

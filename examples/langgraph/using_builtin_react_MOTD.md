---
messages:
  - "ReAct agent ready to reason and act! 🤔💡"
  - "Thinking through problems step by step! 🧩"
  - "Gathering evidence and drawing conclusions! 🔬"
  - "Let's reason our way to the answer! 🎯"
  - "Acting on insights, one step at a time! 🚶"
  - "Multi-step reasoning engine activated! ⚡"
  - "Ready to answer your questions thoroughly! 📚"
---

# ReAct Agent Worker - Document Q&A

{message}

## What is ReAct?

ReAct (Reasoning + Acting) enables the agent to:
1. **Reason** about what action to take next
2. **Execute** tools to gather information
3. **Observe** results and continue reasoning
4. **Provide** final answers based on gathered evidence

## Configuration

- **Queue:** doc-qa
- **Timeout:** 900s (15 minutes)
- **Tools:** ReadFile, ReadRecord, ImageOCR
- **LLM:** mistral-large-latest
- **Memory:** Enabled (checkpointing)
- **Max Iterations:** 10

## Example Jobs

### 1. Simple file query

```bash
aimq send doc-qa '{
  "messages": [
    {"role": "user", "content": "Read the file at documents/report.pdf"}
  ],
  "tools": ["read_file"],
  "iteration": 0,
  "errors": []
}'
```

### 2. Multi-step reasoning

```bash
aimq send doc-qa '{
  "messages": [
    {"role": "user", "content": "Compare sales data from Q1 and Q2 reports"}
  ],
  "tools": ["read_file", "read_record"],
  "iteration": 0,
  "errors": []
}'
```

### 3. OCR processing

```bash
aimq send doc-qa '{
  "messages": [
    {"role": "user", "content": "Extract text from images/invoice.jpg"}
  ],
  "tools": ["image_ocr"],
  "iteration": 0,
  "errors": []
}'
```

### 4. Resumable workflow (with thread_id)

```bash
aimq send doc-qa '{
  "messages": [
    {"role": "user", "content": "Continue analyzing the document"}
  ],
  "thread_id": "user-123-session-456",
  "tools": ["read_file"],
  "iteration": 0,
  "errors": []
}'
```

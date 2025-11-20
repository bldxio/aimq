# LLM Provider API Comparison

> **Status**: Active
> **Last Updated**: 2025-11-20
> **Category**: quick-references

## Overview

Different LLM providers have different APIs, causing runtime errors when switching providers or using multiple providers in the same application.

## Common Symptom

```python
AttributeError: 'Chat' object has no attribute 'completions'
```

This happens when you use OpenAI-style API calls with a different provider.

## Provider API Comparison

### OpenAI

```python
from openai import OpenAI

client = OpenAI(api_key="sk-...")

# Chat completions
response = client.chat.completions.create(
    model="gpt-4",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Hello!"}
    ],
    temperature=0.7,
    max_tokens=150
)

# Access response
message = response.choices[0].message.content
```

**Key characteristics**:
- Uses `client.chat.completions.create()`
- Returns `ChatCompletion` object
- Access via `response.choices[0].message.content`

### Mistral

```python
from mistralai import Mistral

client = Mistral(api_key="...")

# Chat completions
response = client.chat.complete(
    model="mistral-large-latest",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Hello!"}
    ],
    temperature=0.7,
    max_tokens=150
)

# Access response
message = response.choices[0].message.content
```

**Key characteristics**:
- Uses `client.chat.complete()` (not `completions.create()`)
- Returns similar structure to OpenAI
- Access via `response.choices[0].message.content`

### Anthropic (Claude)

```python
from anthropic import Anthropic

client = Anthropic(api_key="sk-ant-...")

# Messages API
response = client.messages.create(
    model="claude-3-opus-20240229",
    max_tokens=1024,
    messages=[
        {"role": "user", "content": "Hello!"}
    ]
)

# Access response
message = response.content[0].text
```

**Key characteristics**:
- Uses `client.messages.create()` (not `chat`)
- No system message in messages array (use `system` parameter)
- Access via `response.content[0].text`

### Google (Gemini)

```python
import google.generativeai as genai

genai.configure(api_key="...")
model = genai.GenerativeModel('gemini-pro')

# Generate content
response = model.generate_content("Hello!")

# Access response
message = response.text
```

**Key characteristics**:
- Uses `model.generate_content()`
- Different initialization pattern
- Access via `response.text`

### Cohere

```python
import cohere

client = cohere.Client(api_key="...")

# Chat
response = client.chat(
    message="Hello!",
    model="command",
    temperature=0.7
)

# Access response
message = response.text
```

**Key characteristics**:
- Uses `client.chat()` directly
- Different parameter names (`message` not `messages`)
- Access via `response.text`

## API Differences Cheat Sheet

| Feature | OpenAI | Mistral | Anthropic | Google | Cohere |
|---------|--------|---------|-----------|--------|--------|
| **Method** | `chat.completions.create()` | `chat.complete()` | `messages.create()` | `generate_content()` | `chat()` |
| **Messages** | `messages` array | `messages` array | `messages` array | String or parts | `message` string |
| **System Message** | In messages | In messages | Separate `system` param | In prompt | In `preamble` |
| **Response Access** | `choices[0].message.content` | `choices[0].message.content` | `content[0].text` | `text` | `text` |
| **Streaming** | `stream=True` | `stream=True` | `stream=True` | `stream=True` | `stream=True` |
| **Temperature** | `temperature` | `temperature` | `temperature` | `temperature` | `temperature` |
| **Max Tokens** | `max_tokens` | `max_tokens` | `max_tokens` | `max_output_tokens` | `max_tokens` |

## Common Gotchas

### 1. System Messages

**OpenAI/Mistral**: System message in messages array
```python
messages = [
    {"role": "system", "content": "You are helpful."},
    {"role": "user", "content": "Hello!"}
]
```

**Anthropic**: System message as separate parameter
```python
client.messages.create(
    model="claude-3-opus",
    system="You are helpful.",  # Separate parameter
    messages=[
        {"role": "user", "content": "Hello!"}
    ]
)
```

### 2. Response Structure

**OpenAI/Mistral**: Nested structure
```python
content = response.choices[0].message.content
```

**Anthropic**: Different nesting
```python
content = response.content[0].text
```

**Google**: Direct access
```python
content = response.text
```

### 3. Streaming

**OpenAI/Mistral**: Similar streaming
```python
for chunk in client.chat.completions.create(stream=True, ...):
    print(chunk.choices[0].delta.content)
```

**Anthropic**: Different event structure
```python
with client.messages.stream(...) as stream:
    for text in stream.text_stream:
        print(text)
```

### 4. Error Handling

**Different providers** throw different exceptions:

```python
from openai import OpenAIError
from mistralai.exceptions import MistralException
from anthropic import AnthropicError

try:
    response = client.chat(...)
except (OpenAIError, MistralException, AnthropicError) as e:
    # Handle provider-specific errors
    pass
```

## Real-World Example

### The Problem

```python
# ReAct agent code (originally written for OpenAI)
def _reasoning_node(state: AgentState) -> AgentState:
    client = get_llm_client()  # Returns Mistral client

    # This works with OpenAI but fails with Mistral
    response = client.chat.completions.create(
        model=model_name,
        messages=messages
    )
```

### The Error

```
AttributeError: 'Chat' object has no attribute 'completions'
Traceback (most recent call last):
  File "src/aimq/agents/react.py", line 108, in _reasoning_node
    response = client.chat.completions.create(
               ^^^^^^^^^^^^^^^^^^^^^^^
AttributeError: 'Chat' object has no attribute 'completions'
```

### The Fix

```python
def _reasoning_node(state: AgentState) -> AgentState:
    client = get_llm_client()

    # Use Mistral's API
    response = client.chat.complete(  # Changed from completions.create
        model=model_name,
        messages=messages
    )
```

## Related

- [LLM Provider Best Practices](./llm-provider-best-practices.md) - Prevention strategies and patterns
- [Error Handling](../patterns/error-handling.md) - Handling provider-specific errors
- [Testing](./testing.md) - Testing with multiple providers

## References

- [OpenAI API Reference](https://platform.openai.com/docs/api-reference)
- [Mistral API Reference](https://docs.mistral.ai/api/)
- [Anthropic API Reference](https://docs.anthropic.com/claude/reference)
- [Google AI API Reference](https://ai.google.dev/docs)
- [Cohere API Reference](https://docs.cohere.com/reference)

---

**Key Takeaway**: LLM provider APIs are NOT interchangeable. Always check the documentation! 🔌

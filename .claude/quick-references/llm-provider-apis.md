# LLM Provider API Differences

> **⚠️ DEPRECATED - This file has been archived**
>
> **Last Updated**: 2025-11-20
> **Archived**: 2025-11-24
> **Superseded By**:
> - [@llm-provider-comparison.md](./llm-provider-comparison.md) - Provider comparison
> - [@llm-provider-best-practices.md](./llm-provider-best-practices.md) - Best practices

---

## 🔄 Redirect

This file has been split into focused documents for better maintainability.

**Please use the new files:**
- **[LLM Provider Comparison](./llm-provider-comparison.md)** - Compare providers and their APIs
- **[LLM Provider Best Practices](./llm-provider-best-practices.md)** - Best practices for integration

---

## Archive Notice

The content below is preserved for reference but is no longer maintained. Please refer to the superseding documents above for current information.

---

**Category**: Quick Reference
**Audience**: Developers integrating LLM providers
**Related**: [Common Pitfalls](./common-pitfalls.md)

---

## Problem

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

## Real-World Example: Message Agent Bug

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

## Prevention Strategies

### 1. Check Provider Documentation

**Before integrating**, read the provider's API docs:
- OpenAI: https://platform.openai.com/docs/api-reference
- Mistral: https://docs.mistral.ai/api/
- Anthropic: https://docs.anthropic.com/claude/reference
- Google: https://ai.google.dev/docs
- Cohere: https://docs.cohere.com/reference

### 2. Test with Actual Provider Early

**Don't assume** APIs are compatible.

```python
# Test immediately after integration
def test_llm_provider():
    client = get_llm_client()
    response = client.chat.complete(  # Or whatever the API is
        model="test-model",
        messages=[{"role": "user", "content": "test"}]
    )
    assert response is not None
```

### 3. Use Abstraction Layer

**Create a wrapper** to hide provider differences:

```python
class LLMClient:
    """Unified interface for different LLM providers."""

    def __init__(self, provider: str, api_key: str):
        self.provider = provider
        if provider == "openai":
            from openai import OpenAI
            self.client = OpenAI(api_key=api_key)
        elif provider == "mistral":
            from mistralai import Mistral
            self.client = Mistral(api_key=api_key)
        elif provider == "anthropic":
            from anthropic import Anthropic
            self.client = Anthropic(api_key=api_key)

    def chat(self, model: str, messages: List[Dict]) -> str:
        """Unified chat interface."""
        if self.provider == "openai":
            response = self.client.chat.completions.create(
                model=model, messages=messages
            )
            return response.choices[0].message.content

        elif self.provider == "mistral":
            response = self.client.chat.complete(
                model=model, messages=messages
            )
            return response.choices[0].message.content

        elif self.provider == "anthropic":
            # Anthropic requires different message format
            response = self.client.messages.create(
                model=model,
                max_tokens=1024,
                messages=messages
            )
            return response.content[0].text

# Usage
client = LLMClient("mistral", api_key)
response = client.chat("mistral-large-latest", messages)
```

### 4. Use LangChain for Unified Interface

**LangChain** provides a unified interface across providers:

```python
from langchain_openai import ChatOpenAI
from langchain_mistralai import ChatMistralAI
from langchain_anthropic import ChatAnthropic

# All use the same interface
openai_llm = ChatOpenAI(model="gpt-4")
mistral_llm = ChatMistralAI(model="mistral-large-latest")
anthropic_llm = ChatAnthropic(model="claude-3-opus-20240229")

# Same method for all
response = llm.invoke([
    {"role": "system", "content": "You are helpful."},
    {"role": "user", "content": "Hello!"}
])
```

**Benefits**:
- ✅ Consistent interface
- ✅ Easy to switch providers
- ✅ Handles API differences
- ✅ Well-tested and maintained

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

## Testing Strategy

### Test with Multiple Providers

```python
import pytest

@pytest.mark.parametrize("provider,model", [
    ("openai", "gpt-4"),
    ("mistral", "mistral-large-latest"),
    ("anthropic", "claude-3-opus-20240229"),
])
def test_llm_provider(provider, model):
    client = get_llm_client(provider)
    response = client.chat(model, [
        {"role": "user", "content": "Say hello"}
    ])
    assert "hello" in response.lower()
```

### Mock Provider Responses

```python
def test_with_mock_openai(mocker):
    mock_response = mocker.Mock()
    mock_response.choices[0].message.content = "Hello!"

    mock_client = mocker.patch('openai.OpenAI')
    mock_client.return_value.chat.completions.create.return_value = mock_response

    # Test your code
```

## Best Practices

### 1. ✅ Use Environment Variables for Provider Selection

```python
PROVIDER = os.getenv("LLM_PROVIDER", "openai")
client = get_llm_client(PROVIDER)
```

### 2. ✅ Document Provider Requirements

```markdown
## Supported LLM Providers

- OpenAI (gpt-4, gpt-3.5-turbo)
- Mistral (mistral-large-latest, mistral-medium)
- Anthropic (claude-3-opus, claude-3-sonnet)

Set `LLM_PROVIDER` environment variable to choose provider.
```

### 3. ✅ Provide Fallback Options

```python
def get_llm_client():
    provider = os.getenv("LLM_PROVIDER", "openai")

    try:
        return create_client(provider)
    except Exception as e:
        logger.warning(f"Failed to create {provider} client: {e}")
        logger.info("Falling back to OpenAI")
        return create_client("openai")
```

### 4. ✅ Log Provider Information

```python
logger.info(f"Using LLM provider: {provider}")
logger.info(f"Model: {model}")
```

## Related Issues

- **[Message Serialization](./common-pitfalls.md#message-serialization)**: LangChain messages and queues
- **[Error Handling](../patterns/error-handling.md)**: Handling provider-specific errors
- **[Testing](./testing.md)**: Testing with multiple providers

## Further Reading

- [OpenAI API Reference](https://platform.openai.com/docs/api-reference)
- [Mistral API Reference](https://docs.mistral.ai/api/)
- [Anthropic API Reference](https://docs.anthropic.com/claude/reference)
- [LangChain Chat Models](https://python.langchain.com/docs/integrations/chat/)

---

**Key Takeaway**: LLM provider APIs are NOT interchangeable. Always check the documentation, test early, and consider using an abstraction layer like LangChain! 🔌✨

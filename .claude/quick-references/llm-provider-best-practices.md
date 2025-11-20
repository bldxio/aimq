# LLM Provider Best Practices

> **Status**: Active
> **Last Updated**: 2025-11-20
> **Category**: quick-references

## Overview

Strategies for working with multiple LLM providers and avoiding common integration pitfalls.

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

## Supported LLM Providers

### OpenAI
- **Models**: gpt-4, gpt-4-turbo, gpt-3.5-turbo
- **Strengths**: Most widely supported, excellent documentation
- **Use case**: General purpose, production workloads

### Mistral
- **Models**: mistral-large-latest, mistral-medium, mistral-small
- **Strengths**: European provider, competitive pricing
- **Use case**: Privacy-conscious applications, European data residency

### Anthropic (Claude)
- **Models**: claude-3-opus, claude-3-sonnet, claude-3-haiku
- **Strengths**: Long context windows, strong reasoning
- **Use case**: Complex analysis, document processing

### Google (Gemini)
- **Models**: gemini-pro, gemini-pro-vision
- **Strengths**: Multimodal capabilities, Google integration
- **Use case**: Vision tasks, Google ecosystem integration

### Cohere
- **Models**: command, command-light
- **Strengths**: Enterprise features, embeddings
- **Use case**: Enterprise applications, semantic search

## Related

- [LLM Provider Comparison](./llm-provider-comparison.md) - API differences and gotchas
- [Error Handling](../patterns/error-handling.md) - Handling provider-specific errors
- [Testing](./testing.md) - Testing strategies

## References

- [LangChain Chat Models](https://python.langchain.com/docs/integrations/chat/)
- [OpenAI API Reference](https://platform.openai.com/docs/api-reference)
- [Mistral API Reference](https://docs.mistral.ai/api/)
- [Anthropic API Reference](https://docs.anthropic.com/claude/reference)

---

**Key Takeaway**: Use abstraction layers like LangChain to avoid provider lock-in! 🔌✨

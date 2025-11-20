# LLM Provider API Differences

Quick reference for navigating different LLM provider APIs.

## Overview

Different LLM providers have different APIs, causing runtime errors when switching providers. This guide helps you navigate those differences.

**See [@.claude/quick-references/llm-provider-apis.md](./llm-provider-apis.md) for the complete guide.**

## Quick Comparison

| Provider | Method | Response Access |
|----------|--------|-----------------|
| OpenAI | `client.chat.completions.create()` | `response.choices[0].message.content` |
| Mistral | `client.chat.complete()` | `response.choices[0].message.content` |
| Anthropic | `client.messages.create()` | `response.content[0].text` |
| Google | `model.generate_content()` | `response.text` |
| Cohere | `client.chat()` | `response.text` |

## Common Issues

### AttributeError: 'Chat' object has no attribute 'completions'

**Cause**: Using OpenAI-style API with Mistral

**Fix**: Use `client.chat.complete()` instead of `client.chat.completions.create()`

### Different Message Formats

**OpenAI/Mistral**: System message in messages array
```python
messages=[
    {"role": "system", "content": "You are helpful"},
    {"role": "user", "content": "Hello"}
]
```

**Anthropic**: System message as separate parameter
```python
system="You are helpful",
messages=[{"role": "user", "content": "Hello"}]
```

## Prevention Strategies

1. **Check provider documentation** before integrating
2. **Test with actual provider early** - don't assume compatibility
3. **Use abstraction layer** - create a unified interface
4. **Use LangChain** - handles provider differences automatically

## Related

- [@.claude/quick-references/llm-provider-apis.md](./llm-provider-apis.md) - Complete API comparison
- [@.claude/quick-references/aimq-pitfalls.md](./aimq-pitfalls.md) - AIMQ-specific issues
- [@.claude/architecture/langchain-integration.md](../architecture/langchain-integration.md) - LangChain patterns

---

**Remember**: Test with the actual provider early—don't assume APIs are compatible! 🔌✨

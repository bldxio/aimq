# Python Pitfalls

Common Python mistakes and how to avoid them.

## Deprecation Warnings

**Problem**: Using deprecated APIs that will break in future versions

**Example**:
```python
# ❌ Deprecated (Python 3.12+)
from datetime import datetime
timestamp = datetime.utcnow()

# ✅ Current
from datetime import datetime, timezone
timestamp = datetime.now(timezone.utc)
```

**Why it matters**: Deprecated APIs will be removed in future versions, causing breaking changes.

**How to avoid**:
- Always fix deprecation warnings when you see them
- Run tests with warnings enabled: `pytest -W default`
- Keep dependencies updated
- Check release notes for deprecations

## Mutable Default Arguments

**Problem**: Using mutable objects as default arguments

**Example**:
```python
# ❌ Bad: List is shared across calls
def add_item(item, items=[]):
    items.append(item)
    return items

add_item(1)  # [1]
add_item(2)  # [1, 2] - Oops!

# ✅ Good: Use None and create new list
def add_item(item, items=None):
    if items is None:
        items = []
    items.append(item)
    return items
```

## None Type Errors

**Problem**: Not checking for None before accessing attributes

**Example**:
```python
# ❌ Bad: Crashes if result is None
def process_result(result):
    return result.data  # AttributeError if result is None

# ✅ Good: Check for None first
def process_result(result):
    if result is None:
        return None
    return result.data

# ✅ Better: Use optional chaining (Python 3.10+)
def process_result(result):
    return result.data if result else None
```

**How to avoid**:
- Use type hints: `result: Optional[Result]`
- Check for None before accessing
- Use mypy for static type checking
- Test with None values

## Related

- [@.claude/standards/code-style.md](../standards/code-style.md) - Python code style guide
- [@.claude/quick-references/common-pitfalls.md](./common-pitfalls.md) - All pitfalls index
- [@.claude/quick-references/development-pitfalls.md](./development-pitfalls.md) - Testing, Git, and more

---

**Remember**: Python is forgiving, but that doesn't mean you should be careless! 🐍✨

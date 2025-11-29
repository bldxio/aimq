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

## Environment Variable Loading

**Problem**: CLI tools don't automatically load `.env` files, causing "missing env var" errors even when `.env` exists.

**Symptom**:
```bash
$ cat .env
SUPABASE_URL=https://...
SUPABASE_KEY=...

$ aimq list
Error: Missing SUPABASE_URL environment variable
```

**Root Cause**: `os.getenv()` only reads from the shell environment, not from `.env` files. You need to explicitly load `.env` or use a library that does it automatically.

**Example**:
```python
# ❌ Bad: Direct os.getenv() doesn't load .env
import os

def get_config():
    url = os.getenv("SUPABASE_URL")  # None if not exported!
    key = os.getenv("SUPABASE_KEY")
    return url, key

# ✅ Good: Use pydantic-settings to auto-load .env
from pydantic_settings import BaseSettings

class Config(BaseSettings):
    supabase_url: str
    supabase_key: str

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

config = Config()  # Automatically loads .env!

# ✅ Also good: Use python-dotenv
from dotenv import load_dotenv
import os

load_dotenv()  # Load .env into environment
url = os.getenv("SUPABASE_URL")  # Now it works!
```

**When It Happens**:
- CLI commands that need configuration
- Scripts run directly (not through shell)
- Docker containers without env vars passed in
- CI/CD without secrets configured

**Prevention**:
- Use pydantic-settings for automatic `.env` loading
- Create a centralized config module
- Document environment setup in README
- Provide helpful error messages when vars are missing

**From Phase 2 Realtime**:
```python
# src/aimq/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """Application settings with automatic .env loading"""
    supabase_url: str
    supabase_key: str

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

config = Settings()

# CLI commands use config, not os.getenv()
# from aimq.config import config
# url = config.supabase_url  # Works with .env!
```

**Testing**:
```python
def test_config_loads_from_env(monkeypatch):
    """Test that config loads from environment"""
    monkeypatch.setenv("SUPABASE_URL", "https://test.supabase.co")
    monkeypatch.setenv("SUPABASE_KEY", "test-key")

    config = Settings()
    assert config.supabase_url == "https://test.supabase.co"
    assert config.supabase_key == "test-key"
```

## Related

- [@.claude/standards/code-style.md](../standards/code-style.md) - Python code style guide
- [@.claude/quick-references/common-pitfalls.md](./common-pitfalls.md) - All pitfalls index
- [@.claude/quick-references/development-pitfalls.md](./development-pitfalls.md) - Testing, Git, and more
- [@.claude/patterns/cli-ux-patterns.md](../patterns/cli-ux-patterns.md) - CLI user experience

## References

- [pydantic-settings Documentation](https://docs.pydantic.dev/latest/concepts/pydantic_settings/)
- [python-dotenv Documentation](https://github.com/theskumar/python-dotenv)

---

**Remember**: Python is forgiving, but that doesn't mean you should be careless! 🐍✨

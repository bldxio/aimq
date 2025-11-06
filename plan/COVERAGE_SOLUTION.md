# Coverage Solution - Final Working Configuration

## TL;DR

**Solution**: Use **parallel execution for fast tests**, **sequential execution for coverage reports**.

```bash
# Fast testing (parallel, no coverage)
just test             # 30-45 seconds

# Coverage reports (sequential, reliable)
just test-cov         # 90-120 seconds, full coverage
```

## Root Cause

Coverage with pytest-xdist parallel execution has fundamental compatibility issues:
- Coverage data collection conflicts across worker processes
- Memory accumulation causes hangs even with `parallel=true` configuration
- The `coverage combine` workflow adds complexity and unreliability

## Final Configuration

### For Fast Development (`just test`)
- **Parallel execution** with `pytest -n auto`
- **No coverage** tracking
- **30-second timeout** per test
- **Result**: ~30-45 seconds, all tests pass

### For Coverage Reports (`just test-cov`)
- **Sequential execution** (no -n auto)
- **Coverage enabled** with `--cov=src/aimq`
- **60-second timeout** (longer for sequential)
- **Result**: ~90-120 seconds, full coverage report

## Files Updated

### 1. `justfile` - Test Commands

```just
# Run all tests (parallel execution with xdist)
test:
    uv run pytest -n auto --timeout=30

# Run tests with coverage report (sequential for reliability)
test-cov:
    uv run pytest --timeout=60 --cov=src/aimq --cov-report=html --cov-report=term

# Run tests without coverage (faster)
test-fast:
    uv run pytest -n auto --no-cov --timeout=30

# Run tests sequentially (for debugging)
test-seq:
    uv run pytest --timeout=30
```

### 2. `pyproject.toml` - Pytest Configuration

```toml
[tool.pytest.ini_options]
minversion = "8.0"
addopts = "-ra -q --timeout=30 --timeout-method=thread"  # NO --cov by default
testpaths = ["tests"]
markers = [
    "slow: marks tests as slow (deselect with '-m \"not slow\"')",
    "integration: marks tests as integration tests",
]
timeout = 30
timeout_method = "thread"

[tool.coverage.run]
branch = true
source = ["aimq"]
omit = ["src/aimq/commands/shared/templates/*"]
parallel = true  # Support parallel if ever needed
concurrency = ["thread", "multiprocessing"]
```

###3. `tests/conftest.py` - Test Isolation

Created comprehensive fixtures for:
- Config singleton reset
- Client module reloading
- Environment variable restoration
- Mock helpers (supabase, mistral, config)

### 4. `.github/workflows/ci.yml` - CI Configuration

```yaml
- name: Run tests with coverage (sequential)
  run: uv run pytest --timeout=60 --cov=src/aimq --cov-report=xml --cov-report=term-missing
```

## Usage Guide

### Development Workflow

```bash
# 1. Quick iteration (recommended)
just test

# 2. Test specific file
uv run pytest tests/aimq/test_worker.py -v

# 3. Test with pattern
uv run pytest -k "test_config" -v

# 4. Skip slow tests
uv run pytest -m "not slow"
```

### Coverage Reporting

```bash
# Generate full coverage report
just test-cov

# View HTML report
open htmlcov/index.html

# Check coverage percentage
uv run pytest --cov=src/aimq --cov-report=term-missing | grep TOTAL
```

### CI/CD

```bash
# Fast CI checks (no coverage)
uv run pytest -n auto --timeout=30

# Coverage for reporting (sequential)
uv run pytest --timeout=60 --cov=src/aimq --cov-report=xml
```

## Performance Comparison

| Command | Execution | Coverage | Time | Use Case |
|---------|-----------|----------|------|----------|
| `just test` | Parallel | No | ~30-45s | Development, quick checks |
| `just test-fast` | Parallel | No | ~30-45s | Same as `just test` |
| `just test-cov` | Sequential | Yes | ~90-120s | Coverage reports, CI |
| `just test-seq` | Sequential | No | ~60-90s | Debugging specific issues |

## Why This Works

### Parallel WITHOUT Coverage ✅
- Each worker process is isolated
- No shared state to coordinate
- Fast and reliable
- **Use for development**

### Sequential WITH Coverage ✅
- Single process, no coordination needed
- Coverage data collected cleanly
- Slower but reliable
- **Use for coverage reports**

### Parallel WITH Coverage ❌
- Workers compete for coverage data
- Memory accumulation and coordination issues
- Hangs at ~84% consistently
- **Don't use - it doesn't work reliably**

## Test Isolation (Bonus Fix)

The `tests/conftest.py` fixtures ensure:
1. Config singleton is reset between tests
2. Client modules are reloaded
3. Environment variables are restored
4. No state leakage between tests

This means even sequential execution is now reliable and doesn't accumulate state.

## Troubleshooting

### Tests hang even without coverage
```bash
# Check for zombie processes
ps aux | grep pytest

# Kill all pytest processes
pkill -9 -f pytest

# Run with explicit no-coverage
uv run pytest --no-cov -v
```

### Coverage report incomplete
```bash
# Clean old coverage data
rm -f .coverage .coverage.*

# Run coverage sequentially
just test-cov
```

### Need faster coverage
```bash
# Run coverage on subset of tests
uv run pytest tests/aimq/ --cov=src/aimq --cov-report=term

# Or specific modules
uv run pytest tests/aimq/test_worker.py tests/aimq/test_queue.py --cov=src/aimq
```

## Summary

**The Fix**:
1. ✅ Fast parallel testing without coverage (`just test`)
2. ✅ Reliable sequential testing with coverage (`just test-cov`)
3. ✅ Test isolation fixtures prevent state leakage
4. ✅ Proper timeout configuration (30s default, 60s for coverage)

**Trade-offs**:
- Coverage is slower (sequential execution required)
- But it's **reliable** and **completes successfully**
- For development, use `just test` (fast, no coverage)
- For reports/CI, use `just test-cov` (slower, with coverage)

**Result**:
- ✅ Tests complete without hanging
- ✅ Coverage reports work reliably
- ✅ Fast development workflow
- ✅ Proper CI/CD integration

You now have working coverage reports via `just test-cov`! 🎉

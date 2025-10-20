# Codecov Integration Setup

AIMQ uses [Codecov](https://codecov.io) to track test coverage and display coverage reports on pull requests. This guide will help you set up Codecov for your AIMQ repository.

## What is Codecov?

Codecov is a code coverage reporting tool that:
- Visualizes test coverage in pull requests
- Tracks coverage trends over time
- Shows which lines are covered/uncovered by tests
- Provides coverage badges for README.md
- Free for open source projects

## Prerequisites

- GitHub repository with AIMQ project
- Admin access to the repository
- Codecov account (free for public repositories)

## Setup Steps

### 1. Sign Up for Codecov

1. Visit [https://codecov.io](https://codecov.io)
2. Click "Sign up with GitHub"
3. Authorize Codecov to access your GitHub account

### 2. Add Your Repository

1. In Codecov dashboard, click "Add new repository"
2. Find `bldxio/aimq` in the list
3. Click "Setup repo"
4. Codecov will provide an upload token

### 3. Add Codecov Token to GitHub

1. Go to your GitHub repository: `https://github.com/bldxio/aimq`
2. Navigate to **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Add the following secret:
   - **Name**: `CODECOV_TOKEN`
   - **Value**: The token from Codecov dashboard
5. Click **Add secret**

### 4. Verify Integration

The CI workflow (`.github/workflows/ci.yml`) is already configured to upload coverage reports to Codecov. Once the token is added:

1. Push a commit or create a PR
2. Wait for CI to complete
3. Check the Codecov dashboard for coverage report
4. PR comments will show coverage changes

## Understanding Coverage Reports

### In Pull Requests

Codecov will comment on PRs with:
- **Coverage changes**: How much coverage increased/decreased
- **File-level changes**: Which files have coverage changes
- **Patch coverage**: Coverage of lines changed in the PR

Example comment:
```
Coverage: 89.2% (+0.5%) vs base
Files changed: 3
Patch coverage: 95.2%
```

### In Codecov Dashboard

The dashboard shows:
- **Overall coverage**: Project-wide test coverage percentage
- **Coverage sunburst**: Visual breakdown by file/directory
- **Coverage trend**: Historical coverage over time
- **Uncovered lines**: Specific lines that need tests

## Adding Coverage Badge to README

After setup, add the Codecov badge to your README.md:

```markdown
[![codecov](https://codecov.io/gh/bldxio/aimq/branch/main/graph/badge.svg)](https://codecov.io/gh/bldxio/aimq)
```

This will display:
[![codecov](https://codecov.io/gh/bldxio/aimq/branch/main/graph/badge.svg)](https://codecov.io/gh/bldxio/aimq)

## Current Coverage Status

AIMQ currently has **89%+ test coverage**. Our goal is to maintain coverage above 85%.

## Coverage Configuration

Coverage is configured in `pyproject.toml`:

```toml
[tool.coverage.run]
branch = true
source = ["aimq"]
omit = ["src/aimq/commands/shared/templates/*"]

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "if self.debug:",
    "raise NotImplementedError",
    "if __name__ == .__main__.:",
    "pass",
    "raise ImportError",
]
show_missing = true
skip_empty = true
```

## CI Workflow Integration

The CI workflow uploads coverage only for Python 3.11 to avoid duplicate reports:

```yaml
- name: Upload coverage to Codecov
  uses: codecov/codecov-action@v4
  if: matrix.python-version == '3.11'
  with:
    file: ./coverage.xml
    fail_ci_if_error: false
  env:
    CODECOV_TOKEN: ${{ secrets.CODECOV_TOKEN }}
```

## Running Coverage Locally

To generate coverage reports locally:

```bash
# Run tests with coverage
just test-cov

# Or manually:
uv run pytest --cov=src/aimq --cov-report=term-missing --cov-report=html

# Open HTML report in browser
open htmlcov/index.html
```

## Coverage Guidelines

### What to Test

- ✅ Core business logic (Worker, Queue, Job)
- ✅ Public APIs and functions
- ✅ Error handling paths
- ✅ Edge cases and boundary conditions
- ✅ Data transformations and validations

### What Can Be Excluded

- ❌ Third-party library code
- ❌ Generated code (templates)
- ❌ Debug/development code
- ❌ Simple getters/setters
- ❌ Type stubs and protocols

Use `# pragma: no cover` to exclude specific lines:

```python
def debug_function():  # pragma: no cover
    """Only used during development."""
    print("Debug info")
```

## Troubleshooting

### Coverage Not Uploading

1. Check CI logs for upload errors
2. Verify `CODECOV_TOKEN` is set in GitHub secrets
3. Check Codecov status page: [https://status.codecov.io](https://status.codecov.io)

### Coverage Decreased Unexpectedly

1. Check Codecov PR comment for details
2. Review which lines are uncovered
3. Add tests for new code paths
4. Check if tests are failing silently

### Coverage Too Low

1. Run `just test-cov` locally to see missing coverage
2. Identify critical paths without tests
3. Write tests for high-value code first
4. Gradually increase coverage over time

## Best Practices

1. **Write tests before merging** - Ensure new code has adequate coverage
2. **Review coverage reports** - Check Codecov comments on PRs
3. **Don't game the system** - 100% coverage doesn't mean quality tests
4. **Focus on critical paths** - Prioritize testing important functionality
5. **Keep coverage above 85%** - Our project standard

## Resources

- [Codecov Documentation](https://docs.codecov.com/)
- [Understanding Coverage Reports](https://docs.codecov.com/docs/quick-start)
- [Python Coverage.py Guide](https://coverage.readthedocs.io/)
- [Testing Best Practices](https://docs.pytest.org/en/stable/goodpractices.html)

## Support

If you encounter issues with Codecov integration:
1. Check the [Codecov Community Forum](https://community.codecov.com/)
2. Review CI logs for error messages
3. Contact the team via GitHub issues

---

**Note**: The CI workflow is already configured for Codecov. You only need to add the `CODECOV_TOKEN` secret to enable reporting.

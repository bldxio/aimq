## Description

<!-- Provide a brief description of the changes in this PR -->

## Type of Change

<!-- Mark the relevant option with an "x" -->

- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update
- [ ] Refactoring (no functional changes)
- [ ] Performance improvement
- [ ] Test coverage improvement
- [ ] Dependency update
- [ ] Release (version bump)

## Testing

<!-- Describe the tests you ran to verify your changes -->

- [ ] All existing tests pass (`just ci`)
- [ ] Added new tests for new functionality
- [ ] Tested manually (describe below)

**Manual Testing Details:**
<!-- Describe manual testing performed -->

## Conventional Commits

<!-- CHANGELOG.md is auto-generated from git commits during release workflow -->

**Commit Message Format:**
All commits MUST use conventional commit format for automatic CHANGELOG generation:

- `feat:` → Added section (new features)
- `fix:` → Fixed section (bug fixes)
- `docs:` → Changed section (documentation)
- `refactor:` → Changed section (code refactoring)
- `perf:` → Changed section (performance improvements)
- `security:` → Security section
- `deprecate:` → Deprecated section
- `remove:` → Removed section
- `test:`, `chore:`, `ci:`, `build:` → Not included in CHANGELOG

**Examples:**
```
feat: add batch processing for OCR jobs
fix: resolve race condition in worker startup
docs: update Docker deployment guide
refactor: simplify queue provider interface
```

**Manual CHANGELOG Edits (Optional):**
- [ ] I have manually edited `CHANGELOG.md` for additional clarity/context
- [ ] No manual edits needed (commits are sufficient)

Manual edits are optional and only needed to:
- Add user-facing context or breaking change warnings
- Clarify generated entries
- Combine related commits into one entry

## Checklist

- [ ] My code follows the style guidelines of this project
- [ ] I have performed a self-review of my own code
- [ ] I have commented my code, particularly in hard-to-understand areas
- [ ] I have made corresponding changes to the documentation
- [ ] My changes generate no new warnings
- [ ] I have added tests that prove my fix is effective or that my feature works
- [ ] New and existing unit tests pass locally with my changes
- [ ] Any dependent changes have been merged and published

## Related Issues

<!-- Link to related issues using #issue_number -->

Fixes #
Closes #
Related to #

## Additional Notes

<!-- Any additional information that reviewers should know -->

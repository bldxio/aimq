# Release Process

This document outlines the process for creating and publishing new releases of AIMQ.

## Version Numbering

We follow [Semantic Versioning](https://semver.org/):

- MAJOR version for incompatible API changes
- MINOR version for new functionality in a backward compatible manner
- PATCH version for backward compatible bug fixes

## Release Checklist

1. **Update Version**

   - Update version in `pyproject.toml`
   - Update CHANGELOG.md
   - Commit changes: `git commit -m "Bump version to X.Y.Z"`

1. **Run Tests**

   ```bash
   poetry run pytest
   poetry run pytest --cov=src
   ```

1. **Build Documentation**

   ```bash
   poetry run mkdocs build
   ```

1. **Create Release Branch**

   ```bash
   git checkout -b release/vX.Y.Z
   git push origin release/vX.Y.Z
   ```

1. **Create Pull Request**

   - Title: "Release vX.Y.Z"
   - Include changelog in description
   - Get required approvals

1. **Merge and Tag**

   ```bash
   git checkout main
   git pull origin main
   git tag -a vX.Y.Z -m "Release vX.Y.Z"
   git push origin vX.Y.Z
   ```

1. **Build and Publish**

   ```bash
   poetry build
   poetry publish
   ```

1. **Deploy Documentation**

   ```bash
   poetry run mkdocs gh-deploy
   ```

## Post-Release

1. Update version to next development version in `pyproject.toml`
1. Create new section in CHANGELOG.md for unreleased changes
1. Announce release in appropriate channels

## Hotfix Process

For critical bugs in production:

1. Create hotfix branch from the release tag
1. Fix the bug and update patch version
1. Create PR back to both `main` and the release branch
1. Follow steps 6-8 from the release checklist

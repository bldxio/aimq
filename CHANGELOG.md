# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Automated PyPI publishing workflow via GitHub Actions
- Comprehensive CI/CD pipeline (lint, type-check, test on Python 3.11-3.13)
- Release management `just` commands for version bumping
- Version synchronization script for pyproject.toml and __init__.py
- Beta/RC/stable release workflows
- TestPyPI publishing for dev branch
- PyPI publishing for main branch
- Custom `/release` slash command for guided release workflow in Claude Code
- Pre-commit hook for version synchronization validation
- Comprehensive Codecov integration documentation
- Enhanced testing documentation with coverage best practices
- Automatic CHANGELOG generation from git commits using conventional commit format
- CHANGELOG finalization script for stable releases with git tag links
- `just changelog` command for generating CHANGELOG entries
- `just changelog-finalize` command for stable release CHANGELOG sections
- Conventional commits documentation and best practices guide
- Integrated CHANGELOG automation into release workflows
- Git URL loading support for Docker deployments
- Enhanced Docker deployment guide
- Kubernetes deployment examples

### Changed
- Migrated from Poetry to uv for dependency management
- Updated all GitHub Actions workflows to use uv
- Improved release process with guided workflows
- Documentation updated to reflect uv migration and tag creation strategy
- Improved type hints and type checker compatibility across codebase
- Apply black formatting to test files
- CHANGELOG workflow: beta releases update [Unreleased], stable releases create version sections

### Removed
- Poetry dependency management
- Beta version sections from CHANGELOG (consolidated into [Unreleased])

### Fixed
- Version synchronization between pyproject.toml and __init__.py
- Test coverage improvements (89%+)
- Resolve test failures in CI environment
- Correct pytest minversion and black formatting

### Security
- Update torch minimum version to >=2.8.0 to fix resource shutdown vulnerability
- Add explicit langchain-text-splitters>=0.3.9 dependency to prevent CVE-2025-6985 (XXE attack vulnerability)

## [0.1.0] - 2025-01-17

### Added
- Initial release
- Basic project structure
- Core functionality for processing tasks from Supabase pgmq
- OCR processing capabilities
- Docker configuration for development and production environments

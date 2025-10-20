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

### Changed
- Migrated from Poetry to uv for dependency management
- Updated all GitHub Actions workflows to use uv
- Improved release process with guided workflows
- Documentation updated to reflect uv migration

### Deprecated
- N/A

### Removed
- Poetry dependency management

### Fixed
- Version synchronization between pyproject.toml and __init__.py

### Security
- N/A

## [0.1.1b1] - 2025-10-19

### Added
- Git URL loading support for Docker deployments
- Enhanced Docker deployment guide
- Kubernetes deployment examples

### Changed
- Version bumped to beta for testing release workflow

### Fixed
- Test coverage improvements (89%+)

## [0.1.0] - 2025-01-17

### Added
- Initial release
- Basic project structure
- Core functionality for processing tasks from Supabase pgmq
- OCR processing capabilities
- Docker configuration for development and production environments

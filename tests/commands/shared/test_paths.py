"""Tests for project path management functionality in the shared commands package.

This module contains tests for the ProjectPath class and related functionality in the
shared commands package.

"""

from pathlib import Path

import pytest
from freezegun import freeze_time

from aimq.commands.shared.paths import ProjectPath


@pytest.fixture
def temp_project_dir(tmp_path):
    """Create a temporary project directory."""
    return tmp_path


@pytest.fixture
def project_path(temp_project_dir):
    """Create a ProjectPath instance with a temporary root directory."""
    return ProjectPath(temp_project_dir)


def test_project_path_init_with_root():
    """Test ProjectPath initialization with a specific root."""
    root = Path("/test/path")
    paths = ProjectPath(root)
    assert paths.root == root


def test_project_path_init_without_root(monkeypatch):
    """Test ProjectPath initialization without root (should use cwd)."""
    test_cwd = Path("/test/cwd")
    monkeypatch.setattr(Path, "cwd", lambda: test_cwd)
    paths = ProjectPath()
    assert paths.root == test_cwd


def test_supabase_path(project_path, temp_project_dir):
    """Test supabase directory path property."""
    assert project_path.supabase == temp_project_dir / "supabase"


def test_migrations_path(project_path, temp_project_dir):
    """Test migrations directory path property."""
    assert project_path.migrations == temp_project_dir / "supabase" / "migrations"


def test_supabase_config_path(project_path, temp_project_dir):
    """Test supabase config file path property."""
    assert project_path.supabase_config == temp_project_dir / "supabase" / "config.toml"


@freeze_time("2025-01-21 01:02:03", tz_offset=0)
def test_migration_path(project_path):
    """Test migration path generation with frozen time."""
    migration_path = project_path.migration_path("test_migration")
    expected_name = "20250121010203_test_migration.sql"
    assert migration_path.name == expected_name


def test_find_existing_migration(project_path):
    """Test finding existing migration files."""
    # Create a test migration file
    migrations_dir = project_path.migrations
    migrations_dir.mkdir(parents=True)
    test_file = migrations_dir / "20250121010203_test_migration.sql"
    test_file.touch()

    # Test finding the migration
    found = project_path.find_existing_migration("test_migration")
    assert found == test_file

    # Test with non-existent migration
    not_found = project_path.find_existing_migration("nonexistent")
    assert not_found is None


def test_find_existing_migration_no_dir(project_path):
    """Test finding migration when migrations directory doesn't exist."""
    assert project_path.find_existing_migration("test") is None


def test_get_current_timestamp():
    """Test timestamp generation."""
    with freeze_time("2025-01-21 01:02:03", tz_offset=0):
        timestamp = ProjectPath.get_current_timestamp()
        assert timestamp == "20250121010203"

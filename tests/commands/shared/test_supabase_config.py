"""Tests for the Supabase configuration management in the shared commands package."""

from pathlib import Path
from typing import cast

import pytest
import tomlkit
from tomlkit import TOMLDocument, items

from aimq.commands.shared.config import SupabaseConfig
from aimq.commands.shared.paths import ProjectPath


@pytest.fixture
def temp_project_dir(tmp_path: Path) -> Path:
    """Create a temporary project directory.

    Args:
        tmp_path: Pytest fixture providing temporary directory path.

    Returns:
        Path: Path to temporary project directory.
    """
    return tmp_path


@pytest.fixture
def project_path(temp_project_dir: Path) -> ProjectPath:
    """Create a ProjectPath instance with a temporary root directory.

    Args:
        temp_project_dir: Temporary directory path.

    Returns:
        ProjectPath: Configured project path instance.
    """
    return ProjectPath(temp_project_dir)


@pytest.fixture
def supabase_config(project_path: ProjectPath) -> SupabaseConfig:
    """Create a SupabaseConfig instance with a temporary project path.

    Args:
        project_path: Project path instance.

    Returns:
        SupabaseConfig: Configured Supabase config instance.
    """
    return SupabaseConfig(project_path)


@pytest.fixture
def config_with_template(
    supabase_config: SupabaseConfig, project_path: ProjectPath
) -> SupabaseConfig:
    """Create a config with template content.

    Args:
        supabase_config: Supabase config instance.
        project_path: Project path instance.

    Returns:
        SupabaseConfig: Configured Supabase config instance with template content.
    """
    # Create necessary directories
    project_path.supabase.mkdir(parents=True)

    # Create a minimal config file
    config: TOMLDocument = tomlkit.document()
    config.add("api", {"schemas": ["public", "auth"]})  # type: ignore

    with open(project_path.supabase_config, "w") as f:
        tomlkit.dump(config, f)

    return supabase_config


def test_load_creates_config_if_not_exists(
    supabase_config: SupabaseConfig, project_path: ProjectPath
) -> None:
    """Test that load creates config file if it doesn't exist.

    Args:
        supabase_config: Supabase config instance.
        project_path: Project path instance.
    """
    assert not project_path.supabase_config.exists()
    supabase_config.load()
    assert project_path.supabase_config.exists()


def test_load_ensures_api_schemas_exists(
    supabase_config: SupabaseConfig, project_path: ProjectPath
) -> None:
    """Test that load ensures api.schemas exists in config.

    Args:
        supabase_config: Supabase config instance.
        project_path: Project path instance.
    """
    project_path.supabase.mkdir(parents=True)

    # Create empty config
    with open(project_path.supabase_config, "w") as f:
        tomlkit.dump(tomlkit.document(), f)

    config = supabase_config.load()
    api_table = cast(items.Table, config["api"])
    assert "schemas" in api_table
    assert isinstance(api_table["schemas"], items.Array)


def test_enable_adds_pgmq_public(config_with_template: SupabaseConfig) -> None:
    """Test enabling PGMQ adds pgmq_public to schemas.

    Args:
        config_with_template: Supabase config instance with template content.
    """
    config_with_template.load()
    config_with_template.enable()
    api_table = cast(items.Table, config_with_template.config["api"])
    schemas = cast(items.Array, api_table["schemas"])
    assert "pgmq_public" in schemas


def test_enable_idempotent(config_with_template: SupabaseConfig) -> None:
    """Test enabling PGMQ multiple times doesn't duplicate pgmq_public.

    Args:
        config_with_template: Supabase config instance with template content.
    """
    config_with_template.load()
    config_with_template.enable()
    config_with_template.enable()
    api_table = cast(items.Table, config_with_template.config["api"])
    schemas = cast(items.Array, api_table["schemas"])
    schema_list = [str(item) for item in schemas]
    assert schema_list.count("pgmq_public") == 1


def test_disable_removes_pgmq_public(config_with_template: SupabaseConfig) -> None:
    """Test disabling PGMQ removes pgmq_public from schemas.

    Args:
        config_with_template: Supabase config instance with template content.
    """
    config_with_template.load()
    # First enable it
    config_with_template.enable()
    api_table = cast(items.Table, config_with_template.config["api"])
    schemas = cast(items.Array, api_table["schemas"])
    assert "pgmq_public" in schemas

    # Then disable it
    config_with_template.disable()
    api_table = cast(items.Table, config_with_template.config["api"])
    schemas = cast(items.Array, api_table["schemas"])
    assert "pgmq_public" not in schemas


def test_disable_idempotent(config_with_template: SupabaseConfig) -> None:
    """Test disabling PGMQ when it's already disabled doesn't cause errors.

    Args:
        config_with_template: Supabase config instance with template content.
    """
    config_with_template.load()
    config_with_template.disable()  # Should not raise any errors

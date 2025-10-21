from pathlib import Path
from unittest.mock import Mock, mock_open, patch

import pytest

from aimq.commands.shared.migration import SupabaseMigrations
from aimq.commands.shared.paths import ProjectPath


@pytest.fixture
def project_path() -> Mock:
    """
    Fixture providing a mocked ProjectPath instance.

    Returns:
        Mock: Mocked ProjectPath instance
    """
    mock = Mock(spec=ProjectPath)
    mock.migrations = Path("/test/migrations")
    return mock


@pytest.fixture
def migrations(project_path: Mock) -> SupabaseMigrations:
    """
    Fixture providing a SupabaseMigrations instance with mocked ProjectPath.

    Args:
        project_path: Mocked ProjectPath fixture

    Returns:
        SupabaseMigrations: Instance for testing
    """
    return SupabaseMigrations(project_path)


def test_get_template_exists(migrations: SupabaseMigrations) -> None:
    """
    Test _get_template when template exists.

    Args:
        migrations: SupabaseMigrations fixture
    """
    with patch.object(Path, "exists", return_value=True):
        template_path = migrations._get_template("test.sql")
        assert isinstance(template_path, Path)
        assert template_path.name == "test.sql"


def test_get_template_not_exists(migrations: SupabaseMigrations) -> None:
    """
    Test _get_template when template doesn't exist.

    Args:
        migrations: SupabaseMigrations fixture
    """
    with patch.object(Path, "exists", return_value=False):
        with pytest.raises(FileNotFoundError):
            migrations._get_template("nonexistent.sql")


def test_create_migration_new(migrations: SupabaseMigrations, project_path: Mock) -> None:
    """
    Test create_migration for a new migration.

    Args:
        migrations: SupabaseMigrations fixture
        project_path: ProjectPath mock
    """
    template_content = "create table {{table_name}};"
    context = {"table_name": "test_table"}
    expected_content = "create table test_table;"

    # Mock file operations
    project_path.find_existing_migration.return_value = None
    project_path.migration_path.return_value = Path("/test/migrations/test_migration.sql")

    with (
        patch("builtins.open", mock_open(read_data=template_content)) as mock_file,
        patch("os.makedirs") as mock_makedirs,
        patch.object(Path, "exists", return_value=True),
    ):
        result = migrations.create_migration("test_migration", "template.sql", context)

        # Verify the migration was created correctly
        assert result == Path("/test/migrations/test_migration.sql")
        mock_makedirs.assert_called_once_with(migrations.project_path.migrations, exist_ok=True)

        # Verify file operations
        write_handle = mock_file.return_value.__enter__.return_value
        write_handle.write.assert_called_once_with(expected_content)


def test_create_migration_existing(migrations: SupabaseMigrations, project_path: Mock) -> None:
    """
    Test create_migration when migration already exists.

    Args:
        migrations: SupabaseMigrations fixture
        project_path: ProjectPath mock
    """
    existing_path = Path("/test/migrations/existing.sql")
    project_path.find_existing_migration.return_value = existing_path

    result = migrations.create_migration("existing", "template.sql")
    assert result == existing_path
    project_path.migration_path.assert_not_called()


def test_setup_aimq_migration(migrations: SupabaseMigrations) -> None:
    """
    Test setup_aimq_migration creates correct migration.

    Args:
        migrations: SupabaseMigrations fixture
    """
    with patch.object(migrations, "create_migration") as mock_create:
        migrations.setup_aimq_migration()
        mock_create.assert_called_once_with(name="setup_aimq", template_name="setup_aimq.sql")


def test_create_queue_migration(migrations: SupabaseMigrations) -> None:
    """
    Test create_queue_migration creates migration with correct context.

    Args:
        migrations: SupabaseMigrations fixture
    """
    queue_name = "test_queue"
    with patch.object(migrations, "create_migration") as mock_create:
        migrations.create_queue_migration(queue_name)
        mock_create.assert_called_once_with(
            name=f"create_queue_{queue_name}",
            template_name="create_queue.sql",
            context={"queue_name": queue_name},
        )

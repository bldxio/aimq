"""Tests for tool input validation."""

from unittest.mock import MagicMock

import pytest
from langchain.tools import BaseTool
from pydantic import BaseModel, Field, ValidationError  # noqa: F401

from aimq.agents.validation import ToolInputValidator
from aimq.common.exceptions import ToolValidationError


class MockToolSchema(BaseModel):
    """Mock Pydantic schema for tool validation."""

    query: str = Field(..., description="Query string")
    limit: int = Field(default=10, ge=1, le=100)


class ToolWithSchema(BaseTool):
    """Test tool with Pydantic schema."""

    name: str = "test_tool"
    description: str = "Test tool with schema"
    args_schema: type[BaseModel] = MockToolSchema

    def _run(self, query: str, limit: int = 10) -> str:
        return f"Query: {query}, Limit: {limit}"


class ToolWithoutSchema(BaseTool):
    """Test tool without Pydantic schema."""

    name: str = "no_schema_tool"
    description: str = "Test tool without schema"

    def _run(self, input: str) -> str:
        return f"Input: {input}"


def test_validator_initialization():
    """Test ToolInputValidator can be initialized."""
    validator = ToolInputValidator()
    assert validator is not None


def test_validate_with_valid_input():
    """Test validation passes with valid input."""
    validator = ToolInputValidator()
    tool = ToolWithSchema()

    input_data = {"query": "test", "limit": 5}
    result = validator.validate(tool, input_data)

    assert result["query"] == "test"
    assert result["limit"] == 5


def test_validate_with_invalid_input():
    """Test validation fails with invalid input."""
    validator = ToolInputValidator()
    tool = ToolWithSchema()

    # Missing required field
    input_data = {"limit": 5}

    with pytest.raises(ToolValidationError, match="Invalid input"):
        validator.validate(tool, input_data)


def test_validate_with_out_of_range_value():
    """Test validation fails with out-of-range value."""
    validator = ToolInputValidator()
    tool = ToolWithSchema()

    # limit must be >= 1 and <= 100
    input_data = {"query": "test", "limit": 200}

    with pytest.raises(ToolValidationError):
        validator.validate(tool, input_data)


def test_validate_without_schema():
    """Test validation passes through when tool has no schema."""
    validator = ToolInputValidator()
    tool = ToolWithoutSchema()

    input_data = {"input": "test"}
    result = validator.validate(tool, input_data)

    # Should pass through without validation
    assert result == input_data


def test_validate_file_path_safe():
    """Test safe file path validation."""
    validator = ToolInputValidator()

    # Relative paths are safe
    validator.validate_file_path("data/file.txt")
    validator.validate_file_path("subdir/file.json")


def test_validate_file_path_traversal():
    """Test path traversal is blocked."""
    validator = ToolInputValidator()

    with pytest.raises(ToolValidationError, match="Path traversal not allowed"):
        validator.validate_file_path("../etc/passwd")

    with pytest.raises(ToolValidationError, match="Path traversal not allowed"):
        validator.validate_file_path("data/../../etc/passwd")


def test_validate_file_path_sensitive_files():
    """Test access to sensitive files is blocked."""
    validator = ToolInputValidator()

    with pytest.raises(ToolValidationError, match="sensitive file not allowed"):
        validator.validate_file_path("/etc/passwd")

    with pytest.raises(ToolValidationError, match="sensitive file not allowed"):
        validator.validate_file_path(".ssh/id_rsa")

    with pytest.raises(ToolValidationError, match="sensitive file not allowed"):
        validator.validate_file_path(".env")


def test_validate_file_path_absolute_allowed():
    """Test absolute paths with allowed patterns."""
    validator = ToolInputValidator()

    # Allow /tmp/* paths
    validator.validate_file_path("/tmp/file.txt", allowed_patterns=["/tmp/*"])


def test_validate_file_path_absolute_not_allowed():
    """Test absolute paths not in allowed patterns."""
    validator = ToolInputValidator()

    with pytest.raises(ToolValidationError, match="not in allowed patterns"):
        validator.validate_file_path("/home/user/file.txt", allowed_patterns=["/tmp/*"])


def test_validate_sql_query_safe():
    """Test safe SQL queries pass validation."""
    validator = ToolInputValidator()

    # Safe queries
    validator.validate_sql_query("SELECT * FROM users")
    validator.validate_sql_query("SELECT id, name FROM products WHERE active = true")
    validator.validate_sql_query("INSERT INTO logs (message) VALUES ('test')")


def test_validate_sql_query_drop_table():
    """Test DROP TABLE is blocked."""
    validator = ToolInputValidator()

    with pytest.raises(ToolValidationError, match="Suspicious SQL pattern"):
        validator.validate_sql_query("DROP TABLE users")

    with pytest.raises(ToolValidationError, match="Suspicious SQL pattern"):
        validator.validate_sql_query("drop table users")


def test_validate_sql_query_delete():
    """Test DELETE FROM is blocked."""
    validator = ToolInputValidator()

    with pytest.raises(ToolValidationError, match="Suspicious SQL pattern"):
        validator.validate_sql_query("DELETE FROM users")


def test_validate_sql_query_truncate():
    """Test TRUNCATE is blocked."""
    validator = ToolInputValidator()

    with pytest.raises(ToolValidationError, match="Suspicious SQL pattern"):
        validator.validate_sql_query("TRUNCATE TABLE users")


def test_validate_sql_query_alter_table():
    """Test ALTER TABLE is blocked."""
    validator = ToolInputValidator()

    with pytest.raises(ToolValidationError, match="Suspicious SQL pattern"):
        validator.validate_sql_query("ALTER TABLE users ADD COLUMN test VARCHAR(100)")


def test_validate_sql_query_exec():
    """Test EXEC/EXECUTE is blocked."""
    validator = ToolInputValidator()

    with pytest.raises(ToolValidationError, match="Suspicious SQL pattern"):
        validator.validate_sql_query("EXEC sp_executesql 'DROP TABLE users'")

    with pytest.raises(ToolValidationError, match="Suspicious SQL pattern"):
        validator.validate_sql_query("EXECUTE sp_executesql 'DROP TABLE users'")


def test_validate_sql_query_comment_injection():
    """Test SQL comment injection patterns are blocked."""
    validator = ToolInputValidator()

    with pytest.raises(ToolValidationError, match="Suspicious SQL pattern"):
        validator.validate_sql_query("SELECT * FROM users;-- DROP TABLE users")

    with pytest.raises(ToolValidationError, match="Suspicious SQL pattern"):
        validator.validate_sql_query("SELECT * FROM users/**/WHERE id = 1")


def test_validate_with_default_values():
    """Test validation with Pydantic default values."""
    validator = ToolInputValidator()
    tool = ToolWithSchema()

    # Only provide required field, use default for limit
    input_data = {"query": "test"}
    result = validator.validate(tool, input_data)

    assert result["query"] == "test"
    assert result["limit"] == 10  # Default value


def test_validate_tool_name_in_error():
    """Test tool name appears in validation error."""
    validator = ToolInputValidator()
    tool = ToolWithSchema()

    input_data = {}  # Missing required field

    with pytest.raises(ToolValidationError) as exc_info:
        validator.validate(tool, input_data)

    assert "test_tool" in str(exc_info.value)


def test_validate_file_path_normalized():
    """Test file paths are normalized."""
    validator = ToolInputValidator()

    # Redundant slashes are normalized
    validator.validate_file_path("data//file.txt")
    validator.validate_file_path("./data/file.txt")


def test_validate_handles_unexpected_error():
    """Test validation handles unexpected errors gracefully."""
    validator = ToolInputValidator()

    # Create a tool that will raise an unexpected error
    tool = MagicMock(spec=BaseTool)
    tool.name = "error_tool"
    tool.args_schema = MagicMock()
    tool.args_schema.side_effect = RuntimeError("Unexpected error")

    with pytest.raises(ToolValidationError, match="Tool validation failed"):
        validator.validate(tool, {"test": "data"})

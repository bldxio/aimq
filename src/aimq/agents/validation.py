"""
Tool input validation for security.

Validates tool inputs before execution to prevent injection attacks.
This module implements Fix #12 from PLAN_FIXES.md.
"""

import logging
import os

from langchain.tools import BaseTool
from pydantic import ValidationError

from aimq.common.exceptions import ToolValidationError

logger = logging.getLogger(__name__)


class ToolInputValidator:
    """Validates tool inputs against tool schemas for security (Fix #12)."""

    def validate(self, tool: BaseTool, input_data: dict) -> dict:
        """Validate tool input against tool's args_schema.

        Args:
            tool: LangChain tool to validate against
            input_data: Input data from LLM or user

        Returns:
            Validated input dict

        Raises:
            ToolValidationError: If validation fails

        Examples:
            >>> validator = ToolInputValidator()
            >>> validated = validator.validate(read_file_tool, {"path": "file.txt"})
        """
        tool_name = tool.name

        try:
            if hasattr(tool, "args_schema") and tool.args_schema:
                validated = tool.args_schema(**input_data)
                logger.debug(f"Tool '{tool_name}' input validated")
                return validated.model_dump()
            else:
                logger.warning(
                    f"Tool '{tool_name}' has no args_schema, " f"input validation skipped"
                )
                return input_data

        except ValidationError as e:
            logger.error(
                f"Tool '{tool_name}' input validation failed: {e}",
                extra={"tool": tool_name, "input": input_data},
            )
            raise ToolValidationError(f"Invalid input for tool '{tool_name}': {e}") from e

        except Exception as e:
            logger.error(
                f"Unexpected error validating tool '{tool_name}': {e}",
                exc_info=True,
            )
            raise ToolValidationError(f"Tool validation failed for '{tool_name}': {e}") from e

    def validate_file_path(self, path: str, allowed_patterns: list[str] | None = None) -> None:
        """Validate file path for security (Fix #12).

        Prevents:
        - Path traversal attacks (../)
        - Absolute paths outside allowed directories
        - Access to sensitive system files

        Args:
            path: File path to validate
            allowed_patterns: List of allowed path patterns (glob style)

        Raises:
            ToolValidationError: If path is invalid or unauthorized

        Examples:
            >>> validator = ToolInputValidator()
            >>> validator.validate_file_path("data/file.txt")
            >>> validator.validate_file_path("/tmp/file.txt", ["/tmp/*"])
        """
        normalized = os.path.normpath(path)

        if ".." in normalized:
            raise ToolValidationError(f"Path traversal not allowed: {path}")

        if os.path.isabs(normalized):
            if allowed_patterns:
                from fnmatch import fnmatch

                if not any(fnmatch(normalized, pattern) for pattern in allowed_patterns):
                    raise ToolValidationError(f"Absolute path not in allowed patterns: {path}")

        sensitive = ["/etc/passwd", "/etc/shadow", ".ssh/", ".env"]
        if any(s in normalized for s in sensitive):
            raise ToolValidationError(f"Access to sensitive file not allowed: {path}")

        logger.debug(f"File path validated: {normalized}")

    def validate_sql_query(self, query: str) -> None:
        """Validate SQL query for basic injection patterns (Fix #12).

        This is a simple check - use parameterized queries in production.

        Args:
            query: SQL query to validate

        Raises:
            ToolValidationError: If query contains suspicious patterns

        Examples:
            >>> validator = ToolInputValidator()
            >>> validator.validate_sql_query("SELECT * FROM users")
            >>> # Raises for: "DROP TABLE users"
        """
        suspicious = [
            "DROP TABLE",
            "DELETE FROM",
            "TRUNCATE",
            "ALTER TABLE",
            "EXEC ",
            "EXECUTE ",
            ";--",
            "/**/",
        ]

        query_upper = query.upper()

        for pattern in suspicious:
            if pattern in query_upper:
                raise ToolValidationError(f"Suspicious SQL pattern detected: {pattern}")

        logger.debug("SQL query validated")

# CLI Command Conventions

This document outlines the conventions for writing CLI commands in the AIMQ project.
These conventions ensure consistency and maintainability across all command
implementations.

## File Structure

Each command should be in its own module within the `commands` directory and follow
these conventions:

1. **Module Documentation**:

   - Each module must start with a docstring describing the command's purpose
   - Use triple quotes (`"""`) for docstrings

1. **Imports**:

   - Group imports in the following order:
     1. Standard library imports
     1. Third-party imports (e.g., `typer`)
     1. Local imports from `aimq`
   - Use `isort` for consistent import ordering

## Command Implementation

### 1. Arguments and Options

- Define command arguments and options as module-level constants:

  ```python
  DIRECTORY_ARG = typer.Argument(
      default=None,
      help="Directory to initialize AIMQ project in",
  )

  LOG_LEVEL_OPTION = typer.Option(
      LogLevel.INFO,
      "--log-level",
      "-l",
      help="Set the log level",
      case_sensitive=False,
  )
  ```

- Never use function calls in argument defaults directly

- Use descriptive names with `_ARG` suffix for arguments and `_OPTION` suffix for
  options

- Always include help text for each argument and option

### 2. Function Definitions

- Use type hints for all parameters and return values:

  ```python
  def init(
      directory: Optional[str] = DIRECTORY_ARG,
      log_level: LogLevel = LOG_LEVEL_OPTION,
  ) -> None:
  ```

- Include comprehensive Google-style docstrings with:

  - Brief description
  - Args section
  - Raises section (if applicable)
  - Returns section (if returning a value)

### 3. Error Handling

- Use try/except blocks for error handling
- Raise `typer.Exit(1)` for command failures
- Include descriptive error messages using `typer.echo(..., err=True)`
- Log errors appropriately when logging is available

### 4. Main Block

- Include a `__main__` block using `typer.run()`:

  ```python
  if __name__ == "__main__":
      typer.run(command_function)
  ```

## Examples

### Basic Command Structure

```python
"""Command description."""

from typing import Optional

import typer

from aimq.some_module import SomeClass

SOME_ARG = typer.Argument(
    default=None,
    help="Description of argument",
)

def command_name(
    some_arg: Optional[str] = SOME_ARG,
) -> None:
    """Command description.

    Args:
        some_arg: Description of argument.

    Raises:
        typer.Exit: If command fails.
    """
    try:
        # Command implementation
        pass
    except Exception as e:
        typer.echo(f"Error: {str(e)}", err=True)
        raise typer.Exit(1)

if __name__ == "__main__":
    typer.run(command_name)
```

### Enum Options

For commands with enumerated options:

```python
class Provider(str, Enum):
    """Provider options for the command.

    Supported providers:
        OPTION_ONE: Description
        OPTION_TWO: Description
    """

    OPTION_ONE = "one"
    OPTION_TWO = "two"
```

## Best Practices

1. **Modularity**:

   - Keep commands focused on a single responsibility
   - Break complex commands into smaller functions

1. **Documentation**:

   - Document all public functions and classes
   - Include examples in docstrings for complex commands
   - Keep help text concise but informative

1. **Testing**:

   - Write tests for all commands
   - Test both success and failure cases
   - Mock external dependencies

1. **Error Messages**:

   - Make error messages clear and actionable
   - Include relevant context in error messages
   - Use appropriate exit codes

1. **Code Style**:

   - Follow PEP 8 guidelines
   - Use Black for code formatting
   - Maximum line length: 88 characters

## Reference Commands

See these commands for reference implementations:

- `init.py`: Project initialization
- `send.py`: Queue job submission
- `start.py`: Worker process management

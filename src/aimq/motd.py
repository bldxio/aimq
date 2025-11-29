"""MOTD (Message of the Day) and queue information display."""

import random
import re
import sys
from pathlib import Path
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from aimq.worker import Worker


def _parse_motd_content(content: str) -> str:
    """Parse markdown with optional YAML front matter.

    Extracts 'messages' list from front matter and randomly picks one
    to replace {message} placeholder in content.

    Args:
        content: Markdown content with optional YAML front matter

    Returns:
        Parsed markdown with {message} replaced
    """
    # Extract YAML front matter if present (between --- markers)
    match = re.match(r"^---\n(.*?)\n---\n(.*)$", content, re.DOTALL)
    if match:
        try:
            import yaml

            front_matter = yaml.safe_load(match.group(1))
            content = match.group(2)

            # Replace {message} with random message
            if front_matter and "messages" in front_matter:
                messages = front_matter["messages"]
                if messages:
                    random_msg = random.choice(messages)
                    content = content.replace("{message}", random_msg)
        except Exception:
            # If YAML parsing fails, just use content as-is
            pass

    return content


def _get_motd_content(motd: Optional[str | bool]) -> Optional[str]:
    """Resolve and load MOTD content.

    Args:
        motd: MOTD source:
            - None: Auto-detect MOTD.md in script dir, fallback to built-in
            - False: Disable MOTD
            - True: Use module's __doc__ string
            - str: Path to markdown file

    Returns:
        Markdown content string or None if disabled
    """
    # Explicitly disabled
    if motd is False:
        return None

    # Use module docstring
    if motd is True:
        main_module = sys.modules.get("__main__")
        if main_module and hasattr(main_module, "__doc__"):
            return main_module.__doc__
        return None

    # Auto-detect or explicit path
    if motd is None:
        # Try to find MOTD.md in script directory
        main_module = sys.modules.get("__main__")
        if main_module and hasattr(main_module, "__file__"):
            script_dir = Path(main_module.__file__).parent
            motd_file = script_dir / "MOTD.md"

            if motd_file.exists():
                return motd_file.read_text()

        # Fallback to built-in MOTD
        builtin_motd = Path(__file__).parent / "MOTD.md"
        if builtin_motd.exists():
            return builtin_motd.read_text()

        return None

    # Explicit file path
    motd_path = Path(motd)
    if motd_path.exists():
        return motd_path.read_text()

    raise FileNotFoundError(f"MOTD file not found: {motd}")


def _build_queue_list(worker: "Worker") -> str:
    """Build markdown-formatted list of registered queues.

    Args:
        worker: Worker instance with registered queues

    Returns:
        Markdown string with queue details
    """
    if not worker.queues:
        return "\n**No queues registered.**\n"

    md_lines = [f"\n## Registered Queues ({len(worker.queues)} total)\n"]

    for queue in worker.queues.values():
        # Extract description from docstring
        doc = None
        if hasattr(queue.runnable, "__doc__") and queue.runnable.__doc__:
            doc = queue.runnable.__doc__
        elif hasattr(queue.runnable, "__class__"):
            doc = queue.runnable.__class__.__doc__

        # Get first line as summary
        description = "No description available"
        if doc:
            first_line = doc.strip().split("\n")[0]
            description = first_line.strip()

        # Build queue section
        md_lines.append(f"\n### `{queue.name}` (timeout: {queue.timeout}s)")
        md_lines.append(f"{description}\n")

        # Add configuration details
        md_lines.append("**Configuration:**")
        md_lines.append(f"- Tags: {', '.join(queue.tags) if queue.tags else 'None'}")
        md_lines.append(f"- Max Retries: {queue.max_retries}")
        md_lines.append(f"- DLQ: {queue.dlq if queue.dlq else 'None'}")
        md_lines.append(f"- Delete on Finish: {'Yes' if queue.delete_on_finish else 'No'}")

    return "\n".join(md_lines)


def print_startup_info(
    worker: "Worker",
    motd: Optional[str | bool] = None,
    show_info: bool = False,
) -> None:
    """Display MOTD and queue information using Rich Markdown.

    Args:
        worker: Worker instance with registered queues
        motd: MOTD source:
            - None (default): Auto-detect MOTD.md or use built-in
            - False: Disable MOTD
            - True: Use module docstring
            - str: Path to markdown file
        show_info: Whether to show queue list
    """
    from rich.console import Console
    from rich.markdown import Markdown
    from rich.panel import Panel

    console = Console()

    # Display MOTD
    motd_content = _get_motd_content(motd)
    if motd_content:
        # Parse front matter and get random message
        parsed_content = _parse_motd_content(motd_content)

        # Render as markdown in a panel
        md = Markdown(parsed_content)
        console.print(Panel(md, border_style="cyan", padding=(1, 2)))
        console.print()  # Blank line

    # Display queue list if requested
    if show_info:
        queue_list = _build_queue_list(worker)
        md = Markdown(queue_list)
        console.print(Panel(md, title="Queue Information", border_style="cyan", padding=(1, 2)))
        console.print()  # Blank line
